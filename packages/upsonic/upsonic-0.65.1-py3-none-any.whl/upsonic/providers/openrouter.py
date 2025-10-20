from __future__ import annotations as _annotations

import os
from typing import overload

import httpx

from upsonic.utils.package.exception import UserError
from upsonic.models import cached_async_http_client
from upsonic.profiles import ModelProfile
from upsonic.profiles.amazon import amazon_model_profile
from upsonic.profiles.anthropic import anthropic_model_profile
from upsonic.profiles.cohere import cohere_model_profile
from upsonic.profiles.deepseek import deepseek_model_profile
from upsonic.profiles.google import google_model_profile
from upsonic.profiles.grok import grok_model_profile
from upsonic.profiles.meta import meta_model_profile
from upsonic.profiles.mistral import mistral_model_profile
from upsonic.profiles.openai import OpenAIJsonSchemaTransformer, OpenAIModelProfile, openai_model_profile
from upsonic.profiles.qwen import qwen_model_profile
from upsonic.providers import Provider

try:
    from openai import AsyncOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    AsyncOpenAI = None
    _OPENAI_AVAILABLE = False



class OpenRouterProvider(Provider[AsyncOpenAI]):
    """Provider for OpenRouter API."""

    @property
    def name(self) -> str:
        return 'openrouter'

    @property
    def base_url(self) -> str:
        return 'https://openrouter.ai/api/v1'

    @property
    def client(self) -> AsyncOpenAI:
        return self._client

    def model_profile(self, model_name: str) -> ModelProfile | None:
        provider_to_profile = {
            'google': google_model_profile,
            'openai': openai_model_profile,
            'anthropic': anthropic_model_profile,
            'mistralai': mistral_model_profile,
            'qwen': qwen_model_profile,
            'x-ai': grok_model_profile,
            'cohere': cohere_model_profile,
            'amazon': amazon_model_profile,
            'deepseek': deepseek_model_profile,
            'meta-llama': meta_model_profile,
        }

        profile = None

        provider, model_name = model_name.split('/', 1)
        if provider in provider_to_profile:
            model_name, *_ = model_name.split(':', 1)  # drop tags
            profile = provider_to_profile[provider](model_name)

        # As OpenRouterProvider is always used with OpenAIChatModel, which used to unconditionally use OpenAIJsonSchemaTransformer,
        # we need to maintain that behavior unless json_schema_transformer is set explicitly
        return OpenAIModelProfile(json_schema_transformer=OpenAIJsonSchemaTransformer).update(profile)

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, *, api_key: str) -> None: ...

    @overload
    def __init__(self, *, api_key: str, http_client: httpx.AsyncClient) -> None: ...

    @overload
    def __init__(self, *, openai_client: AsyncOpenAI | None = None) -> None: ...

    def __init__(
        self,
        *,
        api_key: str | None = None,
        openai_client: AsyncOpenAI | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if not _OPENAI_AVAILABLE:
            from upsonic.utils.printing import import_error
            import_error(
                package_name="openai",
                install_command='pip install openai',
                feature_name="openai provider"
            )

                api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not api_key and openai_client is None:
            raise UserError(
                'Set the `OPENROUTER_API_KEY` environment variable or pass it via `OpenRouterProvider(api_key=...)`'
                'to use the OpenRouter provider.'
            )

        if openai_client is not None:
            self._client = openai_client
        elif http_client is not None:
            self._client = AsyncOpenAI(base_url=self.base_url, api_key=api_key, http_client=http_client)
        else:
            http_client = cached_async_http_client(provider='openrouter')
            self._client = AsyncOpenAI(base_url=self.base_url, api_key=api_key, http_client=http_client)