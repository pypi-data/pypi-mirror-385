"""
Shadai Client - Official Python SDK for Shadai AI
==================================================

Beautiful, Pythonic client for interacting with Shadai AI services.

Quick Start:
    >>> from shadai import Shadai, tool
    >>>
    >>> # Ingest documents from a folder
    >>> async with Shadai(name="my-session") as shadai:
    ...     async for chunk in shadai.ingest(folder_path="/path/to/docs"):
    ...         print(chunk, end="", flush=True)
    >>>
    >>> # Query knowledge base with session management
    >>> async with Shadai(name="my-session") as shadai:
    ...     async for chunk in shadai.query(query="What is machine learning?"):
    ...         print(chunk, end="", flush=True)
    >>>
    >>> # Create temporal session (auto-deleted)
    >>> async with Shadai(temporal=True) as shadai:
    ...     async for chunk in shadai.query(query="What is AI?"):
    ...         print(chunk, end="", flush=True)
    >>>
    >>> # Define tools with automatic schema inference
    >>> @tool
    ... def search_database(query: str, limit: int = 10) -> str:
    ...     '''Search the database for records.
    ...
    ...     Args:
    ...         query: Search query string
    ...         limit: Maximum number of results to return
    ...     '''
    ...     return "results"
    >>>
    >>> # Use intelligent agent (plan → execute → synthesize)
    >>> async with Shadai(name="my-session") as shadai:
    ...     async for chunk in shadai.agent(
    ...         prompt="Find top 5 users",
    ...         tools=[search_database]
    ...     ):
    ...         print(chunk, end="", flush=True)

Documentation: https://docs.shadai.com
GitHub: https://github.com/shadai/shadai-client
"""

from .__version__ import __author__, __description__, __version__
from .client import ShadaiClient
from .error_handler import install_exception_handler
from .exceptions import (
    # Connection & Auth
    AuthenticationError,
    # Authorization & Limits
    AuthorizationError,
    ChunkIngestionError,
    ConfigurationError,
    ConnectionError,
    # External Services
    ExternalServiceError,
    FileNotFoundError,
    FileParsingError,
    FileSizeLimitExceededError,
    InvalidAPIKeyError,
    InvalidFileTypeError,
    InvalidParameterError,
    KnowledgePointsLimitExceededError,
    LLMProviderError,
    MissingAccountSetupError,
    MissingParameterError,
    PlanLimitExceededError,
    # Processing
    ProcessingError,
    # Resources
    ResourceError,
    ServerError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
    # Base
    ShadaiError,
    # System
    SystemError,
    # Validation
    ValidationError,
)
from .models import (
    AgentTool,
    EmbeddingModel,
    LLMModel,
    Tool,
    ToolDefinition,
    ToolRegistry,
    tool,
)
from .tools import (
    EngineTool,
    IngestTool,
    QueryTool,
    Shadai,
    SummarizeTool,
    WebSearchTool,
)

__all__ = [
    # Main client
    "Shadai",
    # Low-level client
    "ShadaiClient",
    # Tool classes
    "QueryTool",
    "SummarizeTool",
    "WebSearchTool",
    "EngineTool",
    "IngestTool",
    "AgentTool",
    # Tool utilities
    "tool",
    # Models
    "Tool",
    "ToolDefinition",
    "ToolRegistry",
    "LLMModel",
    "EmbeddingModel",
    # Exceptions - Base
    "ShadaiError",
    # Exceptions - Connection & Auth
    "AuthenticationError",
    "ConnectionError",
    "InvalidAPIKeyError",
    "MissingAccountSetupError",
    # Exceptions - Resources
    "ResourceError",
    "SessionNotFoundError",
    "FileNotFoundError",
    "SessionAlreadyExistsError",
    # Exceptions - Validation
    "ValidationError",
    "InvalidFileTypeError",
    "InvalidParameterError",
    "MissingParameterError",
    # Exceptions - Authorization & Limits
    "AuthorizationError",
    "PlanLimitExceededError",
    "KnowledgePointsLimitExceededError",
    "FileSizeLimitExceededError",
    # Exceptions - External Services
    "ExternalServiceError",
    "LLMProviderError",
    # Exceptions - Processing
    "ProcessingError",
    "FileParsingError",
    "ChunkIngestionError",
    # Exceptions - System
    "SystemError",
    "ConfigurationError",
    "ServerError",
    # Version info
    "__version__",
    "__author__",
    "__description__",
]

# Install custom exception handler for clean error messages
install_exception_handler()
