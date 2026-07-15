# core/testrail/reporter.py

from __future__ import annotations

import os
from typing import Any

from core.logger import get_logger
from core.testrail.client import TestRailClient


log = get_logger("testrail.reporter")


class TestRailReporter:
    """
    Converts automation results into TestRail results and publishes them.

    Responsibilities:
        - Create a new TestRail run
        - Reuse an existing TestRail run
        - Build stakeholder-readable result comments
        - Convert execution duration to TestRail elapsed format
        - Upload results in bulk
        - Optionally close a newly created run
    """

    def __init__(
        self,
        config: dict[str, Any],
        runtime_config: dict[str, Any] | None = None,
    ):
        self.config = config
        self.runtime_config = runtime_config or {}

        self.client = TestRailClient(config)

    # ======================================================================
    # RESULT FORMATTING
    # ======================================================================

    @staticmethod
    def format_elapsed(seconds: float) -> str:
        """
        Converts seconds into a TestRail-friendly elapsed value.

        Examples:
            0.4  -> 1s
            45   -> 45s
            75   -> 1m 15s
            3665 -> 1h 1m 5s
        """

        total_seconds = max(1, round(seconds))

        hours, remaining_seconds = divmod(
            total_seconds,
            3600,
        )

        minutes, seconds = divmod(
            remaining_seconds,
            60,
        )

        elapsed_parts = []

        if hours:
            elapsed_parts.append(f"{hours}h")

        if minutes:
            elapsed_parts.append(f"{minutes}m")

        if seconds or not elapsed_parts:
            elapsed_parts.append(f"{seconds}s")

        return " ".join(elapsed_parts)

    def build_result_comment(
        self,
        result: dict[str, Any],
    ) -> str:
        """
        Builds a readable TestRail result comment.

        No credentials or sensitive values are included.
        """

        environment = str(
            self.runtime_config.get("env")
            or os.getenv("TEST_ENV", "qa")
        ).upper()

        browser = str(
            self.runtime_config.get("browser")
            or os.getenv("BROWSER", "chromium")
        )

        headed = self.runtime_config.get("headed")

        execution_mode = (
            "Headed"
            if headed is True
            else "Headless"
            if headed is False
            else "Not specified"
        )

        job_name = os.getenv("JOB_NAME", "")
        build_number = os.getenv("BUILD_NUMBER", "")
        build_url = os.getenv("BUILD_URL", "")
        git_commit = os.getenv("GIT_COMMIT", "")

        comment_lines = [
            "Automated Test Execution",
            "",
            f"Test: {result['nodeid']}",
            f"Outcome: {result['outcome'].upper()}",
            f"Environment: {environment}",
            f"Browser: {browser}",
            f"Execution Mode: {execution_mode}",
        ]

        if job_name:
            comment_lines.append(
                f"Jenkins Job: {job_name}"
            )

        if build_number:
            comment_lines.append(
                f"Build Number: {build_number}"
            )

        if build_url:
            comment_lines.append(
                f"Build URL: {build_url}"
            )

        if git_commit:
            comment_lines.append(
                f"Git Commit: {git_commit}"
            )

        failure_details = result.get("failure")

        if failure_details:
            comment_lines.extend(
                [
                    "",
                    "Failure Details:",
                    str(failure_details)[:5000],
                ]
            )

        return "\n".join(comment_lines)

    # ======================================================================
    # TEST RUN MANAGEMENT
    # ======================================================================

    def create_run(
        self,
        case_ids: list[int],
    ) -> dict[str, Any]:
        """
        Creates a TestRail run containing only the automated cases
        executed in the current Pytest session.
        """

        unique_case_ids = sorted(set(case_ids))

        if not unique_case_ids:
            raise ValueError(
                "Cannot create a TestRail run without case IDs."
            )

        payload: dict[str, Any] = {
            "name": self.config["run_name"],
            "description": (
                "Automatically created by the OpenCart "
                "Playwright and Pytest automation framework."
            ),
            "include_all": False,
            "case_ids": unique_case_ids,
        }

        suite_id = self.config.get("suite_id")

        if suite_id is not None:
            payload["suite_id"] = suite_id

        run = self.client.create_run(
            project_id=self.config["project_id"],
            payload=payload,
        )

        log.info(
            "TestRail run created: "
            f"ID={run.get('id')} | "
            f"Name={run.get('name')}"
        )

        return run

    def resolve_run(
        self,
        case_ids: list[int],
    ) -> tuple[int, bool, dict[str, Any]]:
        """
        Returns the TestRail run to use.

        Returns:
            run_id
            run_created
            run_details
        """

        existing_run_id = self.config.get("run_id")

        if existing_run_id:
            run_details = self.client.get_run(
                existing_run_id
            )

            log.info(
                "Using existing TestRail run: "
                f"ID={existing_run_id} | "
                f"Name={run_details.get('name')}"
            )

            return (
                int(existing_run_id),
                False,
                run_details,
            )

        run_details = self.create_run(case_ids)

        return (
            int(run_details["id"]),
            True,
            run_details,
        )

    # ======================================================================
    # PAYLOAD CREATION
    # ======================================================================

    def build_results_payload(
        self,
        execution_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Converts internal execution results into the TestRail API format.

        One automated test can be linked to one or more TestRail cases.
        """

        results_payload = []

        for result in execution_results:
            case_ids = result.get("case_ids", [])

            for case_id in case_ids:
                payload: dict[str, Any] = {
                    "case_id": int(case_id),
                    "status_id": int(result["status_id"]),
                    "comment": self.build_result_comment(
                        result
                    ),
                    "elapsed": self.format_elapsed(
                        result.get("duration", 0)
                    ),
                }

                version = self.config.get("version")

                if version:
                    payload["version"] = version

                results_payload.append(payload)

        return results_payload

    # ======================================================================
    # RESULT PUBLISHING
    # ======================================================================

    def publish(
        self,
        execution_results: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Publishes the completed Pytest execution to TestRail.

        Flow:
            1. Extract case IDs
            2. Create or reuse a TestRail run
            3. Build result payloads
            4. Upload all results in one request
            5. Optionally close a newly created run
        """

        if not execution_results:
            log.info(
                "No TestRail-linked test results were found."
            )

            self.client.close()
            return None

        all_case_ids = sorted(
            {
                int(case_id)
                for result in execution_results
                for case_id in result.get(
                    "case_ids",
                    [],
                )
            }
        )

        if not all_case_ids:
            log.info(
                "No TestRail case IDs were found."
            )

            self.client.close()
            return None

        try:
            run_id, run_created, run_details = (
                self.resolve_run(all_case_ids)
            )

            results_payload = (
                self.build_results_payload(
                    execution_results
                )
            )

            if not results_payload:
                log.info(
                    "No TestRail result payloads were created."
                )

                return None

            self.client.add_results_for_cases(
                run_id=run_id,
                results=results_payload,
            )

            log.info(
                f"Uploaded {len(results_payload)} "
                f"result(s) to TestRail run {run_id}."
            )

            run_closed = False

            if (
                run_created
                and self.config.get("close_run")
            ):
                self.client.close_run(run_id)

                run_closed = True

                log.info(
                    f"TestRail run closed: {run_id}"
                )

            return {
                "run_id": run_id,
                "run_name": run_details.get("name", ""),
                "run_url": run_details.get("url", ""),
                "run_created": run_created,
                "run_closed": run_closed,
                "result_count": len(results_payload),
            }

        finally:
            self.client.close()