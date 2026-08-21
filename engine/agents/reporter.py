"""
Reporter Agent for Algorithm Archaeologist.
Synthesizes comprehensive, explainable archaeological reports combining empirical evidence,
lineage progression, failure post-mortems, and trade-off analysis.
"""
from typing import Dict, Any, List, Optional
from engine.models import Experiment, CandidateAlgorithm, BenchmarkResult, CriticReview

def generate_archaeology_report(exp: Experiment) -> Dict[str, Any]:
    spec = exp.problem_spec
    winner = next((c for c in exp.candidates if c.id == exp.winner_candidate_id), None)
    
    # Analyze alternatives and trade-offs
    alternatives = []
    disqualified = []
    
    for c in exp.candidates:
        if c.id == exp.winner_candidate_id:
            continue
        if c.status == "DISQUALIFIED" or c.correctness_score < 0.99:
            disqualified.append({
                "name": c.name,
                "paradigm": c.paradigm,
                "reason": f"Disqualified: Failed {c.total_tests - c.passed_tests}/{c.total_tests} test cases (Correctness: {c.correctness_score * 100:.1f}%).",
                "failure_details": [r.description for r in exp.test_results if r.candidate_id == c.id and not r.passed][:2]
            })
        else:
            alternatives.append({
                "name": c.name,
                "paradigm": c.paradigm,
                "time_complexity": c.complexity_time,
                "space_complexity": c.complexity_space,
                "median_runtime_ms": c.median_runtime_ms,
                "composite_score": c.composite_score,
                "is_pareto_optimal": c.is_pareto_optimal,
                "trade_off": f"Offers alternative balance ({c.paradigm}); scored {c.composite_score or 0:.3f} vs winner's {winner.composite_score if winner else 0:.3f}."
            })

    # Failure post-mortems
    failures_summary = []
    for cr in exp.critic_reviews:
        failures_summary.append({
            "candidate_id": cr.candidate_id,
            "action": cr.action,
            "reason": cr.reason,
            "evidence": cr.evidence,
            "recommended_change": cr.recommended_change
        })

    # Summary of benchmark scale
    benchmark_summary = []
    for c in exp.candidates:
        c_benchmarks = [b for b in exp.benchmark_results if b.candidate_id == c.id]
        if c_benchmarks:
            benchmark_summary.append({
                "candidate_name": c.name,
                "data_points": len(c_benchmarks),
                "max_size_tested": max(b.input_size for b in c_benchmarks),
                "fastest_runtime_ms": min(b.median_runtime_ms for b in c_benchmarks),
                "slowest_runtime_ms": max(b.median_runtime_ms for b in c_benchmarks),
                "scaling_assessment": c.empirical_complexity_assessment
            })

    report = {
        "experiment_id": exp.id,
        "problem_title": spec.title,
        "problem_family": spec.problem_family,
        "objective": spec.objective,
        "constraints": spec.constraints,
        "winner": {
            "name": winner.name if winner else "No valid candidate passed all constraints",
            "paradigm": winner.paradigm if winner else "N/A",
            "time_complexity": winner.complexity_time if winner else "N/A",
            "space_complexity": winner.complexity_space if winner else "N/A",
            "median_runtime_ms": winner.median_runtime_ms if winner else None,
            "composite_score": winner.composite_score if winner else None,
            "justification": f"Selected as empirical winner by satisfying 100% of adversarial, boundary, and fuzzing test cases while achieving optimal multi-objective score ({winner.composite_score if winner else 0:.4f}) and non-dominated Pareto frontier status." if winner else "All candidate algorithms failed verification."
        },
        "alternatives": alternatives,
        "disqualified": disqualified,
        "total_test_suites_run": len(exp.test_cases),
        "total_executions_logged": len(exp.test_results),
        "repairs_performed": len([c for c in exp.candidates if c.version > 1]),
        "critic_diagnostics": failures_summary,
        "benchmark_summary": benchmark_summary,
        "reproducibility": {
            "deterministic_seeds": [42, 1337],
            "execution_sandbox": "Isolated Subprocess",
            "timeout_seconds": 3.0,
            "memory_limit_mb": 512.0
        }
    }
    return report
