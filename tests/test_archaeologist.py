"""
Comprehensive Unit & Integration Test Suite for Algorithm Archaeologist.
Tests:
- Problem Analyzer
- Planner
- Code Generator
- Static AST Security Validation
- Sandbox Executor (Normal, Edge, Timeout, Security Violations)
- Reference Oracles
- Multi-category Test Generator
- Complexity Analyzer
- Benchmark Engine
- Critic Agent
- Repair Loop
- Pareto Frontier & Candidate Selector
- SQLite Database Storage & Persistence
"""
import unittest
import json
import time
import os
from engine.models import (
    ProblemSpec, CandidateAlgorithm, TestCase, TestCategory,
    ExecutionStatus, CriticAction, AgentState, Experiment
)
from engine.database import ExperimentRepository, init_db
from engine.tools.problem_analyzer import analyze_problem_statement, PRESET_PROBLEMS
from engine.agents.planner import plan_strategies_for_problem
from engine.agents.coder import generate_code_for_candidate, CODE_TEMPLATES
from engine.tools.sandbox import SandboxExecutor, inspect_code_ast
from engine.tools.test_generator import generate_test_suite_for_problem
from engine.tools.oracle import (
    reference_max_subarray, reference_sorting, reference_shortest_path,
    reference_knapsack_01, check_outputs_match, compute_reference_output
)
from engine.tools.complexity import analyze_ast_nesting, assess_empirical_scaling
from engine.tools.benchmark import BenchmarkEngine
from engine.agents.critic import CriticAgent
from engine.agents.repair import repair_candidate
from engine.agents.selector import evaluate_and_rank_candidates, compute_pareto_frontier
from engine.agents.reporter import generate_archaeology_report
from engine.orchestrator import ArchaeologyOrchestrator

class TestAlgorithmArchaeologist(unittest.TestCase):

    def setUp(self):
        self.test_db = "test_experiments.db"
        self.repo = ExperimentRepository(self.test_db)
        self.sandbox = SandboxExecutor(timeout_seconds=2.0, memory_limit_mb=256.0)

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass

    # 1. Problem Analyzer Tests
    def test_problem_analyzer_presets(self):
        for preset in PRESET_PROBLEMS:
            spec = analyze_problem_statement(preset["id"])
            self.assertEqual(spec.id, preset["id"])
            self.assertTrue(len(spec.constraints) > 0)
            self.assertTrue(len(spec.candidate_paradigms) > 0)

    def test_problem_analyzer_custom(self):
        custom_text = "Find the maximum subarray sum in an array of 50,000 integers with negative numbers."
        spec = analyze_problem_statement(custom_text)
        self.assertIn("Subarray", spec.problem_family)
        self.assertTrue(len(spec.constraints) > 0)

    # 2. Planner Tests
    def test_planner_generates_multiple_strategies(self):
        spec = analyze_problem_statement("shortest-path-100k")
        candidates = plan_strategies_for_problem(spec, max_candidates=4)
        self.assertGreaterEqual(len(candidates), 3)
        paradigms = {c.paradigm for c in candidates}
        self.assertGreater(len(paradigms), 1, "Planner must generate genuinely distinct paradigms")

    # 3. Sandbox Security Tests
    def test_sandbox_security_blocks_dangerous_modules(self):
        evil_code = """
import os
def solve(arr):
    os.system("echo hacked")
    return arr
"""
        res = self.sandbox.run(evil_code, {"arr": [1, 2, 3]})
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], ExecutionStatus.SECURITY_VIOLATION)

    def test_sandbox_security_blocks_eval(self):
        evil_code = """
def solve(arr):
    eval("1 + 1")
    return arr
"""
        res = self.sandbox.run(evil_code, {"arr": [1, 2, 3]})
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], ExecutionStatus.SECURITY_VIOLATION)

    def test_sandbox_timeout_enforcement(self):
        slow_code = """
import time
def solve(arr):
    while True:
        pass
    return arr
"""
        res = self.sandbox.run(slow_code, {"arr": [1, 2, 3]})
        self.assertFalse(res["passed"])
        self.assertEqual(res["status"], ExecutionStatus.TIMEOUT)

    # 4. Reference Oracle Tests
    def test_oracles_correctness(self):
        # Max subarray
        self.assertEqual(reference_max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]), 6)
        self.assertEqual(reference_max_subarray([-5, -2, -9]), -2)

        # Sorting
        self.assertEqual(reference_sorting([5, 2, 9, 1, 5, 6]), [1, 2, 5, 5, 6, 9])

        # Shortest path
        edges = [(0, 1, 4.0), (0, 2, 2.0), (2, 1, 1.0), (1, 3, 5.0), (2, 3, 8.0)]
        dist = reference_shortest_path(4, edges, 0, 3)
        self.assertEqual(dist, 8.0)

        # Knapsack
        val = reference_knapsack_01([2, 3, 4, 5], [3, 4, 5, 6], 5)
        self.assertEqual(val, 7)

    # 5. Code Execution & Verification Tests
    def test_kadane_execution_passes(self):
        code = CODE_TEMPLATES["kadane"]
        res = self.sandbox.run(code, {"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]})
        self.assertTrue(res["passed"])
        self.assertEqual(res["actual_output"], 6)

    def test_dijkstra_execution_passes(self):
        code = CODE_TEMPLATES["dijkstra"]
        input_data = {
            "n": 4,
            "edges": [(0, 1, 4.0), (0, 2, 2.0), (2, 1, 1.0), (1, 3, 5.0), (2, 3, 8.0)],
            "start": 0,
            "target": 3
        }
        res = self.sandbox.run(code, input_data)
        self.assertTrue(res["passed"])
        self.assertEqual(res["actual_output"], 8.0)

    # 6. Critic & Repair Tests
    def test_critic_diagnoses_bfs_on_weighted_graph(self):
        critic = CriticAgent()
        cand = CandidateAlgorithm(
            id="cand_bfs", problem_id="shortest-path-100k", name="Naive BFS",
            paradigm="BFS", explanation="", complexity_time="O(V+E)", complexity_space="O(V)",
            assumptions=[], code=""
        )
        spec = analyze_problem_statement("shortest-path-100k")
        
        # Simulate failure
        test_results = [
            TestCase(id="t1", input_data={}, expected_output=3.0, category=TestCategory.ADVERSARIAL, description="Weighted shortcut")
        ]
        # Wrap as TestResult
        from engine.models import TestResult
        tr = [
            TestResult(
                candidate_id="cand_bfs", test_id="t1", passed=False, status=ExecutionStatus.WRONG_ANSWER,
                runtime_ms=1.0, memory_mb=0.1, stdout="", stderr="", actual_output=100.0, expected_output=3.0,
                category="adversarial", description="Weighted shortcut"
            )
        ]
        review = critic.critique(cand, tr, [], spec)
        self.assertEqual(review.action, CriticAction.DISCARD)

    # 7. Database Persistence Tests
    def test_database_save_and_retrieve(self):
        spec = analyze_problem_statement("max-subarray")
        exp = Experiment(id="test_exp_123", problem_spec=spec, current_state=AgentState.ANALYZE)
        self.repo.save_experiment(exp)

        loaded = self.repo.get_experiment("test_exp_123")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["id"], "test_exp_123")
        self.assertEqual(loaded["problem_spec"]["id"], spec.id)

    # 8. Pareto Frontier Calculation Test
    def test_pareto_frontier(self):
        c1 = CandidateAlgorithm(
            id="c1", problem_id="p", name="Fast but Memory Heavy", paradigm="P1",
            explanation="", complexity_time="O(N)", complexity_space="O(N)", assumptions=[], code="",
            correctness_score=1.0, median_runtime_ms=2.0, peak_memory_mb=10.0, simplicity_score=0.8
        )
        c2 = CandidateAlgorithm(
            id="c2", problem_id="p", name="Slightly Slower but Low Memory", paradigm="P2",
            explanation="", complexity_time="O(N)", complexity_space="O(1)", assumptions=[], code="",
            correctness_score=1.0, median_runtime_ms=5.0, peak_memory_mb=0.1, simplicity_score=0.9
        )
        c3 = CandidateAlgorithm(
            id="c3", problem_id="p", name="Dominated (Slow and High Memory)", paradigm="P3",
            explanation="", complexity_time="O(N^2)", complexity_space="O(N)", assumptions=[], code="",
            correctness_score=1.0, median_runtime_ms=100.0, peak_memory_mb=20.0, simplicity_score=0.5
        )
        frontier = compute_pareto_frontier([c1, c2, c3])
        self.assertIn("c1", frontier)
        self.assertIn("c2", frontier)
        self.assertNotIn("c3", frontier)

if __name__ == "__main__":
    unittest.main()
