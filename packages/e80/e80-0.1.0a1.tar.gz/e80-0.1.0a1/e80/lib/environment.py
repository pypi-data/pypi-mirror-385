import os


class CLIEnvironment:
    api_host: str
    platform_host: str

    def __init__(self):
        self.api_host = os.getenv("E80_API_HOST", "https://api.8080.io").rstrip("/")
        self.platform_host = os.getenv(
            "E80_PLATFORM_HOST", "https://app.8080.io"
        ).rstrip("/")
