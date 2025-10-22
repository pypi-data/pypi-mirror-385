import inspect
from typing import AsyncGenerator, Generator, List, Literal, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, field_validator
import asyncio
import time
import threading
import queue
from datetime import datetime, timezone


def forward_with_heartbeat_sync(source: Generator, heartbeat_interval_sec: int | None = 10) -> Generator:
    """Sync version of forward_with_heartbeat using thread-based queue approach"""
    if heartbeat_interval_sec is None:
        for x in source:
            yield x
        return

    # Create a queue to communicate between threads
    item_queue = queue.Queue()
    exception_holder = [None]  # Use list to allow modification from thread

    def consumer_thread():
        """Thread function that consumes the source generator and puts items in queue"""
        try:
            for item in source:
                item_queue.put(("item", item))
            item_queue.put(("done", None))
        except Exception as e:
            exception_holder[0] = e
            item_queue.put(("error", e))

    # Start the consumer thread
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()

    last_heartbeat = time.time()
    yield HeartBeat()

    while True:
        time_until_heartbeat = last_heartbeat + heartbeat_interval_sec - time.time()

        # Check if we need to send a heartbeat
        if time_until_heartbeat <= 0:
            last_heartbeat = time.time()
            yield HeartBeat()
            time_until_heartbeat = heartbeat_interval_sec

        try:
            # Try to get an item from queue with timeout
            msg_type, item = item_queue.get(timeout=max(0.1, time_until_heartbeat))

            if msg_type == "done":
                break
            elif msg_type == "error":
                raise item
            elif msg_type == "item":
                # Forward heartbeats and update last_heartbeat time
                if isinstance(item, HeartBeat):
                    last_heartbeat = time.time()
                yield item

        except queue.Empty:
            # Timeout occurred, continue to check for heartbeat
            continue

    # Wait for thread to finish
    thread.join(timeout=1.0)


async def forward_with_heartbeat_async(
    source: AsyncGenerator, heartbeat_interval_sec: int | None = 10
) -> AsyncGenerator:
    """Async version of forward_with_heartbeat"""
    if heartbeat_interval_sec is None:
        async for x in source:
            yield x
        return

    iter = source.__aiter__()

    last_heartbeat = time.time()
    yield HeartBeat()
    next_item_task = asyncio.create_task(iter.__anext__())
    while True:
        time_until_heartbeat = last_heartbeat + heartbeat_interval_sec - time.time()
        if time_until_heartbeat <= 0:
            last_heartbeat = time.time()
            yield HeartBeat()

        try:
            item = await asyncio.wait_for(asyncio.shield(next_item_task), time_until_heartbeat)
            # Forward heartbeats
            if isinstance(item, HeartBeat):
                last_heartbeat = time.time()

            yield item
            next_item_task = asyncio.create_task(iter.__anext__())
        except asyncio.TimeoutError:
            pass
        except StopAsyncIteration:
            break


def forward_with_heartbeat(
    source: Union[Generator, AsyncGenerator], heartbeat_interval_sec: int | None = 10
) -> Union[Generator, AsyncGenerator]:
    """Forward items from source generator with heartbeats. Handles both sync and async generators."""
    if inspect.isasyncgen(source):
        return forward_with_heartbeat_async(source, heartbeat_interval_sec)
    else:
        return forward_with_heartbeat_sync(source, heartbeat_interval_sec)


class Step(BaseModel):
    title: str = Field(
        description="A Short title of the step, specific and short like 'Einloggen bei bahn.de' or 'Bahnverbindungen suchen' in german."
    )
    task: str = Field(
        description="A detailed description of the task that the user wants to accomplish. It will be passed to the agents. You do not want them to ask questions about the task, therefore it should be a detailed description of the task containg all needed information to accomplish the task."
    )
    fulfilled: bool = Field(description="Whether the step has been completed")


