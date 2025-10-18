from dataclasses import dataclass


@dataclass
class UserApiKey:
    api_key: str
    secrets: list[dict]


@dataclass
class JobToken:
    job_token: str


class Environment:
    organization_slug: str
    project_slug: str
    base_platform_url: str = "https://app.8080.io"
    base_api_url: str = "https://api.8080.io"
    identity: UserApiKey | JobToken | None
