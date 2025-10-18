import asyncio
from e80_sdk.internal.environment import Environment, UserApiKey, JobToken
from e80_sdk.internal.httpx_async import async_client
from pydantic import BaseModel


class PlatformClient:
    async def create_sandbox(self) -> "CreateSandboxResponse":
        headers = {}
        if isinstance(Environment.identity, UserApiKey):
            headers["authorization"] = f"Bearer {Environment.identity.api_key}"
        elif isinstance(Environment.identity, JobToken):
            headers["x-8080-job-token"] = Environment.identity.job_token

        resp = await async_client.post(
            f"{Environment.base_platform_url}/api/sandbox/{Environment.organization_slug}/{Environment.project_slug}/deploy",
            headers=headers,
        )
        resp.raise_for_status()
        # TODO: Remove this sleep.
        # The endpoint returns the service when it is registered, but we must wait
        # for the service to be ready in the endpoint.
        await asyncio.sleep(10)
        return CreateSandboxResponse.model_validate(resp.json())


class CreateSandboxResponse(BaseModel):
    address: str
    auth_token: str
