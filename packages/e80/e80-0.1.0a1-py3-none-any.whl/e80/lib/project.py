import yaml

from typing import Optional
from pydantic import BaseModel
from pathlib import Path


class CloudProjectConfig(BaseModel):
    project: str
    project_slug: Optional[str] = None
    organization_slug: str
    entrypoint: str


def read_project_config() -> CloudProjectConfig:
    path = _find_config_path()

    with path.open() as f:
        yaml_dict = yaml.safe_load(f)
        parsed = CloudProjectConfig.model_validate(yaml_dict)
        return parsed


def write_project_config(config: CloudProjectConfig, bootstrap=False):
    if bootstrap:
        path = Path("8080.yaml")
    else:
        path = _find_config_path()

    with path.open(mode="w") as f:
        model_dict = config.model_dump(exclude_none=True, exclude_unset=True)
        model_str = yaml.dump(model_dict)
        f.write(model_str)


def _find_config_path() -> Path:
    find_path = Path("8080.yaml")

    for _ in range(0, 3):
        if find_path.exists():
            find_path.resolve()
            return find_path

        find_path = find_path / ".."

    raise Exception("Config not found")
