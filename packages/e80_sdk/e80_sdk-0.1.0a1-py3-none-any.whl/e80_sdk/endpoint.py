import os
import asyncio
import logging
from . import fastapi
from e80_sdk.secrets import Secrets
from e80_sdk.internal.environment import Environment, UserApiKey, JobToken
from e80_sdk.internal.httpx_async import async_client
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)

reload_jwt_task = None

_EIGHTY80_HEALTH_CHECK_PATH = "/.8080/health"


def eighty80_app() -> fastapi.FastAPI:
    global reload_jwt_task  # TODO: Remove this global.

    api_url = os.environ.get("8080_API_URL", None)
    platform_url = os.environ.get("8080_PLATFORM_URL", None)
    identity_token = os.environ.get("8080_IDENTITY_TOKEN", None)
    project_slug = os.environ.get("8080_PROJECT_SLUG", None)
    org_slug = os.environ.get("8080_ORGANIZATION_SLUG", None)

    if os.environ.get("8080_SECRETS_FILE", None):
        Secrets.load_secrets_file()
    if identity_token:
        Environment.identity = JobToken(job_token=identity_token)
    if api_url:
        Environment.base_api_url = api_url
    if platform_url:
        Environment.base_platform_url = platform_url
    if project_slug:
        Environment.project_slug = project_slug
    if org_slug:
        Environment.organization_slug = org_slug

    if Environment.identity is None:
        raise Eighty80FatalError(
            "Are you using the eighty80 CLI or running this on 8080?"
        )
    elif isinstance(Environment.identity, UserApiKey):
        Secrets.load_secrets_dict(Environment.identity.secrets)

    eighty80_app = fastapi.FastAPI()
    FastAPIInstrumentor.instrument_app(
        eighty80_app,
        excluded_urls=_EIGHTY80_HEALTH_CHECK_PATH,
    )

    eighty80_app.get(_EIGHTY80_HEALTH_CHECK_PATH)(_eighty80_health_check)

    return eighty80_app


async def _eighty80_health_check():
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    yield
    await async_client.aclose()


class Eighty80FatalError(Exception):
    pass
