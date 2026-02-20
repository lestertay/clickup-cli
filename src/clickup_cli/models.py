from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Space:
    id: str
    name: str

    @classmethod
    def from_api(cls, data: dict) -> Space:
        return cls(id=data["id"], name=data["name"])


@dataclass
class Folder:
    id: str
    name: str
    space_id: str

    @classmethod
    def from_api(cls, data: dict) -> Folder:
        return cls(
            id=data["id"],
            name=data["name"],
            space_id=data.get("space", {}).get("id", ""),
        )


@dataclass
class TaskList:
    id: str
    name: str
    folder_id: str

    @classmethod
    def from_api(cls, data: dict) -> TaskList:
        return cls(
            id=data["id"],
            name=data["name"],
            folder_id=data.get("folder", {}).get("id", ""),
        )


@dataclass
class Task:
    id: str
    name: str
    status: str
    assignees: list[str] = field(default_factory=list)
    priority: str | None = None
    due_date: str | None = None
    time_estimate: int | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""
    url: str = ""
    list_id: str = ""

    @classmethod
    def from_api(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            status=data.get("status", {}).get("status", ""),
            assignees=[a.get("username", a.get("email", "")) for a in data.get("assignees", [])],
            priority=data.get("priority", {}).get("priority") if data.get("priority") else None,
            due_date=data.get("due_date"),
            time_estimate=data.get("time_estimate"),
            tags=[t["name"] for t in data.get("tags", [])],
            description=data.get("description", ""),
            url=data.get("url", ""),
            list_id=data.get("list", {}).get("id", ""),
        )
