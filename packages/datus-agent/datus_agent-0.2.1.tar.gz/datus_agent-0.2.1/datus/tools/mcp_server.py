# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

import os
import threading
from pathlib import Path

from agents.mcp import MCPServerStdio, MCPServerStdioParams, create_static_tool_filter

from datus.configuration.agent_config import DbConfig
from datus.utils.constants import DBType
from datus.utils.env import load_metricflow_env_settings
from datus.utils.loggings import get_logger

logger = get_logger(__name__)


class SilentMCPServerStdio(MCPServerStdio):
    """MCP server wrapper that redirects stderr to suppress logs.

    Uses shell wrapping with explicit environment variable passing to ensure:
    1. stderr is redirected to /dev/null (suppresses all console output)
    2. Environment variables are correctly passed to the subprocess
    """

    def __init__(self, params: MCPServerStdioParams, **kwargs):
        # Get command, args, and env
        if hasattr(params, "command"):
            original_command = params.command
            original_args = params.args or []
            env = params.env or {}
        else:
            original_command = params["command"]
            original_args = params["args"] or []
            env = params.get("env") or {}

        import shlex
        import sys

        if sys.platform == "win32":
            # Windows: Use cmd with stderr redirection
            redirect_cmd = "cmd"
            env_sets = " && ".join(f"set {k}={v}" for k, v in env.items())
            args_str = " ".join(original_args)
            redirect_args = ["/c", f"{env_sets} && {original_command} {args_str} 2>nul"]
        else:
            # Unix/Linux/macOS: Use sh with explicit env exports
            redirect_cmd = "sh"

            # Build environment variable exports
            env_exports = " ".join(f"{k}={shlex.quote(str(v))}" for k, v in env.items())

            # Quote command and args properly
            cmd_str = shlex.quote(original_command)
            args_str = " ".join(shlex.quote(str(arg)) for arg in original_args)

            # Combine: export vars, run command, redirect stderr
            full_cmd = f"{env_exports} {cmd_str} {args_str} 2>/dev/null"
            redirect_args = ["-c", full_cmd]

        # Update params
        if hasattr(params, "command"):
            params.command = redirect_cmd
            params.args = redirect_args
            params.env = None  # Already included in the shell command
        else:
            params["command"] = redirect_cmd
            params["args"] = redirect_args
            params["env"] = None

        super().__init__(params, **kwargs)


def find_mcp_directory(mcp_name: str) -> str:
    """Find the MCP directory, whether in development or installed package"""

    relative_path = f"mcp/{mcp_name}"
    if Path(relative_path).exists():
        logger.info(f"Found MCP directory in development: {Path(relative_path).resolve()}")
        return relative_path

    import sys

    for path in sys.path:
        if "site-packages" in path:
            datus_mcp_path = Path(path) / "mcp" / mcp_name
            if datus_mcp_path.exists():
                logger.info(f"Found MCP directory via sys.path: {datus_mcp_path}")
                return str(datus_mcp_path)

    raise FileNotFoundError(
        f"MCP directory '{mcp_name}' not found in development mcp directory or installed datus-mcp package"
    )


def check_filesystem_mcp_installed() -> bool:
    """Check if @modelcontextprotocol/server-filesystem is installed and available."""
    import shutil

    # Simply check if the binary is available in PATH
    # If npm package is correctly installed, the binary should be available
    if shutil.which("mcp-server-filesystem"):
        logger.info("Found mcp-server-filesystem executable in PATH")
        return True

    logger.debug("mcp-server-filesystem executable not found in PATH")
    return False


