# Mini-Courier Planner — Capstone Report

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**Project:** Mini-Courier Planner  
**Implementation:** Python

## 1. Problem definition
The system receives a list of parcels and a weighted road network. It prioritizes parcels, chooses the most valuable set that fits within the vehicle's weight capacity, and produces an approximate delivery tour beginning and ending at the warehouse.

## 2. Input data design
Each parcel has an ID, destination, weight (kg), value, delivery deadline (lower number means earlier), and priority (1–5, where 5 is highest). The road network is an undirected weighted graph: locations are vertices and road distances in kilometres are edge weights. The sample data is stored in `data/parcels.csv` and `data/roads.json`.

## 3. Algorithm selection and integration
### 3.1 Merge Sort — parcel prioritization
Merge Sort recursively divides the parcel list, sorts each half, and merges the halves. The comparison key is `(deadline, -priority, parcel ID)`. This gives earliest-deadline-first ordering, with higher-priority parcels first when deadlines tie. Complexity: **O(n log n)** time and **O(n)** auxiliary space.

### 3.2 0/1 Knapsack — box filling
Dynamic programming builds a table `dp[i][c]`, the maximum value obtainable from the first `i` parcels with capacity `c`. Each parcel is either selected once or not selected. The recurrence is:
- If weight[i] > c: `dp[i][c] = dp[i-1][c]`
- Otherwise: `dp[i][c] = max(dp[i-1][c], value[i] + dp[i-1][c-weight[i]])`

The selected parcels are reconstructed by tracing the table backwards. Complexity: **O(nW)** time and **O(nW)** space, where `n` is the number of parcels and `W` is the integer capacity.

### 3.3 Dijkstra — individual shortest paths
The road map is represented using adjacency lists. Dijkstra uses a min-heap to repeatedly process the currently closest unvisited vertex and relax its outgoing edges. It returns distances and predecessor links. Complexity with a binary heap: **O((V+E) log V)**.

### 3.4 Nearest-Neighbor TSP approximation — delivery route
The planner starts at the warehouse and repeatedly chooses the unvisited delivery location with the smallest Dijkstra distance from the current location. After visiting all selected destinations, it returns to the warehouse when a return path exists. This is a practical approximation; it does not guarantee the globally shortest travelling-salesperson tour.

## 4. Integrated workflow
1. Read parcels and road graph from CSV and JSON.
2. Sort parcels by deadline and priority using Merge Sort.
3. Run 0/1 Knapsack to select parcels within the vehicle capacity.
4. Extract unique destinations from selected parcels.
5. Run Dijkstra from graph vertices to build shortest-path distances.
6. Apply nearest-neighbor route selection and expand route legs into road paths.
7. Benchmark major algorithmic components and save timing data.

## 5. Testing and performance
The application includes a small sample dataset and a benchmark that increases parcel input sizes (10, 50, 100, 250, 500). It records sorting and knapsack runtime, and repeated Dijkstra runtime, in `results/runtime_results.csv`. The accompanying chart is a sample illustration; exact timings vary with computer hardware, operating system, Python version, and background processes. For a fair experiment, run the benchmark several times on the same machine and compare averages.

## 6. Test cases
| Test | Input / condition | Expected result |
|---|---|---|
| Sorting | Different deadlines and priorities | Earliest deadline first; priority descending for ties |
| Knapsack | Capacity 18 kg | Selected total weight never exceeds 18 kg |
| Knapsack boundary | Parcel heavier than capacity | Parcel is not selected |
| Dijkstra | Connected road graph | Shortest distance and predecessor path returned |
| Route | Several selected destinations | Each unique destination visited once; depot return attempted |
| Empty route | No selected destinations | Route contains only the depot; distance is zero |

## 7. Complexity summary
| Component | Time complexity | Space complexity |
|---|---|---|
| Merge Sort | O(n log n) | O(n) |
| 0/1 Knapsack | O(nW) | O(nW) |
| Dijkstra (binary heap) | O((V+E) log V) | O(V+E) |
| Nearest Neighbor after shortest paths | O(k²) selection, plus shortest-path preprocessing | O(V²) distance/predecessor storage |

Here `n` is parcel count, `W` is vehicle capacity, `V` is number of graph vertices, `E` is number of edges, and `k` is number of unique selected delivery destinations.

## 8. Limitations and future improvements
- The road network and distances are sample data, not live traffic or GPS data.
- Nearest Neighbor is a heuristic and may not find the optimal tour.
- The current graph assumes two-way roads.
- Knapsack maximizes parcel value; deadline and priority influence sorting but are not included in the knapsack objective.
- Future work could include live map APIs, one-way roads, traffic-aware weights, delivery time windows, and stronger TSP heuristics such as 2-opt.

## 9. Conclusion
The prototype demonstrates how sorting, dynamic programming, graph shortest paths, and approximation algorithms can be integrated into one courier-planning workflow. It produces a prioritized parcel list, a capacity-feasible packing plan, and an approximate delivery route, while recording runtime measurements for evaluation.
