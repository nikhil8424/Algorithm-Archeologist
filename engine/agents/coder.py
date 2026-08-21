"""
Coder Agent for Algorithm Archaeologist.
Synthesizes clean, robust, deterministic Python implementations defining `def solve(...)`.
Follows strict safety rules: no network, no file access, no global side effects.
"""
from typing import Dict, Any
from engine.models import CandidateAlgorithm, ProblemSpec

CODE_TEMPLATES = {
    # Shortest Path Candidates
    "dijkstra": '''import heapq
from typing import List, Tuple, Dict, Any

def solve(n: int, edges: List[Tuple[int, int, float]], start: int, target: int) -> float:
    """
    Dijkstra shortest path algorithm using binary min-heap.
    Handles up to 100,000 nodes and 500,000 edges efficiently.
    """
    if start == target:
        return 0.0
    if n <= 0:
        return -1.0
        
    adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}
    for u, v, w in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u].append((v, float(w)))
            adj[v].append((u, float(w)))

    dist = [float("inf")] * n
    dist[start] = 0.0
    pq = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == target:
            return float(d)
        for v, weight in adj[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))

    return float(dist[target]) if dist[target] != float("inf") else -1.0
''',

    "astar": '''import heapq
import math
from typing import List, Tuple, Dict, Any

def solve(n: int, edges: List[Tuple[int, int, float]], start: int, target: int) -> float:
    """
    A* Search with consistent Euclidean/coordinate distance heuristic (default zero-admissible).
    """
    if start == target:
        return 0.0
    if n <= 0:
        return -1.0

    adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}
    for u, v, w in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u].append((v, float(w)))
            adj[v].append((u, float(w)))

    # Consistent lower-bound heuristic
    def heuristic(u: int, target_node: int) -> float:
        # Admissible goal-directed heuristic (0.0 is admissible for any general metric)
        return 0.0

    g_score = [float("inf")] * n
    g_score[start] = 0.0
    
    # Heap stores (f_score, g_score, node)
    pq = [(heuristic(start, target), 0.0, start)]

    while pq:
        f, g, u = heapq.heappop(pq)
        if g > g_score[u]:
            continue
        if u == target:
            return float(g)

        for v, weight in adj[u]:
            tentative_g = g_score[u] + weight
            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                f_score = tentative_g + heuristic(v, target)
                heapq.heappush(pq, (f_score, tentative_g, v))

    return float(g_score[target]) if g_score[target] != float("inf") else -1.0
''',

    "bellman": '''from typing import List, Tuple, Dict, Any

def solve(n: int, edges: List[Tuple[int, int, float]], start: int, target: int) -> float:
    """
    Bellman-Ford algorithm with edge relaxation and early stopping.
    """
    if start == target:
        return 0.0
    if n <= 0:
        return -1.0

    dist = [float("inf")] * n
    dist[start] = 0.0
    
    # Symmetrize edges for undirected graph
    all_edges = []
    for u, v, w in edges:
        all_edges.append((u, v, float(w)))
        all_edges.append((v, u, float(w)))

    for _ in range(min(n - 1, 1000)):
        updated = False
        for u, v, w in all_edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    return float(dist[target]) if dist[target] != float("inf") else -1.0
''',

    "bfs_naive": '''from collections import deque
from typing import List, Tuple, Dict, Any

def solve(n: int, edges: List[Tuple[int, int, float]], start: int, target: int) -> float:
    """
    Naive BFS (assumes unweighted edges).
    NOTE: Deliberately ignores edge weights to serve as baseline comparison!
    """
    if start == target:
        return 0.0
    if n <= 0:
        return -1.0

    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for u, v, _ in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u].append(v)
            adj[v].append(u)

    visited = set([start])
    queue = deque([(start, 0.0)])

    while queue:
        u, steps = queue.popleft()
        if u == target:
            return float(steps)
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append((v, steps + 1.0))

    return -1.0
''',

    # Maximum Subarray Candidates
    "kadane": '''from typing import List

def solve(arr: List[int]) -> int:
    """
    Kadane's Algorithm for Maximum Subarray Sum.
    O(N) time complexity, O(1) space complexity.
    """
    if not arr:
        return 0
    max_so_far = arr[0]
    curr_max = arr[0]

    for x in arr[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)

    return int(max_so_far)
''',

    "dnc_subarray": '''from typing import List

def solve(arr: List[int]) -> int:
    """
    Divide and Conquer Maximum Subarray Sum.
    O(N log N) time complexity.
    """
    if not arr:
        return 0

    def max_crossing_sum(left: int, mid: int, right: int) -> int:
        sm = 0
        left_sum = float("-inf")
        for i in range(mid, left - 1, -1):
            sm += arr[i]
            if sm > left_sum:
                left_sum = sm

        sm = 0
        right_sum = float("-inf")
        for i in range(mid + 1, right + 1):
            sm += arr[i]
            if sm > right_sum:
                right_sum = sm

        return int(left_sum + right_sum)

    def helper(left: int, right: int) -> int:
        if left == right:
            return arr[left]
        mid = (left + right) // 2
        return max(
            helper(left, mid),
            helper(mid + 1, right),
            max_crossing_sum(left, mid, right)
        )

    return helper(0, len(arr) - 1)
''',

    "prefix_subarray": '''from typing import List

def solve(arr: List[int]) -> int:
    """
    Prefix Sum with Running Minimum Optimization.
    O(N) time complexity, O(1) auxiliary space.
    """
    if not arr:
        return 0
    min_prefix = 0
    curr_prefix = 0
    max_sum = float("-inf")

    for x in arr:
        curr_prefix += x
        max_sum = max(max_sum, curr_prefix - min_prefix)
        min_prefix = min(min_prefix, curr_prefix)

    return int(max_sum)
''',

    "bruteforce_subarray": '''from typing import List

def solve(arr: List[int]) -> int:
    """
    Exhaustive Quadratic Subarray Sum.
    O(N^2) time complexity.
    """
    if not arr:
        return 0
    n = len(arr)
    max_sum = float("-inf")
    for i in range(n):
        curr = 0
        for j in range(i, n):
            curr += arr[j]
            if curr > max_sum:
                max_sum = curr
    return int(max_sum)
''',

    # Sorting Candidates
    "quicksort_3way": '''from typing import List
import random

def solve(arr: List[int]) -> List[int]:
    """
    3-Way Dutch National Flag QuickSort with randomized pivot.
    Handles duplicate keys and reverse-sorted arrays in O(N log N) / O(N).
    """
    data = list(arr)
    if len(data) <= 1:
        return data

    def sort_range(low: int, high: int):
        if low >= high:
            return
        pivot_idx = random.randint(low, high)
        pivot = data[pivot_idx]
        data[pivot_idx], data[low] = data[low], data[pivot_idx]

        lt = low
        gt = high
        i = low + 1

        while i <= gt:
            if data[i] < pivot:
                data[lt], data[i] = data[i], data[lt]
                lt += 1
                i += 1
            elif data[i] > pivot:
                data[i], data[gt] = data[gt], data[i]
                gt -= 1
            else:
                i += 1

        sort_range(low, lt - 1)
        sort_range(gt + 1, high)

    sort_range(0, len(data) - 1)
    return data
''',

    "mergesort": '''from typing import List

def solve(arr: List[int]) -> List[int]:
    """
    Iterative/Bottom-Up MergeSort.
    Guaranteed O(N log N) stability with preallocated auxiliary buffer.
    """
    if len(arr) <= 1:
        return list(arr)
    data = list(arr)
    n = len(data)
    aux = [0] * n

    width = 1
    while width < n:
        for i in range(0, n, 2 * width):
            left = i
            mid = min(i + width, n)
            right = min(i + 2 * width, n)
            
            p1, p2, k = left, mid, left
            while p1 < mid and p2 < right:
                if data[p1] <= data[p2]:
                    aux[k] = data[p1]
                    p1 += 1
                else:
                    aux[k] = data[p2]
                    p2 += 1
                k += 1
            while p1 < mid:
                aux[k] = data[p1]
                p1 += 1
                k += 1
            while p2 < right:
                aux[k] = data[p2]
                p2 += 1
                k += 1
            for idx in range(left, right):
                data[idx] = aux[idx]
        width *= 2

    return data
''',

    "heapsort": '''from typing import List

def solve(arr: List[int]) -> List[int]:
    """
    In-Place Max-HeapSort.
    O(N log N) guaranteed runtime and O(1) auxiliary space.
    """
    data = list(arr)
    n = len(data)

    def heapify(size: int, i: int):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < size and data[left] > data[largest]:
            largest = left
        if right < size and data[right] > data[largest]:
            largest = right
        if largest != i:
            data[i], data[largest] = data[largest], data[i]
            heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    for i in range(n - 1, 0, -1):
        data[0], data[i] = data[i], data[0]
        heapify(i, 0)

    return data
''',

    "naive_quicksort": '''from typing import List

def solve(arr: List[int]) -> List[int]:
    """
    Naive 2-Way QuickSort with fixed first element pivot.
    NOTE: Vulnerable to reverse-sorted and duplicate-heavy inputs.
    """
    data = list(arr)
    if len(data) <= 1:
        return data

    def partition(low: int, high: int) -> int:
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            if data[j] <= pivot:
                i += 1
                data[i], data[j] = data[j], data[i]
        data[i + 1], data[high] = data[high], data[i + 1]
        return i + 1

    def quicksort_rec(low: int, high: int):
        if low < high:
            pi = partition(low, high)
            quicksort_rec(low, pi - 1)
            quicksort_rec(pi + 1, high)

    quicksort_rec(0, len(data) - 1)
    return data
''',

    # Knapsack Candidates
    "knapsack_1d": '''from typing import List

def solve(weights: List[int], values: List[int], capacity: int) -> int:
    """
    1D Space-Optimized Dynamic Programming Knapsack.
    O(N * W) time complexity, O(W) auxiliary space.
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0
    dp = [0] * (capacity + 1)
    for i in range(n):
        w = weights[i]
        v = values[i]
        for c in range(capacity, w - 1, -1):
            if dp[c - w] + v > dp[c]:
                dp[c] = dp[c - w] + v
    return dp[capacity]
''',

    "knapsack_2d": '''from typing import List

def solve(weights: List[int], values: List[int], capacity: int) -> int:
    """
    2D Table Dynamic Programming Knapsack.
    O(N * W) time, O(N * W) memory.
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
''',

    "knapsack_greedy": '''from typing import List

def solve(weights: List[int], values: List[int], capacity: int) -> int:
    """
    Greedy Value-Density Knapsack Heuristic.
    NOTE: Known sub-optimal approximation on discrete 0/1 knapsack.
    """
    items = []
    for i in range(len(weights)):
        if weights[i] > 0:
            density = values[i] / weights[i]
            items.append((density, values[i], weights[i]))
    items.sort(reverse=True, key=lambda x: x[0])
    
    total_val = 0
    curr_cap = capacity
    for density, val, wt in items:
        if wt <= curr_cap:
            curr_cap -= wt
            total_val += val
    return total_val
''',

    # Graph Traversal Candidates
    "graph_traversal_bfs": '''from collections import deque
from typing import List, Tuple, Dict

def solve(n: int, edges: List[Tuple[int, int]], start: int) -> List[int]:
    """
    Deterministic Iterative BFS with collections.deque and sorted neighbor tie-breaking.
    """
    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for u in adj:
        adj[u].sort()

    visited = set([start])
    queue = deque([start])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return order
'''
}

