"""
Trusted Reference Oracles for Algorithm Archaeologist.
Provides mathematically simple, unambiguous ground-truth solvers used to evaluate
correctness on randomized and adversarial test cases without relying on LLM self-judgement.
"""
from typing import Any, Dict, List, Optional, Tuple
import heapq

def reference_max_subarray(arr: List[int]) -> int:
    """
    O(n^2) unoptimized reference solution for Maximum Subarray problem.
    """
    if not arr:
        return 0
    best = float("-inf")
    for i in range(len(arr)):
        current = 0
        for j in range(i, len(arr)):
            current += arr[j]
            if current > best:
                best = current
    return int(best)

def reference_sorting(arr: List[int]) -> List[int]:
    """
    Canonical Python sorted reference for sorting problem.
    """
    return sorted(arr)

def reference_shortest_path(n: int, edges: List[Tuple[int, int, float]], start: int, target: int) -> float:
    """
    Canonical Dijkstra reference for shortest path with non-negative weights.
    Returns infinity (-1 or float('inf')) if unreachable.
    """
    graph: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}
    for u, v, w in edges:
        if 0 <= u < n and 0 <= v < n:
            graph[u].append((v, float(w)))
            graph[v].append((u, float(w))) # undirected/directed depending on problem

    dist = {i: float("inf") for i in range(n)}
    dist[start] = 0.0
    pq = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == target:
            return float(d)
        for v, weight in graph.get(u, []):
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))

    return float(dist[target]) if dist[target] != float("inf") else -1.0

def reference_knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    """
    Simple 2D DP reference for 0/1 knapsack.
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]
            if c >= w:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
    return dp[n][capacity]

def reference_graph_traversal(n: int, edges: List[Tuple[int, int]], start: int) -> List[int]:
    """
    Canonical deterministic BFS traversal (sorted neighbors) from start node.
    """
    adj = {i: [] for i in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for u in adj:
        adj[u].sort()

    visited = set()
    order = []
    queue = [start]
    visited.add(start)

    while queue:
        u = queue.pop(0)
        order.append(u)
        for v in adj.get(u, []):
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return order

def compute_reference_output(problem_family: str, input_data: Any) -> Any:
    """
    Dispatches to trusted oracle based on problem family.
    """
    pf = (problem_family or "").lower()
    
    if "subarray" in pf:
        if isinstance(input_data, list):
            return reference_max_subarray(input_data)
        elif isinstance(input_data, dict) and "arr" in input_data:
            return reference_max_subarray(input_data["arr"])
            
    elif "sort" in pf:
        if isinstance(input_data, list):
            return reference_sorting(input_data)
        elif isinstance(input_data, dict) and "arr" in input_data:
            return reference_sorting(input_data["arr"])
            
    elif "shortest" in pf or "path" in pf or "dijkstra" in pf:
        if isinstance(input_data, dict):
            return reference_shortest_path(
                input_data.get("n", 0),
                input_data.get("edges", []),
                input_data.get("start", 0),
                input_data.get("target", 0)
            )
            
    elif "knapsack" in pf:
        if isinstance(input_data, dict):
            return reference_knapsack_01(
                input_data.get("weights", []),
                input_data.get("values", []),
                input_data.get("capacity", 0)
            )
            
    elif "traversal" in pf or "graph" in pf:
        if isinstance(input_data, dict):
            return reference_graph_traversal(
                input_data.get("n", 0),
                input_data.get("edges", []),
                input_data.get("start", 0)
            )

    return None

def check_outputs_match(actual: Any, expected: Any, tolerance: float = 1e-6) -> bool:
    """
    Deep equality check with floating point tolerance and list handling.
    """
    if actual is None and expected is None:
        return True
    if actual is None or expected is None:
        return False

    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) <= tolerance

    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            return False
        return all(check_outputs_match(a, e, tolerance) for a, e in zip(actual, expected))

    if isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual.keys()) != set(expected.keys()):
            return False
        return all(check_outputs_match(actual[k], expected[k], tolerance) for k in actual)

    return str(actual).strip() == str(expected).strip()
