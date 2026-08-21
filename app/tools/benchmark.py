import random
import time
from typing import List, Dict, Any
from app.models.problem import ProblemSpec
from app.models.candidate import AlgorithmCandidate
from app.models.results import BenchmarkResult
from app.tools.executor import code_executor

class BenchmarkRunner:
    """Empirical multi-scale stress benchmark executor."""

    def run_benchmarks(self, candidate: AlgorithmCandidate, problem: ProblemSpec) -> List[BenchmarkResult]:
        scales = [100, 1000, 5000, 20000]
        if problem.id == "shortest-path-100k":
            scales = [50, 250, 1000, 4000]
        elif problem.id == "convex-hull-2d":
            scales = [100, 500, 2000, 10000]

        results: List[BenchmarkResult] = []

        for size in scales:
            payload = self._generate_scale_payload(problem.id, size)
            exec_res = code_executor.execute(candidate.code, payload)
            
            runtime = exec_res.get("runtime_ms", 0.0) if exec_res.get("passed") else 9999.0
            memory = exec_res.get("memory_mb", 0.0)

            results.append(BenchmarkResult(
                candidate_id=candidate.id,
                input_size=size,
                scale_label=f"N={size:,}",
                runtime_ms=round(runtime, 3),
                memory_mb=round(memory, 2),
                iterations=1,
            ))

        return results

    def _generate_scale_payload(self, problem_id: str, size: int) -> Dict[str, Any]:
        random.seed(42 + size)
        if problem_id == "shortest-path-100k":
            edges = []
            for u in range(size):
                # Out-degree 3
                for _ in range(3):
                    v = random.randint(0, size - 1)
                    w = random.randint(1, 100)
                    edges.append((u, v, w))
            return {"n": size, "edges": edges, "source": 0, "target": size - 1}

        elif problem_id == "max-subarray-sum":
            arr = [random.randint(-1000, 1000) for _ in range(size)]
            return {"arr": arr}

        elif problem_id == "kth-largest-element":
            nums = [random.randint(-10000, 10000) for _ in range(size)]
            k = max(1, size // 10)
            return {"nums": nums, "k": k}

        elif problem_id == "longest-increasing-subsequence":
            nums = [random.randint(1, 10000) for _ in range(min(size, 2000))]
            return {"nums": nums}

        elif problem_id == "convex-hull-2d":
            pts = [(random.uniform(-1000, 1000), random.uniform(-1000, 1000)) for _ in range(size)]
            return {"points": pts}

        elif problem_id == "string-search-kmp":
            chars = "ABCD"
            txt = "".join(random.choice(chars) for _ in range(size))
            pat = "".join(random.choice(chars) for _ in range(min(20, size)))
            return {"text": txt, "pattern": pat}

        return {"input_data": list(range(size))}

benchmark_runner = BenchmarkRunner()
