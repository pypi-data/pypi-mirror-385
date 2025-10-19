import inspect
from typing import Any, Callable, Type, get_type_hints
from .signature import MethodSignature

class SignatureCache:
    """Cache for method signatures"""
    
    def __init__(self) -> None:
        self._cache: dict[int, MethodSignature] = {}
    
    def get(self, method: Callable[..., Any], cls: Type[Any]) -> MethodSignature:
        method_id = id(method)
        if method_id not in self._cache:
            self._cache[method_id] = self._extract_signature(method)
        return self._cache[method_id]
    
    def clear(self) -> None:
        self._cache.clear()
    
    @staticmethod
    def _extract_signature(method: Callable[..., Any]) -> MethodSignature:
        sig = inspect.signature(method)
        try:
            hints = get_type_hints(method, globalns=method.__globals__)
        except Exception:
            hints = {}
        parameters = tuple(sig.parameters.keys())
        param_types = {name: hints.get(name, Any) for name in parameters}
        defaults = tuple(
            sig.parameters[name].default 
            for name in parameters 
            if sig.parameters[name].default != inspect.Parameter.empty
        )
        return_type = hints.get('return', Any)
        
        is_async = (inspect.iscoroutinefunction(method) or 
                    inspect.iscoroutinefunction(getattr(method, '__func__', None)) or
                    (hasattr(method, '_is_coroutine') and method._is_coroutine))
        
        is_abstract = getattr(method, '__isabstractmethod__', False)
        
        method_name = getattr(method, '__name__', '')
        is_context_manager = method_name == '__enter__' and not is_async
        is_async_context_manager = method_name == '__aenter__' and is_async
        
        return MethodSignature(
            parameters, param_types, defaults, return_type, is_async, 
            is_abstract=is_abstract,
            is_context_manager=is_context_manager,
            is_async_context_manager=is_async_context_manager
        )