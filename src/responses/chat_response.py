import time
import orjson
import traceback
import uuid
from fastapi.responses import StreamingResponse, ORJSONResponse
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk
from collections.abc import AsyncGenerator
from typing import Union
from ..utils import gen_system_fingerprint, gen_completion_id, make_response

def generate_chunk(chunk: str, model: str) -> dict[str, Union[str, list, float]]:
    """Generates a chunk of a chat response"""
    return {
        "id": f"chatcmpl-{gen_system_fingerprint()}",
        "object": "chat.completion",
        "system_fingerprint": gen_completion_id(),
        "created": time.time(),
        "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": chunk}, "finish_reason": "stop"}]
    }

async def generate_response(response: Union[AsyncStream[ChatCompletionChunk], str], data: dict) -> AsyncGenerator[bytes]:
    """Generates a response and returns a bytes async generator"""
    try:
        if isinstance(response, str):
            for chunk in response:
                yield b"data: " + orjson.dumps(generate_chunk(chunk, data.get("model"))) + b"\n\n"
        else:
            async for chunk in response:
                yield b"data: " + chunk.model_dump_json().encode("utf-8") + b"\n\n"
    finally:
        yield b"data: [DONE]"

async def streaming_chat_response(response: Union[AsyncStream[ChatCompletionChunk], str], data: dict) -> StreamingResponse:
    """Streaming response generator"""
    try:
        return StreamingResponse(generate_response(response, data), status_code=200, headers={"X-Request-ID": str(uuid.uuid4())})
    except Exception:
        traceback.print_exc()
        return make_response(
            message="We were unable to generate a response. Please try again later.",
            type="invalid_response_error",
            status=500
        )

async def normal_chat_response(response: str, data: dict) -> ORJSONResponse:
    """Non-streaming response generator"""
    return ORJSONResponse({
        "id": f"chatcmpl-{gen_completion_id()}",
        "object": "chat.completion",
        "system_fingerprint": gen_system_fingerprint(),
        "created": time.time(),
        "model": data.get("model"),
        "choices": [{"index": 0, "message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })