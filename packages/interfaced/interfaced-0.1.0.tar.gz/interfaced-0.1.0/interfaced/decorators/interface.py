from typing import Type, TypeVar
from ..metadata.interface_meta import InterfaceMeta

T = TypeVar('T')

class InterfaceDecorator:
    """Decorator for creating interface classes"""
    
    def __call__(self, cls: Type[T]) -> Type[T]:
        # Allow custom metaclasses, but ensure InterfaceMeta is used if none specified
        metaclass = getattr(cls, '__metaclass__', InterfaceMeta) or InterfaceMeta
        return metaclass(cls.__name__, cls.__bases__, dict(cls.__dict__))

interface: InterfaceDecorator = InterfaceDecorator()