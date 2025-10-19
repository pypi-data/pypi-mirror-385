# mcp_use/middleware/middleware.py
import warnings

from typing_extensions import deprecated

from mcp_use.client.middleware.middleware import (
    CallbackClientSession as _CallbackClientSession,
)
from mcp_use.client.middleware.middleware import (
    MCPResponseContext as _MCPResponseContext,
)
from mcp_use.client.middleware.middleware import (
    Middleware as _Middleware,
)
from mcp_use.client.middleware.middleware import (
    MiddlewareContext as _MiddlewareContext,
)
from mcp_use.client.middleware.middleware import (
    MiddlewareManager as _MiddlewareManager,
)
from mcp_use.client.middleware.middleware import (
    NextFunctionT as _NextFunctionT,
)

warnings.warn(
    "mcp_use.middleware.middleware is deprecated. "
    "Use mcp_use.client.middleware.middleware. "
    "This import will be removed in version 1.4.0",
    DeprecationWarning,
    stacklevel=2,
)


@deprecated("Use mcp_use.client.middleware.middleware.CallbackClientSession")
class CallbackClientSession(_CallbackClientSession): ...


@deprecated("Use mcp_use.client.middleware.middleware.MCPResponseContext")
class MCPResponseContext(_MCPResponseContext): ...


@deprecated("Use mcp_use.client.middleware.middleware.Middleware")
class Middleware(_Middleware): ...


@deprecated("Use mcp_use.client.middleware.middleware.MiddlewareContext")
class MiddlewareContext(_MiddlewareContext): ...


@deprecated("Use mcp_use.client.middleware.middleware.MiddlewareManager")
class MiddlewareManager(_MiddlewareManager): ...


@deprecated("Use mcp_use.client.middleware.middleware.NextFunctionT")
class NextFunctionT(_NextFunctionT): ...
