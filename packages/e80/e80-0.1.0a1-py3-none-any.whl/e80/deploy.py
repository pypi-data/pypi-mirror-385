import click
from e80.archive import archive_project
from e80.lib.environment import CLIEnvironment
from e80.lib.project import read_project_config, write_project_config
from e80.lib.platform import PlatformClient
from e80.lib.user import get_auth_info
from pathlib import Path


def deploy_project(env: CLIEnvironment, artifact_id: str | None = None) -> None:
    config = read_project_config()
    auth_info = get_auth_info(env)
    if auth_info is None:
        raise click.UsageError("You are not logged in! Please run 'eighty80 login'.")

    pc = PlatformClient(api_key=auth_info.auth_token, env=env)
    if config.project_slug is None:
        cr = pc.create_project(config)
        config.project_slug = cr.project_slug
        write_project_config(config)

    artifact_id_to_deploy: str | None = None
    if artifact_id is not None:
        artifact_id_to_deploy = artifact_id
        click.echo(f"Using artifact '{artifact_id}'")
    else:
        archive_project()
        with Path(".8080_cache/archive.zip").open("rb") as f:
            click.echo("Uploading artifact...")
            resp = pc.upload_artifact(config, f)
            click.echo(
                f"Uploading artifact '{resp.artifact_id}' finished. Starting deploy..."
            )
            artifact_id_to_deploy = resp.artifact_id

    deploy_resp = pc.deploy_artifact(config, artifact_id=artifact_id_to_deploy)
    if deploy_resp.deployment_id is None:
        click.echo("No change detected")
    else:
        click.echo(
            f"Deploy started! Follow along: {env.platform_host}/o/{config.organization_slug}/p/{config.project_slug}/deploy/{deploy_resp.deployment_id}"
        )
