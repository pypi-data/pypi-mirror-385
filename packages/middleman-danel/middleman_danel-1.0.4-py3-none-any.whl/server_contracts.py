"""Server contracts for WebSocket communication."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class WebSocketClientMethodArgument:
    """Represents a method argument or return type in the WebSocket client."""

    name: Optional[str] = None
    is_primitive: bool = False
    is_array: bool = False
    is_nullable: bool = False
    is_numeric: bool = False
    is_boolean: bool = False
    type: Optional[str] = None
    components: List['WebSocketClientMethodArgument'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "isPrimitive": self.is_primitive,
            "isArray": self.is_array,
            "isNullable": self.is_nullable,
            "isNumeric": self.is_numeric,
            "isBoolean": self.is_boolean,
            "type": self.type,
            "components": [comp.to_dict() for comp in self.components]
        }

@dataclass
class WebSocketClientMethod:
    """Represents a client method that can be called via WebSocket."""

    name: str
    arguments: List[WebSocketClientMethodArgument] = field(default_factory=list)
    returns: Optional[WebSocketClientMethodArgument] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "arguments": [arg.to_dict() for arg in self.arguments],
            "returns": self.returns.to_dict() if self.returns else None
        }
