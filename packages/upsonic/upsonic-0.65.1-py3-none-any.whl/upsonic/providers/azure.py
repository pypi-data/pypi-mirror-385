from __future__ import annotations as _annotations

import os
from typing import overload

import httpx

from upsonic.utils.package.exception import UserError
from upsonic.models import cached_async_http_client
from upsonic.profiles import ModelProfile
from upsonic.profiles.cohere import cohere_model_profile
from upsonic.profiles.deepseek import deepseek_model_profile
from upsonic.profiles.grok import grok_model_profile
from upsonic.profiles.meta import meta_model_profile
from upsonic.profiles.mistral import mistral_model_profile
from upsonic.profiles.openai import OpenAIJsonSchemaTransformer, OpenAIModelProfile, openai_model_profile
from upsonic.providers import Provider

try:
    from openai import AsyncOpenAI, AsyncAzureOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    AsyncOpenAI = None
    AsyncAzureOpenAI = None
    _OPENAI_AVAILABLE = False



class AzureProvider(Provider[AsyncOpenAI]):
    """Provider for Azure OpenAI API.

    See <https://azure.microsoft.com/en-us/products/ai-foundry> for more information.
    """

    @property
    def name(self) -> str:
        return 'azure'

    @property
    def base_url(self) -> str:
        assert self._base_url is not None
        return self._base_url

    @property
    def client(self) -> AsyncOpenAI:
        return self._client

    def model_profile(self, model_name: str) -> ModelProfile | None:
        model_name = model_name.lower()

        prefix_to_profile = {
            'llama': meta_model_profile,
            'meta-': meta_model_profile,
            'deepseek': deepseek_model_profile,
            'mistralai-': mistral_model_profile,
            'mistral': mistral_model_profile,
            'cohere-': cohere_model_profile,
            'grok': grok_model_profile,
        }

        for prefix, profile_func in prefix_to_profile.items():
            if model_name.startswith(prefix):
                if prefix.endswith('-'):
                    model_name = model_name[len(prefix) :]

                profile = profile_func(model_name)

                # As AzureProvider is always used with OpenAIChatModel, which used to unconditionally use OpenAIJsonSchemaTransformer,
                # we need to maintain that behavior unless json_schema_transformer is set explicitly
                return OpenAIModelProfile(json_schema_transformer=OpenAIJsonSchemaTransformer).update(profile)

        # OpenAI models are unprefixed
        return openai_model_profile(model_name)

    @overload
    def __init__(self, *, openai_client: AsyncAzureOpenAI) -> None: ...

    @overload
    def __init__(
        self,
        *,
        azure_endpoint: str | None = None,
        api_version: str | None = None,
        api_key: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None: ...

    def __init__(
        self,
        *,
        azure_endpoint: str | None = None,
        api_version: str | None = None,
        api_key: str | None = None,
        openai_client: AsyncAzureOpenAI | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Create a new Azure provider.

        Args:
            azure_endpoint: The Azure endpoint to use for authentication, if not provided, the `AZURE_OPENAI_ENDPOINT`
                environment variable will be used if available.
            api_version: The API version to use for authentication, if not provided, the `OPENAI_API_VERSION`
                environment variable will be used if available.
            api_key: The API key to use for authentication, if not provided, the `AZURE_OPENAI_API_KEY` environment variable
                will be used if available.
            openai_client: An existing
                [`AsyncAzureOpenAI`](https://github.com/openai/openai-python#microsoft-azure-openai)
                client to use. If provided, `base_url`, `api_key`, and `http_client` must be `None`.
            http_client: An existing `httpx.AsyncClient` to use for making HTTP requests.
        """
        if not _OPENAI_AVAILABLE:
            from upsonic.utils.printing import import_error
            import_error(
                package_name="openai",
                install_command='pip install "upsonic[openai]"',
                feature_name="Azure provider"
            )
        if openai_client is not None:
            assert azure_endpoint is None, 'Cannot provide both `openai_client` and `azure_endpoint`'
            assert http_client is None, 'Cannot provide both `openai_client` and `http_client`'
            assert api_key is None, 'Cannot provide both `openai_client` and `api_key`'
            self._base_url = str(openai_client.base_url)
            self._client = openai_client
        else:
            azure_endpoint = azure_endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
            api_version = api_version or os.getenv('OPENAI_API_VERSION') or os.getenv('AZURE_OPENAI_API_VERSION')
            api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
            if not azure_endpoint:
                raise UserError(
                    'Must provide one of the `azure_endpoint` argument or the `AZURE_OPENAI_ENDPOINT` environment variable'
                )

            if not api_key:  # pragma: no cover
                raise UserError(
                    'Must provide one of the `api_key` argument or the `AZURE_OPENAI_API_KEY` environment variable'
                )

            if not api_version:  # pragma: no cover
                raise UserError(
                    'Must provide one of the `api_version` argument or the `OPENAI_API_VERSION` environment variable'
                )

            http_client = http_client or cached_async_http_client(provider='azure')
            self._client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                http_client=http_client,
            )
            self._base_url = str(self._client.base_url)