import time
import ujson
from litestar.response import Stream
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk
from ..exceptions import InvalidResponseException
from ..responses import PrettyJSONResponse
from ..utils import gen_cmpl_id, gen_sys_fp

async def streaming_chat_response(response: AsyncStream[ChatCompletionChunk] | str, data: dict):
    try:
        """Streaming response generator"""

        completion_id = gen_cmpl_id()
        fingerprint = gen_sys_fp()

        def generate_chunk(chunk: str):
            return {
                "id": f"chatcmpl-{completion_id}",
                "object": "chat.completion",
                "system_fingerprint": fingerprint,
                "created": time.time(),
                "model": data.get("model"),
                "choices": [{"index": 0, "delta": {"role": "assistant", "content": chunk}, "finish_reason": "stop"}]
            }

        async def generate_response(chunk: AsyncStream[ChatCompletionChunk] | str):
            try:
                if isinstance(response, str):
                    for chunk in response:
                        yield b"data: " + ujson.dumps(generate_chunk(chunk)).encode("utf-8") + b"\n\n"
                else:
                    async for chunk in response:
                        yield b"data: " + chunk.model_dump_json().encode("utf-8") + b"\n\n"
            finally:
                yield b"data: [DONE]"

        return Stream(generate_response(response), media_type="text/event-stream", status_code=200)
    except:
        return InvalidResponseException(
            message="We were unable to generate a response. Please try again later.",
            status=500
        ).to_response()

async def normal_chat_response(response: str, data: dict):
    """Non-streaming response generator"""

    return PrettyJSONResponse({
        "id": f"chatcmpl-{gen_cmpl_id()}",
        "object": "chat.completion",
        "system_fingerprint": gen_sys_fp(),
        "created": time.time(),
        "model": data.get("model"),
        "choices": [{"index": 0, "message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })