from typing import List
from app.models.candidate import AlgorithmCandidate

class ParetoRanker:
    """Computes the true non-dominated Pareto Frontier across multiple objectives."""

    def compute_frontier(self, candidates: List[AlgorithmCandidate]) -> List[AlgorithmCandidate]:
        if not candidates:
            return []

        # Objectives to minimize: runtime_ms, peak_memory_mb, ast_node_count
        # Objective to maximize: accuracy_percentage
        
        n = len(candidates)
        domination_counts = [0] * n
        dominated_sets = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                c1 = candidates[i]
                c2 = candidates[j]
                
                # Check if c1 dominates c2
                c1_better_or_equal = (
                    c1.accuracy_percentage >= c2.accuracy_percentage and
                    c1.avg_runtime_ms <= c2.avg_runtime_ms and
                    c1.peak_memory_mb <= c2.peak_memory_mb and
                    c1.ast_node_count <= c2.ast_node_count
                )
                c1_strictly_better = (
                    c1.accuracy_percentage > c2.accuracy_percentage or
                    c1.avg_runtime_ms < c2.avg_runtime_ms or
                    c1.peak_memory_mb < c2.peak_memory_mb or
                    c1.ast_node_count < c2.ast_node_count
                )
                
                if c1_better_or_equal and c1_strictly_better:
                    dominated_sets[i].append(j)
                elif (
                    c2.accuracy_percentage >= c1.accuracy_percentage and
                    c2.avg_runtime_ms <= c1.avg_runtime_ms and
                    c2.peak_memory_mb <= c1.peak_memory_mb and
                    c2.ast_node_count <= c1.ast_node_count and
                    (
                        c2.accuracy_percentage > c1.accuracy_percentage or
                        c2.avg_runtime_ms < c1.avg_runtime_ms or
                        c2.peak_memory_mb < c1.peak_memory_mb or
                        c2.ast_node_count < c1.ast_node_count
                    )
                ):
                    domination_counts[i] += 1

        for i, count in enumerate(domination_counts):
            candidates[i].pareto_rank = count + 1
            candidates[i].is_pareto_optimal = (count == 0)

        # Sort candidates by Pareto rank ascending, then score descending
        candidates.sort(key=lambda c: (c.pareto_rank, -c.pareto_composite_score))
        return candidates

pareto_ranker = ParetoRanker()
