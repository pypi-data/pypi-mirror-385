from functools import cache

from gw_settings_management.settings_model import SettingsModel

@cache
def server_url() -> str:
    settings = SettingsModel()
    host = settings.server_host
    port = settings.server_port

    server_connection_string = f"http://{host}:{port}/"
    return server_connection_string

def get_endpoint(endpoint: str) -> str:
    server = server_url()
    if server.endswith("/") and endpoint.startswith("/"):
        endpoint = endpoint[1:]
    return f"{server}{endpoint}"

@cache
def database_url(*, short: bool = False) -> str:
    settings = SettingsModel()
    host = settings.database_host
    port = settings.database_port
    if short:
        database_connection_string = f"{host}:{port}"
    else:
        database_connection_string = f"'{database_user}:{database_password}@{host}:{port}"
    return database_connection_string

@cache
def database_name() -> str:
    settings = SettingsModel()
    return settings.database_name


@cache
def database_user() -> str:
    settings = SettingsModel()
    return settings.database_user

@cache
def database_password() -> str:
    settings = SettingsModel()
    return settings.database_password