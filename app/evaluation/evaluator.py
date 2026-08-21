from typing import List, Dict, Tuple
from app.models.candidate import AlgorithmCandidate
from app.models.testcase import TestCase, TestResult, TestStatus
from app.models.results import BenchmarkResult
from app.evaluation.metrics import calculate_pareto_composite_score
from app.evaluation.ranking import pareto_ranker
from app.tools.complexity import complexity_estimator

class CandidateEvaluator:
    """Evaluates candidate correctness, performance metrics, and empirical curves."""

    def evaluate_candidates(
        self,
        candidates: List[AlgorithmCandidate],
        test_results: List[TestResult],
        benchmark_results: List[BenchmarkResult],
    ) -> List[AlgorithmCandidate]:
        results_by_cand: Dict[str, List[TestResult]] = {}
        for r in test_results:
            results_by_cand.setdefault(r.candidate_id, []).append(r)

        bench_by_cand: Dict[str, List[BenchmarkResult]] = {}
        for b in benchmark_results:
            bench_by_cand.setdefault(b.candidate_id, []).append(b)

        for c in candidates:
            c_tests = results_by_cand.get(c.id, [])
            total_tests = len(c_tests)
            passed_tests = sum(1 for t in c_tests if t.passed)

            c.accuracy_percentage = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0
            c.passed_correctness = (passed_tests == total_tests and total_tests > 0)

            c_bench = bench_by_cand.get(c.id, [])
            if c_bench:
                valid_runtimes = [b.runtime_ms for b in c_bench if b.runtime_ms < 9000]
                c.avg_runtime_ms = (sum(valid_runtimes) / len(valid_runtimes)) if valid_runtimes else 9999.0
                c.peak_memory_mb = max((b.memory_mb for b in c_bench), default=0.1)

                # Fit empirical complexity curve
                points = [(b.input_size, b.runtime_ms) for b in c_bench]
                c.complexity.time_empirical_fitted = complexity_estimator.fit_curve(points)
            else:
                c.avg_runtime_ms = 0.0
                c.peak_memory_mb = 0.0

            # Calculate composite fitness
            c.pareto_composite_score = calculate_pareto_composite_score(
                accuracy=c.accuracy_percentage,
                runtime_ms=c.avg_runtime_ms,
                memory_mb=c.peak_memory_mb,
                ast_nodes=c.ast_node_count,
            )

        # Compute Pareto non-dominated frontier and rank
        pareto_ranker.compute_frontier(candidates)
        return candidates

candidate_evaluator = CandidateEvaluator()
