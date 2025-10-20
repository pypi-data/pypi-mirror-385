"""
Crucible SDK - A high-performance OpenAI logging and monitoring library.

This package provides seamless integration with OpenAI's API while automatically
logging requests and responses to Crucible for monitoring, analytics, and optimization.

Example usage:
    from crucible import CrucibleOpenAI, CrucibleConfig
    
    # Basic usage
    client = CrucibleOpenAI()
    
    # With custom configuration
    config = CrucibleConfig(api_key="your-key", batch_size=20)
    client = CrucibleOpenAI(crucible_config=config)
    
    # Make API calls (automatically logged)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}],
        crucible={"tags": {"prompt_id": "greeting"}}
    )
"""

from .client import CrucibleOpenAI
from .async_client import CrucibleAsyncOpenAI
from .config import CrucibleConfig
from .errors import CrucibleError, LoggingError, ConfigurationError, APIError, NetworkError
from .types import LogRequest, LogResponse, UpdateTagsRequest, UpdateTagsResponse, Filter
from .logger import CrucibleLogger
from .streaming import StreamingMerger
from .langchain_llm import ChatOpenAI

# Version
__version__ = "0.1.0"

# Main exports
__all__ = [
    "CrucibleOpenAI",
    "CrucibleAsyncOpenAI", 
    "CrucibleConfig",
    "CrucibleLogger",
    "StreamingMerger",
    "ChatOpenAI",
    "CrucibleError",
    "LoggingError",
    "ConfigurationError",
    "APIError",
    "NetworkError",
    "LogRequest",
    "LogResponse",
    "UpdateTagsRequest",
    "UpdateTagsResponse",
    "Filter",
]

# Convenience imports for common usage
from openai import OpenAI as OriginalOpenAI
from openai import AsyncOpenAI as OriginalAsyncOpenAI

# Re-export OpenAI types for convenience
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage

__all__.extend([
    "OriginalOpenAI",
    "OriginalAsyncOpenAI", 
    "ChatCompletion",
    "ChatCompletionChunk",
    "Choice",
    "ChatCompletionMessage",
])
