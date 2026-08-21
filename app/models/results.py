from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from app.models.base import BaseModel

@dataclass
class BenchmarkResult(BaseModel):
    candidate_id: str
    input_size: int
    scale_label: str
    runtime_ms: float
    memory_mb: float
    iterations: int = 1
    std_dev_ms: float = 0.0

@dataclass
class ParetoPoint(BaseModel):
    candidate_id: str
    candidate_name: str
    runtime_ms: float
    memory_mb: float
    accuracy: float
    code_simplicity: float
    pareto_rank: int
    is_non_dominated: bool

class DiagnosisAction(str, Enum):
    REPAIR_CORRECTNESS = "REPAIR_CORRECTNESS"
    OPTIMIZE_PERFORMANCE = "OPTIMIZE_PERFORMANCE"
    MUTATE_AST = "MUTATE_AST"
    DISCARD = "DISCARD"
    ACCEPT = "ACCEPT"

@dataclass
class CriticVerdict(BaseModel):
    candidate_id: str
    passed_all: bool
    failure_category: Optional[str] = None
    root_cause_explanation: str = ""
    recommended_action: DiagnosisAction = DiagnosisAction.ACCEPT
    patch_instructions: Optional[str] = None
    suggested_code: Optional[str] = None
