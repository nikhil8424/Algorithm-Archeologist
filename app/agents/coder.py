from typing import List, Dict, Any
from app.models.problem import ProblemSpec
from app.models.candidate import AlgorithmCandidate, Complexity, CandidateOrigin
from app.tools.profiler import profiler

CODE_CATALOG: Dict[str, Dict[str, str]] = {
    "shortest-path-100k": {
        "Dijkstra Priority Queue (Min-Heap)": """import heapq

def solve(n, edges, source, target):
    # Standard Min-Heap Dijkstra
    adj = {i: [] for i in range(n)}
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
""",
        "Naive Unit BFS (Pathological Trap)": """from collections import deque

def solve(n, edges, source, target):
    # Naive Unweighted BFS (Fails on Weighted Graphs)
    adj = {i: [] for i in range(n)}
    for u, v, w in edges:
        if u < n and v < n:
            adj[u].append(v)
            
    visited = {source: 0}
    q = deque([source])
    
    while q:
        u = q.popleft()
        if u == target:
            return visited[u]
        for v in adj[u]:
            if v not in visited:
                visited[v] = visited[u] + 1
                q.append(v)
                
    return -1
""",
        "Dial's Bucket Queues": """def solve(n, edges, source, target):
    # Dial's Algorithm with Integer Buckets
    adj = {i: [] for i in range(n)}
    max_w = 1
    for u, v, w in edges:
        if u < n and v < n:
            adj[u].append((v, w))
            max_w = max(max_w, w)
            
    max_dist = n * max_w + 1
    buckets = [[] for _ in range(max_dist + 1)]
    dist = [float('inf')] * n
    
    dist[source] = 0
    buckets[0].append(source)
    idx = 0
    
    while idx <= max_dist:
        while buckets[idx]:
            u = buckets[idx].pop()
            if idx > dist[u]:
                continue
            if u == target:
                return idx
            for v, w in adj[u]:
                new_d = dist[u] + w
                if new_d < dist[v]:
                    dist[v] = new_d
                    if new_d <= max_dist:
                        buckets[new_d].append(v)
        idx += 1
        
    return int(dist[target]) if dist[target] != float('inf') else -1
""",
        "Bidirectional Dijkstra Search": """import heapq

def solve(n, edges, source, target):
    if source == target:
        return 0
    adj_f = {i: [] for i in range(n)}
    adj_b = {i: [] for i in range(n)}
    for u, v, w in edges:
        if u < n and v < n:
            adj_f[u].append((v, w))
            adj_b[v].append((u, w))
            
    dist_f = {i: float('inf') for i in range(n)}
    dist_b = {i: float('inf') for i in range(n)}
    dist_f[source] = 0
    dist_b[target] = 0
    
    pq_f = [(0, source)]
    pq_b = [(0, target)]
    mu = float('inf')
    
    while pq_f and pq_b:
        df, u = heapq.heappop(pq_f)
        if df <= dist_f[u]:
            for v, w in adj_f[u]:
                if dist_f[u] + w < dist_f[v]:
                    dist_f[v] = dist_f[u] + w
                    heapq.heappush(pq_f, (dist_f[v], v))
                if dist_b[v] != float('inf'):
                    mu = min(mu, dist_f[u] + w + dist_b[v])
                    
        db, u = heapq.heappop(pq_b)
        if db <= dist_b[u]:
            for v, w in adj_b[u]:
                if dist_b[u] + w < dist_b[v]:
                    dist_b[v] = dist_b[u] + w
                    heapq.heappush(pq_b, (dist_b[v], v))
                if dist_f[v] != float('inf'):
                    mu = min(mu, dist_b[u] + w + dist_f[v])
                    
        if min(pq_f[0][0] if pq_f else float('inf'), pq_b[0][0] if pq_b else float('inf')) >= mu:
            break
            
    return int(mu) if mu != float('inf') else -1
"""
    },
    "max-subarray-sum": {
        "Kadane's Dynamic Programming": """def solve(arr):
    # Kadane's single-pass DP
    if not arr:
        return 0
    max_so_far = arr[0]
    curr = arr[0]
    for x in arr[1:]:
        curr = max(x, curr + x)
        max_so_far = max(max_so_far, curr)
    return max_so_far
""",
        "Divide and Conquer Max Subarray": """def solve(arr):
    if not arr:
        return 0
    def helper(low, high):
        if low == high:
            return arr[low]
        mid = (low + high) // 2
        left_max = helper(low, mid)
        right_max = helper(mid + 1, high)
        
        # Crossing sum
        left_cross = -float('inf')
        curr = 0
        for i in range(mid, low - 1, -1):
            curr += arr[i]
            left_cross = max(left_cross, curr)
            
        right_cross = -float('inf')
        curr = 0
        for i in range(mid + 1, high + 1):
            curr += arr[i]
            right_cross = max(right_cross, curr)
            
        return max(left_max, right_max, left_cross + right_cross)
        
    return helper(0, len(arr) - 1)
""",
        "Prefix Sum Array Sweep": """def solve(arr):
    if not arr:
        return 0
    min_prefix = 0
    running = 0
    max_sum = arr[0]
    for x in arr:
        running += x
        max_sum = max(max_sum, running - min_prefix)
        min_prefix = min(min_prefix, running)
    return max_sum
""",
        "Naive Brute Force Cubic": """def solve(arr):
    if not arr:
        return 0
    # Limited to small N to prevent complete freeze
    max_so_far = arr[0]
    for i in range(min(len(arr), 100)):
        for j in range(i, min(len(arr), 100)):
            curr = sum(arr[i:j+1])
            if curr > max_so_far:
                max_so_far = curr
    return max_so_far
"""
    }
}

class CoderAgent:
    """Archaeological Coder: Implements algorithm candidates with clean AST structure."""

    def synthesize_candidates(self, problem: ProblemSpec, plans: List[Dict[str, Any]]) -> List[AlgorithmCandidate]:
        candidates: List[AlgorithmCandidate] = []
        problem_codes = CODE_CATALOG.get(problem.id, {})

        for i, plan in enumerate(plans):
            name = plan["name"]
            code = problem_codes.get(name)
            if not code:
                # Generic fallback solver
                code = """def solve(*args, **kwargs):
    if 'nums' in kwargs and 'k' in kwargs:
        return sorted(kwargs['nums'], reverse=True)[kwargs['k'] - 1]
    if 'arr' in kwargs:
        m = kwargs['arr'][0]
        c = 0
        for x in kwargs['arr']:
            c = max(x, c + x)
            m = max(m, c)
        return m
    return 0
"""

            ast_stats = profiler.analyze_ast(code)
            cand_id = f"cand-{i+1:02d}-{name.lower().replace(' ', '-')[:15]}"

            candidates.append(AlgorithmCandidate(
                id=cand_id,
                name=name,
                paradigm=plan["paradigm"],
                strategy_description=plan["strategy"],
                code=code,
                origin=CandidateOrigin.INITIAL_PLAN,
                generation=0,
                complexity=Complexity(
                    time_theoretical=plan.get("time_theo", "O(N)"),
                    space_theoretical=plan.get("space_theo", "O(1)"),
                    asymptotic_constant_factor=plan.get("constant_factor", "medium"),
                ),
                ast_node_count=ast_stats["ast_node_count"],
                cyclomatic_complexity=ast_stats["cyclomatic_complexity"],
            ))

        return candidates

coder_agent = CoderAgent()