class HeartBeat(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Plan(BaseModel):
    steps: List[Step] = []


class ImageUrl(BaseModel):
    url: str
    score: float


class Source(BaseModel):
    url: Optional[str] = None
    raw_content: Optional[str] = None
    image_urls: Optional[list[ImageUrl]] = None
    title: str


class Attachment(BaseModel):
    type: str
    name: str
    size: Optional[int] = None
    mimeType: Optional[str] = None
    base64: Optional[str] = None
    extractedText: Optional[str] = None
    reference_id: Optional[str] = None  # UUID identifier for stored file (url field removed v1.6)
    source: Optional[Literal["ai", "user"]] = None  # Source of attachment: AI-generated or user-uploaded
    thumbnail_base64: Optional[str] = None  # Base64 encoded thumbnail for images (~20-30KB)


class GeneratedImage(BaseModel):
    url: str
    prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class Status(BaseModel):
    type: Literal["basic", "complete", "error"] = "basic"
    """
    basic: Adds a new status to the list of statuses (uncompleted)
    completed: Marks the message as completed, no more statuses expected
    error: Marks the message as errored
    """
    text: str
    """
    The text of the status to display
    """
    replace: bool = False
    """
    If true, the last status in the list of statuses will be replaced with the new status. Can be used for progress updates.
    """

    @field_validator("type", mode="before")
    def validate_type(cls, v):
        if v not in ["complete", "error"]:
            return "basic"
        return v


class HiddenContext(BaseModel):
    text: str
    """
    The text of the hidden context to display
    """


class Reasoning(BaseModel):
    text: str
    """
    The text of the reasoning to display
    """


class StreamedMessage(BaseModel):
    text: str
    reasoning: str
    sources: list[Source]
    status: list[Status]
    attachments: list[Attachment]
    generated_images: list[GeneratedImage]
    plan: Optional[Plan] = None
    hidden_contexts: list[HiddenContext] = []


StreamableType = Union[str, Source, Status, Attachment, GeneratedImage, Plan, HiddenContext, Reasoning, HeartBeat]

SourceGenType = Union[Generator[StreamableType, None, None], AsyncGenerator[StreamableType, None]]


# Events
class Event(BaseModel):
    event: Literal["start", "done", "data", "error", "title_generation", "heartbeat"]
    data: Optional[StreamableType] = None
    type: Optional[
        Literal["chunk", "source", "status", "attachment", "generated_image", "plan", "hidden_context", "reasoning"]
    ] = None

    def to_streamable_line(self):
        return f"data: {self.model_dump_json()}\n\n"


def start_event():
    return Event(event="start")


def done_event():
    return Event(event="done")


def title_generation_event(title: str):
    return Event(event="title_generation", data=title)


def error_event(error: str):
    status = Status(type="error", text=error)
    return Event(event="data", data=status, type="status")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class StreamingMessage:

    MAX_CHUNK_SIZE = 1000

    def __init__(self, source_gen: SourceGenType, *, heartbeat_interval_sec: int | None = 5):
        self.source_gen = source_gen
        self._is_done = False
        self._text_content = ""
        self._reasoning_content = ""
        self._sources = []
        self._status = []
        self._attachments = []
        self._generated_images = []
        self._plan = None
        self._hidden_contexts = []
        self._is_async = inspect.isasyncgen(source_gen)

        self.heartbeat_interval_sec = heartbeat_interval_sec

    def get_message(self):
        return StreamedMessage(
            text=self._text_content,
            reasoning=self._reasoning_content,
            sources=self._sources,
            status=self._status,
            attachments=self._attachments,
            generated_images=self._generated_images,
            plan=self._plan,
            hidden_contexts=self._hidden_contexts,
        )

    def is_done(self):
        return self._is_done

    def _process_data(self, data: StreamableType) -> str:
        """Helper method to process each data item from the generator"""
        result = None
        if isinstance(data, Event):
            result = data.to_streamable_line()
        elif isinstance(data, str):
            result = Event(event="data", data=data, type="chunk").to_streamable_line()
            self._text_content += data
        elif isinstance(data, Reasoning):
            result = Event(event="data", data=data, type="reasoning").to_streamable_line()
            self._reasoning_content += data.text
        elif isinstance(data, Source):
            result = Event(event="data", data=data, type="source").to_streamable_line()
            self._sources.append(data)
        elif isinstance(data, Status):
            result = Event(event="data", data=data, type="status").to_streamable_line()
            if data.replace and len(self._status) > 0:
                self._status[-1] = data
            else:
                self._status.append(data)
        elif isinstance(data, Attachment):
            result = Event(event="data", data=data, type="attachment").to_streamable_line()
            self._attachments.append(data)
        elif isinstance(data, GeneratedImage):
            result = Event(event="data", data=data, type="generated_image").to_streamable_line()
            self._generated_images.append(data)
        elif isinstance(data, Plan):
            result = Event(event="data", data=data, type="plan").to_streamable_line()
            self._plan = data
        elif isinstance(data, HiddenContext):
            result = Event(event="data", data=data, type="hidden_context").to_streamable_line()
            self._hidden_contexts.append(data)
        elif isinstance(data, HeartBeat):
            result = Event(event="heartbeat", data=data, type="chunk").to_streamable_line()
        elif isinstance(data, list):
            result = Event(event="data", data=str(data), type="chunk").to_streamable_line()
            self._text_content += data
        elif isinstance(data, dict):
            result = Event(event="data", data=str(data), type="chunk").to_streamable_line()
            self._text_content += data
        else:
            logger.warning(f"Unknown data type: {type(data)}. Ignoring.")
        return result

    def __iter__(self):
        if self._is_async:
            raise TypeError("Cannot use __iter__ with an async generator. Use __aiter__ instead.")

        yield Event(event="start").to_streamable_line()
        try:
            for data in self.source_gen:
                result = self._process_data(data)
                if result:
                    yield from chunks(result, self.MAX_CHUNK_SIZE)
        except Exception as e:
            yield from chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE)
        finally:
            self._is_done = True
            yield Event(event="done").to_streamable_line()

    async def __aiter__(self):
        # If it's a sync generator, we'll convert it to async
        if not self._is_async:
            yield Event(event="start").to_streamable_line()
            try:
                for data in forward_with_heartbeat_sync(self.source_gen, self.heartbeat_interval_sec):
                    result = self._process_data(data)
                    if result:
                        for chunk in chunks(result, self.MAX_CHUNK_SIZE):
                            yield chunk
            except Exception as e:
                for chunk in chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE):
                    yield chunk
            finally:
                self._is_done = True
                yield Event(event="done").to_streamable_line()
            return

        # Handle async generator
        yield Event(event="start").to_streamable_line()
        try:
            async for data in forward_with_heartbeat_async(self.source_gen, self.heartbeat_interval_sec):
                result = self._process_data(data)
                if result:
                    for chunk in chunks(result, self.MAX_CHUNK_SIZE):
                        yield chunk
        except Exception as e:
            for chunk in chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE):
                yield chunk
        finally:
            yield Event(event="done").to_streamable_line()
            self._is_done = True