class MCPServer:
    _metricflow_mcp_server = None
    _filesystem_mcp_server = None
    _lock = threading.Lock()

    @classmethod
    def _extract_db_path_from_uri(cls, uri: str, db_type: str) -> str:
        """Extract database path from URI and convert to absolute path."""
        # Remove protocol prefix if present
        if uri.startswith(f"{db_type.lower()}:///"):
            db_path = uri.replace(f"{db_type.lower()}:///", "")
        else:
            db_path = uri

        # Expand user home directory (handle ~ paths)
        db_path = str(Path(db_path).expanduser())

        # Convert relative path to absolute path, if not already absolute
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)

        return db_path

    @classmethod
    def get_metricflow_mcp_server(cls, database_name: str, db_config: DbConfig):
        if cls._metricflow_mcp_server is None:
            with cls._lock:
                if cls._metricflow_mcp_server is None:
                    directory = os.getenv("METRICFLOW_MCP_DIR")
                    if not directory:
                        try:
                            directory = find_mcp_directory("mcp-metricflow-server")
                        except FileNotFoundError as e:
                            logger.error(f"Could not find MetricFlow MCP directory: {e}")
                            return None
                    logger.info(f"Using MetricFlow MCP server with directory: {directory}")

                    # Try to load env_settings from ~/.datus/metricflow/env_settings.yml first
                    env_settings = load_metricflow_env_settings()

                    # Fallback to existing logic if config file doesn't exist or failed to load
                    if not env_settings:
                        env_settings = {
                            "MF_MODEL_PATH": os.getenv("MF_MODEL_PATH", "/tmp"),
                            "MF_PATH": os.getenv("MF_PATH", ""),
                        }
                        if db_config.type in (DBType.DUCKDB, DBType.SQLITE):
                            env_settings["MF_DWH_SCHEMA"] = db_config.schema or "default_schema"
                            env_settings["MF_DWH_DIALECT"] = db_config.type
                            # Handle sqlite:// URI format properly
                            if db_config.uri.startswith(f"{db_config.type}://"):
                                # Handle both sqlite:///path (3 slashes) and sqlite:////path (4 slashes)
                                uri_prefix = f"{db_config.type}://"
                                file_path = db_config.uri[len(uri_prefix) :]
                                # For 4-slash format (sqlite:////path), remove one leading slash
                                if file_path.startswith("//"):
                                    file_path = file_path[1:]
                                # file_path should now be /absolute/path for both 3 and 4 slash formats
                                env_settings["MF_DWH_DB"] = str(Path(file_path).expanduser())
                            else:
                                env_settings["MF_DWH_DB"] = str(Path(db_config.uri).expanduser())
                        elif db_config.type == DBType.STARROCKS:
                            env_settings["MF_DWH_SCHEMA"] = db_config.schema
                            env_settings["MF_DWH_DIALECT"] = DBType.MYSQL.value
                            env_settings["MF_DWH_HOST"] = db_config.host
                            env_settings["MF_DWH_PORT"] = db_config.port
                            env_settings["MF_DWH_USER"] = db_config.username
                            env_settings["MF_DWH_PASSWORD"] = db_config.password
                            env_settings["MF_DWH_DB"] = database_name

                    mcp_server_params = MCPServerStdioParams(
                        command="uv",
                        args=[
                            "--directory",
                            directory,
                            "run",
                            "mcp-metricflow-server",
                        ],
                        env=env_settings,
                    )
                    cls._metricflow_mcp_server = SilentMCPServerStdio(
                        params=mcp_server_params, client_session_timeout_seconds=20
                    )
        return cls._metricflow_mcp_server

    @classmethod
    def get_filesystem_mcp_server(cls, path=None):
        if cls._filesystem_mcp_server is None:
            with cls._lock:
                if cls._filesystem_mcp_server is None:
                    filesystem_mcp_directory = path or os.getenv("FILESYSTEM_MCP_DIRECTORY", "/tmp")

                    # Convert to absolute path
                    if not os.path.isabs(filesystem_mcp_directory):
                        filesystem_mcp_directory = os.path.abspath(filesystem_mcp_directory)

                    # Check if directory exists
                    if not os.path.exists(filesystem_mcp_directory):
                        logger.error(f"Filesystem MCP directory does not exist: {filesystem_mcp_directory}")
                        return None

                    logger.info(f"Creating filesystem MCP server for directory: {filesystem_mcp_directory}")

                    # Check if filesystem MCP server is already installed
                    if check_filesystem_mcp_installed():
                        # Option 1: Use direct executable if available (fastest)
                        logger.info("Using pre-installed mcp-server-filesystem executable")
                        mcp_server_params = MCPServerStdioParams(
                            command="mcp-server-filesystem",
                            args=[filesystem_mcp_directory],
                            env={
                                "NODE_OPTIONS": "--no-warnings",
                                "MCP_SERVER_QUIET": "1",
                            },
                        )
                    else:
                        # Option 2: Use npx to download and run if not installed
                        logger.info("Using npx to download and run @modelcontextprotocol/server-filesystem")
                        mcp_server_params = MCPServerStdioParams(
                            command="npx",
                            args=[
                                "--silent",
                                "-y",
                                "@modelcontextprotocol/server-filesystem",
                                filesystem_mcp_directory,
                            ],
                            env={
                                "NODE_OPTIONS": "--no-warnings",
                                "NPM_CONFIG_LOGLEVEL": "silent",
                                "NPM_CONFIG_PROGRESS": "false",
                                "NPX_SILENT": "true",
                                "SUPPRESS_NO_CONFIG_WARNING": "1",
                                "MCP_SERVER_QUIET": "1",  # Custom flag for MCP servers
                            },
                        )

                    # Create tool filter for filesystem operations
                    tool_filter = create_static_tool_filter(
                        allowed_tool_names=[
                            "read_text_file",
                            "read_multiple_files",
                            "write_file",
                            "edit_file",
                            "search_files",
                            "list_directory",
                            "list_allowed_directories",
                        ]
                    )

                    cls._filesystem_mcp_server = SilentMCPServerStdio(
                        params=mcp_server_params, client_session_timeout_seconds=30, tool_filter=tool_filter
                    )
        return cls._filesystem_mcp_server
