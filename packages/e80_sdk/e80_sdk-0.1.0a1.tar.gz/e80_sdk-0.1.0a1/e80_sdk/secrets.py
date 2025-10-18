import json
from pydantic import BaseModel
from typing import TypeVar, Any


class Secrets:
    """
    Access secrets set on the 8080 platform in your code.

    You should not need to manually ingest any secrets. Calling the `get_*` methods should just work.
    To use secrets when developing locally with `eighty80 dev`, please make sure the option to expose
    the secret locally is checked on the platform.
    """

    _string_secrets: dict[str, str] = {}
    _json_secrets: dict[str, Any] = {}
    _openai_secrets: "dict[str, OpenAISecret]" = {}

    @staticmethod
    def load_secrets_file():
        with open("/local/secrets.json", "r") as f:
            secrets_list = json.loads(f.read())
        _load_secrets(secrets_list)

    @staticmethod
    def load_secrets_dict(dicts: list[dict]):
        _load_secrets(dicts)

    @staticmethod
    def get_string_secret(key: str) -> str:
        """
        Access a string secret, and returns the string.

        Throws an exception if:
          - Secret `key` does not exist
          - Secret `key` has a different type
          - Secret `key` is not exposed for the environment
             - Please make sure to expose the secret for local development
        """
        return _get_secret_from_dict(Secrets._string_secrets, key)

    @staticmethod
    def get_json_secret(key: str) -> Any:
        """
        Access and parse a JSON secret.

        After parsing as JSON, no type checking or coercion occurs. The format
        will be whatever you set in the 8080 platform.

        Throws an exception if:
          - Secret `key` does not exist
          - Secret `key` has a different type
          - Secret `key` is not exposed for the environment
             - Please make sure to expose the secret for local development
        """

        return _get_secret_from_dict(Secrets._json_secrets, key)

    @staticmethod
    def get_openai_secret(key: str) -> "OpenAISecret":
        """
        Access and parse an OpenAI secret.

        Throws an exception if:
          - This secret with key `key` does not exist
          - This secret with key `key` is not exposed for the environment
             - Please make sure to expose the secret for local development

        The return value is strongly typed. See the example below. Example:

        ```python
        from e80_sdk import Eighty80

        # Set in the 8080 platform
        foo = Eighty80.secrets().get_openai_secret('foo')

        print(foo.url) # The URL as a string
        print(foo.api_key) # The API key as a string
        ```

        Note that you don't need to create an OpenAI SDK client manually.
        You can directly get an OpenAI SDK like such:

        ```python
        from e80_sdk import Eighty80

        # Assumes you set an OpenAI secret named 'foo' in the 8080 platform.
        sdk = Eighty80.completion_sdk('foo')
        async_sdk = Eighty80.async_completion_sdk('foo') # Async client
        ```
        """
        return _get_secret_from_dict(Secrets._openai_secrets, key)


T = TypeVar("T")


def _get_secret_from_dict(secret_dict: dict[str, T], key: str) -> T:
    value = secret_dict.get(key)
    if value is None:
        all_keys = secret_dict.keys()
        raise SecretException(
            f"Could not find secret with key: {key}. Should be one of: {all_keys}"
        )
    return value


def _load_secrets(secrets_list: list[dict]):
    for s in secrets_list:
        secret = Secret.model_validate(s)
        if secret.type == "string":
            if not isinstance(secret.value, str):
                raise SecretException(f"{secret.name} should've been a string")
            Secrets._string_secrets[secret.name] = secret.value
        elif secret.type == "json":
            if not isinstance(secret.value, dict):
                raise SecretException(f"{secret.name} should've been a dict")
            Secrets._json_secrets[secret.name] = secret.value
        elif secret.type == "openai":
            if not isinstance(secret.value, dict):
                raise SecretException(f"{secret.name} should've been a dict")
            value = OpenAISecret.model_validate(secret.value)
            Secrets._openai_secrets[secret.name] = value


class SecretException(Exception):
    pass


class Secret(BaseModel):
    name: str
    value: str | dict
    type: str


class OpenAISecret(BaseModel):
    url: str
    api_key: str
