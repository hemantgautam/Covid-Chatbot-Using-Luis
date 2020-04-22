import os
from config.config_reader import ConfigReader


class DefaultConfig:
    """ Bot Configuration """
    config_reader = ConfigReader()
    configuration = config_reader.read_config()
    MicrosoftAppId = configuration['MicrosoftAppId']
    MicrosoftAppPassword = configuration['MicrosoftAppPassword']
    APP_ID = os.environ.get("MicrosoftAppId", MicrosoftAppId)
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", MicrosoftAppPassword)
    CONNECTION_NAME = os.environ.get("ConnectionName", "")
