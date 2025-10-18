import uvicorn
import sys
import os

from e80.lib.project import read_project_config
from e80.lib.environment import CLIEnvironment
from e80.lib.sdk import set_sdk_environment


def run_dev_server(env: CLIEnvironment, bind: str, port: int) -> None:
    config = read_project_config()

    set_sdk_environment(env)

    sys.path.append(os.getcwd())

    uvicorn.run(config.entrypoint, host=bind, port=port)
