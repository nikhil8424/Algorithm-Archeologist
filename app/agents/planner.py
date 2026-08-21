from typing import List, Dict, Any
from app.models.problem import ProblemSpec
from app.models.candidate import AlgorithmCandidate, Complexity, CandidateOrigin

class PlannerAgent:
    """Archaeological Strategy Planner: Decomposes the algorithm design space."""

    def plan_paradigms(self, problem: ProblemSpec, candidate_count: int = 4) -> List[Dict[str, Any]]:
        plans_by_problem = {
            "shortest-path-100k": [
                {
                    "name": "Dijkstra Priority Queue (Min-Heap)",
                    "paradigm": "Greedy / Priority Queue",
                    "strategy": "Classical Dijkstra using binary min-heap for single-source shortest path with non-negative weights.",
                    "time_theo": "O((V + E) log V)",
                    "space_theo": "O(V + E)",
                    "constant_factor": "low",
                },
                {
                    "name": "Naive Unit BFS (Pathological Trap)",
                    "paradigm": "Queue Breadth-First Search",
                    "strategy": "Ignores edge weights and assumes unit distances. Designed to uncover adversarial shortest-path bugs.",
                    "time_theo": "O(V + E)",
                    "space_theo": "O(V)",
                    "constant_factor": "very low",
                },
                {
                    "name": "Dial's Bucket Queues",
                    "paradigm": "Bounded Integer Bucket Array",
                    "strategy": "Array of buckets indexed by distance for integer weights <= W, eliminating heap overhead.",
                    "time_theo": "O(V + E + W)",
                    "space_theo": "O(V + W)",
                    "constant_factor": "ultra-low",
                },
                {
                    "name": "Bidirectional Dijkstra Search",
                    "paradigm": "Bidirectional Frontier Expansion",
                    "strategy": "Expands two search frontiers simultaneously from source and target until meeting.",
                    "time_theo": "O((V + E) log V)",
                    "space_theo": "O(V + E)",
                    "constant_factor": "low",
                },
            ],
            "max-subarray-sum": [
                {
                    "name": "Kadane's Dynamic Programming",
                    "paradigm": "Linear DP / Streaming",
                    "strategy": "Optimal single-pass tracking current subarray and global maximum.",
                    "time_theo": "O(N)",
                    "space_theo": "O(1)",
                    "constant_factor": "minimal",
                },
                {
                    "name": "Divide and Conquer Max Subarray",
                    "paradigm": "Divide & Conquer",
                    "strategy": "Recursively split array into left, right, and crossing middle segments.",
                    "time_theo": "O(N log N)",
                    "space_theo": "O(log N)",
                    "constant_factor": "medium",
                },
                {
                    "name": "Prefix Sum Array Sweep",
                    "paradigm": "Prefix Reductions",
                    "strategy": "Compute running prefix sums and track running minimum prefix.",
                    "time_theo": "O(N)",
                    "space_theo": "O(N)",
                    "constant_factor": "low",
                },
                {
                    "name": "Naive Brute Force Cubic",
                    "paradigm": "Exhaustive Iteration",
                    "strategy": "Iterate over all (i, j) subarray endpoints and recompute sum.",
                    "time_theo": "O(N^3)",
                    "space_theo": "O(1)",
                    "constant_factor": "high",
                },
            ],
            "kth-largest-element": [
                {
                    "name": "Quickselect (Hoare Partition)",
                    "paradigm": "Divide & Conquer Selection",
                    "strategy": "In-place randomized pivoting targeting k-th rank in linear expected time.",
                    "time_theo": "O(N) avg, O(N^2) worst",
                    "space_theo": "O(1)",
                    "constant_factor": "low",
                },
                {
                    "name": "Min-Heap Top-K Streaming",
                    "paradigm": "Bounded Priority Queue",
                    "strategy": "Maintain size-k min heap of largest elements encountered.",
                    "time_theo": "O(N log K)",
                    "space_theo": "O(K)",
                    "constant_factor": "low",
                },
                {
                    "name": "Full Array Sort Baseline",
                    "paradigm": "Comparison Sorting (Timsort)",
                    "strategy": "Sort entire array in descending order and return index k-1.",
                    "time_theo": "O(N log N)",
                    "space_theo": "O(N)",
                    "constant_factor": "medium",
                },
                {
                    "name": "Median of Medians Quickselect",
                    "paradigm": "Deterministic Linear Selection",
                    "strategy": "Groups of 5 with deterministic true median pivot selection.",
                    "time_theo": "O(N) worst-case",
                    "space_theo": "O(N)",
                    "constant_factor": "high",
                },
            ],
        }

        plans = plans_by_problem.get(problem.id)
        if not plans:
            plans = [
                {
                    "name": "Optimal Standard Solution",
                    "paradigm": "Optimized Core",
                    "strategy": "Standard algorithmic solution with optimal data structures.",
                    "time_theo": problem.theoretical_lower_bound_time,
                    "space_theo": problem.theoretical_lower_bound_space,
                    "constant_factor": "low",
                },
                {
                    "name": "Iterative Baseline",
                    "paradigm": "Iterative",
                    "strategy": "Straightforward implementation.",
                    "time_theo": "O(N^2)",
                    "space_theo": "O(N)",
                    "constant_factor": "medium",
                },
            ]

        return plans[:candidate_count]

planner_agent = PlannerAgent()
