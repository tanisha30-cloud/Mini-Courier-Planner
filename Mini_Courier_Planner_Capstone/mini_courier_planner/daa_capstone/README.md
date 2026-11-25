# Mini-Courier Planner — DAA Capstone

A Python prototype for planning a courier trip. It integrates the four algorithmic components requested in the assignment: sorting, dynamic programming, shortest paths, and route approximation.

## Requirements
- Python 3.9 or newer
- No third-party Python packages are required to run `main.py`.
- `pandas` and `matplotlib` are used only if you want to regenerate the runtime chart from the CSV.

## Run
1. Extract the ZIP.
2. Open a terminal in the `mini_courier_planner` folder.
3. Run: `python main.py`
4. Enter vehicle capacity in kg, or press Enter to use 18 kg.

## Project structure
- `main.py` — complete application and algorithms.
- `data/parcels.csv` — sample parcel records.
- `data/roads.json` — road network represented as an undirected weighted graph.
- `tests/test_algorithms.py` — basic correctness tests.
- `results/runtime_results.csv` — sample benchmark measurements.
- `results/runtime_chart.png` — runtime chart generated from the sample measurements.
- `report.md` — assignment report with design, algorithms, complexity, test plan and limitations.

## Algorithm design
1. **Merge Sort:** parcels are ordered by earliest deadline, then higher priority. Time: O(n log n); auxiliary space: O(n).
2. **0/1 Knapsack DP:** chooses a subset with maximum total value while keeping total weight within vehicle capacity. Time: O(nW); space: O(nW), where W is capacity.
3. **Dijkstra:** computes shortest road distances from a source using a min-priority queue. With an adjacency list and binary heap: O((V+E) log V).
4. **Nearest-Neighbor TSP approximation:** repeatedly visits the nearest unvisited delivery point using Dijkstra shortest-path distances, then returns to the depot if reachable. It is a heuristic, not a guaranteed optimal TSP solution.

## Important interpretation
The packing stage maximizes the sum of parcel `value`. The deadline and priority are used for display/order, while the selected set is optimized by value under the weight limit. The route visits unique destinations among selected parcels. Distances are illustrative sample data, not live map distances.

## Test
Run: `python -m unittest discover -s tests -v`
