import ast
import re
from typing import Dict, List, Optional
from app.models.problem import ProblemSpec, ProblemFamily

PRESET_PROBLEMS: Dict[str, ProblemSpec] = {
    "shortest-path-100k": ProblemSpec(
        id="shortest-path-100k",
        title="Single-Source Shortest Path in Weighted Directed Graphs",
        description="Given a directed graph with non-negative edge weights and N vertices, find the shortest path cost from source vertex S to target vertex T.",
        problem_family=ProblemFamily.GRAPH,
        objective="Minimize runtime and space while handling edge weights correctly.",
        input_signature={"n": "int", "edges": "List[Tuple[int, int, int]]", "source": "int", "target": "int"},
        output_signature="int",
        constraints=["N up to 100,000", "Weights >= 0", "Sparse and Dense graphs"],
        theoretical_lower_bound_time="O((V + E) log V)",
        theoretical_lower_bound_space="O(V + E)",
        tags=["graph", "shortest-path", "dijkstra", "bfs-trap", "priority-queue"],
    ),
    "max-subarray-sum": ProblemSpec(
        id="max-subarray-sum",
        title="Maximum Subarray Sum (Kadane's Archaeological Exploration)",
        description="Find the contiguous subarray within a one-dimensional array of numbers which has the largest sum.",
        problem_family=ProblemFamily.DYNAMIC_PROGRAMMING,
        objective="Achieve O(N) linear time with O(1) auxiliary space, overcoming naive O(N^3) and O(N^2) variants.",
        input_signature={"arr": "List[int]"},
        output_signature="int",
        constraints=["N up to 1,000,000", "Elements in [-10^9, 10^9]"],
        theoretical_lower_bound_time="O(N)",
        theoretical_lower_bound_space="O(1)",
        tags=["dynamic_programming", "kadane", "divide_and_conquer", "streaming"],
    ),
    "kth-largest-element": ProblemSpec(
        id="kth-largest-element",
        title="Kth Largest Element in Unsorted Array",
        description="Find the k-th largest element in an unsorted array.",
        problem_family=ProblemFamily.ARRAY_SEARCH,
        objective="Achieve O(N) expected average time using Quickselect or Min-Heap, avoiding full O(N log N) sorting.",
        input_signature={"nums": "List[int]", "k": "int"},
        output_signature="int",
        constraints=["1 <= k <= N <= 500,000"],
        theoretical_lower_bound_time="O(N) expected",
        theoretical_lower_bound_space="O(1)",
        tags=["quickselect", "min-heap", "selection", "partition"],
    ),
    "longest-increasing-subsequence": ProblemSpec(
        id="longest-increasing-subsequence",
        title="Longest Strictly Increasing Subsequence (LIS)",
        description="Find the length of the longest strictly increasing subsequence in an array of integers.",
        problem_family=ProblemFamily.DYNAMIC_PROGRAMMING,
        objective="Synthesize Patience Sorting with Binary Search O(N log N), breaking the standard O(N^2) DP barrier.",
        input_signature={"nums": "List[int]"},
        output_signature="int",
        constraints=["N up to 200,000"],
        theoretical_lower_bound_time="O(N log N)",
        theoretical_lower_bound_space="O(N)",
        tags=["lis", "patience-sorting", "binary-search", "dp"],
    ),
    "convex-hull-2d": ProblemSpec(
        id="convex-hull-2d",
        title="Convex Hull of 2D Planar Points",
        description="Given a set of 2D points, compute the convex hull boundary vertices in counter-clockwise order.",
        problem_family=ProblemFamily.GEOMETRY,
        objective="Synthesize Graham Scan / Monotone Chain O(N log N) with robust cross-product orientation.",
        input_signature={"points": "List[Tuple[float, float]]"},
        output_signature="List[Tuple[float, float]]",
        constraints=["N up to 50,000", "Collinear points handling"],
        theoretical_lower_bound_time="O(N log N)",
        theoretical_lower_bound_space="O(N)",
        tags=["geometry", "graham-scan", "monotone-chain", "cross-product"],
    ),
    "string-search-kmp": ProblemSpec(
        id="string-search-kmp",
        title="Exact Substring Pattern Search",
        description="Find all starting indices of pattern P in text T.",
        problem_family=ProblemFamily.STRING_MATCHING,
        objective="Avoid pathological O(|T| * |P|) degradation with Knuth-Morris-Pratt or Boyer-Moore-Horspool.",
        input_signature={"text": "str", "pattern": "str"},
        output_signature="List[int]",
        constraints=["|T| up to 2,000,000", "|P| up to 100,000"],
        theoretical_lower_bound_time="O(|T| + |P|)",
        theoretical_lower_bound_space="O(|P|)",
        tags=["kmp", "string-search", "lps-array", "boyer-moore", "rabin-karp"],
    ),
}

class ProblemAnalyzer:
    def get_preset_problem(self, problem_id: str) -> ProblemSpec:
        if problem_id in PRESET_PROBLEMS:
            return PRESET_PROBLEMS[problem_id]
        return self.analyze_raw_description(problem_id)

    def list_preset_problems(self) -> List[ProblemSpec]:
        return list(PRESET_PROBLEMS.values())

    def analyze_raw_description(self, raw_input: str) -> ProblemSpec:
        raw_lower = raw_input.lower()
        family = ProblemFamily.ARRAY_SEARCH
        title = raw_input.strip().split("\n")[0][:80]
        
        if any(w in raw_lower for w in ["graph", "edge", "node", "shortest path", "dijkstra", "vertex"]):
            family = ProblemFamily.GRAPH
        elif any(w in raw_lower for w in ["subarray", "dp", "dynamic programming", "knapsack", "subsequence"]):
            family = ProblemFamily.DYNAMIC_PROGRAMMING
        elif any(w in raw_lower for w in ["string", "pattern", "substring", "text", "match"]):
            family = ProblemFamily.STRING_MATCHING
        elif any(w in raw_lower for w in ["geometry", "polygon", "points", "hull", "plane"]):
            family = ProblemFamily.GEOMETRY
        elif any(w in raw_lower for w in ["sort", "partition", "merge", "quick"]):
            family = ProblemFamily.SORTING

        spec_id = re.sub(r"[^a-z0-9]+", "-", raw_lower[:30]).strip("-") or "custom-problem"

        return ProblemSpec(
            id=spec_id,
            title=title if len(title) > 3 else "Custom Algorithmic Inquiry",
            description=raw_input,
            problem_family=family,
            objective="Discover asymptotically superior and empirically resilient algorithmic candidates.",
            input_signature={"input_data": "Any"},
            output_signature="Any",
            constraints=["Input size N up to 100,000"],
            tags=[family.value, "automated-archaeology"],
        )

problem_analyzer = ProblemAnalyzer()
