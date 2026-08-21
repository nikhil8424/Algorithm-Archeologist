"""
Planner Agent for Algorithm Archaeologist.
Generates 3 to 5 genuinely distinct algorithmic strategies tailored to the problem constraints.
Explicitly accounts for input size, graph properties, value ranges, memory limits, and paradigm trade-offs.
"""
from typing import List, Dict, Any
import uuid
from engine.models import ProblemSpec, CandidateAlgorithm

def plan_strategies_for_problem(spec: ProblemSpec, max_candidates: int = 4) -> List[CandidateAlgorithm]:
    pf = (spec.problem_family or "").lower()
    candidates: List[CandidateAlgorithm] = []

    if "shortest" in pf or "path" in pf or "dijkstra" in pf:
        # Candidate 1: Dijkstra with Min-Heap
        candidates.append(CandidateAlgorithm(
            id=f"cand_dijkstra_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Dijkstra's Algorithm (Min-Heap Priority Queue)",
            paradigm="Greedy / Graph Traversal",
            explanation="Uses a binary min-heap priority queue with adjacency list representation to iteratively relax shortest paths to unvisited vertices.",
            complexity_time="O((V + E) log V)",
            complexity_space="O(V + E)",
            assumptions=["Edge weights are non-negative (w >= 0)", "Graph fits comfortably in memory"],
            potential_weaknesses=["Cannot handle negative weight cycles", "Heap operations incur logarithmic constant factor"],
            code="", # will be populated by coder
            simplicity_score=0.85
        ))

        # Candidate 2: A* Search with Admissible Heuristic
        candidates.append(CandidateAlgorithm(
            id=f"cand_astar_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="A* Heuristic Search",
            paradigm="Informed Best-First Search",
            explanation="Augments Dijkstra with a goal-directed distance heuristic h(u) to prune unpromising branches toward the target vertex.",
            complexity_time="O(E log V) average, O((V + E) log V) worst-case",
            complexity_space="O(V + E)",
            assumptions=["Non-negative weights", "Consistent/admissible heuristic function"],
            potential_weaknesses=["Heuristic calculation overhead per node", "Falls back to standard Dijkstra if heuristic is 0"],
            code="",
            simplicity_score=0.75
        ))

        # Candidate 3: Bellman-Ford Dynamic Programming
        candidates.append(CandidateAlgorithm(
            id=f"cand_bellman_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Bellman-Ford Algorithm",
            paradigm="Dynamic Programming / Edge Relaxation",
            explanation="Iteratively relaxes all E edges (V - 1) times. Highly robust against negative edge weights and capable of cycle detection.",
            complexity_time="O(V * E)",
            complexity_space="O(V)",
            assumptions=["Graph structure provided as edge list"],
            potential_weaknesses=["Extremely slow on large V (100,000 nodes)", "High CPU cycle burn"],
            code="",
            simplicity_score=0.90
        ))

        # Candidate 4: Unweighted Breadth-First Search (Naive Baseline)
        candidates.append(CandidateAlgorithm(
            id=f"cand_bfs_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Breadth-First Search (Unit Step Assumption)",
            paradigm="Queue Traversal / Level Exploration",
            explanation="Explores graph layer-by-layer using FIFO queue under the simplifying assumption that edges have uniform unit weights.",
            complexity_time="O(V + E)",
            complexity_space="O(V)",
            assumptions=["Assumes all edge weights are equal/unit (unweighted graph)"],
            potential_weaknesses=["INCORRECT for non-uniform positive edge weights", "Will fail adversarial multi-hop weighted shortcuts"],
            code="",
            simplicity_score=0.95
        ))

    elif "subarray" in pf:
        # Candidate 1: Kadane's Algorithm
        candidates.append(CandidateAlgorithm(
            id=f"cand_kadane_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Kadane's Dynamic Programming",
            paradigm="Dynamic Programming (State Reduction)",
            explanation="Maintains max ending at current index and global max in a single linear pass with O(1) auxiliary space.",
            complexity_time="O(N)",
            complexity_space="O(1)",
            assumptions=["At least one element is present in array", "Standard arithmetic addition"],
            potential_weaknesses=["Requires handling array of all negative numbers carefully"],
            code="",
            simplicity_score=0.95
        ))

        # Candidate 2: Divide and Conquer
        candidates.append(CandidateAlgorithm(
            id=f"cand_dnc_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Divide and Conquer Subarray Search",
            paradigm="Divide and Conquer",
            explanation="Splits array into halves, recursively solving left, right, and crossing mid-point maximum subarrays.",
            complexity_time="O(N log N)",
            complexity_space="O(log N) recursion stack",
            assumptions=["Array can be partitioned recursively"],
            potential_weaknesses=["Recursion overhead and higher asymptotic complexity than Kadane"],
            code="",
            simplicity_score=0.70
        ))

        # Candidate 3: Prefix Sum Tracking with Running Minimum
        candidates.append(CandidateAlgorithm(
            id=f"cand_prefix_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Prefix Sum with Running Minimum",
            paradigm="Prefix Sum Optimization",
            explanation="Computes prefix sums and maximizes prefix[i] - min_prefix(0...i-1) in one forward pass.",
            complexity_time="O(N)",
            complexity_space="O(1)",
            assumptions=["Array elements are additive"],
            potential_weaknesses=["Off-by-one edge cases on single negative element if min_prefix initialized incorrectly"],
            code="",
            simplicity_score=0.80
        ))

        # Candidate 4: Naive Brute Force
        candidates.append(CandidateAlgorithm(
            id=f"cand_bruteforce_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Exhaustive Quadratic Subarray Sum",
            paradigm="Brute Force",
            explanation="Evaluates all pairs (i, j) and finds the maximum subarray sum by expanding ranges.",
            complexity_time="O(N^2)",
            complexity_space="O(1)",
            assumptions=["None"],
            potential_weaknesses=["Severely unscalable for N > 5,000 elements (timeouts)"],
            code="",
            simplicity_score=0.90
        ))

    elif "sort" in pf:
        # Candidate 1: 3-Way QuickSort
        candidates.append(CandidateAlgorithm(
            id=f"cand_quicksort_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="3-Way Dutch National Flag QuickSort",
            paradigm="Divide and Conquer / Partitioning",
            explanation="Partitions array into elements strictly less, equal, and greater than pivot to withstand duplicate barrage.",
            complexity_time="O(N log N) expected, O(N) for heavy duplicates",
            complexity_space="O(log N) call stack",
            assumptions=["In-place comparison sort"],
            potential_weaknesses=["Worst-case O(N^2) if poor pivot choice on pathological inputs without randomization"],
            code="",
            simplicity_score=0.75
        ))

        # Candidate 2: MergeSort
        candidates.append(CandidateAlgorithm(
            id=f"cand_mergesort_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Iterative/Bottom-Up MergeSort",
            paradigm="Divide and Conquer / Merge",
            explanation="Guarantees strictly stable O(N log N) worst-case performance by merging sorted runs of doubling width.",
            complexity_time="O(N log N) guaranteed",
            complexity_space="O(N) auxiliary buffer",
            assumptions=["Memory available for auxiliary buffer"],
            potential_weaknesses=["O(N) extra memory allocation overhead"],
            code="",
            simplicity_score=0.80
        ))

        # Candidate 3: HeapSort
        candidates.append(CandidateAlgorithm(
            id=f"cand_heapsort_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="In-Place Max-HeapSort",
            paradigm="Priority Queue / Selection",
            explanation="Builds an in-place max-heap in O(N) and repeatedly extracts maximums to the end of the array.",
            complexity_time="O(N log N) guaranteed",
            complexity_space="O(1) in-place",
            assumptions=["In-place mutable list"],
            potential_weaknesses=["Poor cache locality compared to QuickSort / MergeSort"],
            code="",
            simplicity_score=0.85
        ))

        # Candidate 4: Naive 2-Way QuickSort (Vulnerable to duplicates)
        candidates.append(CandidateAlgorithm(
            id=f"cand_naivequick_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Naive 2-Way QuickSort (Fixed Pivot)",
            paradigm="Divide and Conquer",
            explanation="Uses standard fixed first-element pivot with 2-way Lomuto partition.",
            complexity_time="O(N log N) average, O(N^2) worst-case",
            complexity_space="O(N) recursion stack on degenerates",
            assumptions=["Uniform random keys"],
            potential_weaknesses=["Degrades to O(N^2) and recurses deeply on reverse sorted and duplicate arrays"],
            code="",
            simplicity_score=0.90
        ))

    elif "knapsack" in pf:
        # Candidate 1: 1D Rolling Array DP
        candidates.append(CandidateAlgorithm(
            id=f"cand_knap1d_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="1D Space-Optimized Dynamic Programming",
            paradigm="Dynamic Programming (Memory Reduction)",
            explanation="Iterates backwards through capacity using a single 1D array to achieve exact optimal solution with minimal RAM.",
            complexity_time="O(N * W)",
            complexity_space="O(W)",
            assumptions=["Capacity W is an integer within memory constraints"],
            potential_weaknesses=["Pseudo-polynomial time complexity in terms of W"],
            code="",
            simplicity_score=0.90
        ))

        # Candidate 2: 2D Matrix DP
        candidates.append(CandidateAlgorithm(
            id=f"cand_knap2d_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="2D Matrix Dynamic Programming",
            paradigm="Dynamic Programming (Full Table)",
            explanation="Constructs full (N+1) x (W+1) dynamic programming memoization matrix.",
            complexity_time="O(N * W)",
            complexity_space="O(N * W)",
            assumptions=["Capacity and item counts fit in matrix RAM"],
            potential_weaknesses=["High memory footprint for large N and W"],
            code="",
            simplicity_score=0.85
        ))

        # Candidate 3: Greedy Value-to-Weight Density
        candidates.append(CandidateAlgorithm(
            id=f"cand_greedyknap_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Greedy Value Density Approximation",
            paradigm="Greedy Heuristic",
            explanation="Sorts items by value-per-weight density and takes items greedily until capacity is exhausted.",
            complexity_time="O(N log N)",
            complexity_space="O(N)",
            assumptions=["Items are indivisible (0/1)"],
            potential_weaknesses=["SUB-OPTIMAL for 0/1 knapsack: fails adversarial density-trapping test cases"],
            code="",
            simplicity_score=0.92
        ))

    else:
        # Generic Traversal or Array Strategy
        candidates.append(CandidateAlgorithm(
            id=f"cand_opt_{uuid.uuid4().hex[:6]}",
            problem_id=spec.id,
            name="Optimal Linear Algorithm",
            paradigm="Dynamic Programming / Single Pass",
            explanation="Single-pass linear scan with O(1) state space.",
            complexity_time="O(N)",
            complexity_space="O(1)",
            assumptions=["Sequential iterable input"],
            code="",
            simplicity_score=0.90
        ))

    return candidates[:max_candidates]
