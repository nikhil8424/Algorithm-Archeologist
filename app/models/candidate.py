from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from app.models.base import BaseModel, Field

class CandidateOrigin(str, Enum):
    INITIAL_PLAN = "initial_plan"
    CRITIC_REPAIR = "critic_repair"
    GENETIC_MUTATION = "genetic_mutation"
    HEURISTIC_SYNTHESIS = "heuristic_synthesis"

@dataclass
class Complexity(BaseModel):
    time_theoretical: str = "O(N)"
    space_theoretical: str = "O(1)"
    time_empirical_fitted: Optional[str] = None
    space_empirical_fitted: Optional[str] = None
    asymptotic_constant_factor: str = "medium"

@dataclass
class AlgorithmCandidate(BaseModel):
    id: str
    name: str
    paradigm: str
    strategy_description: str
    code: str
    origin: CandidateOrigin = CandidateOrigin.INITIAL_PLAN
    generation: int = 0
    parent_id: Optional[str] = None
    mutation_description: Optional[str] = None
    complexity: Complexity = Field(default_factory=Complexity)
    ast_node_count: int = 0
    cyclomatic_complexity: int = 1
    passed_correctness: bool = False
    accuracy_percentage: float = 0.0
    avg_runtime_ms: float = 0.0
    peak_memory_mb: float = 0.0
    pareto_rank: int = 999
    pareto_composite_score: float = 0.0
    is_pareto_optimal: bool = False
    is_winner: bool = False
