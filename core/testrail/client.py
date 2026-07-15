# core/testrail/client.py

from __future__ import annotations

import time
from typing import Any

import requests

from core.logger import get_logger


log = get_logger("testrail.client")


class TestRailAPIError(RuntimeError):
    """
    Raised when communication with the TestRail API fails.
    """


class TestRailClient:
    """
    Handles communication with the TestRail REST API.

    Responsibilities:
        - Authentication
        - HTTP requests
        - Retry handling
        - Test run creation
        - Result upload
        - Test run closure
    """

    def __init__(self, config: dict[str, Any]):
        self.base_url = config["url"].rstrip("/")
        self.request_timeout = config["request_timeout"]
        self.verify_ssl = config["verify_ssl"]
        self.max_retries = config["max_retries"]

        self.session = requests.Session()

        # TestRail uses HTTP Basic authentication:
        # username/email + API key.
        self.session.auth = (
            config["user"],
            config["api_key"],
        )

        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _build_url(self, endpoint: str) -> str:
        """
        Builds the complete TestRail API URL.

        Example:
            https://company.testrail.io/index.php?/api/v2/get_run/12
        """

        clean_endpoint = endpoint.lstrip("/")

        return (
            f"{self.base_url}/index.php?"
            f"/api/v2/{clean_endpoint}"
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """
        Sends an authenticated API request to TestRail.

        Retries:
            - Network errors
            - HTTP 429 rate-limit responses
            - HTTP 5xx server errors
        """

        url = self._build_url(endpoint)

        for attempt in range(self.max_retries + 1):
            try:
                log.debug(
                    "Sending TestRail request: "
                    f"{method.upper()} {endpoint}"
                )

                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    json=payload,
                    timeout=self.request_timeout,
                    verify=self.verify_ssl,
                )

                # ----------------------------------------------------------
                # Rate-limit handling
                # ----------------------------------------------------------

                if response.status_code == 429:
                    if attempt >= self.max_retries:
                        raise TestRailAPIError(
                            "TestRail API rate limit exceeded "
                            "after all retry attempts."
                        )

                    retry_after = response.headers.get(
                        "Retry-After",
                        "1",
                    )

                    try:
                        wait_seconds = max(
                            int(retry_after),
                            1,
                        )
                    except ValueError:
                        wait_seconds = 1

                    log.warning(
                        "TestRail API rate limit reached. "
                        f"Retrying in {wait_seconds} second(s)."
                    )

                    time.sleep(wait_seconds)
                    continue

                # ----------------------------------------------------------
                # Server-error handling
                # ----------------------------------------------------------

                if 500 <= response.status_code < 600:
                    if attempt >= self.max_retries:
                        raise TestRailAPIError(
                            "TestRail server error: "
                            f"HTTP {response.status_code} - "
                            f"{response.text[:1000]}"
                        )

                    wait_seconds = attempt + 1

                    log.warning(
                        "TestRail server error: "
                        f"HTTP {response.status_code}. "
                        f"Retrying in {wait_seconds} second(s)."
                    )

                    time.sleep(wait_seconds)
                    continue

                # ----------------------------------------------------------
                # Other unsuccessful responses
                # ----------------------------------------------------------

                if not response.ok:
                    raise TestRailAPIError(
                        "TestRail API request failed: "
                        f"HTTP {response.status_code} - "
                        f"{response.text[:1000]}"
                    )

                if not response.content:
                    return {}

                try:
                    return response.json()

                except ValueError as error:
                    raise TestRailAPIError(
                        "TestRail returned an invalid JSON response."
                    ) from error

            except requests.RequestException as error:
                if attempt >= self.max_retries:
                    raise TestRailAPIError(
                        "Unable to connect to TestRail after "
                        f"{self.max_retries + 1} attempt(s): "
                        f"{error}"
                    ) from error

                wait_seconds = attempt + 1

                log.warning(
                    "TestRail connection error. "
                    f"Retrying in {wait_seconds} second(s)."
                )

                time.sleep(wait_seconds)

        raise TestRailAPIError(
            "TestRail request failed after all retry attempts."
        )


    # ======================================================================
    # TEST RUN OPERATIONS
    # ======================================================================

    def get_run(
        self,
        run_id: int,
    ) -> dict[str, Any]:
        """
        Returns an existing TestRail test run.
        """

        return self._request(
            method="GET",
            endpoint=f"get_run/{run_id}",
        )

    def create_run(
        self,
        project_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Creates a new TestRail test run.
        """

        return self._request(
            method="POST",
            endpoint=f"add_run/{project_id}",
            payload=payload,
        )

    def add_results_for_cases(
        self,
        run_id: int,
        results: list[dict[str, Any]],
    ) -> Any:
        """
        Uploads multiple automation results to a TestRail run.

        Each result must contain a TestRail case_id.
        """

        if not results:
            log.info(
                "No TestRail results supplied for upload."
            )
            return []

        return self._request(
            method="POST",
            endpoint=f"add_results_for_cases/{run_id}",
            payload={
                "results": results,
            },
        )

    def close_run(
        self,
        run_id: int,
    ) -> dict[str, Any]:
        """
        Closes an existing TestRail test run.
        """

        return self._request(
            method="POST",
            endpoint=f"close_run/{run_id}",
            payload={},
        )

    def close(self) -> None:
        """
        Closes the underlying HTTP session.
        """

        self.session.close()
        log.debug("TestRail HTTP session closed.")