import os
from importlib.metadata import PackageNotFoundError, version

DEFAULT_BASE_URL = "https://api.streamstraight.com"

DEFAULT_ACK_TIMEOUT_MS = 20_000


def get_base_url() -> str:
    return os.getenv("STREAMSTRAIGHT_API_BASE_URL", DEFAULT_BASE_URL)


def get_package_version() -> str:
    try:
        return version("streamstraight-server")
    except PackageNotFoundError:
        return "0.0.0-dev"