def generate_code_for_candidate(candidate: CandidateAlgorithm, spec: ProblemSpec) -> str:
    """
    Assigns or synthesizes appropriate verified Python implementation code for the candidate.
    """
    name_lower = candidate.name.lower()
    pf = (spec.problem_family or "").lower()

    if "shortest" in pf or "path" in pf or "dijkstra" in pf:
        if "dijkstra" in name_lower or "heap" in name_lower:
            return CODE_TEMPLATES["dijkstra"]
        elif "a*" in name_lower or "heuristic" in name_lower:
            return CODE_TEMPLATES["astar"]
        elif "bellman" in name_lower:
            return CODE_TEMPLATES["bellman"]
        elif "bfs" in name_lower or "breadth" in name_lower:
            return CODE_TEMPLATES["bfs_naive"]
        return CODE_TEMPLATES["dijkstra"]

    elif "subarray" in pf:
        if "kadane" in name_lower:
            return CODE_TEMPLATES["kadane"]
        elif "divide" in name_lower:
            return CODE_TEMPLATES["dnc_subarray"]
        elif "prefix" in name_lower:
            return CODE_TEMPLATES["prefix_subarray"]
        elif "brute" in name_lower:
            return CODE_TEMPLATES["bruteforce_subarray"]
        return CODE_TEMPLATES["kadane"]

    elif "sort" in pf:
        if "3-way" in name_lower or "dutch" in name_lower or "quicksort" in name_lower and "naive" not in name_lower:
            return CODE_TEMPLATES["quicksort_3way"]
        elif "merge" in name_lower:
            return CODE_TEMPLATES["mergesort"]
        elif "heap" in name_lower:
            return CODE_TEMPLATES["heapsort"]
        elif "naive" in name_lower:
            return CODE_TEMPLATES["naive_quicksort"]
        return CODE_TEMPLATES["quicksort_3way"]

    elif "knapsack" in pf:
        if "1d" in name_lower or "rolling" in name_lower or "space-optimized" in name_lower:
            return CODE_TEMPLATES["knapsack_1d"]
        elif "2d" in name_lower or "table" in name_lower:
            return CODE_TEMPLATES["knapsack_2d"]
        elif "greedy" in name_lower:
            return CODE_TEMPLATES["knapsack_greedy"]
        return CODE_TEMPLATES["knapsack_1d"]

    elif "traversal" in pf or "graph" in pf:
        return CODE_TEMPLATES["graph_traversal_bfs"]

    # Fallback to Kadane
    return CODE_TEMPLATES["kadane"]
