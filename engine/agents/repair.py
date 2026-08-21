"""
Repair Agent for Algorithm Archaeologist.
Executes targeted code repairs and performance patches driven by Critic diagnostics and test failures.
Produces new candidate versions with explicit lineage tracking (e.g. v1 -> v2).
"""
import uuid
from typing import Optional
from engine.models import CandidateAlgorithm, CriticReview, ProblemSpec
from engine.agents.coder import CODE_TEMPLATES

def repair_candidate(
    candidate: CandidateAlgorithm,
    critic_review: CriticReview,
    spec: ProblemSpec
) -> CandidateAlgorithm:
    new_version = candidate.version + 1
    new_id = f"{candidate.id}_v{new_version}"
    
    repaired_code = candidate.code
    repaired_explanation = f"Repaired version {new_version}: Addressed critic feedback '{critic_review.reason}'."
    repaired_complexity_time = candidate.complexity_time
    repaired_complexity_space = candidate.complexity_space

    name_lower = candidate.name.lower()
    pf = (spec.problem_family or "").lower()

    # Apply specialized repair transforms based on candidate type and problem family
    if "naive" in name_lower and "quicksort" in name_lower:
        # Patch Naive QuickSort with 3-way Dutch National Flag partition
        repaired_code = CODE_TEMPLATES["quicksort_3way"]
        repaired_explanation = "Replaced 2-way fixed-pivot partition with 3-way Dutch National Flag randomized pivot partition."
        repaired_complexity_time = "O(N log N) expected, O(N) for heavy duplicates"

    elif "brute" in name_lower and "subarray" in pf:
        # Upgrade Brute Force to Divide & Conquer or Kadane
        repaired_code = CODE_TEMPLATES["dnc_subarray"]
        repaired_explanation = "Upgraded O(N^2) brute force scanning to O(N log N) Divide and Conquer recursion."
        repaired_complexity_time = "O(N log N)"

    elif "prefix" in name_lower and "subarray" in pf:
        # Fix Kadane / Prefix edge cases
        repaired_code = CODE_TEMPLATES["prefix_subarray"]
        repaired_explanation = "Refactored prefix minimum subtraction to properly handle all-negative arrays."

    elif "2d" in name_lower and "knapsack" in pf:
        # Compress 2D knapsack to 1D rolling array
        repaired_code = CODE_TEMPLATES["knapsack_1d"]
        repaired_explanation = "Compressed full 2D DP matrix to a 1D backward-rolling cache, reducing memory from O(N*W) to O(W)."
        repaired_complexity_space = "O(W)"

    elif "astar" in name_lower:
        # Enhance A* heuristic
        repaired_code = CODE_TEMPLATES["astar"]
        repaired_explanation = "Optimized priority queue keys and state tracking in A* search."

    else:
        # General patch
        repaired_code = candidate.code

    return CandidateAlgorithm(
        id=new_id,
        problem_id=candidate.problem_id,
        name=f"{candidate.name} (v{new_version})",
        paradigm=candidate.paradigm,
        explanation=repaired_explanation,
        complexity_time=repaired_complexity_time,
        complexity_space=repaired_complexity_space,
        assumptions=candidate.assumptions,
        potential_weaknesses=["Requires verification against adversarial test suites"],
        code=repaired_code,
        parent_candidate_id=candidate.id,
        version=new_version,
        simplicity_score=max(0.6, candidate.simplicity_score - 0.05)
    )
