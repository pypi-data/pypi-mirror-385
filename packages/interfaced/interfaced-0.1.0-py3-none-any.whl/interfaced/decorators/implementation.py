from typing import Tuple, Type, Any, Callable, TypeVar, get_origin
from ..registry.implementation_registry import ImplementationRegistry
from ..core.validation import InterfaceValidator
from ..core.exceptions import InterfaceError

T = TypeVar('T')

class ImplementationDecorator:
    """Decorator for marking classes as interface implementations"""
    
    def __init__(self, registry: ImplementationRegistry, validator: InterfaceValidator) -> None:
        self.registry: ImplementationRegistry = registry
        self.validator: InterfaceValidator = validator
    
    def __call__(self, *interfaces: Type[Any]) -> Callable[[Type[T]], Type[T]]:
        def decorator(cls: Type[T]) -> Type[T]:
            self._validate_interfaces(interfaces)
            
            from ..metadata.cache import SignatureCache
            cls.__signature_cache__ = SignatureCache()
            
            try:
                for interface_cls in interfaces:
                    self.validator.validate_implementation(cls, interface_cls)
            except InterfaceError as e:
                if hasattr(cls, '__signature_cache__'):
                    delattr(cls, '__signature_cache__')
                raise InterfaceError(f"Class {cls.__name__} does not properly implement {interface_cls.__name__}: {e}")
            
            self.registry.register(cls, interfaces)
            cls.__validated__ = True
            
            return cls
        return decorator
    
    def _validate_interfaces(self, interfaces: Tuple[Type[Any], ...]) -> None:
        for interface_cls in interfaces:
            origin = get_origin(interface_cls) or interface_cls
            if not hasattr(origin, '__method_signatures__'):
                raise InterfaceError(f"{interface_cls.__name__} is not an interface. Use @interface decorator.")