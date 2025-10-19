import threading
from typing import Any, Tuple, Type, Callable, TypeVar
from ..core.types import TypeSystem
from ..core.validation import InterfaceValidator
from ..registry.implementation_registry import ImplementationRegistry
from ..decorators.implementation import ImplementationDecorator

T = TypeVar('T')

class InterfaceSystem:
    """Main interface system coordinating all components"""
    
    def __init__(self) -> None:
        self.type_system: TypeSystem = TypeSystem()
        self.registry: ImplementationRegistry = ImplementationRegistry()
        self.validator: InterfaceValidator = InterfaceValidator(self.type_system)
        self.implements_decorator: ImplementationDecorator = ImplementationDecorator(
            self.registry, self.validator
        )
    
    def implements(self, *interfaces: Type[Any]) -> Callable[[Type[T]], Type[T]]:
        return self.implements_decorator(*interfaces)
    
    def is_implementation(self, obj: Any, interface_cls: Type[Any]) -> bool:
        return self.registry.implements(obj, interface_cls)
    
    def get_interfaces(self, cls: Type[Any]) -> Tuple[Type[Any], ...]:
        return self.registry.get_interfaces_for_class(cls)
    
    def reset(self) -> None:
        self.registry.clear()

class _GlobalInterfaceSystem:
    def __init__(self):
        self._system = InterfaceSystem()
        self._lock = threading.RLock()
    
    def __getattr__(self, name):
        return getattr(self._system, name)
    
    def reset(self):
        with self._lock:
            self._system = InterfaceSystem()

_global = _GlobalInterfaceSystem()

def implements(*interfaces: Type[Any]) -> Callable[[Type[T]], Type[T]]:
    return _global.implements(*interfaces)

def is_implementation(obj: Any, interface_cls: Type[Any]) -> bool:
    return _global.is_implementation(obj, interface_cls)

def get_interfaces(cls: Type[Any]) -> Tuple[Type[Any], ...]:
    return _global.get_interfaces(cls)

def reset_global_state() -> None:
    _global.reset()