import os
from copy import deepcopy

from config.qa_config import QA_CONFIG
from config.uat_config import UAT_CONFIG
from config.prod_config import PROD_CONFIG


class ConfigManager:

    CONFIG_MAP = {
        "qa": QA_CONFIG,
        "uat": UAT_CONFIG,
        "prod": PROD_CONFIG,
    }

    @staticmethod
    def get_config(env_name: str) -> dict:
        env_name = env_name.lower().strip()

        if env_name not in ConfigManager.CONFIG_MAP:
            raise ValueError(
                f"Invalid environment: {env_name}. "
                f"Allowed values are: qa, uat, prod"
            )

        config = deepcopy(ConfigManager.CONFIG_MAP[env_name])
        ConfigManager.apply_environment_overrides(config)

        return config

    @staticmethod
    def apply_environment_overrides(config: dict):
        """
        Allows CI/CD pipeline values to override config files.

        Example GitHub Actions env vars:
            TEST_ENV=qa
            BROWSER=chromium
            HEADLESS=true
            BASE_URL=https://example.com
            VIDEO=retain-on-failure
            TRACING=retain-on-failure
        """

        if os.getenv("BASE_URL"):
            config["base_url"] = os.getenv("BASE_URL")

        if os.getenv("BROWSER"):
            config["browser"] = os.getenv("BROWSER")

        if os.getenv("HEADLESS"):
            config["headed"] = not ConfigManager.to_bool(os.getenv("HEADLESS"))

        if os.getenv("HEADED"):
            config["headed"] = ConfigManager.to_bool(os.getenv("HEADED"))

        if os.getenv("SLOW_MO"):
            config["slow_mo"] = int(os.getenv("SLOW_MO"))

        if os.getenv("PLAYWRIGHT_TIMEOUT"):
            config["playwright_timeout"] = int(os.getenv("PLAYWRIGHT_TIMEOUT"))

        if os.getenv("VIDEO"):
            config["video"] = os.getenv("VIDEO")

        if os.getenv("TRACING"):
            config["tracing"] = os.getenv("TRACING")

        if os.getenv("SCREENSHOT"):
            config["screenshot"] = os.getenv("SCREENSHOT")

        if os.getenv("VALID_EMAIL"):
            config["credentials"]["valid_email"] = os.getenv("VALID_EMAIL")

        if os.getenv("VALID_PASSWORD"):
            config["credentials"]["valid_password"] = os.getenv("VALID_PASSWORD")

    @staticmethod
    def to_bool(value: str) -> bool:
        return str(value).lower().strip() in ["true", "1", "yes", "y"]