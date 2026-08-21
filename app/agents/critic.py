from typing import List, Dict
from app.models.candidate import AlgorithmCandidate, CandidateOrigin
from app.models.testcase import TestResult, TestCase, TestCategory, TestStatus
from app.models.results import CriticVerdict, DiagnosisAction
from app.models.experiment import EvolutionStep
from app.tools.profiler import profiler

class CriticAgent:
    """Archaeological Critic & Repair Agent: Diagnoses failures and synthesizes mutations."""

    def critique_and_diagnose(
        self,
        candidates: List[AlgorithmCandidate],
        test_results: List[TestResult],
        test_cases: List[TestCase],
    ) -> List[CriticVerdict]:
        verdicts: List[CriticVerdict] = []
        tests_by_id = {t.id: t for t in test_cases}
        results_by_cand: Dict[str, List[TestResult]] = {}

        for r in test_results:
            results_by_cand.setdefault(r.candidate_id, []).append(r)

        for c in candidates:
            c_results = results_by_cand.get(c.id, [])
            failed_tests = [r for r in c_results if not r.passed]

            if not failed_tests:
                verdicts.append(CriticVerdict(
                    candidate_id=c.id,
                    passed_all=True,
                    failure_category=None,
                    root_cause_explanation="Candidate satisfies all functional, edge-case, and adversarial fuzzer invariants.",
                    recommended_action=DiagnosisAction.ACCEPT,
                ))
                continue

            # Classify primary failure mode
            first_fail = failed_tests[0]
            fail_test_case = tests_by_id.get(first_fail.test_id)

            if fail_test_case and fail_test_case.category == TestCategory.ADVERSARIAL_TRAP:
                explanation = (
                    f"Fails adversarial trap '{fail_test_case.name}'. "
                    f"Candidate uses an unweighted assumption (BFS) which collapses when fewer hops carry heavier weights."
                )
                action = DiagnosisAction.MUTATE_AST
                patch = "Replace unweighted FIFO queue with priority min-heap to handle non-uniform edge weights."
                fixed_code = """import heapq

def solve(n, edges, source, target):
    # Repaired via Critic: Replaced BFS with Min-Heap Dijkstra
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
"""
            elif first_fail.status == TestStatus.TLE:
                explanation = f"Exceeded execution time limit on '{fail_test_case.name if fail_test_case else first_fail.test_id}'."
                action = DiagnosisAction.OPTIMIZE_PERFORMANCE
                patch = "Eliminate nested iteration loops; replace with single-pass DP or bisect search."
                fixed_code = None
            else:
                explanation = f"Incorrect output on '{fail_test_case.name if fail_test_case else first_fail.test_id}': Expected {first_fail.expected_output}, got {first_fail.actual_output}."
                action = DiagnosisAction.REPAIR_CORRECTNESS
                patch = "Fix off-by-one boundary conditions and empty base-case return values."
                fixed_code = None

            verdicts.append(CriticVerdict(
                candidate_id=c.id,
                passed_all=False,
                failure_category=first_fail.status.value,
                root_cause_explanation=explanation,
                recommended_action=action,
                patch_instructions=patch,
                suggested_code=fixed_code,
            ))

        return verdicts

    def evolve_candidate(self, parent: AlgorithmCandidate, verdict: CriticVerdict) -> AlgorithmCandidate:
        """Synthesize genetic mutated offspring candidate from critic verdict."""
        repaired_code = verdict.suggested_code or parent.code
        ast_stats = profiler.analyze_ast(repaired_code)

        child = AlgorithmCandidate(
            id=f"cand-evolved-{parent.id[-4:]}",
            name=f"{parent.name} (Evolved v2)",
            paradigm="Genetic AST Repair",
            strategy_description=f"Evolved from {parent.name} to address: {verdict.patch_instructions}",
            code=repaired_code,
            origin=CandidateOrigin.GENETIC_MUTATION,
            generation=parent.generation + 1,
            parent_id=parent.id,
            mutation_description=verdict.patch_instructions,
            complexity=parent.complexity,
            ast_node_count=ast_stats["ast_node_count"],
            cyclomatic_complexity=ast_stats["cyclomatic_complexity"],
        )
        return child

critic_agent = CriticAgent()
