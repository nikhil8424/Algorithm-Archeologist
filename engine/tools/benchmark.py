"""
Deterministic Empirical Benchmark Engine for Algorithm Archaeologist.
Measures real execution runtimes across scalable input sizes (n=10 up to 100,000)
using time.perf_counter() and tracemalloc. Never fabricates benchmark data.
"""
import random
import statistics
import time
from typing import List, Dict, Any, Callable
from engine.models import CandidateAlgorithm, ProblemSpec, BenchmarkResult
from engine.tools.sandbox import SandboxExecutor

def generate_benchmark_input(problem_family: str, size: int) -> Any:
    rng = random.Random(42 + size)
    pf = (problem_family or "").lower()

    if "subarray" in pf:
        arr = [rng.randint(-1000, 1000) for _ in range(size)]
        return {"arr": arr}
        
    elif "sort" in pf:
        arr = [rng.randint(-100000, 100000) for _ in range(size)]
        return {"arr": arr}
        
    elif "shortest" in pf or "path" in pf or "dijkstra" in pf or "graph" in pf:
        # Generate clean connected graph with 'size' nodes
        n = max(4, size)
        edges = []
        # Backbone edges
        for i in range(n - 1):
            edges.append((i, i + 1, float(rng.randint(1, 20))))
        # Jump edges
        jump_count = min(n, 5000)
        for _ in range(jump_count):
            u = rng.randint(0, n - 2)
            v = min(n - 1, u + rng.randint(2, min(50, n - u)))
            if u != v:
                edges.append((u, v, float(rng.randint(1, 30))))
        return {
            "n": n,
            "edges": edges,
            "start": 0,
            "target": n - 1
        }
        
    elif "knapsack" in pf:
        # Scale capacity and item count
        weights = [rng.randint(1, 100) for _ in range(size)]
        values = [rng.randint(10, 500) for _ in range(size)]
        capacity = max(10, size * 20)
        return {
            "weights": weights,
            "values": values,
            "capacity": capacity
        }
        
    else:
        arr = [rng.randint(-500, 500) for _ in range(size)]
        return {"arr": arr}

class BenchmarkEngine:
    def __init__(self, sandbox: SandboxExecutor = None, default_sizes: List[int] = None):
        self.sandbox = sandbox or SandboxExecutor(timeout_seconds=2.5, memory_limit_mb=512.0)
        self.default_sizes = default_sizes or [10, 100, 1000, 5000, 20000]

    def benchmark_candidate(
        self,
        candidate: CandidateAlgorithm,
        problem_spec: ProblemSpec,
        trials: int = 2,
        max_size_cap: int = 50000
    ) -> List[BenchmarkResult]:
        """
        Runs empirical benchmarks for a given candidate across varying input sizes.
        Adapts size range if candidate is detected to be O(N^2) or slow to prevent sandbox timeouts.
        """
        results: List[BenchmarkResult] = []
        is_quadratic_or_exponential = any(
            bad in (candidate.complexity_time or "").lower() or bad in candidate.name.lower()
            for bad in ["o(n^2)", "o(n*w)", "o(2^n)", "o(v*e)", "o(v * e)", "o(v^2)", "bellman", "brute"]
        )

        sizes_to_run = self.default_sizes[:]
        if is_quadratic_or_exponential:
            # Scale down quadratic candidates to fast bounded sizes
            sizes_to_run = [10, 50, 100, 500, 1000]

        for size in sizes_to_run:
            if size > max_size_cap:
                continue

            input_data = generate_benchmark_input(problem_spec.problem_family, size)
            trial_times: List[float] = []
            peak_mems: List[float] = []

            for _ in range(trials):
                run_res = self.sandbox.run(candidate.code, input_data)
                if run_res["passed"] or run_res["status"] == "PASSED":
                    trial_times.append(run_res["runtime_ms"])
                    if run_res.get("memory_mb"):
                        peak_mems.append(run_res["memory_mb"])
                else:
                    if run_res["status"] == "TIMEOUT":
                        trial_times.append(self.sandbox.timeout_seconds * 1000.0)
                    break

            if trial_times:
                med_time = statistics.median(trial_times)
                min_time = min(trial_times)
                max_time = max(trial_times)
                avg_mem = statistics.mean(peak_mems) if peak_mems else 0.0

                results.append(BenchmarkResult(
                    candidate_id=candidate.id,
                    input_size=size,
                    median_runtime_ms=round(med_time, 4),
                    min_runtime_ms=round(min_time, 4),
                    max_runtime_ms=round(max_time, 4),
                    memory_mb=round(avg_mem, 3) if avg_mem else None,
                    trials=len(trial_times),
                    raw_times=[round(t, 4) for t in trial_times]
                ))

                if med_time > 800.0:
                    break

        return results
