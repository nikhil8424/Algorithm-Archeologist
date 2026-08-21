import unittest
from app.main import orchestrator
from app.models.experiment import PipelineStage
from app.storage.repositories import experiment_repo

class TestPipeline(unittest.TestCase):
    def test_full_autonomous_pipeline(self):
        exp = orchestrator.create_experiment("max-subarray-sum", 3)
        self.assertEqual(exp.current_state, PipelineStage.ANALYZE)

        # Run to completion
        completed_exp = orchestrator.run_all(exp.id)
        self.assertEqual(completed_exp.current_state, PipelineStage.DONE)
        self.assertIsNotNone(completed_exp.winner_candidate_id)
        self.assertIsNotNone(completed_exp.final_report)
        self.assertGreater(len(completed_exp.candidates), 0)
        self.assertGreater(len(completed_exp.test_cases), 0)
        self.assertGreater(len(completed_exp.benchmark_results), 0)

        # Test retrieval from repo
        fetched = experiment_repo.get_by_id(completed_exp.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.winner_candidate_id, completed_exp.winner_candidate_id)

if __name__ == "__main__":
    unittest.main()
