import click
import os
import subprocess
from typing import cast
from pathlib import Path
from shutil import which
from e80.lib.user import read_user_config
from e80.lib.environment import CLIEnvironment
from e80.lib.project import write_project_config, CloudProjectConfig
from e80.lib.platform import PlatformClient, OrganizationMembership


def init_project(project_name: str, install_path: str, env: CLIEnvironment):
    user_config = read_user_config()
    if user_config is None:
        raise click.UsageError("You are not logged in! Please run 'eighty80 login'.")

    auth_info = user_config.auth_info.get(env.platform_host)
    if auth_info is None:
        raise click.UsageError(
            f"You are not logged in to {env.platform_host}. Please run 'eighty80 login --host \"{env.platform_host}\"' first!"
        )

    # uv must be installed and be on PATH
    # We should support normal pip, and cases where pip installs uv
    if which("uv") is None:
        click.echo("uv is not installed. Please install uv first!", err=True)
        return

    mr = PlatformClient(
        env=env, api_key=auth_info.auth_token
    ).list_organization_memberships()
    if len(mr.memberships) == 0:
        raise click.UsageError(
            'You are not part of any organizizations. Please go to "https://app.8080.io" to create your first organization',
        )
    elif len(mr.memberships) == 1:
        selected = mr.memberships[0]
    else:
        selected = None

        while selected is None:
            for [idx, ms] in enumerate(mr.memberships):
                click.echo(
                    f"[{idx}] - {ms.organization_name} - ({ms.organization_slug})"
                )
            value = click.prompt(
                f"Please selected an organization to created this project for [0-{len(mr.memberships)}]",
                type=int,
                default=0,
            )
            if value < len(mr.memberships) and value >= 0:
                selected = mr.memberships[value]
            else:
                click.prompt(f"Unrecognized input: {value}. Please try again.")

    selected = cast(OrganizationMembership, selected)  # Make mypy happy.
    click.echo(
        f"Creating a project for organization: {selected.organization_name} ({selected.organization_slug})"
    )

    path = Path(install_path)

    if path.exists():
        if path.is_file():
            click.echo(
                f"Path {path} was a file. Please choose a new directory.", err=True
            )
        if path.is_dir() and any(path.iterdir()):
            click.echo(
                f"Directory {path} was not empty! Please choose a new or empty directory"
            )

    path.mkdir(parents=True, exist_ok=True)

    os.chdir(path)

    write_project_config(
        CloudProjectConfig(
            project=project_name,
            organization_slug=selected.organization_slug,
            entrypoint=f"{project_name}.main:app",
        ),
        bootstrap=True,
    )

    with open("pyproject.toml", "w") as f:
        f.write(build_pyproject(project_name))

    with open("README.md", "w") as f:
        f.write(build_readme(project_name))

    # All the code goes into its own module
    module_path = Path(project_name)
    module_path.mkdir()
    (module_path / "__init__.py").touch()
    with open(module_path / "main.py", "w") as f:
        f.write(build_initial_file(project_name))

    subprocess.check_call(["uv", "sync"])

    if which("git") is not None:
        subprocess.check_call(["git", "init", "."])

    click.echo("8080 cloud project initialized!")
    click.echo('Run the test server with: "eighty80 dev"')


def build_initial_file(project_name: str) -> str:
    # TODO: Put an actual example that calls to the LLM here.
    return f"""from e80_sdk import Eighty80, eighty80_app

app = eighty80_app()

# Get an OpenAI SDK-compatible object to talk to the 8080 
api = Eighty80().completion_sdk()

# If you previously saved OpenAI SDK credentials to the 8080 platform,
# you can quickly create an OpenAI SDK like this:
# another_openai_compatible_api = Eighty80().completion_sdk("secret_name")

@app.get("/example")
def completion_example():
    # For more information about the OpenAI SDK, see the OpenAI SDK API reference here:
    # https://platform.openai.com/docs/api-reference/chat/create
    return api.chat.completions.create(
        messages=[
            {{
                "role": "user",
                "content": "Tell me a joke."
            }}
        ],
        model="gpt-oss-20b",
        stream=False,
    )


@app.get("/")
def hello_world():
    return {{"Hello": "{project_name}" }}
"""


def build_pyproject(project_name: str) -> str:
    # TODO: Put the 8080 SDK as a dependency in here once it's released.
    return f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A 8080 cloud project."
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "e80-sdk",
]"""


def build_readme(project_name: str) -> str:
    return f"""# {project_name}

This is an 8080 project, made using the `eighty80 init` command.

## Running

To run the dev server, run `eighty80 dev` in your terminal.

## Deploy to 8080

To build the artifact and deploy it to 8080, run `eighty80 deploy` in your terminal.
"""
