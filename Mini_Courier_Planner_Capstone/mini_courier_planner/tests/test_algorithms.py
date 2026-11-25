import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import merge_sort_parcels, knapsack_01, dijkstra, reconstruct_path, nearest_neighbor_tsp

class TestCourierAlgorithms(unittest.TestCase):
    def test_merge_sort(self):
        items = [
            {"id":"b","deadline":2,"priority":3},
            {"id":"a","deadline":1,"priority":1},
            {"id":"c","deadline":2,"priority":5},
        ]
        result = merge_sort_parcels(items)
        self.assertEqual([x["id"] for x in result], ["a","c","b"])

    def test_knapsack_capacity(self):
        items = [
            {"id":"A","weight":4,"value":10},
            {"id":"B","weight":6,"value":30},
            {"id":"C","weight":5,"value":20},
        ]
        selected, value = knapsack_01(items, 10)
        self.assertEqual(value, 40)
        self.assertLessEqual(sum(x["weight"] for x in selected), 10)

    def test_dijkstra_path(self):
        graph = {"A":{"B":2,"C":10}, "B":{"A":2,"C":3}, "C":{"A":10,"B":3}}
        dist, prev = dijkstra(graph, "A")
        self.assertEqual(dist["C"], 5)
        self.assertEqual(reconstruct_path(prev, "A", "C"), ["A","B","C"])

    def test_nearest_neighbor(self):
        graph = {"D":{"A":2,"B":5}, "A":{"D":2,"B":2}, "B":{"D":5,"A":2}}
        order, distance, legs = nearest_neighbor_tsp(graph, "D", ["A","B"])
        self.assertEqual(order[0], "D")
        self.assertEqual(order[-1], "D")
        self.assertGreater(distance, 0)

if __name__ == "__main__":
    unittest.main()
