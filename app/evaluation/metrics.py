import math
from typing import List, Dict
from app.models.candidate import AlgorithmCandidate

def calculate_speedup(baseline_ms: float, target_ms: float) -> float:
    if target_ms <= 0.0001:
        return 1.0
    return round(baseline_ms / target_ms, 2)

def calculate_pareto_composite_score(
    accuracy: float,
    runtime_ms: float,
    memory_mb: float,
    ast_nodes: int,
    w_acc: float = 0.50,
    w_speed: float = 0.30,
    w_mem: float = 0.10,
    w_simplicity: float = 0.10,
) -> float:
    """Compute weighted composite fitness score [0, 100]."""
    # Normalized speed score (log-scale normalized to 0-100)
    speed_score = max(0.0, min(100.0, 100.0 - (math.log10(max(runtime_ms, 0.01) + 1) * 20.0)))
    
    # Normalized memory score
    mem_score = max(0.0, min(100.0, 100.0 - (memory_mb * 5.0)))
    
    # Normalized simplicity score (fewer AST nodes = higher simplicity)
    simplicity_score = max(0.0, min(100.0, 100.0 - (ast_nodes * 0.5)))

    total = (
        (accuracy * w_acc) +
        (speed_score * w_speed) +
        (mem_score * w_mem) +
        (simplicity_score * w_simplicity)
    )
    return round(total, 2)
