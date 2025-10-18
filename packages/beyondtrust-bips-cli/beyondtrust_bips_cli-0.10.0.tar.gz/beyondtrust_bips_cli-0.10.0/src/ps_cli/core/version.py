from pathlib import Path

from secrets_safe_library import config, exceptions


def get_cli_version(app) -> str | None:
    """
    Retrieve the CLI version from the version.txt file.
    """
    try:
        project_root = Path(__file__).parents[3]
        version_file_path = project_root / "version.txt"
        with open(version_file_path, "r") as version_file:
            version = version_file.read().strip()
            return version
    except FileNotFoundError as e:
        app.log.error(f"It was not possible to read CLI version {e}")
        return None


def get_api_version(app) -> str | None:
    """
    Retrieve the API version using the Configuration class.
    """
    try:
        config_obj = config.Configuration(
            authentication=app.authentication, logger=app.log.logger
        )
        version_info = config_obj.get_version()
        version = version_info.get("Version", "Unknown") if version_info else "Unknown"
        return version
    except exceptions.LookupError as e:
        app.log.error(f"Error retrieving API version: {e}")
        return None
