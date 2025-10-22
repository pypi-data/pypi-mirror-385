"""Base classes and utilities for building custom APIs compatible with JAAI Hub."""

import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from jaai_hub.streaming_message import Attachment


class Message(BaseModel):
    role: str
    content: str
    attachments: Optional[List[Attachment]] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


def health_check_endpoint(service_name: str = "custom-api"):
    """Create a standard health check response"""
    return {"status": "healthy", "service": service_name}


class CustomLogsHandler:
    """A custom Logs handler class to handle JSON data."""

    def __init__(self):
        self.logs = []

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON data and log it."""
        self.logs.append(data)


def create_chat_completions_endpoint(stream_func):
    """
    Create a standard /chat/completions endpoint that handles both streaming and non-streaming requests.

    Args:
        stream_func: Async function that takes a ChatCompletionRequest and yields streaming responses

    Returns:
        FastAPI endpoint function
    """
    from fastapi.responses import StreamingResponse
    from jaai_hub.streaming_message import StreamingMessage

    async def chat_completion(request: ChatCompletionRequest):
        """Chat completion endpoint with streaming support"""
        if request.stream:
            return StreamingResponse(StreamingMessage(stream_func(request)), media_type="text/event-stream")
        else:
            # For non-streaming, collect all chunks and return as single response
            content_parts = []
            async for chunk in stream_func(request):
                if isinstance(chunk, str):
                    content_parts.append(chunk)

            response_content = "".join(content_parts) if content_parts else "No response generated"

            return ChatCompletionResponse(
                id=f"chat-{int(time.time())}",
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": response_content},
                        "finish_reason": "stop",
                    }
                ],
                usage={
                    "prompt_tokens": len(str(request.messages)),
                    "completion_tokens": len(response_content),
                    "total_tokens": len(str(request.messages)) + len(response_content),
                },
            )

    return chat_completion
