"""
Mini-Courier Planner
Algorithms: Merge Sort, 0/1 Knapsack (Dynamic Programming),
Dijkstra's shortest path, and Nearest-Neighbor TSP approximation.
Run: python main.py
"""
from __future__ import annotations
import csv
import heapq
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def load_parcels(path: Path = DATA / "parcels.csv") -> List[dict]:
    parcels = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            parcels.append({
                "id": row["id"],
                "destination": row["destination"],
                "weight": int(row["weight"]),
                "value": int(row["value"]),
                "deadline": int(row["deadline"]),
                "priority": int(row["priority"]),
            })
    return parcels


def load_graph(path: Path = DATA / "roads.json") -> dict:
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    graph = {node: {} for node in raw["nodes"]}
    for a, b, distance in raw["edges"]:
        graph[a][b] = float(distance)
        graph[b][a] = float(distance)  # roads are treated as two-way
    return graph


def merge_sort_parcels(items: List[dict]) -> List[dict]:
    """Stable merge sort: deadline first, then priority (higher first)."""
    if len(items) <= 1:
        return items[:]
    mid = len(items) // 2
    left = merge_sort_parcels(items[:mid])
    right = merge_sort_parcels(items[mid:])
    merged, i, j = [], 0, 0

    def key(p):
        return (p["deadline"], -p["priority"], p["id"])

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def knapsack_01(parcels: List[dict], capacity: int) -> Tuple[List[dict], int]:
    """Maximize total parcel value subject to vehicle capacity."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        weight, value = parcels[i - 1]["weight"], parcels[i - 1]["value"]
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i - 1][cap]
            if weight <= cap:
                dp[i][cap] = max(dp[i][cap], value + dp[i - 1][cap - weight])

    chosen = []
    cap = capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i - 1][cap]:
            chosen.append(parcels[i - 1])
            cap -= parcels[i - 1]["weight"]
    chosen.reverse()
    return chosen, dp[n][capacity]


def dijkstra(graph: dict, start: str) -> Tuple[dict, dict]:
    """Return shortest distances and predecessors from start."""
    distances = {node: math.inf for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0.0
    pq = [(0.0, start)]
    while pq:
        current_distance, node = heapq.heappop(pq)
        if current_distance != distances[node]:
            continue
        for neighbor, weight in graph[node].items():
            candidate = current_distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(pq, (candidate, neighbor))
    return distances, previous


def reconstruct_path(previous: dict, start: str, end: str) -> List[str]:
    if start == end:
        return [start]
    path, node = [], end
    while node is not None:
        path.append(node)
        if node == start:
            break
        node = previous[node]
    if not path or path[-1] != start:
        return []
    return list(reversed(path))


def all_pairs_shortest_paths(graph: dict) -> Tuple[dict, dict]:
    distances, predecessors = {}, {}
    for node in graph:
        distances[node], predecessors[node] = dijkstra(graph, node)
    return distances, predecessors


def nearest_neighbor_tsp(graph: dict, depot: str, destinations: List[str]):
    """Approximate a delivery tour using shortest-path distances."""
    if not destinations:
        return [depot], 0.0, []
    distances, predecessors = all_pairs_shortest_paths(graph)
    unvisited = set(destinations)
    current = depot
    visit_order = [depot]
    total = 0.0
    legs = []
    while unvisited:
        reachable = [(distances[current][node], node) for node in unvisited]
        leg_distance, next_node = min(reachable)
        if math.isinf(leg_distance):
            raise ValueError(f"No route from {current} to any remaining destination.")
        legs.append((current, next_node, leg_distance))
        total += leg_distance
        visit_order.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    # Return to depot to complete the tour.
    return_distance = distances[current][depot]
    if not math.isinf(return_distance):
        legs.append((current, depot, return_distance))
        total += return_distance
        visit_order.append(depot)
    return visit_order, total, legs


def expand_route(graph: dict, legs: List[tuple]) -> List[str]:
    """Expand each route leg into the actual shortest road path."""
    expanded = []
    for start, end, _ in legs:
        _, previous = dijkstra(graph, start)
        path = reconstruct_path(previous, start, end)
        if path:
            expanded.extend(path if not expanded else path[1:])
    return expanded


def run_planner(capacity: int = 18, depot: str = "Warehouse") -> dict:
    parcels = load_parcels()
    graph = load_graph()
    sorted_parcels = merge_sort_parcels(parcels)
    selected, total_value = knapsack_01(sorted_parcels, capacity)
    destinations = sorted({p["destination"] for p in selected})
    visit_order, route_distance, legs = nearest_neighbor_tsp(graph, depot, destinations)
    road_path = expand_route(graph, legs)
    return {
        "sorted_parcels": sorted_parcels,
        "selected_parcels": selected,
        "total_value": total_value,
        "total_weight": sum(p["weight"] for p in selected),
        "capacity": capacity,
        "visit_order": visit_order,
        "road_path": road_path,
        "route_distance": round(route_distance, 2),
        "legs": legs,
    }


def benchmark():
    """Measure sorting, knapsack, and shortest-path work on increasing inputs."""
    rng = __import__("random").Random(42)
    rows = []
    graph = load_graph()
    for n in (10, 50, 100, 250, 500):
        parcels = [{
            "id": f"P{i:04}", "destination": "Area A",
            "weight": rng.randint(1, 8), "value": rng.randint(10, 100),
            "deadline": rng.randint(1, 30), "priority": rng.randint(1, 5)
        } for i in range(n)]
        t0 = time.perf_counter()
        merge_sort_parcels(parcels)
        sort_ms = (time.perf_counter() - t0) * 1000

        capacity = max(20, n * 3)
        t0 = time.perf_counter()
        knapsack_01(parcels, capacity)
        knapsack_ms = (time.perf_counter() - t0) * 1000

        # Repeat Dijkstra on the supplied road graph to obtain measurable timings.
        t0 = time.perf_counter()
        for _ in range(max(1, n // 10)):
            dijkstra(graph, "Warehouse")
        dijkstra_ms = (time.perf_counter() - t0) * 1000
        rows.append({
            "input_size": n, "merge_sort_ms": round(sort_ms, 4),
            "knapsack_ms": round(knapsack_ms, 4),
            "dijkstra_repetitions": max(1, n // 10),
            "dijkstra_total_ms": round(dijkstra_ms, 4)
        })
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "runtime_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    return rows


def main():
    print("\\n========== MINI-COURIER PLANNER ==========")
    try:
        raw = input("Enter vehicle capacity in kg [18]: ").strip()
        capacity = int(raw) if raw else 18
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        result = run_planner(capacity)
    except (ValueError, FileNotFoundError) as exc:
        print("Input/data error:", exc)
        return

    print("\\n1) PRIORITIZED PARCELS (deadline ascending, priority descending)")
    for p in result["sorted_parcels"]:
        print(f'{p["id"]}: {p["destination"]}, deadline={p["deadline"]}, '
              f'priority={p["priority"]}, weight={p["weight"]}kg')
    print("\\n2) OPTIMAL PACKING (0/1 Knapsack)")
    for p in result["selected_parcels"]:
        print(f'{p["id"]}: {p["destination"]}, {p["weight"]}kg, value={p["value"]}')
    print(f'Total weight: {result["total_weight"]}/{result["capacity"]} kg')
    print(f'Total value: {result["total_value"]}')
    print("\\n3) DELIVERY ROUTE (Nearest-Neighbor TSP + Dijkstra)")
    print("Visit order:", " -> ".join(result["visit_order"]))
    print("Road path:", " -> ".join(result["road_path"]))
    print(f'Total route distance: {result["route_distance"]} km')

    print("\\n4) PERFORMANCE TEST")
    rows = benchmark()
    print("Runtime results saved to results/runtime_results.csv")
    for row in rows:
        print(row)
    print("\\nDone. See README.md and report.md for explanation.")


if __name__ == "__main__":
    main()
