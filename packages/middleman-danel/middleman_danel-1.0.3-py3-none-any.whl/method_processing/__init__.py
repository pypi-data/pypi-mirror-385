"""Method processing package for discovering and handling methods."""

from .method_discovery import IClientMethodDiscoverer, AttributeMethodDiscoverer, middleman_method
from .method_parsing import IMethodParser, MethodParser
from .method_function_handler_generator import IMethodFunctionHandlerGenerator, FunctionHandlerGenerator

__all__ = [
    "IClientMethodDiscoverer", "AttributeMethodDiscoverer", "middleman_method",
    "IMethodParser", "MethodParser",
    "IMethodFunctionHandlerGenerator", "FunctionHandlerGenerator"
]
