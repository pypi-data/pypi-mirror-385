from typing import Any, Dict, Type, TypeVar, get_origin, get_args, get_type_hints
from ..metadata.signature import MethodSignature
from .types import TypeSystem
from .exceptions import InterfaceError

class InterfaceValidator:
    """Validator for interface implementation compliance"""
    
    def __init__(self, type_system: TypeSystem) -> None:
        self.type_system: TypeSystem = type_system
    
    def validate_implementation(self, cls: Type[Any], interface_cls: Type[Any]) -> None:
        generic_context = self._get_generic_context(cls, interface_cls)
        self._validate_methods(cls, interface_cls, generic_context)
        self._validate_attributes(cls, interface_cls, generic_context)
        self._validate_context_managers(cls, interface_cls, generic_context)
    
    def _get_generic_context(self, cls: Type[Any], interface_cls: Type[Any]) -> Dict[TypeVar, Any]:
        origin = get_origin(interface_cls) or interface_cls
        if not hasattr(origin, '__generic_params__'):
            return {}
        if get_origin(interface_cls):
            interface_args = get_args(interface_cls)
            generic_params = getattr(origin, '__generic_params__', [])
            if len(interface_args) == len(generic_params):
                return dict(zip(generic_params, interface_args))
        return {}
    
    def _validate_methods(self, cls: Type[Any], interface_cls: Type[Any], generic_context: Dict[TypeVar, Any]) -> None:
        origin = get_origin(interface_cls) or interface_cls
        interface_methods: dict[str, MethodSignature] = origin.__method_signatures__
        
        for method_name, interface_sig in interface_methods.items():
            parts = method_name.split('.')
            if len(parts) > 1 and parts[-1] in ('setter', 'deleter'):
                property_name = '.'.join(parts[:-1])
                accessor = parts[-1]
                role = 'set' if accessor == 'setter' else 'del'
                f_access = 'f' + role
                if not hasattr(cls, property_name):
                    raise InterfaceError(f"Class {cls.__name__} missing property '{property_name}' from interface {interface_cls.__name__}")
                impl_prop = getattr(cls, property_name)
                if not isinstance(impl_prop, property):
                    raise InterfaceError(f"'{property_name}' in {cls.__name__} should be a property")
                impl_method = getattr(impl_prop, f_access, None)
                if impl_method is None:
                    raise InterfaceError(f"Missing {accessor} for property '{property_name}' in {cls.__name__}")
            elif len(parts) > 1 and parts[-1] in ('__get__', '__set__', '__delete__'):
                descriptor_name = '.'.join(parts[:-1])
                method_role = parts[-1]
                if descriptor_name in ('__dict__', '__weakref__', '__class__'):
                    continue
                if not hasattr(cls, descriptor_name):
                    raise InterfaceError(f"Class {cls.__name__} missing descriptor '{descriptor_name}' from interface {interface_cls.__name__}")
                impl_descriptor = getattr(cls, descriptor_name)
                if not (hasattr(impl_descriptor, '__get__') or hasattr(impl_descriptor, '__set__') or hasattr(impl_descriptor, '__delete__')):
                    raise InterfaceError(f"'{descriptor_name}' in {cls.__name__} should be a descriptor")
                impl_method = getattr(impl_descriptor, method_role, None)
                if impl_method is None:
                    raise InterfaceError(f"Missing {method_role} for descriptor '{descriptor_name}' in {cls.__name__}")
            else:
                property_name = method_name
                if not hasattr(cls, method_name):
                    if method_name == '__enter__' and hasattr(cls, '__exit__'):
                        continue
                    elif method_name == '__exit__' and hasattr(cls, '__enter__'):
                        continue
                    elif method_name == '__aenter__' and hasattr(cls, '__aexit__'):
                        continue
                    elif method_name == '__aexit__' and hasattr(cls, '__aenter__'):
                        continue
                    else:
                        raise InterfaceError(f"Class {cls.__name__} missing method '{method_name}' from interface {interface_cls.__name__}")
                
                impl_method: Any = getattr(cls, method_name)
                if interface_sig.property_role == 'get':
                    self._validate_property(impl_method, method_name, cls)
                    impl_method = impl_method.fget
                elif interface_sig.is_static:
                    if not isinstance(impl_method, staticmethod):
                        raise InterfaceError(f"Method '{method_name}' in {cls.__name__} should be a staticmethod")
                    impl_method = impl_method.__func__
                elif interface_sig.is_class:
                    if not isinstance(impl_method, classmethod):
                        raise InterfaceError(f"Method '{method_name}' in {cls.__name__} should be a classmethod")
                    impl_method = impl_method.__func__
                elif interface_sig.is_descriptor:
                    if method_name in ('__dict__', '__weakref__', '__class__'):
                        continue
                    if not (hasattr(impl_method, '__get__') or hasattr(impl_method, '__set__') or hasattr(impl_method, '__delete__')):
                        raise InterfaceError(f"'{method_name}' in {cls.__name__} should be a descriptor")
            
            if method_name not in ('__enter__', '__exit__', '__aenter__', '__aexit__'):
                impl_sig: MethodSignature = cls.__signature_cache__.get(impl_method, cls)
                self._validate_method_signature(interface_sig, impl_sig, method_name, cls, generic_context)
            
            if interface_sig.is_abstract and getattr(impl_method, '__isabstractmethod__', False):
                raise InterfaceError(f"Abstract method '{method_name}' in {cls.__name__} must be implemented concretely")
    
    def _validate_property(self, impl_method: Any, method_name: str, cls: Type[Any]) -> None:
        if not isinstance(impl_method, property):
            raise InterfaceError(f"Method '{method_name}' in {cls.__name__} should be a property")
    
    def _validate_method_signature(self, interface_sig: MethodSignature, impl_sig: MethodSignature, method_name: str, 
                                 cls: Type[Any], generic_context: Dict[TypeVar, Any]) -> None:
        if interface_sig.parameters != impl_sig.parameters:
            raise InterfaceError(f"Signature mismatch for '{method_name}' in {cls.__name__}: expected {interface_sig.parameters}, got {impl_sig.parameters}")
        
        self._validate_parameter_types(interface_sig, impl_sig, method_name, generic_context)
        
        if interface_sig.is_async and not impl_sig.is_async:
            raise InterfaceError(f"Method '{method_name}' in {cls.__name__} should be async but is implemented as sync")
        elif not interface_sig.is_async and impl_sig.is_async:
            raise InterfaceError(f"Method '{method_name}' in {cls.__name__} should be sync but is implemented as async")
        
        self._validate_return_type(interface_sig, impl_sig, method_name, cls, generic_context)
    
    def _validate_parameter_types(self, interface_sig: MethodSignature, impl_sig: MethodSignature, 
                                method_name: str, generic_context: Dict[TypeVar, Any]) -> None:
        for param_name in interface_sig.parameters:
            if param_name in interface_sig.param_types and param_name in impl_sig.param_types:
                interface_param_type: Any = interface_sig.param_types[param_name]
                impl_param_type: Any = impl_sig.param_types[param_name]
                if generic_context:
                    interface_param_type = self._apply_generic_context(interface_param_type, generic_context)
                if not self.type_system.is_compatible(interface_param_type, impl_param_type, generic_context):
                    raise InterfaceError(f"Parameter type mismatch for '{param_name}' in '{method_name}': "
                                       f"expected {impl_param_type} to accept {interface_param_type}")
    
    def _validate_return_type(self, interface_sig: MethodSignature, impl_sig: MethodSignature, 
                            method_name: str, cls: Type[Any], generic_context: Dict[TypeVar, Any]) -> None:
        if (interface_sig.return_type != Any and impl_sig.return_type != Any):
            interface_return_type = interface_sig.return_type
            if generic_context:
                interface_return_type = self._apply_generic_context(interface_return_type, generic_context)
            if not self.type_system.is_compatible(impl_sig.return_type, interface_return_type, generic_context):
                raise InterfaceError(f"Return type mismatch for '{method_name}' in {cls.__name__}: "
                                   f"expected {impl_sig.return_type} to be compatible with {interface_return_type}")
    
    def _apply_generic_context(self, tp: Any, generic_context: Dict[TypeVar, Any]) -> Any:
        if isinstance(tp, TypeVar):
            return generic_context.get(tp, tp)
        origin = get_origin(tp)
        if origin:
            args = get_args(tp)
            new_args = tuple(self._apply_generic_context(arg, generic_context) for arg in args)
            return origin[new_args]
        return tp
    
    def _validate_attributes(self, cls: Type[Any], interface_cls: Type[Any], generic_context: Dict[TypeVar, Any]) -> None:
        origin = get_origin(interface_cls) or interface_cls
        interface_attrs: dict[str, Any] = origin.__attribute_types__
        cls_hints = self._get_class_annotations(cls)
        for attr_name, expected_type in interface_attrs.items():
            if attr_name not in cls_hints:
                raise InterfaceError(f"Class {cls.__name__} missing attribute '{attr_name}' from interface {interface_cls.__name__}")
            actual_type: Any = cls_hints[attr_name]
            if generic_context:
                expected_type = self._apply_generic_context(expected_type, generic_context)
            if not self.type_system.is_compatible(actual_type, expected_type, generic_context):
                raise InterfaceError(f"Type mismatch for '{attr_name}' in {cls.__name__}: "
                                    f"expected {actual_type} to be compatible with {expected_type}")

    def _get_class_annotations(self, cls: Type[Any]) -> Dict[str, Any]:
        try:
            return get_type_hints(cls, localns=cls.__dict__.copy())
        except (NameError, TypeError):
            annotations = {}
            for base in cls.__mro__:
                if hasattr(base, '__annotations__'):
                    annotations.update(base.__annotations__)
            return annotations

    def _validate_context_managers(self, cls: Type[Any], interface_cls: Type[Any], generic_context: Dict[TypeVar, Any]) -> None:
        """Validate context manager method pairs"""
        origin = get_origin(interface_cls) or interface_cls
        
        if origin.__context_managers__:
            if '__enter__' in origin.__context_managers__:
                if not hasattr(cls, '__enter__'):
                    raise InterfaceError(f"Class {cls.__name__} missing __enter__ method required by interface {interface_cls.__name__}")
                if not hasattr(cls, '__exit__'):
                    raise InterfaceError(f"Class {cls.__name__} missing __exit__ method required by interface {interface_cls.__name__}")
                
                enter_method = getattr(cls, '__enter__')
                exit_method = getattr(cls, '__exit__')
                
                enter_sig = cls.__signature_cache__.get(enter_method, cls)
                exit_sig = cls.__signature_cache__.get(exit_method, cls)
                
                if len(enter_sig.parameters) != 1 or 'self' not in enter_sig.parameters:
                    raise InterfaceError(f"__enter__ method in {cls.__name__} should have exactly 'self' parameter")
                
                expected_exit_params = ('self', 'exc_type', 'exc_val', 'exc_tb')
                if exit_sig.parameters != expected_exit_params:
                    raise InterfaceError(f"__exit__ method in {cls.__name__} should have parameters {expected_exit_params}, got {exit_sig.parameters}")
                
                if exit_sig.return_type not in (bool, Any):
                    raise InterfaceError(f"__exit__ method in {cls.__name__} should return bool, got {exit_sig.return_type}")

        if origin.__async_context_managers__:
            if '__aenter__' in origin.__async_context_managers__:
                if not hasattr(cls, '__aenter__'):
                    raise InterfaceError(f"Class {cls.__name__} missing __aenter__ method required by interface {interface_cls.__name__}")
                if not hasattr(cls, '__aexit__'):
                    raise InterfaceError(f"Class {cls.__name__} missing __aexit__ method required by interface {interface_cls.__name__}")
                
                aenter_method = getattr(cls, '__aenter__')
                aexit_method = getattr(cls, '__aexit__')
                
                aenter_sig = cls.__signature_cache__.get(aenter_method, cls)
                aexit_sig = cls.__signature_cache__.get(aexit_method, cls)
                
                # __aenter__ should take only self and return context type
                if len(aenter_sig.parameters) != 1 or 'self' not in aenter_sig.parameters:
                    raise InterfaceError(f"__aenter__ method in {cls.__name__} should have exactly 'self' parameter")
                
                if not aenter_sig.is_async:
                    raise InterfaceError(f"__aenter__ method in {cls.__name__} should be async")
                
                # __aexit__ should have specific signature and be async
                expected_aexit_params = ('self', 'exc_type', 'exc_val', 'exc_tb')
                if aexit_sig.parameters != expected_aexit_params:
                    raise InterfaceError(f"__aexit__ method in {cls.__name__} should have parameters {expected_aexit_params}, got {aexit_sig.parameters}")
                
                if not aexit_sig.is_async:
                    raise InterfaceError(f"__aexit__ method in {cls.__name__} should be async")
                
                if aexit_sig.return_type not in (bool, Any):
                    raise InterfaceError(f"__aexit__ method in {cls.__name__} should return bool, got {aexit_sig.return_type}")
