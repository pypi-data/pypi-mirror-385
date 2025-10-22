import inspect
import sys
import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Union, get_type_hints, get_origin, get_args

# Ensure the parent directory is in the Python path for server_contracts import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import server contracts
from server_contracts import WebSocketClientMethod, WebSocketClientMethodArgument

class IMethodParser(ABC):
    """Interface for parsing method information."""

    @abstractmethod
    def parse(self, method: Callable) -> WebSocketClientMethod:
        """Parse a method and return WebSocketClientMethod information."""
        pass

class MethodParser(IMethodParser):
    """Parser for converting Python methods to WebSocketClientMethod objects."""

    def parse(self, method: Callable) -> WebSocketClientMethod:
        """Parse a method and return WebSocketClientMethod information."""
        signature = inspect.signature(method)
        type_hints = get_type_hints(method)

        # Get method name
        name = method.__name__

        # Parse arguments
        arguments = []
        for param_name, param in signature.parameters.items():
            if param_name == 'self':  # Skip self parameter
                continue

            param_type = type_hints.get(param_name, param.annotation if param.annotation != inspect.Parameter.empty else str)
            argument = self._describe_type(param_name, param_type)
            arguments.append(argument)

        # Parse return type
        return_type = type_hints.get('return', signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None)
        returns = None
        if return_type and return_type != type(None):
            returns = self._describe_type(None, return_type)

        return WebSocketClientMethod(
            name=name,
            arguments=arguments,
            returns=returns
        )

    def _describe_type(self, name: Optional[str], type_annotation: Any) -> WebSocketClientMethodArgument:
        """Describe a type and return WebSocketClientMethodArgument."""

        # Handle None type
        if type_annotation is type(None):
            return WebSocketClientMethodArgument(
                name=name,
                type="NoneType",
                is_primitive=True,
                is_array=False,
                is_nullable=True,
                is_numeric=False,
                is_boolean=False,
                components=[]
            )

        # Handle Union types (including Optional)
        origin = get_origin(type_annotation)
        if origin is Union:
            args = get_args(type_annotation)
            # Check if it's Optional (Union with None)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                result = self._describe_type(name, non_none_type)
                result.is_nullable = True
                return result

        # Handle List types
        if origin is list or (hasattr(type_annotation, '__origin__') and type_annotation.__origin__ is list):
            args = get_args(type_annotation)
            if args:
                element_type = args[0]
                element_description = self._describe_type(name, element_type)
                element_description.is_array = True
                return element_description

        # Get type name
        type_name = getattr(type_annotation, '__name__', str(type_annotation))
        if hasattr(type_annotation, '__module__') and type_annotation.__module__ != 'builtins':
            type_name = f"{type_annotation.__module__}.{type_name}"

        # Check if primitive
        is_primitive = type_annotation in (int, float, str, bool, bytes) or type_name in ('int', 'float', 'str', 'bool', 'bytes')
        is_numeric = type_annotation in (int, float) or type_name in ('int', 'float')
        is_boolean = type_annotation is bool or type_name == 'bool'

        argument = WebSocketClientMethodArgument(
            name=name,
            type=type_name,
            is_primitive=is_primitive,
            is_array=False,
            is_nullable=False,
            is_numeric=is_numeric,
            is_boolean=is_boolean,
            components=[]
        )

        # If not primitive, analyze components (for complex objects)
        if not is_primitive and hasattr(type_annotation, '__annotations__'):
            for field_name, field_type in type_annotation.__annotations__.items():
                component = self._describe_type(field_name, field_type)
                argument.components.append(component)

        return argument
