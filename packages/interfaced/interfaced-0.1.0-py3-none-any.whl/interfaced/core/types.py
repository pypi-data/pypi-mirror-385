from typing import Any, Dict, TypeVar, get_origin, get_args, Union

class TypeSystem:
    @staticmethod
    def is_compatible(actual: Any, expected: Any, generic_context: Dict[TypeVar, Any] = None) -> bool:
        if generic_context is None:
            generic_context = {}
            
        if isinstance(expected, TypeVar):
            if expected in generic_context:
                expected = generic_context[expected]
            else:
                return True
                
        if actual == expected:
            return True
            
        if expected is Any or actual is Any:
            return True
            
        if TypeSystem._is_optional(expected) and actual is type(None):
            return True
            
        if TypeSystem._is_union(actual):
            return all(TypeSystem.is_compatible(arg, expected, generic_context) for arg in get_args(actual))
        
        if TypeSystem._is_union(expected):
            return any(TypeSystem.is_compatible(actual, arg, generic_context) for arg in get_args(expected))
            
        actual_origin = get_origin(actual) or actual
        expected_origin = get_origin(expected) or expected
        
        if actual_origin == expected_origin:
            actual_args = get_args(actual)
            expected_args = get_args(expected)
            
            if not actual_args and not expected_args:
                return True
            
            if (actual_args and not expected_args) or (not actual_args and expected_args):
                return False
                
            if len(actual_args) != len(expected_args):
                return False
                
            return all(
                TypeSystem.is_compatible(actual_arg, expected_arg, generic_context)
                for actual_arg, expected_arg in zip(actual_args, expected_args)
            )
        
        if isinstance(actual_origin, type) and isinstance(expected_origin, type):
            try:
                return issubclass(actual_origin, expected_origin)
            except TypeError:
                return False
                
        return False

    @staticmethod
    def _is_optional(tp: Any) -> bool:
        """Check if type is Optional[T]"""
        origin = get_origin(tp)
        if origin is Union:
            args = get_args(tp)
            return type(None) in args
        return False
    
    @staticmethod
    def _is_union(tp: Any) -> bool:
        """Check if type is Union"""
        return get_origin(tp) is Union