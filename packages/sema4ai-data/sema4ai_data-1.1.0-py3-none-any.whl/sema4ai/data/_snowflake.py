import os
from pathlib import Path

from sema4ai.actions import ActionError
from sema4ai.data._config import _get_snowflake_connection_details_from_file

_SPCS_TOKEN_FILE_PATH = Path("/snowflake/session/token")
_LOCAL_AUTH_FILE_PATH = Path.home() / ".sema4ai" / "sf-auth.json"


class SnowflakeAuthenticationError(ActionError):
    """Raised when there are authentication-related issues with Snowflake connection."""

    pass


def get_snowflake_connection_details(
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    """
    Get Snowflake connection details based on the environment.

    This function first checks if running in SPCS by looking for the token file.
    If found, it uses SPCS authentication, otherwise falls back to local config-based authentication.

    Args:
        role: Snowflake role to use. Falls back to env var
        warehouse: Snowflake warehouse to use. Falls back to env var
        database: Snowflake database to use. Falls back to env var
        schema: Snowflake schema to use. Falls back to env var

    Returns:
        dict: Connection credentials for Snowflake containing environment-specific fields:
            For SPCS:
               host: from SNOWFLAKE_HOST env var
               account: from SNOWFLAKE_ACCOUNT env var
               authenticator: "OAUTH"
               token: from SPCS token file
               role, warehouse, database, schema: from args or env vars
               client_session_keep_alive: True
               port: from SNOWFLAKE_PORT env var
               protocol: "https"
            For local machine:
               account: from config
               authenticator: from config (OAUTH, or SNOWFLAKE_JWT)
               user: from config (only for SNOWFLAKE_JWT)
               token: from config (only for OAUTH)
               role: from args or config
               warehouse: from args or config
               database, schema: from args
               client_session_keep_alive: True
               private_key and private_key_password (only for SNOWFLAKE_JWT)

    Raises:
        SnowflakeAuthenticationError: If required credentials are missing or invalid
    """

    # Check for SPCS environment first
    if _SPCS_TOKEN_FILE_PATH.exists():
        token = _SPCS_TOKEN_FILE_PATH.read_text().strip()

        host = os.getenv("SNOWFLAKE_HOST")
        account = os.getenv("SNOWFLAKE_ACCOUNT")

        if not host or not account:
            raise SnowflakeAuthenticationError(
                "Required environment variables SNOWFLAKE_HOST and SNOWFLAKE_ACCOUNT must be set"
            )

        return {
            "host": host,
            "account": account,
            "authenticator": "OAUTH",
            "token": token,
            "role": role or os.getenv("SNOWFLAKE_ROLE"),
            "warehouse": warehouse or os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": database or os.getenv("SNOWFLAKE_DATABASE"),
            "schema": schema or os.getenv("SNOWFLAKE_SCHEMA"),
            "client_session_keep_alive": True,
            "port": os.getenv("SNOWFLAKE_PORT"),
            "protocol": "https",
        }

    # Fall back to local config-based authentication
    try:
        return _get_snowflake_connection_details_from_file(
            _LOCAL_AUTH_FILE_PATH, role, warehouse, database, schema
        )
    except Exception as e:
        raise SnowflakeAuthenticationError(
            f"Failed to read authentication config from {_LOCAL_AUTH_FILE_PATH}: {str(e)}"
        ) from e
