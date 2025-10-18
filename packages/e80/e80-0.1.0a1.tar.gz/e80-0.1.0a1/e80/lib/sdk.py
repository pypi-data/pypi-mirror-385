import click

from e80.lib.environment import CLIEnvironment
from e80_sdk.internal.environment import Environment, UserApiKey
from e80.lib.project import read_project_config
from e80.lib.platform import PlatformClient
from e80.lib.user import get_auth_info


def set_sdk_environment(env: CLIEnvironment) -> None:
    config = read_project_config()
    auth_info = get_auth_info(env)
    if auth_info is None:
        raise click.UsageError("You are not logged in! Please run 'eighty80 login'.")

    pc = PlatformClient(api_key=auth_info.auth_token, env=env)

    secrets_resp = pc.list_secrets_for_local(config)

    # Add the current working directory to PYTHONPATH
    # This means the command will search the CWD for the entrypoint
    config = read_project_config()

    Environment.base_api_url = env.api_host
    Environment.base_platform_url = env.platform_host
    Environment.identity = UserApiKey(
        api_key=auth_info.auth_token,
        secrets=[s.model_dump() for s in secrets_resp.secrets],
    )
    Environment.project_slug = config.project_slug or ""
    Environment.organization_slug = config.organization_slug or ""
