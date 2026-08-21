from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from app.models.base import BaseModel

class TestCategory(str, Enum):
    NORMAL = "normal"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"
    ADVERSARIAL_TRAP = "adversarial_trap"
    RANDOMIZED_DISTRIBUTION = "randomized_distribution"
    METAMORPHIC_INVARIANT = "metamorphic_invariant"
    PROPERTY_BASED = "property_based"

@dataclass
class TestCase(BaseModel):
    id: str
    name: str
    category: TestCategory
    description: str
    input_payload: Dict[str, Any]
    expected_output: Optional[Any] = None
    input_size: int = 1

class TestStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    TLE = "TIMEOUT"
    MLE = "OUT_OF_MEMORY"
    CRASH = "CRASH"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"

@dataclass
class TestResult(BaseModel):
    test_id: str
    candidate_id: str
    status: TestStatus
    passed: bool
    runtime_ms: float = 0.0
    memory_mb: float = 0.0
    actual_output: Optional[Any] = None
    expected_output: Optional[Any] = None
    error_message: Optional[str] = None
