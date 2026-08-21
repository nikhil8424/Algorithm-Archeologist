import unittest
from app.tools.sandbox import validate_code_safety
from app.tools.executor import code_executor
from app.tools.oracle import oracle
from app.tools.problem_analyzer import problem_analyzer
from app.tools.complexity import complexity_estimator

class TestTools(unittest.TestCase):
    def test_sandbox_ast_security_blocks_os(self):
        code = "import os\ndef solve(): os.system('ls')"
        safe, violations = validate_code_safety(code)
        self.assertFalse(safe)
        self.assertTrue(any("os" in v for v in violations))

    def test_sandbox_ast_security_blocks_eval(self):
        code = "def solve(x): return eval(x)"
        safe, violations = validate_code_safety(code)
        self.assertFalse(safe)
        self.assertTrue(any("eval" in v for v in violations))

    def test_executor_runs_kadane(self):
        code = """def solve(arr):
    m = arr[0]
    c = arr[0]
    for x in arr[1:]:
        c = max(x, c + x)
        m = max(m, c)
    return m
"""
        res = code_executor.execute(code, {"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]})
        self.assertTrue(res["passed"])
        self.assertEqual(res["actual_output"], 6)

    def test_oracles_correctness(self):
        # Oracle shortest path
        edges = [(0, 1, 1), (1, 2, 2), (0, 2, 5)]
        cost = oracle.solve_shortest_path(3, edges, 0, 2)
        self.assertEqual(cost, 3)

        # Oracle max subarray
        max_sub = oracle.solve_max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])
        self.assertEqual(max_sub, 6)

    def test_complexity_curve_fitting(self):
        linear_data = [(100, 1.0), (1000, 10.0), (10000, 100.0)]
        fit = complexity_estimator.fit_curve(linear_data)
        self.assertIn("O(N)", fit)

if __name__ == "__main__":
    unittest.main()
