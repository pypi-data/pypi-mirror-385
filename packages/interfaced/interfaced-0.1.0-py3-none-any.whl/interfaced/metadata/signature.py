from dataclasses import dataclass, replace
from typing import Any, Optional

@dataclass(frozen=True)
class MethodSignature:
    parameters: tuple[str, ...]
    param_types: dict[str, Any]
    defaults: tuple[Any, ...]
    return_type: Any
    is_async: bool
    is_static: bool = False
    is_class: bool = False
    property_role: Optional[str] = None  # 'get', 'set', 'del' or None
    is_abstract: bool = False
    is_descriptor: bool = False
    is_context_manager: bool = False
    is_async_context_manager: bool = False

    def __post_init__(self) -> None:
        self._validate_parameters()
        if self.property_role not in (None, 'get', 'set', 'del'):
            raise ValueError("Invalid property_role")

    def _validate_parameters(self) -> None:
        if not isinstance(self.parameters, tuple):
            raise ValueError("Parameters must be a tuple")
        if not all(isinstance(p, str) for p in self.parameters):
            raise ValueError("All parameter names must be strings")
        if not isinstance(self.param_types, dict):
            raise ValueError("Param types must be a dictionary")
        if not isinstance(self.defaults, tuple):
            raise ValueError("Defaults must be a tuple")
