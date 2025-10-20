from typing import List, Union, Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.base import BaseLLMProvider
from ..core.config import LLMConfig, ChatMessage, ChatResponse
from ..exceptions import APIKeyNotFoundError, ProviderConnectionError

class QwenProvider(BaseLLMProvider):
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.api_key:
            raise APIKeyNotFoundError("Qwen API key is required")
        
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url or self.BASE_URL,
            timeout=config.timeout
        )

    def validate_config(self) -> bool:
        return self.config.api_key is not None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def chat(self, messages: Union[str, List[ChatMessage]], **kwargs) -> ChatResponse:
        try:
            formatted_messages = self._prepare_messages(messages)
            params = self._merge_config(**kwargs)
            
            if self._is_thinking_enabled():
                extra_body = params.get("extra_body", {})
                if self._is_vl_high_resolution_images_enabled():
                    extra_body["enable_vl_high_resolution_images"] = True
                if isinstance(self.config.thinking, bool):
                    extra_body["enable_thinking"] = self.config.thinking
                params["extra_body"] = extra_body
            

            return self._sync_chat(formatted_messages, params)
                
        except Exception as e:
            raise ProviderConnectionError(f"Qwen API error: {str(e)}")

    def _is_thinking_enabled(self) -> bool:
        return (
            self.config.thinking is not None and 
            self.config.model.startswith("qwen3")
        )

    def _is_vl_high_resolution_images_enabled(self) -> bool:
        return (
            self.config.vl_high_resolution_images and 
            (self.config.model.startswith("qwen3-vl") or self.config.model.startswith("qwen-vl-max") or self.config.model.startswith("qwen-vl-plus"))
        )

    def _sync_chat(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> ChatResponse:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **params
        )

        if params.get("stream") is True:
            return response
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )

