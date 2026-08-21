from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Type, TypeVar
import json

T = TypeVar("T", bound="BaseModel")

@dataclass
class BaseModel:
    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def model_dump_json(self, indent: int = None) -> str:
        return json.dumps(self.model_dump(), indent=indent)

    @classmethod
    def model_validate(cls: Type[T], data: Dict[str, Any]) -> T:
        if isinstance(data, cls):
            return data
        # Filter fields matching dataclass
        field_names = getattr(cls, "__dataclass_fields__", {}).keys()
        kwargs = {}
        for k, v in data.items():
            if k in field_names:
                kwargs[k] = v
        return cls(**kwargs)

def Field(default_factory=None, default=None, **kwargs):
    if default_factory is not None:
        return field(default_factory=default_factory)
    return field(default=default)
