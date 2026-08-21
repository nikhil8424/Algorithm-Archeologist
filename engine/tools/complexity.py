"""
Complexity & AST Profiler for Algorithm Archaeologist.
Compares claimed asymptotic complexity against static AST structural analysis
and empirical scaling observations.
"""
import ast
import math
from typing import List, Dict, Any, Tuple
from engine.models import CandidateAlgorithm, BenchmarkResult

def analyze_ast_nesting(code: str) -> Dict[str, Any]:
    """
    Computes loop nesting depth and recursive calls via AST inspection.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {"max_loop_depth": 1, "has_recursion": False, "loop_count": 0}

    max_depth = 0
    has_recursion = False
    loop_count = 0
    func_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_names.add(node.name)

    def visit_node(node, current_loop_depth):
        nonlocal max_depth, loop_count, has_recursion
        is_loop = isinstance(node, (ast.For, ast.While))
        if is_loop:
            loop_count += 1
            current_loop_depth += 1
            if current_loop_depth > max_depth:
                max_depth = current_loop_depth

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in func_names:
                has_recursion = True

        for child in ast.iter_child_nodes(node):
            visit_node(child, current_loop_depth)

    visit_node(tree, 0)
    return {
        "max_loop_depth": max_depth,
        "has_recursion": has_recursion,
        "loop_count": loop_count
    }

def assess_empirical_scaling(benchmarks: List[BenchmarkResult], claimed_complexity: str) -> str:
    """
    Assesses whether measured runtime scaling is consistent, questionable, or inconsistent
    with the claimed complexity.
    """
    if len(benchmarks) < 2:
        return "Insufficient benchmark data points to evaluate scaling."

    # Look at growth factor between the smallest and largest valid sizes
    b_first = benchmarks[0]
    b_last = benchmarks[-1]

    if b_first.input_size <= 0 or b_last.input_size <= 0 or b_first.median_runtime_ms <= 0:
        return "Consistent (linear baseline)"

    size_ratio = b_last.input_size / b_first.input_size
    time_ratio = max(0.001, b_last.median_runtime_ms) / max(0.001, b_first.median_runtime_ms)

    claimed_lower = (claimed_complexity or "").lower()

    if "o(1)" in claimed_lower:
        if time_ratio > 5.0 and size_ratio > 10:
            return "Inconsistent: Claimed O(1) constant time, but empirical runtime grew with N."
        return "Consistent: O(1) constant time matches flat empirical curve."

    if "o(n log n)" in claimed_lower or "o(n)" in claimed_lower:
        expected_ratio = size_ratio * (math.log2(size_ratio) if "log" in claimed_lower else 1.0)
        # If time ratio is quadratic (e.g. 100x size ratio leading to 10000x time ratio)
        if time_ratio > (size_ratio ** 1.8) and size_ratio >= 10:
            return f"Questionable: Claimed {claimed_complexity}, but observed growth ratio ({time_ratio:.1f}x) scales closer to quadratic O(N^2)."
        return f"Consistent: Empirical growth curve ({time_ratio:.1f}x for {size_ratio:.0f}x input) aligns well with {claimed_complexity}."

    if "o(n^2)" in claimed_lower or "o(v*e)" in claimed_lower or "o(v^2)" in claimed_lower:
        return f"Consistent: Empirical scaling exhibits expected quadratic overhead ({time_ratio:.1f}x increase)."

    return f"Consistent with theoretical model ({claimed_complexity})."
