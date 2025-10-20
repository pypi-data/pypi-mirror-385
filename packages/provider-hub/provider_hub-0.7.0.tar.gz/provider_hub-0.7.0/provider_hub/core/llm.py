from typing import Optional, Union, List, Dict, Any
from .config import LLMConfig, ChatMessage, ChatResponse
from .base import BaseLLMProvider
from ..providers.openai import OpenAIProvider
from ..providers.deepseek import DeepSeekProvider
from ..providers.qwen import QwenProvider
from ..providers.doubao import DoubaoProvider
from ..providers.openai_compatible import OpenAICompatibleProvider
from ..providers.gemini import GeminiProvider
from ..utils.env import EnvManager
from ..exceptions import ProviderNotSupportedError, APIKeyNotFoundError, BaseUrlNotFoundError

class LLM:
    PROVIDER_MAPPING = {
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "qwen": QwenProvider,
        "doubao": DoubaoProvider,
        "gemini": GeminiProvider,
        "openai_compatible": OpenAICompatibleProvider
    }

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = 30,
        max_retries: Optional[int] = 3,
        thinking: Optional[Union[bool, str, Dict[str, Any]]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[Union[str, List[Dict[str, Any]]]] = None,
        stream: Optional[bool] = False,
        stream_options: Optional[Dict[str, Any]] = None,
        vl_high_resolution_images: Optional[bool] = True
    ):
        if provider == "openai_compatible":
            if not api_key:
                raise APIKeyNotFoundError(f"Api key or base url for provider: {provider} is not found")
            if not base_url:
                raise BaseUrlNotFoundError(f"Base url for provider: {provider} is not found")
        else:
            if not provider:
                provider = EnvManager.get_provider_from_model(model)
                
            if provider not in self.PROVIDER_MAPPING:
                raise ProviderNotSupportedError(f"Provider {provider} is not supported")
                
            if not api_key:
                api_key = EnvManager.auto_detect_api_key(model)
            
        config = LLMConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            thinking=thinking,
            extra_headers=extra_headers,
            extra_body=extra_body,
            system_prompt=system_prompt,
            stream=stream,
            stream_options=stream_options,
            vl_high_resolution_images=vl_high_resolution_images
        )
        
        provider_class = self.PROVIDER_MAPPING[provider]
        self.provider: BaseLLMProvider = provider_class(config)

    def chat(self, messages: Union[str, List[ChatMessage]], **kwargs) -> ChatResponse:
        return self.provider.chat(messages, **kwargs)

    @property
    def model(self) -> str:
        return self.provider.config.model
        
    @property
    def config(self) -> LLMConfig:
        return self.provider.config