import click
import zipfile
import subprocess
import shutil
from pathlib import Path
from e80.lib.project import read_project_config
from e80.lib.pyproject import get_uv_local_sources


def archive_project():
    project_config = read_project_config()
    local_sources = get_uv_local_sources()

    archive_root = Path(".8080_cache")

    if archive_root.exists():
        shutil.rmtree(archive_root)

    Path(".8080_cache").mkdir()
    Path(".8080_cache/download").mkdir()
    Path(".8080_cache/unpacked").mkdir()
    Path(".8080_cache/packages").mkdir()

    Path(".8080_cache")

    if (
        subprocess.call(
            [
                "uv",
                "pip",
                "compile",
                "pyproject.toml",
                "-o",
                ".8080_cache/requirements.txt",
            ]
        )
        != 0
    ):
        raise click.ClickException("Compiling your packages returned a non-0 exit code")
    if (
        subprocess.call(
            [
                "uv",
                "run",
                "pip",
                "download",
                "-r",
                ".8080_cache/requirements.txt",
                "--only-binary=:all:",
                "-d",
                ".8080_cache/download",
                "--platform",
                "musllinux_1_1_x86_64",
                "--python-version",
                "313",
            ]
        )
        != 0
    ):
        raise click.ClickException(
            "Downloading Python wheels returned a non-0 exit code."
        )

    unpacked_path = Path(".8080_cache/unpacked")
    packages_path = Path(".8080_cache/packages")

    for child in Path(".8080_cache/download").iterdir():
        if not child.name.endswith(".whl"):
            continue
        if (
            subprocess.call(
                [
                    "uv",
                    "tool",
                    "run",
                    "wheel",
                    "unpack",
                    f".8080_cache/download/{child.name}",
                    "--dest",
                    ".8080_cache/unpacked",
                ]
            )
            != 0
        ):
            raise click.ClickException(
                f"Unpacking wheel {child.name} returned non-0 exit code"
            )
    for child in unpacked_path.iterdir():
        if not child.is_dir():
            continue
        for package_item in (unpacked_path / child.name).iterdir():
            if package_item.is_dir():
                shutil.copytree(
                    unpacked_path / child.name / package_item.name,
                    packages_path / package_item.name,
                    dirs_exist_ok=True,
                )
            else:
                shutil.move(
                    unpacked_path / child.name / package_item.name, packages_path
                )

    with zipfile.ZipFile(".8080_cache/archive.zip", "w") as f:
        # Archive all the dependencies
        lib_path = packages_path

        for root, _, files in lib_path.walk():
            stripped = root.relative_to(lib_path)
            for file in files:
                f.write(root / file, stripped / file)

        # Archive locally installed packages by uv
        # This will be used in cases like installing a working instance of the SDK
        for source in local_sources:
            source_path = Path(source.path)
            for root, _, files in source_path.walk():
                stripped = root.relative_to(source_path)
                if root == source_path:
                    continue
                for file in files:
                    f.write(root / file, stripped / file)

        # Archive all the user's code
        # Everything in the module used in the entrypoint will be archived.
        ep_split = project_config.entrypoint.split(".")
        if len(ep_split) < 2:
            click.echo(
                f"Could not find module from entrypoint: '{project_config.entrypoint}'. Your entrypoint should be in a module like: 'foo.bar:app'",
                err=True,
            )
        module = ep_split[0]

        for root, _, files in Path(module).walk():
            for file in files:
                f.write(root / file)

        # Archive an __init__.py so this can be used as a module.
        f.writestr("__init__.py", "")
