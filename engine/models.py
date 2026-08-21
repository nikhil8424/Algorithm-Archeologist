"""
Data models for Algorithm Archaeologist.
Provides strict typed representations of problems, candidates, tests, benchmarks,
evaluations, experiments, and agent states.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import json
import time
import uuid

class AgentState(str, Enum):
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
    FAILED = "failed"
    STOPPED = "stopped"

class TestCategory(str, Enum):
    NORMAL = "normal"
    BOUNDARY = "boundary"
    EDGE = "edge"
    RANDOM = "random"
    ADVERSARIAL = "adversarial"
    METAMORPHIC = "metamorphic"
    PROPERTY = "property"
    HIDDEN = "hidden"

class ExecutionStatus(str, Enum):
    PASSED = "PASSED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT = "MEMORY_LIMIT"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"

class CriticAction(str, Enum):
    ACCEPT = "ACCEPT"
    REPAIR_CORRECTNESS = "REPAIR_CORRECTNESS"
    OPTIMIZE_PERFORMANCE = "OPTIMIZE_PERFORMANCE"
    ADD_TESTS = "ADD_TESTS"
    DISCARD = "DISCARD"
    STOP_SEARCH = "STOP_SEARCH"

@dataclass
class ProblemSpec:
    id: str
    title: str
    description: str
    input_format: str
    output_format: str
    constraints: List[str]
    objective: str
    problem_family: str
    language: str = "python"
    sample_inputs: List[Dict[str, Any]] = field(default_factory=list)
    candidate_paradigms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSpec":
        return cls(**data)

@dataclass
class CandidateAlgorithm:
    id: str
    problem_id: str
    name: str
    paradigm: str
    explanation: str
    complexity_time: str
    complexity_space: str
    assumptions: List[str]
    code: str
    parent_candidate_id: Optional[str] = None
    version: int = 1
    mutation_type: Optional[str] = None
    potential_weaknesses: List[str] = field(default_factory=list)
    status: str = "PENDING"
    correctness_score: float = 0.0
    passed_tests: int = 0
    total_tests: int = 0
    median_runtime_ms: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    simplicity_score: float = 0.8
    composite_score: Optional[float] = None
    is_pareto_optimal: bool = False
    empirical_complexity_assessment: str = "Unassessed"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateAlgorithm":
        return cls(**data)

@dataclass
class TestCase:
    id: str
    input_data: Any
    expected_output: Any
    category: TestCategory
    description: str
    is_adversarial: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value if isinstance(self.category, TestCategory) else self.category
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        data = data.copy()
        if isinstance(data.get("category"), str):
            data["category"] = TestCategory(data["category"])
        return cls(**data)

@dataclass
class TestResult:
    candidate_id: str
    test_id: str
    passed: bool
    status: ExecutionStatus
    runtime_ms: float
    memory_mb: Optional[float]
    stdout: str
    stderr: str
    actual_output: Any = None
    expected_output: Any = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    category: str = "normal"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, ExecutionStatus) else self.status
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        data = data.copy()
        if isinstance(data.get("status"), str):
            data["status"] = ExecutionStatus(data["status"])
        return cls(**data)

@dataclass
class BenchmarkResult:
    candidate_id: str
    input_size: int
    median_runtime_ms: float
    min_runtime_ms: float
    max_runtime_ms: float
    memory_mb: Optional[float]
    trials: int
    raw_times: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CriticReview:
    candidate_id: str
    iteration: int
    action: CriticAction
    reason: str
    evidence: List[str]
    recommended_change: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["action"] = self.action.value if isinstance(self.action, CriticAction) else self.action
        return d

@dataclass
class TimelineEvent:
    id: str
    timestamp: float
    state: AgentState
    title: str
    detail: str
    level: str = "info" # info, success, warning, error
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value if isinstance(self.state, AgentState) else self.state
        return d

@dataclass
class Experiment:
    id: str
    problem_spec: ProblemSpec
    current_state: AgentState
    max_candidates: int = 4
    max_iterations: int = 3
    benchmark_budget_seconds: float = 15.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    candidates: List[CandidateAlgorithm] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)
    test_results: List[TestResult] = field(default_factory=list)
    benchmark_results: List[BenchmarkResult] = field(default_factory=list)
    critic_reviews: List[CriticReview] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    winner_candidate_id: Optional[str] = None
    final_report: Optional[Dict[str, Any]] = None
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "problem_spec": self.problem_spec.to_dict(),
            "current_state": self.current_state.value if isinstance(self.current_state, AgentState) else self.current_state,
            "max_candidates": self.max_candidates,
            "max_iterations": self.max_iterations,
            "benchmark_budget_seconds": self.benchmark_budget_seconds,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "candidates": [c.to_dict() for c in self.candidates],
            "test_cases": [t.to_dict() for t in self.test_cases],
            "test_results": [r.to_dict() for r in self.test_results],
            "benchmark_results": [b.to_dict() for b in self.benchmark_results],
            "critic_reviews": [cr.to_dict() for cr in self.critic_reviews],
            "timeline": [t.to_dict() for t in self.timeline],
            "winner_candidate_id": self.winner_candidate_id,
            "final_report": self.final_report,
            "evolution_history": self.evolution_history,
        }
