import os

from dotenv import load_dotenv


class SettingsModel:

    def __init__(self):
        load_dotenv(os.environ.get("APP_ENVIRONMENT"))
        self.database_host = os.getenv('DATABASE_HOST', "<HOST>")
        self.database_port = os.getenv('DATABASE_PORT', "<PORT>")
        self.database_user = os.getenv('DATABASE_USER', "<USER>")
        self.database_password = os.getenv('DATABASE_PASSWORD', "<PASSWORD>")
        self.database_name = os.getenv('DATABASE_NAME', "<DATABASE_NAME>")
        self.server_host = os.getenv('SERVER_HOST', "<HOST>")
        self.server_port = os.getenv('SERVER_PORT', "<PORT>")



