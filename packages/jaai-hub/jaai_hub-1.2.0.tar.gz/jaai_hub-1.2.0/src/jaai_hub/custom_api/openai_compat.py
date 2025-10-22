"""OpenAI API compatibility utilities for streaming responses."""

import asyncio
import json
import random
import time
from typing import Any, Dict, List

from pydantic import BaseModel

from .base import ChatCompletionRequest


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response model."""

    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


def create_data_chunk(content: str, model: str = "gpt-3.5-turbo", content_type: str = "content") -> str:
    """
    Transform content into a formatted SSE data chunk for streaming responses.

    Args:
        content (str): The content to be included in the chunk
        model (str, optional): The model identifier. Defaults to "gpt-3.5-turbo"
        content_type (str, optional): The type of content in the delta field. Defaults to "content"

    Returns:
        str: SSE formatted data chunk string
    """
    chunk = {
        "id": f"chunk-{random.randint(1000, 9999)}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {content_type: content}}],
    }
    return f"data: {json.dumps(chunk)}\n\n"


async def generate_stream_response(request: ChatCompletionRequest):
    """Generate streaming response in chunks for testing purposes.

    Args:
        request: The chat completion request

    Yields:
        str: SSE formatted data chunks
    """
    # Get the last message content
    last_message = request.messages[-1].content if request.messages else ""

    response = last_message

    # Split response into words for streaming
    words = response.split(" ")

    # Stream each word with a small delay
    for i, word in enumerate(words):
        # Add space before words (except first word)
        if i > 0:
            word = " " + word

        yield create_data_chunk(word, request.model)
        await asyncio.sleep(0.01)  # Add small delay between words

    # Send final [DONE] message
    yield "data: [DONE]\n\n"
