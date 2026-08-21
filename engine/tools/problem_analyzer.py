"""
Problem Analyzer Agent & Heuristic Synthesizer for Algorithm Archaeologist.
Parses natural language problem statements, classifies problem family, detects constraints,
extracts objective, and identifies viable algorithmic candidate paradigms.
Works 100% standalone without requiring external API keys.
"""
import re
import uuid
from typing import Dict, Any, List
from engine.models import ProblemSpec

PRESET_PROBLEMS = [
    {
        "id": "shortest-path-100k",
        "title": "Shortest Path in Weighted Graph (100k Nodes)",
        "description": "Find the shortest path from node A to node B in a weighted graph with up to 100,000 nodes and non-negative edge weights.",
        "input_format": "Dictionary with keys 'n' (int), 'edges' (list of (u, v, w)), 'start' (int), 'target' (int)",
        "output_format": "Float representing total minimum distance or -1.0 if unreachable",
        "constraints": ["V <= 100,000", "E <= 500,000", "weight >= 0.0", "memory <= 512MB"],
        "objective": "Minimize total path weight while maintaining low memory and fast lookup for large V",
        "problem_family": "Graph / Shortest Path",
        "candidate_paradigms": ["greedy / priority queue", "a* heuristic search", "breadth-first search", "bellman-ford dynamic programming"]
    },
    {
        "id": "max-subarray",
        "title": "Maximum Subarray Problem",
        "description": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
        "input_format": "Dictionary with key 'arr' (list of integers)",
        "output_format": "Integer representing the maximum contiguous sum",
        "constraints": ["1 <= nums.length <= 100,000", "-10,000 <= nums[i] <= 10,000"],
        "objective": "Maximize the sum of contiguous elements in single-pass linear time",
        "problem_family": "Arrays / Maximum Subarray",
        "candidate_paradigms": ["dynamic programming (kadane)", "divide and conquer", "prefix sum optimization", "brute force"]
    },
    {
        "id": "large-sorting",
        "title": "Large-Scale Array Sorting",
        "description": "Sort an array of up to 100,000 numbers in ascending order under adversarial duplicate distributions and reverse-sorted conditions.",
        "input_format": "Dictionary with key 'arr' (list of integers)",
        "output_format": "List of integers sorted in non-decreasing order",
        "constraints": ["0 <= nums.length <= 100,000", "Must handle heavy duplicates gracefully"],
        "objective": "Stable/in-place ordering in O(N log N) worst-case time",
        "problem_family": "Sorting / Comparison Sort",
        "candidate_paradigms": ["3-way quicksort (dutch national flag)", "mergesort (divide & conquer)", "heapsort", "timsort / hybrid sort"]
    },
    {
        "id": "knapsack-01",
        "title": "0/1 Knapsack Optimization",
        "description": "Given weights and values of N items, put these items in a knapsack of capacity W to get the maximum total value in the knapsack.",
        "input_format": "Dictionary with keys 'weights' (list[int]), 'values' (list[int]), 'capacity' (int)",
        "output_format": "Integer representing the maximum obtainable value",
        "constraints": ["1 <= N <= 1,000", "1 <= W <= 5,000", "weights[i], values[i] > 0"],
        "objective": "Maximize knapsack value under strict capacity limit",
        "problem_family": "Dynamic Programming / Knapsack",
        "candidate_paradigms": ["1d rolling array dynamic programming", "2d table dynamic programming", "greedy density approximation", "branch and bound"]
    },
    {
        "id": "graph-traversal",
        "title": "Deterministic Graph Traversal",
        "description": "Given an undirected graph with N vertices and an adjacency structure, produce the complete traversal order starting from vertex 0.",
        "input_format": "Dictionary with keys 'n' (int), 'edges' (list of (u, v)), 'start' (int)",
        "output_format": "List of integers representing visited vertex order",
        "constraints": ["1 <= V <= 50,000", "Deterministic tie-breaking on smaller index first"],
        "objective": "Complete exploration of connected components without recursion stack overflow",
        "problem_family": "Graph / Traversal",
        "candidate_paradigms": ["iterative queue bfs (collections.deque)", "recursive dfs", "explicit stack dfs", "bidirectional search"]
    }
]

def analyze_problem_statement(text: str) -> ProblemSpec:
    """
    Parses natural language problem statement into a structured ProblemSpec.
    Matches presets if text is similar or constructs a tailored ProblemSpec.
    """
    text_lower = text.lower()

    # Check for preset matches
    for p in PRESET_PROBLEMS:
        if p["id"] == text.strip() or p["title"].lower() in text_lower or (
            "subarray" in text_lower and "subarray" in p["id"]
        ) or (
            ("shortest path" in text_lower or "dijkstra" in text_lower or "100,000 nodes" in text_lower) and "shortest" in p["id"]
        ) or (
            "knapsack" in text_lower and "knapsack" in p["id"]
        ) or (
            ("sorting" in text_lower or "sort an array" in text_lower) and "sort" in p["id"]
        ) or (
            ("traversal" in text_lower or "dfs" in text_lower or "bfs" in text_lower) and "traversal" in p["id"]
        ):
            return ProblemSpec(
                id=p["id"],
                title=p["title"],
                description=p["description"],
                input_format=p["input_format"],
                output_format=p["output_format"],
                constraints=p["constraints"],
                objective=p["objective"],
                problem_family=p["problem_family"],
                candidate_paradigms=p["candidate_paradigms"]
            )

    # Dynamic classification heuristic
    title = text.strip()[:60] if len(text.strip()) > 5 else "Custom Algorithmic Problem"
    problem_family = "General Algorithmic Search"
    candidate_paradigms = ["greedy", "dynamic programming", "divide and conquer", "brute force"]
    constraints = ["Execution timeout <= 5s", "Memory <= 512MB"]

    if "graph" in text_lower or "node" in text_lower or "edge" in text_lower:
        problem_family = "Graph / Shortest Path"
        candidate_paradigms = ["greedy / priority queue", "a* heuristic search", "breadth-first search", "bellman-ford"]
    elif "sub" in text_lower or "sum" in text_lower or "array" in text_lower:
        problem_family = "Arrays / Maximum Subarray"
        candidate_paradigms = ["dynamic programming (kadane)", "divide and conquer", "prefix sum optimization", "brute force"]
    elif "sort" in text_lower or "order" in text_lower:
        problem_family = "Sorting / Comparison Sort"
        candidate_paradigms = ["3-way quicksort", "mergesort", "heapsort", "timsort"]
    elif "capacity" in text_lower or "weight" in text_lower or "knapsack" in text_lower:
        problem_family = "Dynamic Programming / Knapsack"
        candidate_paradigms = ["1d rolling dynamic programming", "2d table dynamic programming", "greedy approximation", "branch and bound"]

    # Extract numeric constraints if present (e.g. 100,000 nodes)
    nums = re.findall(r"\b\d{1,3}(?:,\d{3})*\b", text)
    if nums:
        constraints.append(f"Detected scale parameters: {', '.join(nums)}")

    return ProblemSpec(
        id=f"prob_{uuid.uuid4().hex[:8]}",
        title=title,
        description=text,
        input_format="Dictionary / structured arguments",
        output_format="Computed result matching problem objective",
        constraints=constraints,
        objective="Find optimal algorithmic balance of time complexity, memory overhead, and robustness",
        problem_family=problem_family,
        candidate_paradigms=candidate_paradigms
    )
