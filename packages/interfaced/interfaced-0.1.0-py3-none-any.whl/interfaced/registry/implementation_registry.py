import threading
from typing import Any, Type, Tuple, Dict, Set
from typing import get_origin, get_args

class ImplementationRegistry:
    """Registry for tracking interface implementations"""
    
    __slots__ = ('_implementations', '_interface_mapping', '_lock')
    
    def __init__(self) -> None:
        self._implementations: Dict[type, Tuple[str, ...]] = {}
        self._interface_mapping: Dict[str, Type[Any]] = {}
        self._lock: threading.RLock = threading.RLock()
    
    def register(self, cls: Type[Any], interfaces: Tuple[Type[Any], ...]) -> None:
        with self._lock:
            interface_ids = []
            for iface in interfaces:
                all_interfaces = self._get_all_interfaces(iface)
                for interface in all_interfaces:
                    interface_id = self._get_interface_id(interface)
                    interface_ids.append(interface_id)
                    self._interface_mapping[interface_id] = interface
            self._implementations[cls] = tuple(interface_ids)
    
    def _get_all_interfaces(self, interface_cls: Type[Any]) -> Set[Type[Any]]:
        """Get all interfaces in the inheritance hierarchy"""
        interfaces = set()
        to_process = [interface_cls]
        
        while to_process:
            current = to_process.pop()
            interfaces.add(current)
            
            # Add base interfaces
            for base in getattr(current, '__bases__', []):
                if hasattr(base, '__method_signatures__'):  # Its an interface
                    to_process.append(base)
        
        return interfaces
    
    def implements(self, obj: Any, interface_cls: Type[Any]) -> bool:
        obj_cls: Type[Any] = obj if isinstance(obj, type) else type(obj)
        with self._lock:
            implemented_interface_ids = self._implementations.get(obj_cls)
            if implemented_interface_ids is None:
                return False
            
            target_id = self._get_interface_id(interface_cls)
            return target_id in implemented_interface_ids
    
    def _get_interface_id(self, interface_cls: Type[Any]) -> str:
        origin = get_origin(interface_cls) or interface_cls
        args = get_args(interface_cls)
        if args:
            arg_ids = sorted(str(arg) for arg in args)
            return f"{origin.__name__}[{','.join(arg_ids)}]"
        return origin.__name__
    
    def get_implementations(self) -> Dict[type, Tuple[str, ...]]:
        return self._implementations.copy()
    
    def get_interfaces_for_class(self, cls: Type[Any]) -> Tuple[Type[Any], ...]:
        with self._lock:
            interface_ids = self._implementations.get(cls, ())
            interfaces = []
            for interface_id in interface_ids:
                if interface_id in self._interface_mapping:
                    interfaces.append(self._interface_mapping[interface_id])
            return tuple(interfaces)
    
    def clear(self) -> None:
        with self._lock:
            self._implementations.clear()
            self._interface_mapping.clear()