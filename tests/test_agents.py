import unittest
from app.agents.planner import planner_agent
from app.agents.coder import coder_agent
from app.agents.tester import tester_agent
from app.agents.critic import critic_agent
from app.agents.selector import selector_agent
from app.tools.problem_analyzer import problem_analyzer
from app.tools.test_generator import test_generator

class TestAgents(unittest.TestCase):
    def test_planner_and_coder(self):
        problem = problem_analyzer.get_preset_problem("shortest-path-100k")
        plans = planner_agent.plan_paradigms(problem, 3)
        self.assertGreaterEqual(len(plans), 3)

        candidates = coder_agent.synthesize_candidates(problem, plans)
        self.assertEqual(len(candidates), len(plans))
        self.assertTrue(candidates[0].ast_node_count > 0)

    def test_tester_and_critic_diagnoses_bfs_failure(self):
        problem = problem_analyzer.get_preset_problem("shortest-path-100k")
        plans = planner_agent.plan_paradigms(problem, 2)
        candidates = coder_agent.synthesize_candidates(problem, plans)
        tests = test_generator.generate_suite(problem)

        results = tester_agent.test_candidates(candidates, tests)
        self.assertGreater(len(results), 0)

        verdicts = critic_agent.critique_and_diagnose(candidates, results, tests)
        self.assertEqual(len(verdicts), len(candidates))

        # BFS should fail adversarial trap
        bfs_cand = next((c for c in candidates if "BFS" in c.name), None)
        if bfs_cand:
            bfs_verdict = next((v for v in verdicts if v.candidate_id == bfs_cand.id), None)
            self.assertIsNotNone(bfs_verdict)
            self.assertFalse(bfs_verdict.passed_all)

if __name__ == "__main__":
    unittest.main()
