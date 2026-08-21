from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from app.models.base import BaseModel, Field

class ProblemFamily(str, Enum):
    GRAPH = "graph"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    ARRAY_SEARCH = "array_search"
    SORTING = "sorting"
    STRING_MATCHING = "string_matching"
    GREEDY = "greedy"
    GEOMETRY = "geometry"
    NUMBER_THEORY = "number_theory"
    TREE = "tree"

@dataclass
class ProblemSpec(BaseModel):
    id: str
    title: str
    description: str
    problem_family: ProblemFamily
    objective: str = "Find optimal solution"
    input_signature: Dict[str, str] = Field(default_factory=dict)
    output_signature: str = "Any"
    constraints: List[str] = Field(default_factory=list)
    theoretical_lower_bound_time: str = "O(N)"
    theoretical_lower_bound_space: str = "O(1)"
    tags: List[str] = Field(default_factory=list)
