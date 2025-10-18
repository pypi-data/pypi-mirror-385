import tomllib
from dataclasses import dataclass


def get_uv_local_sources() -> "list[LocalUVSource]":
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

        sources = data.get("tool", {}).get("uv", {}).get("sources", {})

        return [LocalUVSource(pkg, data["path"]) for pkg, data in sources.items()]


@dataclass
class LocalUVSource:
    pkg: str
    path: str