class StreamingMessageDecoder:
    def __init__(self):
        self._text_content = ""
        self._reasoning_content = ""
        self._sources = []
        self._status = []
        self._attachments = []
        self._generated_images = []
        self._plan = None
        self._hidden_contexts = []
        self._is_done = False
        self._started = False
        self._title = None
        self.buffer = ""

    def process_chunk(self, chunk: Union[str, bytes]) -> list[Event]:
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8")

        self.buffer += chunk

        lines = self.buffer.split("\n")
        self.buffer = lines.pop() or ""
        events = []

        for line in lines:
            if not line or not line.startswith("data: "):
                continue

            data = Event.model_validate_json(line[6:])
            events.append(data)
            if data.event == "data":
                if data.type == "chunk":
                    self._text_content += data.data
                elif data.type == "reasoning":
                    self._reasoning_content += data.data.text
                elif data.type == "source":
                    self._sources.append(data.data)
                elif data.type == "status":
                    if data.data.replace and len(self._status) > 0:
                        self._status[-1] = data.data
                    else:
                        self._status.append(data.data)
                elif data.type == "attachment":
                    self._attachments.append(data.data)
                elif data.type == "generated_image":
                    self._generated_images.append(data.data)
                elif data.type == "plan":
                    self._plan = data.data
                elif data.type == "hidden_context":
                    if not isinstance(data.data, HiddenContext):
                        logger.error(f"Invalid hidden_context data type: {type(data.data)}, expected HiddenContext")
                        continue
                    self._hidden_contexts.append(data.data)
            elif data.event == "title_generation":
                self._title = data.data
            elif data.event == "done":
                self._is_done = True
            elif data.event == "error":
                raise Exception(data.data)
            elif data.event == "start":
                self._started = True

        return events

    def consume_chunks(self, chunks: Generator[Union[str, bytes], None, None]):
        for chunk in chunks:
            self.process_chunk(chunk)

    async def consume_chunks_async(self, chunks: AsyncGenerator[Union[str, bytes], None]):
        async for chunk in chunks:
            self.process_chunk(chunk)

    def get_message(self):
        return StreamedMessage(
            text=self._text_content,
            reasoning=self._reasoning_content,
            sources=self._sources,
            status=self._status,
            attachments=self._attachments,
            generated_images=self._generated_images,
            plan=self._plan,
            hidden_contexts=self._hidden_contexts,
        )

    def is_done(self):
        return self._is_done

    def get_title(self):
        return self._title


class StreamingMessageForwarder:
    def __init__(self, message_stream: Union[Generator[str, None, None], AsyncGenerator[str, None]]):
        self.message_stream = message_stream
        self.is_async = inspect.isasyncgen(message_stream)
        self.decoder = StreamingMessageDecoder()

    def __iter__(self):
        for chunk in self.message_stream:
            self.decoder.process_chunk(chunk)
            yield chunk

    async def __aiter__(self):
        if self.is_async:
            async for chunk in self.message_stream:
                self.decoder.process_chunk(chunk)
                yield chunk
        else:
            for chunk in self.message_stream:
                self.decoder.process_chunk(chunk)
                yield chunk

    def is_done(self):
        return self.decoder.is_done()

    def get_message(self):
        return self.decoder.get_message()


async def exhaust_streaming_message(streaming_message: Union[StreamingMessage, StreamingMessageForwarder]):
    async for _ in streaming_message:
        pass
