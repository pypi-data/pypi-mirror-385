import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

def middleman_method(func: Callable) -> Callable:
    """Decorator to mark methods as MiddleMan methods."""
    func._is_middleman_method = True
    return func

class IClientMethodDiscoverer(ABC):
    """Interface for discovering client methods."""

    @abstractmethod
    def discover(self, module: Optional[Any]) -> List[Callable]:
        """Discover methods in the given module."""
        pass

class AttributeMethodDiscoverer(IClientMethodDiscoverer):
    """Discovers methods marked with the middleman_method decorator."""

    def discover(self, module: Optional[Any]) -> List[Callable]:
        """Discover methods marked with the middleman_method decorator."""
        if module is None:
            # If no module provided, discover from the calling frame
            import sys
            frame = sys._getframe(1)
            module = frame.f_globals

        methods = []

        if isinstance(module, dict):
            # Handle module globals dictionary
            for name, obj in module.items():
                if callable(obj) and hasattr(obj, '_is_middleman_method'):
                    methods.append(obj)
                elif inspect.isclass(obj):
                    # Check class methods
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
                        if hasattr(method, '_is_middleman_method'):
                            methods.append(method)
                    # Check static methods and functions
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_middleman_method'):
                            methods.append(method)
        else:
            # Handle module objects
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and hasattr(obj, '_is_middleman_method'):
                    methods.append(obj)
                elif inspect.isclass(obj):
                    # Check class methods
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
                        if hasattr(method, '_is_middleman_method'):
                            methods.append(method)
                    # Check static methods and functions
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_middleman_method'):
                            methods.append(method)

        return methods
