# core/testrail/pytest_plugin.py

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pytest

from config.testrail_config import get_testrail_config
from core.logger import get_logger
from core.testrail.reporter import TestRailReporter


log = get_logger("testrail.pytest_plugin")


# ============================================================================
# PLUGIN INITIALISATION
# ============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """
    Creates session-level storage for:

    1. Pytest test-to-TestRail case mappings
    2. Setup, call and teardown execution results
    """

    config._testrail_case_map = {}
    config._testrail_phase_reports = defaultdict(dict)


# ============================================================================
# TESTRAIL CASE-ID HANDLING
# ============================================================================

def normalise_case_id(value: Any) -> int:
    """
    Converts supported TestRail case-ID formats to integers.

    Supported formats:
        101
        "101"
        "C101"
        "c101"
    """

    cleaned_value = str(value).strip().upper()

    if cleaned_value.startswith("C"):
        cleaned_value = cleaned_value[1:]

    if not cleaned_value.isdigit():
        raise ValueError(
            f"Invalid TestRail case ID: {value}. "
            "Use formats such as 101 or C101."
        )

    return int(cleaned_value)


def extract_case_ids(item: pytest.Item) -> list[int]:
    """
    Reads TestRail case IDs from a test marker.

    Supported marker formats:

        @pytest.mark.testrail(case_id=101)

        @pytest.mark.testrail(case_id="C101")

        @pytest.mark.testrail(case_ids=[101, 102])

        @pytest.mark.testrail(101)
    """

    marker = item.get_closest_marker("testrail")

    if marker is None:
        return []

    raw_case_ids = marker.kwargs.get("case_ids")

    if raw_case_ids is None:
        raw_case_ids = marker.kwargs.get("case_id")

    if raw_case_ids is None and marker.args:
        raw_case_ids = marker.args[0]

    if raw_case_ids is None:
        raise ValueError(
            f"TestRail marker on '{item.nodeid}' does not contain "
            "'case_id' or 'case_ids'."
        )

    if isinstance(raw_case_ids, (list, tuple, set)):
        case_ids = [
            normalise_case_id(case_id)
            for case_id in raw_case_ids
        ]
    else:
        case_ids = [
            normalise_case_id(raw_case_ids)
        ]

    if not case_ids:
        raise ValueError(
            f"No TestRail case IDs were supplied for '{item.nodeid}'."
        )

    return list(dict.fromkeys(case_ids))


# ============================================================================
# TEST COLLECTION
# ============================================================================

def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """
    Creates a mapping between Pytest tests and TestRail cases.

    Tests without the TestRail marker continue to run normally,
    but their results are not published to TestRail.
    """

    case_map = config._testrail_case_map

    for item in items:
        case_ids = extract_case_ids(item)

        if not case_ids:
            continue

        case_map[item.nodeid] = case_ids

        log.debug(
            f"Mapped Pytest test '{item.nodeid}' "
            f"to TestRail case(s): {case_ids}"
        )


# ============================================================================
# PYTEST RESULT CAPTURE
# ============================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo,
):
    """
    Captures the result of each Pytest phase:

        setup
        call
        teardown

    Capturing all phases ensures fixture, browser and teardown failures
    are also published to TestRail.
    """

    outcome = yield
    report = outcome.get_result()

    phase_reports = item.config._testrail_phase_reports

    phase_reports[item.nodeid][report.when] = {
        "outcome": report.outcome,
        "duration": report.duration,
        "failure": (
            str(report.longrepr)
            if report.failed
            else ""
        ),
        "was_xfail": bool(
            getattr(report, "wasxfail", False)
        ),
    }


# ============================================================================
# STATUS MAPPING
# ============================================================================

def build_execution_result(
    nodeid: str,
    case_ids: list[int],
    phases: dict[str, dict[str, Any]],
    testrail_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Converts Pytest phase results into one final TestRail result.

    Status mapping:

        Pytest passed  -> TestRail Passed
        Pytest failed  -> TestRail Failed
        Pytest skipped -> TestRail Blocked
    """

    setup_phase = phases.get("setup", {})
    call_phase = phases.get("call", {})
    teardown_phase = phases.get("teardown", {})

    phase_values = [
        phase
        for phase in [
            setup_phase,
            call_phase,
            teardown_phase,
        ]
        if phase
    ]

    failed_phase = next(
        (
            phase
            for phase in phase_values
            if phase.get("outcome") == "failed"
        ),
        None,
    )

    skipped_phase = next(
        (
            phase
            for phase in phase_values
            if phase.get("outcome") == "skipped"
        ),
        None,
    )

    if failed_phase:
        final_outcome = "failed"
        status_id = testrail_config["status_failed"]
        failure = failed_phase.get("failure", "")

    elif skipped_phase:
        final_outcome = "blocked"
        status_id = testrail_config["status_blocked"]
        failure = ""

    elif call_phase.get("outcome") == "passed":
        final_outcome = "passed"
        status_id = testrail_config["status_passed"]
        failure = ""

    else:
        final_outcome = "blocked"
        status_id = testrail_config["status_blocked"]
        failure = ""

    total_duration = sum(
        float(phase.get("duration", 0))
        for phase in phase_values
    )

    return {
        "nodeid": nodeid,
        "case_ids": case_ids,
        "outcome": final_outcome,
        "status_id": status_id,
        "duration": total_duration,
        "failure": failure,
    }


# ============================================================================
# SESSION-END PUBLISHING
# ============================================================================

def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,
) -> None:
    """
    Publishes TestRail-linked results after the Pytest session completes.

    Publishing occurs once per execution rather than once per test.
    """

    pytest_config = session.config

    # Prevent duplicate publishing from pytest-xdist workers.
    if hasattr(pytest_config, "workerinput"):
        return

    runtime_config = getattr(
        pytest_config,
        "_runtime_env_config",
        {},
    )

    testrail_config: dict[str, Any] | None = None

    try:
        testrail_config = get_testrail_config(
            runtime_config=runtime_config
        )

        if not testrail_config["enabled"]:
            log.info("TestRail integration is disabled.")
            return

        case_map = getattr(
            pytest_config,
            "_testrail_case_map",
            {},
        )

        phase_reports = getattr(
            pytest_config,
            "_testrail_phase_reports",
            {},
        )

        execution_results = []

        for nodeid, case_ids in case_map.items():
            phases = phase_reports.get(nodeid, {})

            if not phases:
                log.warning(
                    "No execution result was captured for "
                    f"TestRail-linked test: {nodeid}"
                )
                continue

            execution_result = build_execution_result(
                nodeid=nodeid,
                case_ids=case_ids,
                phases=phases,
                testrail_config=testrail_config,
            )

            execution_results.append(
                execution_result
            )

        reporter = TestRailReporter(
            config=testrail_config,
            runtime_config=runtime_config,
        )

        published_run = reporter.publish(
            execution_results
        )

        if not published_run:
            return

        log.info(
            "TestRail publishing completed successfully. "
            f"Run ID: {published_run['run_id']} | "
            f"Results: {published_run['result_count']}"
        )

        if published_run.get("run_url"):
            log.info(
                "TestRail run URL: "
                f"{published_run['run_url']}"
            )

    except Exception as error:
        log.exception(
            f"TestRail publishing failed: {error}"
        )

        if (
            testrail_config
            and testrail_config.get("fail_on_error")
        ):
            session.exitstatus = pytest.ExitCode.TESTS_FAILED