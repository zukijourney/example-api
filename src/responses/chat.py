import time
import ujson
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk
from ..responses import PrettyJSONResponse
from ..utils import gen_cmpl_id, gen_sys_fp

async def streaming_chat_response(response: AsyncStream[ChatCompletionChunk] | str, data: dict):
    """Streaming response generator"""

    completion_id = gen_cmpl_id()

    def generate_response(chunk: str):
        return {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion",
            "created": time.time(),
            "model": data.get("model"),
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": chunk}, "finish_reason": "stop"}]
        }

    try:
        if isinstance(response, str):
            for chunk in response:
                yield b"data: " + ujson.dumps(generate_response(chunk)).encode("utf-8") + b"\n\n"
        else:
            async for chunk in response:
                yield b"data: " + chunk.model_dump_json().encode("utf-8") + b"\n\n"
    finally:
        yield b"data: [DONE]"

async def normal_chat_response(response: str, data: dict):
    """Non-streaming response generator"""

    completion_id = gen_cmpl_id()
    system_fingerprint = gen_sys_fp()

    return PrettyJSONResponse({
        "id": f"chatcmpl-{completion_id}",
        "object": "chat.completion",
        "system_fingerprint": system_fingerprint,
        "created": time.time(),
        "model": data.get("model"),
        "choices": [{"index": 0, "message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })