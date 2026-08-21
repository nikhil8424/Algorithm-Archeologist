import unittest
from app.models.problem import ProblemSpec, ProblemFamily
from app.models.candidate import AlgorithmCandidate
from app.models.testcase import TestCase, TestCategory, TestStatus
from app.models.experiment import Experiment, PipelineStage

class TestModels(unittest.TestCase):
    def test_problem_spec_creation(self):
        p = ProblemSpec(
            id="test-prob",
            title="Test Problem",
            description="Testing spec",
            problem_family=ProblemFamily.ARRAY_SEARCH,
        )
        self.assertEqual(p.id, "test-prob")
        self.assertEqual(p.problem_family, ProblemFamily.ARRAY_SEARCH)

    def test_candidate_creation(self):
        c = AlgorithmCandidate(
            id="cand-1",
            name="Kadane DP",
            paradigm="Dynamic Programming",
            strategy_description="Single pass",
            code="def solve(arr): return max(arr)",
        )
        self.assertEqual(c.id, "cand-1")
        self.assertEqual(c.generation, 0)
        self.assertFalse(c.is_winner)

if __name__ == "__main__":
    unittest.main()
