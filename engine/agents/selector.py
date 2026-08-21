"""
Selector Agent for Algorithm Archaeologist.
Performs deterministic multi-objective candidate selection using:
1. Hard Correctness Verification Constraint (disqualifies incorrect algorithms)
2. Weighted Multi-Factor Composite Scoring
3. Non-dominated Pareto Frontier Computation across (Runtime, Memory, Simplicity)
"""
from typing import List, Dict, Any, Tuple, Optional
from engine.models import CandidateAlgorithm, BenchmarkResult

def compute_pareto_frontier(candidates: List[CandidateAlgorithm]) -> List[str]:
    """
    Computes Pareto optimal candidate IDs (non-dominated in: min runtime, min memory, max simplicity).
    Only considers candidates with 100% correctness.
    """
    valid = [c for c in candidates if c.correctness_score >= 1.0 and c.median_runtime_ms is not None]
    if not valid:
        return []

    pareto_ids = []
    for c1 in valid:
        c1_time = c1.median_runtime_ms or float("inf")
        c1_mem = c1.peak_memory_mb or float("inf")
        c1_simp = c1.simplicity_score

        dominated = False
        for c2 in valid:
            if c1.id == c2.id:
                continue
            c2_time = c2.median_runtime_ms or float("inf")
            c2_mem = c2.peak_memory_mb or float("inf")
            c2_simp = c2.simplicity_score

            # c2 dominates c1 if c2 is <= in time, <= in mem, >= in simp, and strictly better in at least one
            better_or_equal = (c2_time <= c1_time) and (c2_mem <= c1_mem) and (c2_simp >= c1_simp)
            strictly_better = (c2_time < c1_time) or (c2_mem < c1_mem) or (c2_simp > c1_simp)

            if better_or_equal and strictly_better:
                dominated = True
                break

        if not dominated:
            pareto_ids.append(c1.id)

    return pareto_ids

def evaluate_and_rank_candidates(
    candidates: List[CandidateAlgorithm],
    benchmarks: List[BenchmarkResult]
) -> Tuple[List[CandidateAlgorithm], Optional[CandidateAlgorithm]]:
    """
    Computes composite scores, tags Pareto optimality, and selects the empirical winner.
    """
    # 1. Update candidate median times and peak memories from benchmark data
    for cand in candidates:
        cand_bs = [b for b in benchmarks if b.candidate_id == cand.id]
        if cand_bs:
            # Pick largest input size benchmark
            largest_b = max(cand_bs, key=lambda b: b.input_size)
            cand.median_runtime_ms = largest_b.median_runtime_ms
            cand.peak_memory_mb = largest_b.memory_mb or 0.1

    # 2. Normalize and compute composite score for correct candidates
    correct_candidates = [c for c in candidates if c.correctness_score >= 0.99 and c.median_runtime_ms is not None]

    if correct_candidates:
        min_time = min(c.median_runtime_ms for c in correct_candidates if c.median_runtime_ms > 0) or 0.001
        min_mem = min(c.peak_memory_mb for c in correct_candidates if (c.peak_memory_mb or 0) > 0) or 0.01

        pareto_ids = set(compute_pareto_frontier(candidates))

        for c in candidates:
            if c.correctness_score < 0.99 or c.median_runtime_ms is None:
                c.composite_score = round(c.correctness_score * 0.2, 4)
                c.is_pareto_optimal = False
                c.status = "DISQUALIFIED" if c.correctness_score < 0.99 else "EVALUATED"
                continue

            # Higher is better for all score components (0.0 to 1.0)
            perf_score = min(1.0, min_time / max(0.0001, c.median_runtime_ms))
            mem_score = min(1.0, min_mem / max(0.001, c.peak_memory_mb or 0.1))
            robust_score = c.correctness_score
            simp_score = c.simplicity_score

            score = (
                0.50 * perf_score +
                0.20 * mem_score +
                0.15 * robust_score +
                0.15 * simp_score
            )
            c.composite_score = round(score, 4)
            c.is_pareto_optimal = c.id in pareto_ids
            c.status = "PASSED"

        # Sort correct candidates by composite score descending
        ranked_correct = sorted(correct_candidates, key=lambda c: c.composite_score or 0.0, reverse=True)
        winner = ranked_correct[0] if ranked_correct else None
    else:
        # Fallback if no candidate passed 100%
        for c in candidates:
            c.composite_score = round(c.correctness_score * 0.5, 4)
            c.is_pareto_optimal = False
            c.status = "FAILED"
        winner = None

    return candidates, winner
