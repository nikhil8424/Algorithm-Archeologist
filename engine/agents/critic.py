"""
Critic Agent for Algorithm Archaeologist.
Inspects candidate test results, execution bottlenecks, edge-case failures,
and empirical scaling to produce structured actionable decisions.
"""
from typing import List, Dict, Any, Optional
from engine.models import (
    CandidateAlgorithm, TestResult, BenchmarkResult, CriticReview,
    CriticAction, ExecutionStatus, ProblemSpec
)

class CriticAgent:
    def critique(
        self,
        candidate: CandidateAlgorithm,
        test_results: List[TestResult],
        benchmarks: List[BenchmarkResult],
        problem_spec: ProblemSpec,
        iteration: int = 1
    ) -> CriticReview:
        cand_results = [r for r in test_results if r.candidate_id == candidate.id]
        failures = [r for r in cand_results if not r.passed]
        
        # 1. Check for hard correctness failures
        if failures:
            fail_descs = [f"{r.category.upper()}: {r.description or r.test_id} (Status: {r.status}, Error: {r.error_message or 'Wrong Output'})" for r in failures[:3]]
            
            # Check if failure is fundamentally unsuited to paradigm (e.g. BFS on weighted graph)
            if "bfs" in candidate.name.lower() and "shortest" in (problem_spec.problem_family or "").lower():
                return CriticReview(
                    candidate_id=candidate.id,
                    iteration=iteration,
                    action=CriticAction.DISCARD,
                    reason="Unweighted BFS fundamentally violates correctness on graphs with non-uniform edge weights.",
                    evidence=fail_descs,
                    recommended_change="Discard candidate. BFS cannot find shortest paths when edge weights > 1."
                )

            if "greedy" in candidate.name.lower() and "knapsack" in (problem_spec.problem_family or "").lower():
                return CriticReview(
                    candidate_id=candidate.id,
                    iteration=iteration,
                    action=CriticAction.DISCARD,
                    reason="Greedy value-density heuristic is sub-optimal for 0/1 integer knapsack.",
                    evidence=fail_descs,
                    recommended_change="Discard or switch to Dynamic Programming or Branch & Bound."
                )

            # If it's a repairable correctness defect (e.g. pivot strategy, negative number handling, all-zero edge cases)
            if iteration < 3:
                return CriticReview(
                    candidate_id=candidate.id,
                    iteration=iteration,
                    action=CriticAction.REPAIR_CORRECTNESS,
                    reason=f"Candidate failed {len(failures)}/{len(cand_results)} verification tests.",
                    evidence=fail_descs,
                    recommended_change="Repair state transitions, edge case handling, or partition mechanics to satisfy failing test cases."
                )
            else:
                return CriticReview(
                    candidate_id=candidate.id,
                    iteration=iteration,
                    action=CriticAction.DISCARD,
                    reason=f"Exceeded maximum repair iterations ({iteration}). Candidate remains incorrect.",
                    evidence=fail_descs,
                    recommended_change="Disqualify candidate from final selection due to unrecovered correctness failures."
                )

        # 2. Correctness passed: evaluate performance & scalability
        cand_benchmarks = [b for b in benchmarks if b.candidate_id == candidate.id]
        if cand_benchmarks:
            max_b = max(cand_benchmarks, key=lambda b: b.input_size)
            # Quadratic or slow candidate
            if max_b.median_runtime_ms > 1000.0 or "o(n^2)" in (candidate.complexity_time or "").lower():
                if iteration < 2 and "naive" in candidate.name.lower():
                    return CriticReview(
                        candidate_id=candidate.id,
                        iteration=iteration,
                        action=CriticAction.OPTIMIZE_PERFORMANCE,
                        reason="Candidate passed all correctness tests but exhibits unscalable O(N^2) runtime growth on large inputs.",
                        evidence=[f"Input size N={max_b.input_size} took {max_b.median_runtime_ms:.2f}ms."],
                        recommended_change="Apply algorithmic optimization (e.g. 3-way Dutch partitioning, heap-based acceleration, or memory rolling)."
                    )

        # 3. Passed all tests with acceptable performance
        return CriticReview(
            candidate_id=candidate.id,
            iteration=iteration,
            action=CriticAction.ACCEPT,
            reason="Candidate successfully passed 100% of functional, edge, and adversarial test cases with valid empirical scaling.",
            evidence=[f"Passed all {len(cand_results)} test suites."],
            recommended_change="Retain candidate for final Pareto frontier comparison and selection."
        )
