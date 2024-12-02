import tiktoken
from fastapi import Request
from typing import Union, List, Optional
from dataclasses import dataclass
from .models import ChatRequest, Message, TextContentPart, ImageContentPart

@dataclass
class TokenizerConfig:
    encoding_name: str = 'o200k_base'
    non_text_token_count: int = 100

class TokenCounter:
    def __init__(self, config: Optional[TokenizerConfig] = None):
        self.config = config or TokenizerConfig()
        self.encoding = tiktoken.get_encoding(self.config.encoding_name)

    def count_text_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def count_message_content_tokens(
        self,
        content: Union[str, List[Union[TextContentPart, ImageContentPart]]]
    ) -> int:
        if isinstance(content, str):
            return self.count_text_tokens(content)

        return sum(
            self.count_text_tokens(part.text)
            if part.type == 'text'
            else self.config.non_text_token_count
            for part in content
        )

    def count_message_tokens(self, message: Union[Message, str]) -> int:
        if isinstance(message, str):
            return self.count_text_tokens(message)

        return self.count_message_content_tokens(message.content)

    def count_request_tokens(self, request: ChatRequest) -> int:
        return sum(
            self.count_message_tokens(msg)
            for msg in request.messages
        )

class APIKeyExtractor:
    def __init__(self, config: Optional[TokenizerConfig] = None):
        self.config = config or TokenizerConfig()

    def extract_api_key(self, request: Request) -> str:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return 'none'

        return auth_header.replace('Bearer ', '', 1)

    def validate_api_key(self, api_key: str) -> bool:
        return (
            api_key != 'none' and
            len(api_key.strip()) > 0
        )

class RequestProcessor:
    def __init__(
        self,
        token_counter: Optional[TokenCounter] = None,
        key_extractor: Optional[APIKeyExtractor] = None,
        config: Optional[TokenizerConfig] = None
    ):
        self.config = config or TokenizerConfig()
        self.token_counter = token_counter or TokenCounter(self.config)
        self.key_extractor = key_extractor or APIKeyExtractor(self.config)

    def count_tokens(self, input_data: Union[ChatRequest, str]) -> int:
        if isinstance(input_data, ChatRequest):
            return self.token_counter.count_request_tokens(input_data)
        return self.token_counter.count_message_tokens(input_data)

    def get_api_key(self, request: Request) -> str:
        return self.key_extractor.extract_api_key(request)

request_processor = RequestProcessor()