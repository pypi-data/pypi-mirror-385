import requests
from pydantic import BaseModel

from dataclasses import dataclass


class SandboxClient:
    _auth_token: str
    _base_url: str

    def __init__(self, auth_token: str, base_url: str):
        self._auth_token = auth_token
        self._base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self._auth_token}",
                "Content-Type": "application/json",
            }
        )

    def run_python(self, code: str) -> "RunCodeResult":
        return self._run_command("python", code)

    def run_javascript(self, code: str) -> "RunCodeResult":
        return self._run_command("js", code)

    def install_javascript_dependency(self, deps: list[str]):
        return self._install_dependencies("js", deps)

    def install_python_dependencies(self, deps: list[str]):
        return self._install_dependencies("python", deps)

    def _run_command(self, lang: str, code: str) -> "RunCodeResult":
        resp = self.session.post(f"{self._base_url}/{lang}/run", json={"code": code})
        resp.raise_for_status()
        run_code_resp = _RunCodeResponse.model_validate(resp.json())
        return RunCodeResult(
            is_successful=run_code_resp.exit_code == 0, result=run_code_resp.message
        )

    def _install_dependencies(self, lang: str, deps: list[str]):
        resp = self.session.post(
            f"{self._base_url}/{lang}/deps", json={"dependencies": deps}
        )
        resp.raise_for_status()

    def destroy(self):
        self.session.delete(f"{self._base_url}/me")


@dataclass
class RunCodeResult:
    is_successful: bool
    result: str


class _RunCodeResponse(BaseModel):
    exit_code: int
    message: str
