import openai

from typing import AsyncIterator, overload
from contextlib import asynccontextmanager
from e80_sdk.internal.platform import PlatformClient
from e80_sdk.secrets import Secrets
from e80_sdk.sandbox import SandboxClient
from e80_sdk.internal.environment import Environment, UserApiKey, JobToken
from openai.resources.responses.responses import Responses, AsyncResponses
from openai.resources.chat.chat import Chat, AsyncChat
from openai.resources.models import Models, AsyncModels


class Eighty80:
    """
    The main entrypoint into the 8080 SDK.

    Call its methods to access different 8080 services.
    """

    def secrets(self) -> type[Secrets]:
        return Secrets

    @overload
    def completion_sdk(self) -> "_Eighty80OpenAISDK": ...

    @overload
    def completion_sdk(self, secret_name: str) -> openai.OpenAI: ...

    def completion_sdk(self, secret_name: str | None = None):
        """
        Obtain an OpenAI SDK-compatible object that can be a drop-in
        replacement for the OpenAI SDK client.

        ```python
        from openai import OpenAI
        from e80_sdk import Eighty80

        old_client = OpenAI(...)
        drop_me_in = Eighty80.completion_sdk(...)
        ```

        To use 8080 models, simply call this method without any arguments.
        Note that not all properties are implemented for 8080 models.

        ```python
        from e80_sdk import Eighty80

        Eighty80.completion_sdk().responses.create(...)
        Eighty80.completion_sdk().chat.completions.create(...)
        ```

        You can set an OpenAI SDK secret in the 8080 platform, and obtain
        an OpenAI SDK-compatible object. An SDK object created this way has
        no restrictions on what properties are available.

        ```python
        from e80_sdk import Eighty80

        # Assumes 'foo' is an OpenAI SDK secret set in the 8080 platform
        Eighty80.completion_sdk('foo').chat.completions.create(...)
        ```
        """
        if secret_name is None:
            return _Eighty80OpenAISDK()

        secret = self.secrets().get_openai_secret(secret_name)
        return openai.OpenAI(base_url=secret.url, api_key=secret.api_key)

    @overload
    def async_completion_sdk(self) -> "_Eighty80OpenAIAsyncSDK": ...

    @overload
    def async_completion_sdk(self, secret_name: str) -> openai.AsyncOpenAI: ...

    def async_completion_sdk(self, secret_name: str | None = None):
        """
        Obtain an async OpenAI SDK-compatible object that can be a drop-in
        replacement for the async OpenAI SDK client.

        ```python
        from openai import AsyncOpenAI
        from e80_sdk import Eighty80

        old_client = AsyncOpenAI(...)
        drop_me_in = Eighty80.async_completion_sdk(...)
        ```

        To use 8080 models, simply call this method without any arguments.
        Note that not all properties are implemented for 8080 models.

        ```python
        from e80_sdk import Eighty80

        await Eighty80.async_completion_sdk().responses.create(...)
        await Eighty80.async_completion_sdk().chat.completions.create(...)
        ```

        You can set an OpenAI SDK secret in the 8080 platform, and obtain
        an async OpenAI SDK-compatible object. An SDK object created this way has
        no restrictions on what properties are available.

        ```python
        from e80_sdk import Eighty80

        # Assumes 'foo' is an OpenAI SDK secret set in the 8080 platform
        await Eighty80.async_completion_sdk('foo').chat.completions.create(...)
        ```
        """

        if secret_name is None:
            return _Eighty80OpenAIAsyncSDK()

        secret = self.secrets().get_openai_secret(secret_name)
        return openai.AsyncOpenAI(base_url=secret.url, api_key=secret.api_key)

    @asynccontextmanager
    async def sandbox(self) -> AsyncIterator[SandboxClient]:
        """
        Create a new sandbox where you can execute arbitrary Python
        and Javascript code.

        Use this as an async context manager so the sandbox will get cleaned up
        automatically.

        ```
        from e80_sdk import Eighty80

        async with Eighty80.sandbox() as sandbox_client:
            sandbox_client.run_python("print('hello world')")
            sandbox_client.install_python_dependencies(["requests"])
        ```
        """
        client = PlatformClient()

        sb_resp = await client.create_sandbox()
        sb_client = SandboxClient(sb_resp.auth_token, sb_resp.address)

        try:
            yield sb_client
        finally:
            sb_client.destroy()


class _Eighty80OpenAISDK:
    _cached_client: openai.OpenAI

    def __init__(self):
        self._cached_client = None

        if isinstance(Environment.identity, JobToken):
            self._cached_client = openai.OpenAI(
                api_key=Environment.identity.job_token,
                base_url=f"{Environment.base_api_url}/v1",
                default_headers={"x-8080-job-token": "1"},
            )
        elif isinstance(Environment.identity, UserApiKey):
            self._cached_client = openai.OpenAI(
                api_key=Environment.identity.api_key,
                base_url=f"{Environment.base_api_url}/v1",
                default_headers={"x-8080-project-slug": Environment.project_slug},
            )
        if self._cached_client is None:
            raise Exception("Somehow got a null client")

    @property
    def chat(self) -> Chat:
        return self._cached_client.chat

    @property
    def models(self) -> Models:
        return self._cached_client.models

    @property
    def responses(self) -> Responses:
        return self._cached_client.responses


class _Eighty80OpenAIAsyncSDK:
    _cached_client: openai.AsyncOpenAI

    def __init__(self):
        if isinstance(Environment.identity, JobToken):
            self._cached_client = openai.AsyncOpenAI(
                api_key=Environment.identity.job_token,
                base_url=f"{Environment.base_api_url}/v1",
                default_headers={"x-8080-job-token": "1"},
            )
        elif isinstance(Environment.identity, UserApiKey):
            self._cached_client = openai.AsyncOpenAI(
                api_key=Environment.identity.api_key,
                base_url=f"{Environment.base_api_url}/v1",
                default_headers={"x-8080-project-slug": Environment.project_slug},
            )
        if self._cached_client is None:
            raise Exception("Somehow got a null client")

    @property
    def chat(self) -> AsyncChat:
        return self._cached_client.chat

    @property
    def models(self) -> AsyncModels:
        return self._cached_client.models

    @property
    def responses(self) -> AsyncResponses:
        return self._cached_client.responses
