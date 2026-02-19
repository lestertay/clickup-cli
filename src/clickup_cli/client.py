from __future__ import annotations

import sys

import httpx
from rich.console import Console

from clickup_cli.models import Folder, Space, Task, TaskList

console = Console()

BASE_URL = "https://api.clickup.com/api/v2"


class ClickUpClient:
    def __init__(self, api_token: str):
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": api_token},
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.ConnectError:
            console.print("[red]Could not reach ClickUp API. Check your connection.[/red]")
            sys.exit(1)

        if response.status_code == 401:
            console.print("[red]Authentication failed. Check your API token (cl config init).[/red]")
            sys.exit(1)
        if response.status_code == 404:
            console.print(f"[red]Resource not found: {path}[/red]")
            sys.exit(1)
        if response.status_code == 429:
            console.print("[red]Rate limited by ClickUp API. Wait a moment and try again.[/red]")
            sys.exit(1)
        if response.status_code >= 400:
            console.print(f"[red]API error ({response.status_code}): {response.text}[/red]")
            sys.exit(1)

        return response.json()

    def get_teams(self) -> list[dict]:
        data = self._request("GET", "/team")
        return data.get("teams", [])

    def list_spaces(self, team_id: str) -> list[Space]:
        data = self._request("GET", f"/team/{team_id}/space")
        return [Space.from_api(s) for s in data.get("spaces", [])]

    def list_folders(self, space_id: str) -> list[Folder]:
        data = self._request("GET", f"/space/{space_id}/folder")
        return [Folder.from_api(f) for f in data.get("folders", [])]

    def list_lists(self, folder_id: str) -> list[TaskList]:
        data = self._request("GET", f"/folder/{folder_id}/list")
        return [TaskList.from_api(l) for l in data.get("lists", [])]

    def list_folderless_lists(self, space_id: str) -> list[TaskList]:
        data = self._request("GET", f"/space/{space_id}/list")
        return [TaskList.from_api(l) for l in data.get("lists", [])]

    def list_tasks(self, list_id: str, **filters) -> list[Task]:
        params = {}
        if "statuses" in filters:
            params["statuses[]"] = filters["statuses"]
        if "assignees" in filters:
            params["assignees[]"] = filters["assignees"]
        data = self._request("GET", f"/list/{list_id}/task", params=params)
        return [Task.from_api(t) for t in data.get("tasks", [])]

    def get_task(self, task_id: str) -> Task:
        data = self._request("GET", f"/task/{task_id}")
        return Task.from_api(data)

    def create_task(self, list_id: str, task_data: dict) -> Task:
        data = self._request("POST", f"/list/{list_id}/task", json=task_data)
        return Task.from_api(data)

    def update_task(self, task_id: str, task_data: dict) -> Task:
        data = self._request("PUT", f"/task/{task_id}", json=task_data)
        return Task.from_api(data)

    def delete_task(self, task_id: str) -> None:
        self._request("DELETE", f"/task/{task_id}")
