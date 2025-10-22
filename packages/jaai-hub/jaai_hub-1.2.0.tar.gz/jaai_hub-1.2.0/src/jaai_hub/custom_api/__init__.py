"""JAAI Hub API utilities for building custom APIs."""

from .base import (
    Message,
    ChatCompletionRequest,
    ChatCompletionResponse,
    health_check_endpoint,
    CustomLogsHandler,
    create_chat_completions_endpoint,
)
from .openai_compat import create_data_chunk, generate_stream_response

__all__ = [
    "Message",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "health_check_endpoint",
    "CustomLogsHandler",
    "create_chat_completions_endpoint",
    "create_data_chunk",
    "generate_stream_response",
    "generate_mock_response",
]
