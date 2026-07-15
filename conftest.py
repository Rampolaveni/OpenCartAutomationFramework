import os
import re
from pathlib import Path

import pytest
import allure
from playwright.sync_api import sync_playwright

from config.config_manager import ConfigManager
from core.pageManager import PageManager
from core.logger import get_logger, get_session_log_file
from core.paths import (
    ROOT_DIR,
    REPORTS_DIR,
    ALLURE_RESULTS_DIR,
    ALLURE_HISTORY_DIR,
    ALLURE_REPORTS_DIR,
    HTML_REPORTS_DIR,
    SCREENSHOTS_DIR,
    TRACES_DIR,
    VIDEOS_DIR,
    LOGS_DIR,
    create_report_directories,
)


log = get_logger("conftest")

pytest_plugins = [
    "core.testrail.pytest_plugin",
]

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Forces Allure results to always be generated under project-root/reports,
    regardless of whether tests are run from PyCharm, terminal, Jenkins, or tests/ directory.
    """
    create_report_directories()

    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(ALLURE_RESULTS_DIR)

# ─────────────────────────────────────────────────────────────────────────────
# PYTEST COMMAND LINE OPTIONS
# ─────────────────────────────────────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        choices=["qa", "uat", "prod"],
        help="Environment to run tests against: qa, uat, or prod"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST HOOK - REQUIRED FOR FAILURE DETECTION
# ─────────────────────────────────────────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    setattr(item, "rep_" + report.when, report)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER METHODS
# ─────────────────────────────────────────────────────────────────────────────

def safe_artifact_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", name)


def is_test_failed(request) -> bool:
    return (
        hasattr(request.node, "rep_call")
        and request.node.rep_call.failed
    )


def attach_file_to_allure(file_path: Path, name: str, attachment_type):
    try:
        if file_path and file_path.exists():
            allure.attach.file(
                str(file_path),
                name=name,
                attachment_type=attachment_type
            )
            log.info(f"Attached to Allure: {file_path.name}")

    except Exception as e:
        log.error(f"Failed to attach file to Allure: {e}")


def write_allure_environment_file(config: dict):
    try:
        environment_file = ALLURE_RESULTS_DIR / "environment.properties"

        content = [
            f"Environment={config['env']}",
            f"Base_URL={config['base_url']}",
            f"Browser={config['browser']}",
            f"Headed={config['headed']}",
            f"Playwright_Timeout={config['playwright_timeout']}",
            f"Locale={config['locale']}",
            f"Timezone={config['timezone_id']}",
            f"Video={config['video']}",
            f"Tracing={config['tracing']}",
            f"Screenshot={config['screenshot']}",
            f"CI={os.getenv('CI', 'false')}",
        ]

        environment_file.write_text("\n".join(content), encoding="utf-8")

    except Exception as e:
        log.error(f"Failed to write Allure environment file: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# ENV CONFIG FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def env_config(request):
    cli_env = request.config.getoption("env")
    env_name = cli_env or os.getenv("TEST_ENV", "qa")

    config = ConfigManager.get_config(env_name)

    log.info("─" * 80)
    log.info(f"Execution Environment : {config['env']}")
    log.info(f"Base URL              : {config['base_url']}")
    log.info(f"Browser               : {config['browser']}")
    log.info(f"Headed Mode           : {config['headed']}")
    log.info(f"Playwright Timeout    : {config['playwright_timeout']}")
    log.info(f"CI                    : {os.getenv('CI', 'false')}")
    log.info("─" * 80)

    # Makes the final runtime configuration available
    # to TestRail and other framework plugins.
    request.config._runtime_env_config = config
    write_allure_environment_file(config)

    return config


# ─────────────────────────────────────────────────────────────────────────────
# PLAYWRIGHT SESSION FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance():
    log.info("Starting Playwright session")

    playwright = sync_playwright().start()

    yield playwright

    playwright.stop()
    log.info("Playwright session stopped")


# ─────────────────────────────────────────────────────────────────────────────
# BROWSER FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser(env_config, playwright_instance):
    browser_name = env_config["browser"].lower()
    headed = env_config["headed"]
    slow_mo = env_config.get("slow_mo", 0)

    launch_options = {
        "headless": not headed,
        "slow_mo": slow_mo,
    }

    log.info(f"Launching browser: {browser_name} | headed={headed}")

    if browser_name == "chromium":
        browser_instance = playwright_instance.chromium.launch(**launch_options)

    elif browser_name == "firefox":
        browser_instance = playwright_instance.firefox.launch(**launch_options)

    elif browser_name == "webkit":
        browser_instance = playwright_instance.webkit.launch(**launch_options)

    else:
        raise ValueError(
            f"Unsupported browser: {browser_name}. "
            f"Allowed values: chromium, firefox, webkit"
        )

    yield browser_instance

    browser_instance.close()
    log.info(f"Browser closed: {browser_name}")


# ─────────────────────────────────────────────────────────────────────────────
# BROWSER CONTEXT FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def browser_context(request, browser, env_config):
    test_name = safe_artifact_name(request.node.nodeid)

    video_option = env_config["video"]
    tracing_option = env_config["tracing"]
    playwright_timeout = env_config["playwright_timeout"]

    context_options = {
        "viewport": env_config["viewport"],
        "ignore_https_errors": env_config["ignore_https_errors"],
        "accept_downloads": env_config["accept_downloads"],
        "locale": env_config["locale"],
        "timezone_id": env_config["timezone_id"],
    }

    if video_option in ["on", "retain-on-failure"]:
        context_options["record_video_dir"] = str(VIDEOS_DIR)
        context_options["record_video_size"] = env_config["viewport"]

    context = browser.new_context(**context_options)

    context.set_default_timeout(playwright_timeout)
    context.set_default_navigation_timeout(playwright_timeout)

    log.info(f"Browser context created for: {request.node.name}")

    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True
        )
        log.info("Tracing started")

    yield context

    test_failed = is_test_failed(request)

    # Trace handling
    try:
        if tracing_option == "on":
            trace_path = TRACES_DIR / f"{test_name}_trace.zip"

            context.tracing.stop(path=str(trace_path))

            attach_file_to_allure(
                trace_path,
                "trace.zip",
                allure.attachment_type.ZIP
            )

            log.info(f"Trace saved: {trace_path.name}")

        elif tracing_option == "retain-on-failure":
            if test_failed:
                trace_path = TRACES_DIR / f"{test_name}_trace.zip"

                context.tracing.stop(path=str(trace_path))

                attach_file_to_allure(
                    trace_path,
                    "failure_trace.zip",
                    allure.attachment_type.ZIP
                )

                log.warning(f"Failure trace saved: {trace_path.name}")

            else:
                context.tracing.stop()
                log.info("Trace discarded because test passed")

    except Exception as e:
        log.error(f"Trace handling failed: {e}")

    video = getattr(request.node, "_playwright_video", None)

    context.close()
    log.info(f"Browser context closed for: {request.node.name}")

    # Video handling
    if video_option == "on" or (video_option == "retain-on-failure" and test_failed):
        try:
            if video:
                video_path = Path(video.path())

                attach_file_to_allure(
                    video_path,
                    "test_video",
                    allure.attachment_type.WEBM
                )

                log.info(f"Video handled: {video_path.name}")

        except Exception as e:
            log.error(f"Video attach failed: {e}")

    # Log handling on failure
    if test_failed:
        try:
            log_file = Path(get_session_log_file())

            attach_file_to_allure(
                log_file,
                "test_run.log",
                allure.attachment_type.TEXT
            )

        except Exception as e:
            log.error(f"Log attach failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def page(request, browser_context, env_config):
    base_url = env_config["base_url"]

    test_name = request.node.name
    safe_test_name = safe_artifact_name(request.node.nodeid)

    log.info("─" * 80)
    log.info(f"TEST START : {test_name}")
    log.info(f"ENV        : {env_config['env']}")
    log.info(f"BASE URL   : {base_url}")

    page = browser_context.new_page()

    page.goto(base_url, wait_until="domcontentloaded")

    if page.video:
        setattr(request.node, "_playwright_video", page.video)

    yield page

    test_failed = is_test_failed(request)

    # Screenshot handling
    if test_failed and env_config["screenshot"] in ["on", "only-on-failure"]:
        try:
            screenshot_path = SCREENSHOTS_DIR / f"{safe_test_name}_failure.png"

            page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            attach_file_to_allure(
                screenshot_path,
                "failure_screenshot",
                allure.attachment_type.PNG
            )

            log.warning(f"Failure screenshot saved: {screenshot_path.name}")

        except Exception as e:
            log.error(f"Screenshot capture failed: {e}")

    status = "FAILED ❌" if test_failed else "PASSED ✅"
    log.info(f"TEST STATUS: {status}")
    log.info(f"TEST END   : {test_name}")

    try:
        page.close()

    except Exception as e:
        log.error(f"Page close failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE MANAGER FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def pages(page):
    return PageManager(page)