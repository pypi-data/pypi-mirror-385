from pathlib import Path

OAUTH = "OAUTH"


class SnowflakeConfigurationError(Exception):
    """Raised when there are configuration-related issues with Snowflake connection."""

    pass


def _get_dict_value(source: dict, key: str, default_value):
    return source.get(key) or default_value


def _get_mandatory_dict_value(source: dict, key: str):
    value = _get_dict_value(source, key, None)
    if value is None:
        raise SnowflakeConfigurationError(
            f'Required configuration attribute "{key}" not found'
        )
    return value


def _parse_snowflake_oauth_connection_details(
    linking_details: dict,
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    token_path = _get_mandatory_dict_value(linking_details, "tokenPath")
    try:
        token = Path(token_path).read_text().strip()
    except Exception as e:
        raise SnowflakeConfigurationError(
            f'Failed to read OAuth token from file "{token_path!s}": {e!s}'
        ) from e

    authenticator = _get_mandatory_dict_value(linking_details, "authenticator")
    if authenticator != OAUTH:
        raise SnowflakeConfigurationError(
            f'Unsupported authenticator "{authenticator}" for OAuth based configuration'
        )

    config = {
        "authenticator": authenticator,
        "account": _get_mandatory_dict_value(linking_details, "account"),
        "role": role or _get_mandatory_dict_value(linking_details, "role"),
        "warehouse": warehouse or _get_dict_value(linking_details, "warehouse", None),
        "database": database,
        "schema": schema,
        "client_session_keep_alive": True,
        "token": token,
    }

    return config


def _parse_snowflake_private_key_connection_details(
    linking_details: dict,
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    authenticator = _get_dict_value(linking_details, "authenticator", "SNOWFLAKE_JWT")
    if authenticator != "SNOWFLAKE_JWT":
        raise SnowflakeConfigurationError(
            f'Unsupported authenticator "{authenticator}" for private key based configuration'
        )

    config = {
        "authenticator": authenticator,
        "account": _get_mandatory_dict_value(linking_details, "account"),
        "user": _get_mandatory_dict_value(linking_details, "user"),
        "private_key_file": _get_mandatory_dict_value(
            linking_details, "privateKeyPath"
        ),
        "role": role or _get_dict_value(linking_details, "role", None),
        "warehouse": warehouse or _get_dict_value(linking_details, "warehouse", None),
        "database": database,
        "schema": schema,
        "client_session_keep_alive": True,
    }

    private_key_file_pwd = _get_dict_value(
        linking_details, "privateKeyPassphrase", None
    )
    if private_key_file_pwd is not None:
        config["private_key_file_pwd"] = private_key_file_pwd

    return config


def _get_snowflake_connection_details_from_file(
    config_file_path: Path,
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    if not config_file_path.exists():
        raise SnowflakeConfigurationError(
            f"Configuration file {config_file_path} not found"
        )

    try:
        import json

        config_json = json.loads(config_file_path.read_text())
    except Exception as e:
        raise SnowflakeConfigurationError(
            f"Failed to read authentication config as JSON from {config_file_path!s}: {e!s}"
        ) from e

    # Default to SNOWFLAKE_PRIVATE_KEY as old SPACE/Studio did not specify the "type" at all
    auth_type = _get_dict_value(config_json, "type", "SNOWFLAKE_PRIVATE_KEY")
    linking_details = _get_mandatory_dict_value(config_json, "linkingDetails")

    if auth_type in ("SNOWFLAKE_OAUTH_PARTNER", "SNOWFLAKE_OAUTH_CUSTOM"):
        return _parse_snowflake_oauth_connection_details(
            linking_details, role, warehouse, database, schema
        )

    if auth_type == "SNOWFLAKE_PRIVATE_KEY":
        return _parse_snowflake_private_key_connection_details(
            linking_details, role, warehouse, database, schema
        )

    raise SnowflakeConfigurationError(f'Configuration type "{auth_type}" not supported')
