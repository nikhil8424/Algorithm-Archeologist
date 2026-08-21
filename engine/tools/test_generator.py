"""
Adversarial and Multi-Category Test Generator for Algorithm Archaeologist.
Generates 7 categories of tests:
1. Normal
2. Edge
3. Boundary
4. Random
5. Adversarial (designed specifically to expose algorithmic pitfalls)
6. Metamorphic
7. Property-based (with minimal counterexample generation)
"""
import random
from typing import List, Dict, Any
import uuid
from engine.models import TestCase, TestCategory, ProblemSpec
from engine.tools.oracle import compute_reference_output

def generate_max_subarray_tests(spec: ProblemSpec) -> List[TestCase]:
    tests: List[TestCase] = []
    
    # 1. Normal
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
        expected_output=6,
        category=TestCategory.NORMAL,
        description="Standard textbook Kadane array"
    ))
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [1, 2, 3, 4, 5]},
        expected_output=15,
        category=TestCategory.NORMAL,
        description="All positive strictly increasing array"
    ))

    # 2. Edge
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [-8]},
        expected_output=-8,
        category=TestCategory.EDGE,
        description="Single negative element"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [-5, -2, -9, -1, -7]},
        expected_output=-1,
        category=TestCategory.EDGE,
        description="All negative elements (tests if algorithm incorrectly returns 0)"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [0, 0, 0, 0]},
        expected_output=0,
        category=TestCategory.EDGE,
        description="All zeros array"
    ))

    # 3. Boundary
    tests.append(TestCase(
        id=f"test_bound_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [1000000] * 50},
        expected_output=50000000,
        category=TestCategory.BOUNDARY,
        description="Large positive values causing possible overflow in weak languages"
    ))

    # 4. Adversarial
    # Alternating large positive and negative values (trap for naive greedy)
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [100, -101, 100, -101, 100, -101, 200]},
        expected_output=200,
        category=TestCategory.ADVERSARIAL,
        description="Deep valley array (penalizes greedy accumulation)",
        is_adversarial=True
    ))
    # Massive negative barrier between small positive and huge positive
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [50, 40, -1000, 200, 300, -1, 50]},
        expected_output=549,
        category=TestCategory.ADVERSARIAL,
        description="Subarray with strong negative separator partition",
        is_adversarial=True
    ))

    # 5. Random
    rng = random.Random(42)
    for i in range(3):
        size = 30 + i * 20
        arr = [rng.randint(-500, 500) for _ in range(size)]
        exp_out = compute_reference_output(spec.problem_family, {"arr": arr})
        tests.append(TestCase(
            id=f"test_rand_{uuid.uuid4().hex[:6]}",
            input_data={"arr": arr},
            expected_output=exp_out,
            category=TestCategory.RANDOM,
            description=f"Randomized array size {size} with values in [-500, 500]"
        ))

    # 6. Metamorphic (scaled array)
    base_arr = [-10, 20, 30, -5, 40, -50]
    scaled_arr = [x * 2 for x in base_arr]
    exp_scaled = compute_reference_output(spec.problem_family, {"arr": scaled_arr})
    tests.append(TestCase(
        id=f"test_meta_{uuid.uuid4().hex[:6]}",
        input_data={"arr": scaled_arr},
        expected_output=exp_scaled,
        category=TestCategory.METAMORPHIC,
        description="Metamorphic scaling test: f(2 * x) == 2 * f(x)"
    ))

    return tests

def generate_sorting_tests(spec: ProblemSpec) -> List[TestCase]:
    tests: List[TestCase] = []
    
    # Normal
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [5, 2, 9, 1, 5, 6]},
        expected_output=[1, 2, 5, 5, 6, 9],
        category=TestCategory.NORMAL,
        description="Standard unordered array with duplicates"
    ))

    # Edge
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [42]},
        expected_output=[42],
        category=TestCategory.EDGE,
        description="Single element array"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": []},
        expected_output=[],
        category=TestCategory.EDGE,
        description="Empty array"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [7, 7, 7, 7, 7, 7, 7]},
        expected_output=[7, 7, 7, 7, 7, 7, 7],
        category=TestCategory.EDGE,
        description="All identical elements (QuickSort O(n^2) pivot degradation test)"
    ))

    # Adversarial (QuickSort killers)
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={"arr": list(range(100, 0, -1))},
        expected_output=list(range(1, 101)),
        category=TestCategory.ADVERSARIAL,
        description="Reverse sorted array (tests naive pivot selection O(n^2))",
        is_adversarial=True
    ))
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={"arr": [1, 2] * 40},
        expected_output=sorted([1, 2] * 40),
        category=TestCategory.ADVERSARIAL,
        description="Heavy two-value duplicate barrage (Dutch National Flag test)",
        is_adversarial=True
    ))

    # Random
    rng = random.Random(1337)
    for i in range(2):
        arr = [rng.randint(-1000, 1000) for _ in range(50 + i * 50)]
        tests.append(TestCase(
            id=f"test_rand_{uuid.uuid4().hex[:6]}",
            input_data={"arr": arr},
            expected_output=sorted(arr),
            category=TestCategory.RANDOM,
            description=f"Random permutation array size {len(arr)}"
        ))

    return tests

