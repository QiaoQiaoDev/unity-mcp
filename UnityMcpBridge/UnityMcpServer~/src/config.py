"""
Configuration settings for the MCP for Unity Server.
This file contains all configurable parameters for the server.
"""

from dataclasses import dataclass
import logging
import os

_logger = logging.getLogger("mcp-for-unity-server")


def _env(name: str, default, cast):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return cast(value)
    except Exception:
        _logger.warning("Invalid value for %s: %s", name, value)
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

@dataclass
class ServerConfig:
    """Main configuration class for the MCP server."""
    
    # Network settings
    unity_host: str = "localhost"
    unity_port: int = 6400
    mcp_port: int = 6500
    
    # Connection settings
    connection_timeout: float = 1.0  # short initial timeout; retries use shorter timeouts
    buffer_size: int = 16 * 1024 * 1024  # 16MB buffer
    # Framed receive behavior
    framed_receive_timeout: float = 2.0  # max seconds to wait while consuming heartbeats only
    max_heartbeat_frames: int = 16       # cap heartbeat frames consumed before giving up
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server settings
    max_retries: int = 10
    retry_delay: float = 0.25
    # Backoff hint returned to clients when Unity is reloading (milliseconds)
    reload_retry_ms: int = 250
    # Number of polite retries when Unity reports reloading
    # 40 × 250ms ≈ 10s default window
    reload_max_retries: int = 40
    
    # Telemetry settings
    telemetry_enabled: bool = True
    # Align with telemetry.py default Cloud Run endpoint
    telemetry_endpoint: str = "https://api-prod.coplay.dev/telemetry/events"

    # Protocol metadata
    protocol_version: str = "1"

    def __post_init__(self) -> None:
        self.unity_host = _env("UNITY_MCP_HOST", self.unity_host, str)
        self.unity_port = _env("UNITY_MCP_PORT", self.unity_port, int)
        self.mcp_port = _env("UNITY_MCP_SERVER_PORT", self.mcp_port, int)
        self.connection_timeout = _env("UNITY_MCP_CONNECTION_TIMEOUT", self.connection_timeout, float)
        self.buffer_size = _env("UNITY_MCP_BUFFER_SIZE", self.buffer_size, int)
        self.framed_receive_timeout = _env("UNITY_MCP_FRAMED_RECEIVE_TIMEOUT", self.framed_receive_timeout, float)
        self.max_heartbeat_frames = _env("UNITY_MCP_MAX_HEARTBEAT_FRAMES", self.max_heartbeat_frames, int)
        self.log_level = _env("UNITY_MCP_LOG_LEVEL", self.log_level, str)
        self.log_format = _env("UNITY_MCP_LOG_FORMAT", self.log_format, str)
        self.max_retries = _env("UNITY_MCP_MAX_RETRIES", self.max_retries, int)
        self.retry_delay = _env("UNITY_MCP_RETRY_DELAY", self.retry_delay, float)
        self.reload_retry_ms = _env("UNITY_MCP_RELOAD_RETRY_MS", self.reload_retry_ms, int)
        self.reload_max_retries = _env("UNITY_MCP_RELOAD_MAX_RETRIES", self.reload_max_retries, int)
        self.telemetry_enabled = _env_bool("UNITY_MCP_TELEMETRY_ENABLED", self.telemetry_enabled)
        self.telemetry_endpoint = _env("UNITY_MCP_TELEMETRY_ENDPOINT", self.telemetry_endpoint, str)
        self.protocol_version = _env("UNITY_MCP_PROTOCOL_VERSION", self.protocol_version, str)


# Create a global config instance
config = ServerConfig()
