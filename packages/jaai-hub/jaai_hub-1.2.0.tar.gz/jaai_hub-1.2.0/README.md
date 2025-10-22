# JAAI Hub

A Python package containing utilities and components for building streaming AI applications with OpenAI-compatible APIs. This package provides comprehensive streaming message handling, custom API development tools, and seamless integration with FastAPI applications.

## Installation

```bash
pip install jaai-hub
```

## Core Features

### 🔄 Streaming Message System
- **StreamingMessage**: Main class for handling streaming data with both sync and async generators
- **Event-based streaming**: Server-Sent Events (SSE) support with start, data, done, error events
- **Multi-modal support**: Text, images, attachments, sources, and status updates
- **Real-time processing**: Stream and process data as it's generated

### 🛠️ Custom API Framework
- **OpenAI-compatible APIs**: Build APIs that work with OpenAI client libraries
- **FastAPI integration**: Seamless integration with FastAPI applications
- **Health checks**: Standard health check endpoints
- **Error handling**: Robust error handling and status reporting

### 📊 Rich Data Types
- **Status**: Progress updates and completion states
- **Source**: Source information and references
- **Attachment**: File attachments with metadata
- **GeneratedImage**: AI-generated images with metadata
- **Plan/Step**: Multi-step planning and task execution
- **HiddenContext**: Internal context that doesn't appear in UI

## Quick Start

### Basic Streaming Message

```python
from jaai_hub.streaming_message import StreamingMessage, Status, Source

# Create a streaming message
def my_generator():
    yield "Hello"
    yield Status(text="Processing...")
    yield Source(title="Example Source", url="https://example.com")
    yield "World"

stream = StreamingMessage(my_generator())
for chunk in stream:
    print(chunk)
```

### Building a Custom API

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from jaai_hub.custom_api import (
    ChatCompletionRequest,
    health_check_endpoint,
    create_chat_completions_endpoint,
)
from jaai_hub.streaming_message import StreamingMessage, Status

# Create your API router
router = APIRouter(tags=["your-service"])

@router.get("/health")
async def health():
    return health_check_endpoint("your-service-name")

# Define your streaming function
async def your_stream_function(request: ChatCompletionRequest):
    yield Status(type="basic", text="Processing request...")

    # Your custom logic here
    last_message = request.messages[-1].content if request.messages else ""
    response = f"Echo: {last_message}"

    yield response
    yield Status(type="complete", text="Done!")

# Create the chat completions endpoint
chat_completion = create_chat_completions_endpoint(your_stream_function)
router.post("/chat/completions")(chat_completion)
```

## Advanced Examples

### Image Generation API

```python
from jaai_hub.streaming_message import GeneratedImage, Status

async def image_generation_stream(request: ChatCompletionRequest):
    yield Status(type="basic", text="🖼️ Creating image...")

    # Your image generation logic
    prompt = request.messages[-1].content
    image_b64 = await create_image(prompt)

    yield GeneratedImage(
        url=f"data:image/png;base64,{image_b64}",
        prompt=prompt,
        width=1024,
        height=1024,
    )

    yield Status(type="complete", text="✅ Image created!")
```

### Research API with Sources

```python
from jaai_hub.streaming_message import Source, Status

async def research_stream(request: ChatCompletionRequest):
    yield Status(type="basic", text="🔍 Starting research...")

    query = request.messages[-1].content
    sources = await perform_research(query)

    for source_data in sources:
        yield Source(
            title=source_data["title"],
            url=source_data["url"],
            raw_content=source_data["content"]
        )

    yield "Based on the research findings..."
    yield Status(type="complete", text="🎉 Research complete!")
```

### Multi-step Planning

```python
from jaai_hub.streaming_message import Plan, Step, Status

async def planning_stream(request: ChatCompletionRequest):
    yield Status(type="basic", text="📋 Creating plan...")

    task = request.messages[-1].content
    steps = await create_plan(task)

    plan = Plan(steps=[
        Step(title=step["title"], task=step["task"], fulfilled=False)
        for step in steps
    ])

    yield plan
    yield Status(type="complete", text="✅ Plan ready!")
```

## API Reference

### StreamingMessage Class

```python
StreamingMessage(source_gen: Union[Generator, AsyncGenerator])
```

- **source_gen**: Generator or async generator yielding StreamableType objects
- **Methods**:
  - `get_message()`: Get current accumulated message
  - `is_done()`: Check if streaming is complete
  - `__iter__()` / `__aiter__()`: Iterate over streaming chunks

### Data Models

#### Status
```python
Status(
    type: Literal["basic", "complete", "error"] = "basic",
    text: str,
    replace: bool = False
)
```

#### Source
```python
Source(
    title: str,
    url: Optional[str] = None,
    raw_content: Optional[str] = None,
    image_urls: Optional[List[ImageUrl]] = None
)
```

#### Attachment
```python
Attachment(
    type: str,
    name: str,
    url: Optional[str] = None,
    size: Optional[int] = None,
    mimeType: Optional[str] = None,
    base64: Optional[str] = None,
    extractedText: Optional[str] = None
)
```

#### GeneratedImage
```python
GeneratedImage(
    url: str,
    prompt: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
)
```

### Custom API Utilities

#### ChatCompletionRequest
```python
ChatCompletionRequest(
    model: str,
    messages: List[Message],
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = None,
    stream: Optional[bool] = False
)
```

#### Utility Functions

- `health_check_endpoint(service_name)`: Standard health check response
- `create_chat_completions_endpoint(stream_func)`: Create OpenAI-compatible endpoint
- `create_data_chunk(content, model, content_type)`: Create SSE data chunks

## Integration Features

### OpenAI Compatibility
Works seamlessly with OpenAI client libraries:

```python
import openai

client = openai.OpenAI(base_url="http://your-api-url", api_key="dummy")
response = client.chat.completions.create(
    model="your-model",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)
```

### FastAPI Integration
Automatic integration with FastAPI features:
- Request/response validation
- OpenAPI documentation
- Error handling
- Middleware support

## Best Practices

1. **Always implement health checks** using `health_check_endpoint()`
2. **Use streaming responses** for better user experience
3. **Yield status updates** to keep users informed of progress
4. **Handle errors gracefully** with appropriate status messages
5. **Follow OpenAI API conventions** for maximum compatibility
6. **Use appropriate data types** (Source, Attachment, etc.) for rich content
7. **Implement proper error handling** with error status types

## Requirements

- Python ≥ 3.11
- pydantic ≥ 2.4.0
- loguru ≥ 0.7.0
- requests ≥ 2.25.0
- langchain-community ≥ 0.0.10
- langchain-core ≥ 1.0
- langchain-openai ≥ 0.0.1
- markdownify ≥ 0.11.0

## License

Proprietary - JAAI Team