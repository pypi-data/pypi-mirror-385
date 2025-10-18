# 8080 CLI

> [!NOTE]
> If you're just trying to use the 8080 API, see here. (TODO)

Use the 8080 CLI to build, deploy, and run hosted code on the 8080 platform.

Requirements:
  - [uv](https://astral.sh/uv)
  - Python 3.12

## Quickstart

1. Create an 8080 account on https://app.8080.io

1. Install the tool: `uv tool install e80`

1. Login to your account `e80 login`

1. Initialize a project `e80 init hello-world; cd hello-world`

1. Run your project using the dev server: `e80 dev`

1. Deploy your project to 8080: `e80 deploy`

## More info

See the [e80_sdk](https://pypi.org/project/e80_sdk) package to interface with the 8080 API.