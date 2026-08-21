import random
from typing import List
from app.models.problem import ProblemSpec, ProblemFamily
from app.models.testcase import TestCase, TestCategory
from app.tools.oracle import oracle

class TestGenerator:
    def generate_suite(self, problem: ProblemSpec, count: int = 14) -> List[TestCase]:
        generator_map = {
            "shortest-path-100k": self._gen_shortest_path_tests,
            "max-subarray-sum": self._gen_max_subarray_tests,
            "kth-largest-element": self._gen_kth_largest_tests,
            "longest-increasing-subsequence": self._gen_lis_tests,
            "convex-hull-2d": self._gen_convex_hull_tests,
            "string-search-kmp": self._gen_string_search_tests,
        }

        gen_func = generator_map.get(problem.id, self._gen_generic_tests)
        return gen_func(problem)

    def _gen_shortest_path_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []

        # 1. Normal Case
        edges1 = [(0, 1, 4), (0, 2, 2), (2, 1, 1), (1, 3, 5), (2, 3, 8)]
        exp1 = oracle.solve_shortest_path(4, edges1, 0, 3)
        tests.append(TestCase(
            id="test-normal-1",
            name="Simple Multi-Hop Weighted Graph",
            category=TestCategory.NORMAL,
            description="Basic triangular detour with edge weights.",
            input_payload={"n": 4, "edges": edges1, "source": 0, "target": 3},
            expected_output=exp1,
            input_size=4,
        ))

        # 2. Edge Case: Disconnected Target
        edges2 = [(0, 1, 2), (2, 3, 5)]
        exp2 = oracle.solve_shortest_path(4, edges2, 0, 3)
        tests.append(TestCase(
            id="test-edge-disconnected",
            name="Unreachable Destination (Disconnected)",
            category=TestCategory.EDGE_CASE,
            description="Graph with separate connected components, target unreachable.",
            input_payload={"n": 4, "edges": edges2, "source": 0, "target": 3},
            expected_output=exp2,
            input_size=4,
        ))

        # 3. Boundary Case: Single Vertex (Source == Target)
        tests.append(TestCase(
            id="test-boundary-single",
            name="Self-Loop / Zero Distance Source",
            category=TestCategory.BOUNDARY,
            description="Source is target; distance must be exactly 0.",
            input_payload={"n": 1, "edges": [], "source": 0, "target": 0},
            expected_output=0,
            input_size=1,
        ))

        # 4. Adversarial Trap: BFS-Killer Path
        # Short hop has high weight (100), long hop has low weights (1 + 1 + 1 = 3).
        # Unweighted BFS chooses 0->3 (cost 100), Dijkstra finds 0->1->2->3 (cost 3).
        edges_trap = [(0, 3, 100), (0, 1, 1), (1, 2, 1), (2, 3, 1)]
        exp_trap = oracle.solve_shortest_path(4, edges_trap, 0, 3)
        tests.append(TestCase(
            id="test-adversarial-bfs-trap",
            name="Adversarial BFS-Killer Shortcut Trap",
            category=TestCategory.ADVERSARIAL_TRAP,
            description="Fewer hops has massive weight; multi-hop has minimal weight.",
            input_payload={"n": 4, "edges": edges_trap, "source": 0, "target": 3},
            expected_output=exp_trap,
            input_size=4,
        ))

        # 5. Randomized Distribution: Dense DAG
        random.seed(42)
        n_rand = 60
        edges_rand = []
        for u in range(n_rand):
            for v in range(u + 1, min(n_rand, u + 8)):
                edges_rand.append((u, v, random.randint(1, 50)))
        exp_rand = oracle.solve_shortest_path(n_rand, edges_rand, 0, n_rand - 1)
        tests.append(TestCase(
            id="test-random-dense-dag",
            name="Randomized Heavy DAG Cluster",
            category=TestCategory.RANDOMIZED_DISTRIBUTION,
            description="60-node randomized multi-path directed acyclic graph.",
            input_payload={"n": n_rand, "edges": edges_rand, "source": 0, "target": n_rand - 1},
            expected_output=exp_rand,
            input_size=n_rand,
        ))

        # 6. Metamorphic Invariant: Linear Chain
        n_chain = 150
        edges_chain = [(i, i + 1, 2) for i in range(n_chain - 1)]
        exp_chain = oracle.solve_shortest_path(n_chain, edges_chain, 0, n_chain - 1)
        tests.append(TestCase(
            id="test-metamorphic-chain",
            name="Metamorphic Scale Invariant (Linear Chain)",
            category=TestCategory.METAMORPHIC_INVARIANT,
            description="Linear chain of N vertices with uniform edge weights.",
            input_payload={"n": n_chain, "edges": edges_chain, "source": 0, "target": n_chain - 1},
            expected_output=exp_chain,
            input_size=n_chain,
        ))

        # 7. Property-Based: Dense Complete Bipartite
        edges_bipartite = []
        for u in range(25):
            for v in range(25, 50):
                edges_bipartite.append((u, v, u + v + 1))
        edges_bipartite.append((49, 50, 1))
        exp_bip = oracle.solve_shortest_path(51, edges_bipartite, 0, 50)
        tests.append(TestCase(
            id="test-property-bipartite",
            name="Property-Based Bipartite Bottleneck",
            category=TestCategory.PROPERTY_BASED,
            description="High-degree transition layers funneling into single sink.",
            input_payload={"n": 51, "edges": edges_bipartite, "source": 0, "target": 50},
            expected_output=exp_bip,
            input_size=51,
        ))

        return tests

    def _gen_max_subarray_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []
        cases = [
            ("Normal Mixed", [-2, 1, -3, 4, -1, 2, 1, -5, 4], TestCategory.NORMAL, "Classic textbook array with mixed signs"),
            ("All Negative Elements", [-12, -4, -20, -1, -8], TestCategory.EDGE_CASE, "Array containing only strictly negative values"),
            ("Single Value Boundary", [42], TestCategory.BOUNDARY, "Array with exactly N=1 element"),
            ("Adversarial Sawtooth Trap", [100, -101, 100, -101, 100, -101, 100], TestCategory.ADVERSARIAL_TRAP, "Oscillating high-variance boundary resets"),
            ("Randomized Uniform Array", [random.randint(-50, 50) for _ in range(500)], TestCategory.RANDOMIZED_DISTRIBUTION, "500 uniformly sampled integers"),
            ("All Positive Invariant", [5, 10, 15, 20, 25, 30], TestCategory.METAMORPHIC_INVARIANT, "Monotonically increasing positive integers"),
            ("Zeros & Flat Valleys", [0, 0, -5, 0, 10, 0, 0, -2, 4], TestCategory.PROPERTY_BASED, "Plateaus of zero boundaries"),
        ]
        for i, (name, arr, cat, desc) in enumerate(cases):
            tests.append(TestCase(
                id=f"test-subarray-{i+1}",
                name=name,
                category=cat,
                description=desc,
                input_payload={"arr": arr},
                expected_output=oracle.solve_max_subarray(arr),
                input_size=len(arr),
            ))
        return tests

    def _gen_kth_largest_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []
        cases = [
            ("Normal Array", [3, 2, 1, 5, 6, 4], 2, TestCategory.NORMAL, "Standard unsorted array, 2nd largest"),
            ("All Duplicates", [7, 7, 7, 7, 7], 3, TestCategory.EDGE_CASE, "Array with uniform identical values"),
            ("K=1 Boundary (Max)", [10, 4, 20, 1, 8], 1, TestCategory.BOUNDARY, "K=1 boundary asking for absolute maximum"),
            ("K=N Boundary (Min)", [10, 4, 20, 1, 8], 5, TestCategory.BOUNDARY, "K=N boundary asking for absolute minimum"),
            ("Adversarial Dutch Flag", [1, 2] * 100 + [999] * 5, 3, TestCategory.ADVERSARIAL_TRAP, "Highly skewed duplicate partition trap"),
            ("Randomized 1k Array", [random.randint(-1000, 1000) for _ in range(1000)], 50, TestCategory.RANDOMIZED_DISTRIBUTION, "1,000 random integers"),
        ]
        for i, (name, nums, k, cat, desc) in enumerate(cases):
            tests.append(TestCase(
                id=f"test-kth-{i+1}",
                name=name,
                category=cat,
                description=desc,
                input_payload={"nums": nums, "k": k},
                expected_output=oracle.solve_kth_largest(nums, k),
                input_size=len(nums),
            ))
        return tests

    def _gen_lis_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []
        cases = [
            ("Normal Mixed", [10, 9, 2, 5, 3, 7, 101, 18], TestCategory.NORMAL, "Standard unsorted permutation"),
            ("Strictly Decreasing", [9, 8, 7, 6, 5, 4, 3, 2, 1], TestCategory.EDGE_CASE, "Inverted array where LIS length is 1"),
            ("Strictly Increasing", [1, 2, 3, 4, 5, 6, 7, 8, 9], TestCategory.BOUNDARY, "Sorted array where LIS length is N"),
            ("Plateau Duplicates", [2, 2, 2, 2, 2], TestCategory.ADVERSARIAL_TRAP, "Strict increase requirement with duplicates"),
            ("Random 500 Array", [random.randint(1, 1000) for _ in range(500)], TestCategory.RANDOMIZED_DISTRIBUTION, "500 randomly distributed integers"),
        ]
        for i, (name, nums, cat, desc) in enumerate(cases):
            tests.append(TestCase(
                id=f"test-lis-{i+1}",
                name=name,
                category=cat,
                description=desc,
                input_payload={"nums": nums},
                expected_output=oracle.solve_lis(nums),
                input_size=len(nums),
            ))
        return tests

    def _gen_convex_hull_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []
        cases = [
            ("Square with Interior Point", [(0, 0), (0, 4), (4, 4), (4, 0), (2, 2)], TestCategory.NORMAL, "4 corners and 1 central interior point"),
            ("Collinear Line", [(0, 0), (1, 1), (2, 2), (3, 3)], TestCategory.EDGE_CASE, "All points lie on single straight line"),
            ("Triangle Boundary", [(0, 0), (5, 0), (2, 4)], TestCategory.BOUNDARY, "Minimum polygon (N=3 points)"),
            ("Concentric Rings", [(0, 0), (1, 1), (-1, -1), (10, 10), (-10, 10), (-10, -10), (10, -10)], TestCategory.ADVERSARIAL_TRAP, "Inner cloud shielded by outer square"),
        ]
        for i, (name, pts, cat, desc) in enumerate(cases):
            tests.append(TestCase(
                id=f"test-hull-{i+1}",
                name=name,
                category=cat,
                description=desc,
                input_payload={"points": pts},
                expected_output=oracle.solve_convex_hull(pts),
                input_size=len(pts),
            ))
        return tests

    def _gen_string_search_tests(self, problem: ProblemSpec) -> List[TestCase]:
        tests: List[TestCase] = []
        cases = [
            ("Normal Match", "ABABDABACDABABCABAB", "ABABCABAB", TestCategory.NORMAL, "Standard pattern matching case"),
            ("No Match", "ABCDEFGH", "XYZ", TestCategory.EDGE_CASE, "Pattern not present in text"),
            ("Pathological Repetitive", "A" * 1000 + "B", "A" * 50 + "B", TestCategory.ADVERSARIAL_TRAP, "Adversarial worst-case for naive O(N*M) matcher"),
            ("Multiple Overlaps", "AAAAAA", "AA", TestCategory.METAMORPHIC_INVARIANT, "Overlapping pattern occurrences"),
        ]
        for i, (name, txt, pat, cat, desc) in enumerate(cases):
            tests.append(TestCase(
                id=f"test-kmp-{i+1}",
                name=name,
                category=cat,
                description=desc,
                input_payload={"text": txt, "pattern": pat},
                expected_output=oracle.solve_string_search(txt, pat),
                input_size=len(txt),
            ))
        return tests

    def _gen_generic_tests(self, problem: ProblemSpec) -> List[TestCase]:
        return [
            TestCase(
                id="test-gen-1",
                name="Generic Normal Input",
                category=TestCategory.NORMAL,
                description="Default smoke test payload",
                input_payload={"input_data": [1, 2, 3, 4, 5]},
                expected_output=None,
                input_size=5,
            )
        ]

test_generator = TestGenerator()
