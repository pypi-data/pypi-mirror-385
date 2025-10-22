import asyncio
import json
import websockets
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from method_processing.method_discovery import IClientMethodDiscoverer
from method_processing.method_function_handler_generator import IMethodFunctionHandlerGenerator
from method_processing.method_parsing import IMethodParser
from server_contracts import WebSocketClientMethod

T = TypeVar('T')

class ClientConnection:
    """Main client connection class that manages SignalR-like connection and method registration."""

    def __init__(self, uri: str, headers: Optional[Dict[str, str]] = None, enable_reconnect: bool = False):
        self._uri = uri
        self._headers = headers or {}
        self._enable_reconnect = enable_reconnect
        self._websocket = None
        self._known_methods: List[WebSocketClientMethod] = []
        self._method_calling_handlers: Dict[Type, Any] = {}
        self._method_handlers: Dict[str, Callable] = {}
        self._connection_id = None
        self._is_connected = False

        self._module = None
        self._method_discoverer: Optional[IClientMethodDiscoverer] = None
        self._handler_generator: Optional[IMethodFunctionHandlerGenerator] = None
        self._method_parser: Optional[IMethodParser] = None

    def use_method_discovery(self, discoverer: IClientMethodDiscoverer) -> None:
        """Set the method discoverer to use for finding methods."""
        self._method_discoverer = discoverer

    def use_method_function_handler_generator(self, generator: IMethodFunctionHandlerGenerator) -> None:
        """Set the function handler generator to use."""
        self._handler_generator = generator

    def use_method_parser(self, parser: IMethodParser) -> None:
        """Set the method parser to use."""
        self._method_parser = parser

    def use_module(self, module) -> None:
        """Set the module to discover methods from."""
        self._module = module

    def add_method_calling_handler(self, handler_type: Type[T], handler: T) -> None:
        """Add a method calling handler instance for a specific type."""
        self._method_calling_handlers[handler_type] = handler

    async def start_async(self) -> None:
        """Start the connection and register discovered methods."""
        # Use default implementations if not set
        if self._method_discoverer is None:
            from method_processing.method_discovery import AttributeMethodDiscoverer
            self._method_discoverer = AttributeMethodDiscoverer()

        if self._method_parser is None:
            from method_processing.method_parsing import MethodParser
            self._method_parser = MethodParser()

        if self._handler_generator is None:
            from method_processing.method_function_handler_generator import FunctionHandlerGenerator
            self._handler_generator = FunctionHandlerGenerator()

        # Discover methods
        methods = self._method_discoverer.discover(self._module)
        print(f"Discovered {len(methods)} methods marked with @middleman_method")

        for method in methods:
            parsed_method = self._method_parser.parse(method)
            self._known_methods.append(parsed_method)
            print(f"  - {parsed_method.name}")

            # Get handler instance for the method's class
            method_class = getattr(method, '__qualname__', '').split('.')[0] if hasattr(method, '__qualname__') else None
            handler_instance = None

            if method_class:
                for handler_type, instance in self._method_calling_handlers.items():
                    if handler_type.__name__ == method_class:
                        handler_instance = instance
                        break

            # Generate function handler
            function_handler = self._handler_generator.generate_handler(method, handler_instance)
            self._method_handlers[parsed_method.name] = function_handler

        # Connect to SignalR-like WebSocket
        await self._connect()

    async def _connect(self) -> None:
        """Connect to the SignalR hub."""
        try:
            print(f"Connecting to {self._uri}...")

            # Prepare connection parameters
            connect_kwargs = {}
            if self._headers:
                connect_kwargs['additional_headers'] = self._headers

            self._websocket = await websockets.connect(
                self._uri,
                **connect_kwargs
            )

            self._is_connected = True
            print("Connected to SignalR hub!")

            # Send handshake and method info
            await self._send_handshake()
            await self._send_method_info()

            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())

        except Exception as e:
            print(f"Failed to connect: {e}")
            if self._enable_reconnect:
                print("Retrying connection in 5 seconds...")
                await asyncio.sleep(5)
                await self._connect()
            else:
                raise

    async def _send_handshake(self) -> None:
        """Send SignalR handshake message."""
        handshake = {
            "protocol": "json",
            "version": 1
        }
        await self._websocket.send(json.dumps(handshake) + "\x1e")

    async def _send_method_info(self) -> None:
        """Send method information to the server like C# version does."""
        method_data = [method.to_dict() for method in self._known_methods]
        message = {
            "type": 1,  # Invocation message type
            "target": "AddMethodInfo",
            "arguments": [method_data]
        }
        print(f"Sending method info for {len(self._known_methods)} methods to server...")
        await self._websocket.send(json.dumps(message) + "\x1e")

    async def _listen_for_messages(self) -> None:
        """Listen for incoming SignalR messages."""
        try:
            async for raw_message in self._websocket:
                try:
                    # Handle SignalR message format (messages end with \x1e)
                    messages = raw_message.strip().split('\x1e')
                    for msg_str in messages:
                        if not msg_str:
                            continue

                        message = json.loads(msg_str)
                        await self._handle_message(message)

                except Exception as e:
                    print(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
            self._is_connected = False
            if self._enable_reconnect:
                print("Attempting to reconnect...")
                await asyncio.sleep(5)
                await self._connect()
        except Exception as e:
            print(f"Error in message listener: {e}")
            self._is_connected = False

    async def _handle_message(self, message: dict) -> None:
        """Handle incoming SignalR message."""
        msg_type = message.get("type")

        if msg_type == 1:  # Invocation
            target = message.get("target")
            arguments = message.get("arguments", [])
            invocation_id = message.get("invocationId")

            print(f"Received method call: {target} with args: {arguments}")

            if target in self._method_handlers:
                try:
                    handler = self._method_handlers[target]
                    args_bytes = json.dumps(arguments).encode('utf-8')
                    result = await handler(args_bytes)

                    # Parse result
                    result_data = json.loads(result.decode('utf-8')) if result else None
                    print(f"Method {target} returned: {result_data}")

                    # Send completion message back if there's an invocation ID
                    if invocation_id:
                        response = {
                            "type": 3,  # Completion message type
                            "invocationId": invocation_id,
                            "result": result_data
                        }
                        await self._websocket.send(json.dumps(response) + "\x1e")

                except Exception as e:
                    print(f"Error executing method {target}: {e}")
                    if invocation_id:
                        error_response = {
                            "type": 3,  # Completion message type
                            "invocationId": invocation_id,
                            "error": str(e)
                        }
                        await self._websocket.send(json.dumps(error_response) + "\x1e")
            else:
                print(f"Unknown method called: {target}")

        elif msg_type == 2:  # StreamItem
            print("Received stream item (not implemented)")

        elif msg_type == 3:  # Completion
            print("Received completion message")

        elif msg_type == 6:  # Ping
            # Respond with pong
            pong = {"type": 6}
            await self._websocket.send(json.dumps(pong) + "\x1e")

        else:
            print(f"Unknown message type: {msg_type}")

    def is_connected(self) -> bool:
        """Check if the connection is active."""
        return self._is_connected
