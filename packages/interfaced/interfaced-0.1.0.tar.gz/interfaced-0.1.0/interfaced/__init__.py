"""
Interface system for Python
"""

from .decorators.interface import interface
from .system.interface_system import implements, is_implementation, get_interfaces, reset_global_state
from .core.exceptions import InterfaceError

__all__ = [
    'interface',
    'implements', 
    'is_implementation',
    'get_interfaces',
    'reset_global_state',
    'InterfaceError'
]