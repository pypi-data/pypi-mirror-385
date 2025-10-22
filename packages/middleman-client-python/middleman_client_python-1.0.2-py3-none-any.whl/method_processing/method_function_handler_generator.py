import asyncio
import inspect
import json
import base64
import binascii
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

class IMethodFunctionHandlerGenerator(ABC):
    """Interface for generating function handlers."""

    @abstractmethod
    def generate_handler(self, method: Callable, method_handler: Optional[Any]) -> Callable[[bytes], bytes]:
        """Generate a handler function for the given method."""
        pass

class FunctionHandlerGenerator(IMethodFunctionHandlerGenerator):
    """Generates function handlers for methods."""

    def generate_handler(self, method: Callable, method_handler: Optional[Any]) -> Callable[[bytes], bytes]:
        """Generate a handler function for the given method."""

        # Check if method is static or if we have a handler instance
        signature = inspect.signature(method)
        is_static = 'self' not in signature.parameters

        if not is_static and method_handler is None:
            raise ValueError(f"Method handler instance cannot be None for instance method {method.__name__}")

        async def handler(data: bytes) -> bytes:
            """Handler function that processes incoming data and calls the method."""
            try:
                # Parse parameters
                parameters = list(signature.parameters.values())
                if not is_static:
                    parameters = parameters[1:]  # Skip 'self' parameter

                args = []

                if parameters:
                    # Deserialize input data
                    if data:
                        try:
                            raw_args = json.loads(data.decode('utf-8'))
                            if not isinstance(raw_args, list):
                                raw_args = [raw_args]
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            raw_args = []
                    else:
                        raw_args = []

                    # Check if we have base64-encoded arguments (from C# server)
                    decoded_args = []
                    if len(raw_args) == 1 and isinstance(raw_args[0], str) and self._is_base64(raw_args[0]):
                        try:
                            # Decode base64 and parse JSON to get the actual arguments
                            decoded_bytes = base64.b64decode(raw_args[0])
                            decoded_json = json.loads(decoded_bytes.decode('utf-8'))

                            if isinstance(decoded_json, list):
                                decoded_args = decoded_json
                            else:
                                decoded_args = [decoded_json]
                        except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
                            # If decoding fails, use original arguments
                            decoded_args = raw_args
                    else:
                        decoded_args = raw_args

                    # Convert arguments to proper types and assign to parameters
                    for i, param in enumerate(parameters):
                        if i < len(decoded_args):
                            arg = decoded_args[i]
                        else:
                            # Use default value if parameter has one, otherwise use type default
                            if param.default != inspect.Parameter.empty:
                                arg = param.default
                            else:
                                arg = self._get_default_value(param.annotation if param.annotation != inspect.Parameter.empty else None)
                        args.append(arg)

                # Call the method
                if is_static:
                    result = method(*args)
                else:
                    result = method(method_handler, *args)

                # Handle async methods
                if inspect.iscoroutine(result):
                    result = await result
                elif asyncio.iscoroutine(result):
                    result = await result

                # Handle void return type
                if result is None:
                    return b''

                # Serialize result
                return json.dumps(result).encode('utf-8')

            except Exception as e:
                # Return error information
                error_info = {
                    "error": str(e),
                    "type": type(e).__name__
                }
                return json.dumps(error_info).encode('utf-8')

        return handler

    def _is_base64(self, s: str) -> bool:
        """Check if a string is base64 encoded."""
        try:
            if isinstance(s, str):
                # Check if string is valid base64
                sb_bytes = bytes(s, 'ascii')
            elif isinstance(s, bytes):
                sb_bytes = s
            else:
                return False
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
            return False

    def _get_default_value(self, type_annotation: Any) -> Any:
        """Get default value for a type."""
        if type_annotation is None:
            return None
        elif type_annotation == int:
            return 0
        elif type_annotation == float:
            return 0.0
        elif type_annotation == str:
            return ""
        elif type_annotation == bool:
            return False
        elif type_annotation == list:
            return []
        elif type_annotation == dict:
            return {}
        else:
            return None
