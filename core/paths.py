from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

REPORTS_DIR = ROOT_DIR / "reports"

ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
ALLURE_HISTORY_DIR = REPORTS_DIR / "allure-history"
ALLURE_REPORTS_DIR = REPORTS_DIR / "allure-reports"
HTML_REPORTS_DIR = REPORTS_DIR / "html-reports"

LOGS_DIR = REPORTS_DIR / "logs"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
TRACES_DIR = REPORTS_DIR / "traces"
VIDEOS_DIR = REPORTS_DIR / "videos"


def create_report_directories():
    directories = [
        REPORTS_DIR,
        ALLURE_RESULTS_DIR,
        ALLURE_HISTORY_DIR,
        ALLURE_REPORTS_DIR,
        HTML_REPORTS_DIR,
        LOGS_DIR,
        SCREENSHOTS_DIR,
        TRACES_DIR,
        VIDEOS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)