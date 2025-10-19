"""
Client for managing MCP servers and sessions.

This module provides a high-level client that manages MCP servers, connectors,
and sessions from configuration.
"""

import json
import warnings
from typing import Any

from mcp.client.session import ElicitationFnT, LoggingFnT, MessageHandlerFnT, SamplingFnT

from mcp_use.client.config import create_connector_from_config, load_config_file
from mcp_use.client.connectors.sandbox import SandboxOptions
from mcp_use.client.middleware import Middleware, default_logging_middleware
from mcp_use.client.session import MCPSession
from mcp_use.logging import logger
from mcp_use.telemetry.telemetry import telemetry


class MCPClient:
    """Client for managing MCP servers and sessions.

    This class provides a unified interface for working with MCP servers,
    handling configuration, connector creation, and session management.
    """

    def __init__(
        self,
        config: str | dict[str, Any] | None = None,
        allowed_servers: list[str] | None = None,
        sandbox: bool = False,
        sandbox_options: SandboxOptions | None = None,
        sampling_callback: SamplingFnT | None = None,
        elicitation_callback: ElicitationFnT | None = None,
        message_handler: MessageHandlerFnT | None = None,
        logging_callback: LoggingFnT | None = None,
        middleware: list[Middleware] | None = None,
    ) -> None:
        """Initialize a new MCP client.

        Args:
            config: Either a dict containing configuration or a path to a JSON config file.
                   If None, an empty configuration is used.
            sandbox: Whether to use sandboxed execution mode for running MCP servers.
            sandbox_options: Optional sandbox configuration options.
            sampling_callback: Optional sampling callback function.
        """
        self.config: dict[str, Any] = {}
        self.allowed_servers: list[str] = allowed_servers
        self.sandbox = sandbox
        self.sandbox_options = sandbox_options
        self.sessions: dict[str, MCPSession] = {}
        self.active_sessions: list[str] = []
        self.sampling_callback = sampling_callback
        self.elicitation_callback = elicitation_callback
        self.message_handler = message_handler
        self.logging_callback = logging_callback
        # Add default logging middleware if no middleware provided, or prepend it to existing middleware
        default_middleware = [default_logging_middleware]
        if middleware:
            self.middleware = default_middleware + middleware
        else:
            self.middleware = default_middleware
        # Load configuration if provided
        if config is not None:
            if isinstance(config, str):
                self.config = load_config_file(config)
            else:
                self.config = config

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any],
        sandbox: bool = False,
        sandbox_options: SandboxOptions | None = None,
        sampling_callback: SamplingFnT | None = None,
        elicitation_callback: ElicitationFnT | None = None,
        message_handler: MessageHandlerFnT | None = None,
        logging_callback: LoggingFnT | None = None,
    ) -> "MCPClient":
        """Create a MCPClient from a dictionary.

        Args:
            config: The configuration dictionary.
            sandbox: Whether to use sandboxed execution mode for running MCP servers.
            sandbox_options: Optional sandbox configuration options.
            sampling_callback: Optional sampling callback function.
            elicitation_callback: Optional elicitation callback function.
        """
        return cls(
            config=config,
            sandbox=sandbox,
            sandbox_options=sandbox_options,
            sampling_callback=sampling_callback,
            elicitation_callback=elicitation_callback,
            message_handler=message_handler,
            logging_callback=logging_callback,
        )

    @classmethod
    def from_config_file(
        cls,
        filepath: str,
        sandbox: bool = False,
        sandbox_options: SandboxOptions | None = None,
        sampling_callback: SamplingFnT | None = None,
        elicitation_callback: ElicitationFnT | None = None,
        message_handler: MessageHandlerFnT | None = None,
        logging_callback: LoggingFnT | None = None,
    ) -> "MCPClient":
        """Create a MCPClient from a configuration file.

        Args:
            filepath: The path to the configuration file.
            sandbox: Whether to use sandboxed execution mode for running MCP servers.
            sandbox_options: Optional sandbox configuration options.
            sampling_callback: Optional sampling callback function.
            elicitation_callback: Optional elicitation callback function.
        """
        return cls(
            config=load_config_file(filepath),
            sandbox=sandbox,
            sandbox_options=sandbox_options,
            sampling_callback=sampling_callback,
            elicitation_callback=elicitation_callback,
            message_handler=message_handler,
            logging_callback=logging_callback,
        )

    @telemetry("client_add_server")
    def add_server(
        self,
        name: str,
        server_config: dict[str, Any],
    ) -> None:
        """Add a server configuration.

        Args:
            name: The name to identify this server.
            server_config: The server configuration.
        """
        if "mcpServers" not in self.config:
            self.config["mcpServers"] = {}

        self.config["mcpServers"][name] = server_config

    @telemetry("client_remove_server")
    def remove_server(self, name: str) -> None:
        """Remove a server configuration.

        Args:
            name: The name of the server to remove.
        """
        if "mcpServers" in self.config and name in self.config["mcpServers"]:
            del self.config["mcpServers"][name]

            # If we removed an active session, remove it from active_sessions
            if name in self.active_sessions:
                self.active_sessions.remove(name)

    def add_middleware(self, middleware: Middleware) -> None:
        """Add a middleware.

        Args:
            middleware: The middleware to add
        """
        if len(self.sessions) == 0 and middleware not in self.middleware:
            self.middleware.append(middleware)
            return

        if middleware not in self.middleware:
            self.middleware.append(middleware)
            for session in self.sessions.values():
                session.connector.middleware_manager.add_middleware(middleware)

    def get_server_names(self) -> list[str]:
        """Get the list of configured server names.

        Returns:
            List of server names.
        """
        return list(self.config.get("mcpServers", {}).keys())

    def save_config(self, filepath: str) -> None:
        """Save the current configuration to a file.

        Args:
            filepath: The path to save the configuration to.
        """
        with open(filepath, "w") as f:
            json.dump(self.config, f, indent=2)

    @telemetry("client_create_session")
    async def create_session(self, server_name: str, auto_initialize: bool = True) -> MCPSession:
        """Create a session for the specified server.

        Args:
            server_name: The name of the server to create a session for.
            auto_initialize: Whether to automatically initialize the session.

        Returns:
            The created MCPSession.

        Raises:
            ValueError: If the specified server doesn't exist.
        """
        # Get server config
        servers = self.config.get("mcpServers", {})
        if not servers:
            warnings.warn("No MCP servers defined in config", UserWarning, stacklevel=2)
            return None

        if server_name not in servers:
            raise ValueError(f"Server '{server_name}' not found in config")

        server_config = servers[server_name]

        # Create connector with options and client-level auth
        connector = create_connector_from_config(
            server_config,
            sandbox=self.sandbox,
            sandbox_options=self.sandbox_options,
            sampling_callback=self.sampling_callback,
            elicitation_callback=self.elicitation_callback,
            message_handler=self.message_handler,
            logging_callback=self.logging_callback,
            middleware=self.middleware,
        )

        # Create the session
        session = MCPSession(connector)
        if auto_initialize:
            await session.initialize()
        self.sessions[server_name] = session

        # Add to active sessions
        if server_name not in self.active_sessions:
            self.active_sessions.append(server_name)

        return session

    @telemetry("client_create_all_sessions")
    async def create_all_sessions(
        self,
        auto_initialize: bool = True,
    ) -> dict[str, MCPSession]:
        """Create sessions for all configured servers.

        Args:
            auto_initialize: Whether to automatically initialize the sessions.

        Returns:
            Dictionary mapping server names to their MCPSession instances.

        Warns:
            UserWarning: If no servers are configured.
        """
        # Get server config
        servers = self.config.get("mcpServers", {})
        if not servers:
            warnings.warn("No MCP servers defined in config", UserWarning, stacklevel=2)
            return {}

        # Create sessions only for allowed servers if applicable else create for all servers
        for name in servers:
            if self.allowed_servers is None or name in self.allowed_servers:
                await self.create_session(name, auto_initialize)

        return self.sessions

    def get_session(self, server_name: str) -> MCPSession:
        """Get an existing session.

        Args:
            server_name: The name of the server to get the session for.
                        If None, uses the first active session.

        Returns:
            The MCPSession for the specified server.

        Raises:
            ValueError: If no active sessions exist or the specified session doesn't exist.
        """
        if server_name not in self.sessions:
            raise ValueError(f"No session exists for server '{server_name}'")

        return self.sessions[server_name]

    def get_all_active_sessions(self) -> dict[str, MCPSession]:
        """Get all active sessions.

        Returns:
            Dictionary mapping server names to their MCPSession instances.
        """
        return {name: self.sessions[name] for name in self.active_sessions if name in self.sessions}

    @telemetry("client_close_session")
    async def close_session(self, server_name: str) -> None:
        """Close a session.

        Args:
            server_name: The name of the server to close the session for.
                        If None, uses the first active session.

        Raises:
            ValueError: If no active sessions exist or the specified session doesn't exist.
        """
        # Check if the session exists
        if server_name not in self.sessions:
            logger.warning(f"No session exists for server '{server_name}', nothing to close")
            return

        # Get the session
        session = self.sessions[server_name]

        try:
            # Disconnect from the session
            logger.debug(f"Closing session for server '{server_name}'")
            await session.disconnect()
        except Exception as e:
            logger.error(f"Error closing session for server '{server_name}': {e}")
        finally:
            # Remove the session regardless of whether disconnect succeeded
            del self.sessions[server_name]

            # Remove from active_sessions
            if server_name in self.active_sessions:
                self.active_sessions.remove(server_name)

    @telemetry("client_close_all_sessions")
    async def close_all_sessions(self) -> None:
        """Close all active sessions.

        This method ensures all sessions are closed even if some fail.
        """
        # Get a list of all session names first to avoid modification during iteration
        server_names = list(self.sessions.keys())
        errors = []

        for server_name in server_names:
            try:
                logger.debug(f"Closing session for server '{server_name}'")
                await self.close_session(server_name)
            except Exception as e:
                error_msg = f"Failed to close session for server '{server_name}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Log summary if there were errors
        if errors:
            logger.error(f"Encountered {len(errors)} errors while closing sessions")
        else:
            logger.debug("All sessions closed successfully")
