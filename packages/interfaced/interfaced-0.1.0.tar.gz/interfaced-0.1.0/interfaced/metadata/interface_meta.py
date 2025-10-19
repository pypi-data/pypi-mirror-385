from abc import ABCMeta
from dataclasses import replace
from typing import Any, Generic, List, Type, Dict, Tuple, TypeVar, get_type_hints
from .signature import MethodSignature
from .cache import SignatureCache

class InterfaceMetadata:
    """Metadata storage for interface classes"""
    
    def __init__(self) -> None:
        self.signature_cache: SignatureCache = SignatureCache()
        self.method_signatures: Dict[str, MethodSignature] = {}
        self.attribute_types: Dict[str, Any] = {}
        self.context_managers: set[str] = set()
        self.async_context_managers: set[str] = set()
    
    def inherit_from_bases(self, bases: Tuple[type, ...]) -> None:
        for base in bases:
            if hasattr(base, '__mro__'):
                for parent in base.__mro__[1:]:
                    if hasattr(parent, '__method_signatures__'):
                        base_methods: Dict[str, MethodSignature] = getattr(parent, '__method_signatures__')
                        self.method_signatures.update(base_methods)
                    if hasattr(parent, '__attribute_types__'):
                        base_attrs: Dict[str, Any] = getattr(parent, '__attribute_types__')
                        self.attribute_types.update(base_attrs)
                    if hasattr(parent, '__context_managers__'):
                        base_cm: set[str] = getattr(parent, '__context_managers__')
                        self.context_managers.update(base_cm)
                    if hasattr(parent, '__async_context_managers__'):
                        base_async_cm: set[str] = getattr(parent, '__async_context_managers__')
                        self.async_context_managers.update(base_async_cm)
    
    def add_from_namespace(self, namespace: Dict[str, Any], cls: Type[Any]) -> None:
        for attr_name, attr_value in namespace.items():
            # Skip built-in dunder methods except important ones
            if (attr_name.startswith('__') and attr_name.endswith('__') and 
                attr_name not in ('__init__', '__call__', '__getattribute__', '__setattr__', 
                                '__delattr__', '__getitem__', '__setitem__', '__delitem__',
                                '__enter__', '__exit__', '__aenter__', '__aexit__')):
                continue
                
            added_as_method = False
            
            # Handle properties
            if isinstance(attr_value, property):
                self._handle_property(attr_name, attr_value, cls)
                added_as_method = True
            
            # Handle static methods
            elif isinstance(attr_value, staticmethod):
                self._handle_staticmethod(attr_name, attr_value)
                added_as_method = True
            
            # Handle class methods
            elif isinstance(attr_value, classmethod):
                self._handle_classmethod(attr_name, attr_value)
                added_as_method = True
            
            # Handle regular methods and functions
            elif callable(attr_value) and not self._is_descriptor_method(attr_name):
                # Check that this is not a descriptor method (__get__, __set__, etc)
                if not attr_name.startswith('__') or (attr_name.startswith('__') and attr_name.endswith('__') and
                    attr_name in ('__enter__', '__exit__', '__aenter__', '__aexit__', '__init__', '__call__')):
                    
                    sig = self.signature_cache._extract_signature(attr_value)
                    sig = replace(sig, is_abstract=getattr(attr_value, '__isabstractmethod__', False))
                    self.method_signatures[attr_name] = sig
                    added_as_method = True
                    
                    if attr_name == '__enter__':
                        self.context_managers.add(attr_name)
                    elif attr_name == '__aenter__':
                        self.async_context_managers.add(attr_name)
            
            if not added_as_method and not callable(attr_value) and not attr_name.startswith('__'):
                hints: Dict[str, Any] = get_type_hints(cls, globalns=globals())
                if attr_name in hints:
                    self.attribute_types[attr_name] = hints[attr_name]
    
    def _is_descriptor_method(self, attr_name: str) -> bool:
        """Check if this is a descriptor method name"""
        descriptor_methods = {'__get__', '__set__', '__delete__'}
        return any(attr_name.endswith(f".{method}") for method in descriptor_methods)
    
    def _handle_property(self, attr_name: str, prop: property, cls: Type[Any]) -> None:
        """Handle property methods"""
        if prop.fget is not None:
            getter_sig = self.signature_cache._extract_signature(prop.fget)
            getter_sig = replace(getter_sig, property_role='get', is_abstract=getattr(prop.fget, '__isabstractmethod__', False))
            self.method_signatures[attr_name] = getter_sig
        if prop.fset is not None:
            setter_sig = self.signature_cache._extract_signature(prop.fset)
            setter_sig = replace(setter_sig, property_role='set', is_abstract=getattr(prop.fset, '__isabstractmethod__', False))
            self.method_signatures[attr_name + '.setter'] = setter_sig
        if prop.fdel is not None:
            deleter_sig = self.signature_cache._extract_signature(prop.fdel)
            deleter_sig = replace(deleter_sig, property_role='del', is_abstract=getattr(prop.fdel, '__isabstractmethod__', False))
            self.method_signatures[attr_name + '.deleter'] = deleter_sig
    
    def _handle_staticmethod(self, attr_name: str, static_method: staticmethod) -> None:
        """Handle static method"""
        func = static_method.__func__
        sig = self.signature_cache._extract_signature(func)
        sig = replace(sig, is_static=True, is_abstract=getattr(func, '__isabstractmethod__', False))
        self.method_signatures[attr_name] = sig
    
    def _handle_classmethod(self, attr_name: str, class_method: classmethod) -> None:
        """Handle class method"""
        func = class_method.__func__
        sig = self.signature_cache._extract_signature(func)
        sig = replace(sig, is_class=True, is_abstract=getattr(func, '__isabstractmethod__', False))
        self.method_signatures[attr_name] = sig

class InterfaceMeta(ABCMeta):
    """Metaclass for interfaces, compatible with ABC and custom metaclasses"""
    
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> Type[Any]:
        filtered_bases = tuple(base for base in bases if not isinstance(base, type) or not issubclass(base, Generic) or base is Generic)
        cls = super().__new__(mcs, name, filtered_bases, namespace)
        return cls
    
    def __init__(cls: Type[Any], name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        metadata: InterfaceMetadata = InterfaceMetadata()
        metadata.inherit_from_bases(bases)
        metadata.add_from_namespace(namespace, cls)
        
        cls.__signature_cache__ = metadata.signature_cache
        cls.__method_signatures__ = metadata.method_signatures
        cls.__attribute_types__ = metadata.attribute_types
        cls.__context_managers__ = metadata.context_managers
        cls.__async_context_managers__ = metadata.async_context_managers
        
        if hasattr(cls, '__parameters__'):
            cls.__generic_params__: List[TypeVar] = getattr(cls, '__parameters__', [])
        else:
            cls.__generic_params__ = []