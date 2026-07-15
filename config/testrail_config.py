# config/testrail_config.py

from __future__ import annotations

import os
from typing import Any


def to_bool(
    value: str | bool | None,
    default: bool = False,
) -> bool:
    """
    Converts environment-variable values to Boolean.

    Examples:
        "true"  -> True
        "1"     -> True
        "yes"   -> True
        "false" -> False
        None    -> default value
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "y",
        "on",
    }


def optional_int(
    value: str | int | None,
) -> int | None:
    """
    Converts an optional environment-variable value to integer.
    """

    if value is None:
        return None

    if str(value).strip() == "":
        return None

    return int(value)


def get_testrail_config(
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Builds the final TestRail configuration.

    TestRail credentials and IDs are loaded from environment
    variables rather than being stored in source code.

    runtime_config contains the final QA/UAT/PROD configuration
    loaded by ConfigManager.
    """

    runtime_config = runtime_config or {}

    environment = str(
        runtime_config.get("env")
        or os.getenv("TEST_ENV", "qa")
    ).upper()

    browser = str(
        runtime_config.get("browser")
        or os.getenv("BROWSER", "chromium")
    )

    build_number = os.getenv(
        "BUILD_NUMBER",
        "LOCAL",
    )

    default_run_name = (
        f"OpenCart Automation | "
        f"{environment} | "
        f"{browser} | "
        f"Build {build_number}"
    )

    config = {
        # Enables or disables TestRail integration.
        "enabled": to_bool(
            os.getenv("TESTRAIL_ENABLED"),
            default=False,
        ),

        # TestRail connection details.
        "url": os.getenv(
            "TESTRAIL_URL",
            "",
        ).rstrip("/"),

        "user": os.getenv(
            "TESTRAIL_USER",
            "",
        ),

        "api_key": os.getenv(
            "TESTRAIL_API_KEY",
            "",
        ),

        # TestRail project, suite and run details.
        "project_id": optional_int(
            os.getenv("TESTRAIL_PROJECT_ID")
        ),

        "suite_id": optional_int(
            os.getenv("TESTRAIL_SUITE_ID")
        ),

        "run_id": optional_int(
            os.getenv("TESTRAIL_RUN_ID")
        ),

        # Run settings.
        "run_name": os.getenv(
            "TESTRAIL_RUN_NAME",
            default_run_name,
        ),

        "close_run": to_bool(
            os.getenv("TESTRAIL_CLOSE_RUN"),
            default=False,
        ),

        "version": os.getenv(
            "TESTRAIL_VERSION",
            os.getenv("BUILD_NUMBER", ""),
        ),

        # API request settings.
        "verify_ssl": to_bool(
            os.getenv("TESTRAIL_VERIFY_SSL"),
            default=True,
        ),

        "request_timeout": int(
            os.getenv(
                "TESTRAIL_REQUEST_TIMEOUT",
                "30",
            )
        ),

        "max_retries": int(
            os.getenv(
                "TESTRAIL_MAX_RETRIES",
                "3",
            )
        ),

        # Determines whether a TestRail API failure should fail
        # the complete Pytest execution.
        "fail_on_error": to_bool(
            os.getenv("TESTRAIL_FAIL_ON_ERROR"),
            default=False,
        ),

        # Default TestRail status IDs.
        "status_passed": int(
            os.getenv(
                "TESTRAIL_STATUS_PASSED",
                "1",
            )
        ),

        "status_blocked": int(
            os.getenv(
                "TESTRAIL_STATUS_BLOCKED",
                "2",
            )
        ),

        "status_retest": int(
            os.getenv(
                "TESTRAIL_STATUS_RETEST",
                "4",
            )
        ),

        "status_failed": int(
            os.getenv(
                "TESTRAIL_STATUS_FAILED",
                "5",
            )
        ),
    }

    if config["enabled"]:
        validate_testrail_config(config)

    return config


def validate_testrail_config(
    config: dict[str, Any],
) -> None:
    """
    Validates required TestRail settings only when the
    integration is enabled.
    """

    missing_fields = []

    required_connection_fields = [
        "url",
        "user",
        "api_key",
    ]

    for field in required_connection_fields:
        if not config.get(field):
            missing_fields.append(field)

    # Existing run:
    # TESTRAIL_RUN_ID is sufficient.
    #
    # New run:
    # TESTRAIL_PROJECT_ID is required.
    if not config.get("run_id") and not config.get("project_id"):
        missing_fields.append(
            "project_id or run_id"
        )

    if missing_fields:
        raise ValueError(
            "Missing TestRail configuration: "
            + ", ".join(missing_fields)
        )