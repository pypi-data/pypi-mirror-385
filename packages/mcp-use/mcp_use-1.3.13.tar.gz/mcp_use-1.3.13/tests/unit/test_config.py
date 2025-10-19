"""
Unit tests for the config module.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from mcp_use.client.auth.bearer import BearerAuth
from mcp_use.client.config import create_connector_from_config, load_config_file
from mcp_use.client.connectors import HttpConnector, SandboxConnector, StdioConnector, WebSocketConnector
from mcp_use.client.connectors.sandbox import SandboxOptions


class TestConfigLoading(unittest.TestCase):
    """Tests for configuration loading functions."""

    def test_load_config_file(self):
        """Test loading a configuration file."""
        test_config = {"mcpServers": {"test": {"url": "http://test.com"}}}

        # Create a temporary file with test config
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            json.dump(test_config, temp)
            temp_path = temp.name

        try:
            # Test loading from file
            loaded_config = load_config_file(temp_path)
            self.assertEqual(loaded_config, test_config)
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    def test_load_config_file_nonexistent(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_config_file("/tmp/nonexistent_file.json")


class TestConnectorCreation(unittest.TestCase):
    """Tests for connector creation from configuration."""

    def test_create_http_connector(self):
        """Test creating an HTTP connector from config."""
        server_config = {
            "url": "http://test.com",
            "headers": {"Content-Type": "application/json"},
            "auth": "test_token",
        }

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, HttpConnector)
        self.assertEqual(connector.base_url, "http://test.com")
        self.assertEqual(
            connector.headers,
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"},
        )
        self.assertIsInstance(connector._auth, BearerAuth)
        self.assertEqual(connector._auth.token.get_secret_value(), "test_token")

    def test_create_http_connector_with_options(self):
        """Test creating an HTTP connector with options."""
        server_config = {
            "url": "http://test.com",
            "headers": {"Content-Type": "application/json"},
            "auth": "test_token",
        }
        options: SandboxOptions = {
            "api_key": "test_key",
            "sandbox_template_id": "test_template",
        }

        connector = create_connector_from_config(server_config, sandbox=True, sandbox_options=options)

        self.assertIsInstance(connector, HttpConnector)
        self.assertEqual(connector.base_url, "http://test.com")
        self.assertEqual(
            connector.headers,
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"},
        )
        self.assertIsInstance(connector._auth, BearerAuth)
        self.assertEqual(connector._auth.token.get_secret_value(), "test_token")

    def test_create_http_connector_minimal(self):
        """Test creating an HTTP connector with minimal config."""
        server_config = {"url": "http://test.com"}

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, HttpConnector)
        self.assertEqual(connector.base_url, "http://test.com")
        self.assertEqual(connector.headers, {})
        self.assertIsNone(connector._auth)

    def test_create_websocket_connector(self):
        """Test creating a WebSocket connector from config."""
        server_config = {
            "ws_url": "ws://test.com",
            "headers": {"Content-Type": "application/json"},
            "auth": "test_token",
        }

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, WebSocketConnector)
        self.assertEqual(connector.url, "ws://test.com")
        self.assertEqual(
            connector.headers,
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"},
        )

    def test_create_websocket_connector_with_options(self):
        """Test creating a WebSocket connector with options."""
        server_config = {
            "ws_url": "ws://test.com",
            "headers": {"Content-Type": "application/json"},
            "auth": "test_token",
        }
        options: SandboxOptions = {
            "api_key": "test_key",
            "sandbox_template_id": "test_template",
        }

        connector = create_connector_from_config(server_config, sandbox=True, sandbox_options=options)

        self.assertIsInstance(connector, WebSocketConnector)
        self.assertEqual(connector.url, "ws://test.com")
        self.assertEqual(
            connector.headers,
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"},
        )

    def test_create_websocket_connector_minimal(self):
        """Test creating a WebSocket connector with minimal config."""
        server_config = {"ws_url": "ws://test.com"}

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, WebSocketConnector)
        self.assertEqual(connector.url, "ws://test.com")
        self.assertEqual(connector.headers, {})

    def test_create_stdio_connector(self):
        """Test creating a stdio connector from config."""
        server_config = {
            "command": "python",
            "args": ["-m", "mcp_server"],
            "env": {"DEBUG": "1"},
        }

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, StdioConnector)
        self.assertEqual(connector.command, "python")
        self.assertEqual(connector.args, ["-m", "mcp_server"])
        self.assertEqual(connector.env, {"DEBUG": "1"})

    def test_create_stdio_connector_with_options(self):
        """Test creating a stdio connector with options."""
        server_config = {
            "command": "python",
            "args": ["-m", "mcp_server"],
            "env": {"DEBUG": "1"},
        }

        connector = create_connector_from_config(
            server_config,
            sandbox=False,
            sandbox_options=SandboxOptions(
                api_key="test_key",
                sandbox_template_id="test_template",
            ),
        )

        self.assertIsInstance(connector, StdioConnector)
        self.assertEqual(connector.command, "python")
        self.assertEqual(connector.args, ["-m", "mcp_server"])
        self.assertEqual(connector.env, {"DEBUG": "1"})

    def test_create_sandboxed_stdio_connector(self):
        """Test creating a sandboxed stdio connector."""
        server_config = {
            "command": "python",
            "args": ["-m", "mcp_server"],
            "env": {"DEBUG": "1"},
        }
        options: SandboxOptions = {
            "api_key": "test_key",
            "sandbox_template_id": "test_template",
        }

        # Use patch to avoid the actual E2B SDK import check
        with patch("mcp_use.connectors.sandbox.AsyncSandbox", create=True):
            connector = create_connector_from_config(server_config, sandbox=True, sandbox_options=options)

            self.assertIsInstance(connector, SandboxConnector)
            self.assertEqual(connector.user_command, "python")
            self.assertEqual(connector.user_args, ["-m", "mcp_server"])
            self.assertEqual(connector.user_env, {"DEBUG": "1"})
            self.assertEqual(connector.api_key, "test_key")
            self.assertEqual(connector.sandbox_template_id, "test_template")

    def test_create_stdio_connector_minimal(self):
        """Test creating a stdio connector with minimal config."""
        server_config = {"command": "python", "args": ["-m", "mcp_server"]}

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, StdioConnector)
        self.assertEqual(connector.command, "python")
        self.assertEqual(connector.args, ["-m", "mcp_server"])
        self.assertIsNone(connector.env)

    def test_create_connector_invalid_config(self):
        """Test creating a connector with invalid config raises ValueError."""
        server_config = {"invalid": "config"}

        with self.assertRaises(ValueError) as context:
            create_connector_from_config(server_config)

        self.assertEqual(str(context.exception), "Cannot determine connector type from config")
