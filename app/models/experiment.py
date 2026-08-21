from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
import time

from app.models.base import BaseModel, Field
from app.models.problem import ProblemSpec
from app.models.candidate import AlgorithmCandidate
from app.models.testcase import TestCase, TestResult
from app.models.results import BenchmarkResult, CriticVerdict

class PipelineStage(str, Enum):
    IDLE = "idle"
    ANALYZE = "analyze"
    PLAN = "plan"
    GENERATE = "generate"
    VALIDATE = "validate"
    TEST = "test"
    BENCHMARK = "benchmark"
    CRITIQUE = "critique"
    REPAIR = "repair"
    EVOLVE = "evolve"
    SELECT = "select"
    REPORT = "report"
    DONE = "done"

@dataclass
class TimelineEvent(BaseModel):
    id: str
    stage: PipelineStage
    agent_name: str
    action: str
    details: str
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

@dataclass
class FinalReport(BaseModel):
    executive_summary: str
    theoretical_vs_empirical_synthesis: str
    winning_candidate_id: str
    winning_candidate_name: str
    pareto_tradeoff_analysis: str
    production_recommendations: str
    markdown_content: str
    pathological_cases_identified: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

@dataclass
class EvolutionStep(BaseModel):
    generation: int
    parent_id: str
    child_id: str
    mutation_type: str
    description: str
    fitness_delta_pct: float

@dataclass
class Experiment(BaseModel):
    id: str
    problem_spec: ProblemSpec
    current_state: PipelineStage = PipelineStage.IDLE
    candidates: List[AlgorithmCandidate] = Field(default_factory=list)
    test_cases: List[TestCase] = Field(default_factory=list)
    test_results: List[TestResult] = Field(default_factory=list)
    benchmark_results: List[BenchmarkResult] = Field(default_factory=list)
    critic_verdicts: List[CriticVerdict] = Field(default_factory=list)
    evolution_history: List[EvolutionStep] = Field(default_factory=list)
    winner_candidate_id: Optional[str] = None
    final_report: Optional[FinalReport] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
