import rich_click as click

from rich.tree import Tree
from rich import print as rich_print

from collections import defaultdict

from e80_sdk import Eighty80
from e80.oauth_handler import start_oauth_flow
from e80.init import init_project
from e80.archive import archive_project
from e80.deploy import deploy_project
from e80.dev import run_dev_server
from e80.lib.environment import CLIEnvironment
from e80.lib.sdk import set_sdk_environment

cli_env = CLIEnvironment()


@click.group()
def cli() -> None:
    """CLI tool for OpenAI-compatible API operations."""
    pass


@cli.command()
def archive() -> None:
    """Just build this project."""
    archive_project()


@cli.command()
@click.option("--bind", default="0.0.0.0", help="Interface to bind the dev server to")
@click.option("--port", default=8080, type=int)
def dev(bind, port) -> None:
    """Runs the dev server."""
    run_dev_server(cli_env, bind, port)


@cli.command()
@click.option("--artifact_id", default=None, help="Redeploy this artifact ID")
def deploy(artifact_id) -> None:
    """Builds and deploys this project."""
    deploy_project(cli_env, artifact_id)


@cli.command()
@click.option("--path", help="The path to create the project in.")
@click.argument("name", type=str, required=True)
def init(path, name) -> None:
    """Initializes an 8080 cloud project."""
    init_project(env=cli_env, install_path=path or name, project_name=name)


@cli.command()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode")
def login(verbose) -> None:
    """Login into 8080 and fetch an access token."""
    start_oauth_flow(cli_env, verbose=verbose)


@cli.command()
def models():
    """List all models."""
    set_sdk_environment(cli_env)
    models = Eighty80().completion_sdk().models.list()

    by_provider = defaultdict(list)
    for model in models.data:
        by_provider[model["provider"]].append(model)

    for provider, models in by_provider.items():
        tree = Tree(f"[bold]{provider}[/]", guide_style="grey42")
        for model in sorted(models, key=lambda x: x["id"]):
            tree.add(f"{model['id']}")
        rich_print(tree)


@cli.command()
@click.argument("text", type=str)
@click.option("--model", default="8080", help="Model to use")
@click.option("--stream", default=True, is_flag=True, help="Stream the response")
def chat(text, model, stream) -> None:
    """Chat with a model."""

    set_sdk_environment(cli_env)
    app = Eighty80().completion_sdk()

    if stream:
        sr = app.chat.completions.create(
            messages=[{"role": "user", "content": text}], model=model, stream=True
        )
        for event in sr:
            click.echo(sr)
        click.echo()
    else:
        resp = app.chat.completions.create(
            messages=[{"role": "user", "content": text}], model=model
        )
        click.echo(resp.choices[0].message.content)


def main():
    """Entry point for the CLI tool."""
    cli()
