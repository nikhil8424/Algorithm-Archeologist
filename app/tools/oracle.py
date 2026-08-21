import heapq
from typing import Any, Dict, List, Tuple

class ReferenceOracle:
    """Deterministic ground truth solvers for mathematical and algorithmic problems."""

    @staticmethod
    def solve_shortest_path(n: int, edges: List[Tuple[int, int, int]], source: int, target: int) -> int:
        adj: Dict[int, List[Tuple[int, int]]] = {i: [] for i in range(n)}
        for u, v, w in edges:
            if u < n and v < n:
                adj[u].append((v, w))
        
        dist = {i: float('inf') for i in range(n)}
        dist[source] = 0
        pq = [(0, source)]
        
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == target:
                return int(d)
            for v, w in adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], v))
        return int(dist[target]) if dist[target] != float('inf') else -1

    @staticmethod
    def solve_max_subarray(arr: List[int]) -> int:
        if not arr:
            return 0
        max_so_far = arr[0]
        curr = arr[0]
        for x in arr[1:]:
            curr = max(x, curr + x)
            max_so_far = max(max_so_far, curr)
        return int(max_so_far)

    @staticmethod
    def solve_kth_largest(nums: List[int], k: int) -> int:
        return sorted(nums, reverse=True)[k - 1]

    @staticmethod
    def solve_lis(nums: List[int]) -> int:
        if not nums:
            return 0
        tails = []
        for x in nums:
            import bisect
            idx = bisect.bisect_left(tails, x)
            if idx == len(tails):
                tails.append(x)
            else:
                tails[idx] = x
        return len(tails)

    @staticmethod
    def solve_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        pts = sorted(set(points))
        if len(pts) <= 1:
            return pts

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for p in pts:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(pts):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]

    @staticmethod
    def solve_string_search(text: str, pattern: str) -> List[int]:
        res = []
        p_len = len(pattern)
        if not pattern:
            return []
        for i in range(len(text) - p_len + 1):
            if text[i : i + p_len] == pattern:
                res.append(i)
        return res

oracle = ReferenceOracle()