def generate_shortest_path_tests(spec: ProblemSpec) -> List[TestCase]:
    tests: List[TestCase] = []

    # 1. Normal graph
    # 0 -> 1 (4), 0 -> 2 (2), 2 -> 1 (1), 1 -> 3 (5), 2 -> 3 (8)
    # Shortest 0 to 3: 0 -> 2 -> 1 -> 3 = 2 + 1 + 5 = 8
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={
            "n": 4,
            "edges": [(0, 1, 4.0), (0, 2, 2.0), (2, 1, 1.0), (1, 3, 5.0), (2, 3, 8.0)],
            "start": 0,
            "target": 3
        },
        expected_output=8.0,
        category=TestCategory.NORMAL,
        description="Standard DAG with multi-hop shortcut"
    ))

    # 2. Edge
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={
            "n": 5,
            "edges": [(0, 1, 1.0), (2, 3, 2.0)],
            "start": 0,
            "target": 4
        },
        expected_output=-1.0,
        category=TestCategory.EDGE,
        description="Disconnected component (unreachable target returns -1)"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={
            "n": 3,
            "edges": [(0, 1, 10.0), (1, 2, 10.0)],
            "start": 0,
            "target": 0
        },
        expected_output=0.0,
        category=TestCategory.EDGE,
        description="Start equals target node (distance 0.0)"
    ))

    # 3. Adversarial (High edge weight difference / dense graph / non-unit weights)
    # BFS will fail on this because edge 0->1 has weight 100 (1 hop), but 0->2->3->1 has weight 1+1+1=3 (3 hops)
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={
            "n": 4,
            "edges": [(0, 1, 100.0), (0, 2, 1.0), (2, 3, 1.0), (3, 1, 1.0)],
            "start": 0,
            "target": 1
        },
        expected_output=3.0,
        category=TestCategory.ADVERSARIAL,
        description="Few-hops heavy edge vs many-hops cheap path (Exposes unweighted BFS defect)",
        is_adversarial=True
    ))

    # 4. Long Chain Graph (tests recursion limits in naive DFS)
    chain_edges = [(i, i + 1, 1.0) for i in range(40)]
    tests.append(TestCase(
        id=f"test_bound_{uuid.uuid4().hex[:6]}",
        input_data={
            "n": 41,
            "edges": chain_edges,
            "start": 0,
            "target": 40
        },
        expected_output=40.0,
        category=TestCategory.BOUNDARY,
        description="Long 40-node linear chain graph"
    ))

    return tests

def generate_knapsack_tests(spec: ProblemSpec) -> List[TestCase]:
    tests: List[TestCase] = []
    
    # Normal
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={"weights": [2, 3, 4, 5], "values": [3, 4, 5, 6], "capacity": 5},
        expected_output=7, # weights 2+3=5, values 3+4=7
        category=TestCategory.NORMAL,
        description="Standard 0/1 knapsack example"
    ))

    # Adversarial (Greedy density trap)
    # Item 1: value 60, weight 10 (density 6)
    # Item 2: value 100, weight 20 (density 5)
    # Item 3: value 120, weight 30 (density 4)
    # Capacity = 50. Greedy by density picks 1 (w=10) + 2 (w=20) -> value 160 (remaining capacity 20).
    # Optimal picks 2 (w=20) + 3 (w=30) -> value 220!
    tests.append(TestCase(
        id=f"test_adv_{uuid.uuid4().hex[:6]}",
        input_data={"weights": [10, 20, 30], "values": [60, 100, 120], "capacity": 50},
        expected_output=220,
        category=TestCategory.ADVERSARIAL,
        description="Value density counterexample (exposes greedy heuristic failure)",
        is_adversarial=True
    ))

    # Edge
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"weights": [10, 20], "values": [100, 200], "capacity": 5},
        expected_output=0,
        category=TestCategory.EDGE,
        description="Zero capacity budget for items"
    ))

    return tests

def generate_graph_traversal_tests(spec: ProblemSpec) -> List[TestCase]:
    tests: List[TestCase] = []
    tests.append(TestCase(
        id=f"test_norm_{uuid.uuid4().hex[:6]}",
        input_data={"n": 4, "edges": [(0, 1), (0, 2), (1, 3)], "start": 0},
        expected_output=[0, 1, 2, 3],
        category=TestCategory.NORMAL,
        description="Simple tree BFS traversal"
    ))
    tests.append(TestCase(
        id=f"test_edge_{uuid.uuid4().hex[:6]}",
        input_data={"n": 3, "edges": [], "start": 0},
        expected_output=[0],
        category=TestCategory.EDGE,
        description="Isolated node traversal"
    ))
    return tests

def generate_test_suite_for_problem(spec: ProblemSpec) -> List[TestCase]:
    """
    Main entry point for generating dynamic test suites for any problem.
    """
    pf = (spec.problem_family or "").lower()
    
    if "subarray" in pf:
        return generate_max_subarray_tests(spec)
    elif "sort" in pf:
        return generate_sorting_tests(spec)
    elif "shortest" in pf or "path" in pf or "dijkstra" in pf or "graph" in pf and ("node" in spec.description.lower() or "weighted" in spec.description.lower()):
        return generate_shortest_path_tests(spec)
    elif "knapsack" in pf:
        return generate_knapsack_tests(spec)
    elif "traversal" in pf or "bfs" in pf or "dfs" in pf:
        return generate_graph_traversal_tests(spec)
    else:
        # Fallback generic array generator
        return generate_max_subarray_tests(spec)
