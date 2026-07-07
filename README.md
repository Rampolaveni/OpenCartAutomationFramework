# OpenCart UI Automation Framework

Enterprise-style UI automation framework built with Python, Playwright, Pytest, Allure, and Jenkins.

## Tech Stack

- Python
- Playwright
- Pytest
- Allure Reports
- Jenkins
- Page Object Model
- DAO and Scenario layers

## Application

```text
https://tutorialsninja.com/demo/index.php?route=common/home
```

## Project Structure

```text
OpenCartAutomationFramework/
│
├── config/
│   ├── qa_config.py
│   ├── uat_config.py
│   ├── prod_config.py
│   ├── config_manager.py
│   └── allure_config.py
│
├── core/
│   ├── actions.py
│   ├── allure_report.py
│   ├── logger.py
│   ├── pageManager.py
│   └── paths.py
│
├── pageObjectLocators/
├── dao/
├── scenarios/
├── tests/
├── scripts/
│   └── run_tests_local.bat
│
├── reports/
│   ├── allure-results/
│   ├── allure-reports/
│   ├── junit/
│   ├── logs/
│   ├── screenshots/
│   ├── traces/
│   └── videos/
│
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Jenkinsfile
└── README.md
```

## Framework Layers

| Layer | Responsibility |
|---|---|
| `tests` | Test entry points, Allure metadata, Pytest markers |
| `scenarios` | Business flow, assertions, Allure steps |
| `dao` | Page actions such as click, fill, and read text |
| `pageObjectLocators` | Playwright locators only |
| `core/actions.py` | Reusable Playwright actions |
| `core/pageManager.py` | Creates and manages DAO objects |
| `core/paths.py` | Central report and project paths |
| `conftest.py` | Browser, context, page, config, and artifact fixtures |

## Environment Configuration

Execution settings are stored in:

```text
config/qa_config.py
config/uat_config.py
config/prod_config.py
```

Example:

```python
QA_CONFIG = {
    "env": "qa",
    "base_url": "https://tutorialsninja.com/demo/index.php?route=common/home",
    "browser": "chromium",
    "headed": True,
    "slow_mo": 0,
    "playwright_timeout": 30000,
    "viewport": {
        "width": 1366,
        "height": 768
    },
    "locale": "en-AU",
    "timezone_id": "Australia/Melbourne",
    "video": "retain-on-failure",
    "tracing": "retain-on-failure",
    "screenshot": "only-on-failure",
    "ignore_https_errors": True,
    "accept_downloads": True
}
```

Configuration priority:

```text
Environment config
        ↓
OS or Jenkins overrides
        ↓
Final runtime config
        ↓
conftest.py
```

Supported overrides:

```text
TEST_ENV
BASE_URL
BROWSER
HEADLESS
HEADED
SLOW_MO
PLAYWRIGHT_TIMEOUT
VIDEO
TRACING
SCREENSHOT
LOG_LEVEL
```

## Timeout Design

### Pytest timeout

Configured in `pytest.ini`:

```ini
--timeout=300
--timeout-method=thread
```

Controls the maximum duration of the entire test.

### Playwright timeout

Configured in environment files:

```python
"playwright_timeout": 30000
```

Controls how long Playwright waits for locators, clicks, fills, and navigation.

## Installation

Create and activate a virtual environment:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Playwright Chromium:

```bat
python -m playwright install chromium
```

## Running Tests

Run all QA tests:

```bat
python -m pytest --env=qa
```

Run by environment:

```bat
python -m pytest --env=uat
python -m pytest --env=prod
```

Run by marker:

```bat
python -m pytest -m smoke --env=qa
python -m pytest -m sanity --env=qa
python -m pytest -m regression --env=qa
```

Run one test file:

```bat
python -m pytest tests\test_LoginFunctionality.py --env=qa
```

Run one test:

```bat
python -m pytest tests\test_LoginFunctionality.py::test_userLogin --env=qa
```

## Pytest Markers

Markers are defined in `pytest.ini`.

```text
smoke
sanity
regression
login
register
search
product
```

Example:

```python
@pytest.mark.smoke
@pytest.mark.login
def test_user_login(pages):
    LoginScenarios(pages).verify_successful_login()
```

## Allure Reporting

Raw Allure results are generated in:

```text
reports/allure-results/
```

Generate the local HTML report:

```bat
allure generate reports\allure-results --clean -o reports\allure-reports
```

Open the report:

```bat
allure open reports\allure-reports
```

Complete local flow:

```bat
python -m pytest --env=qa --alluredir=reports\allure-results
allure generate reports\allure-results --clean -o reports\allure-reports
allure open reports\allure-reports
```

Or run:

```bat
scripts\run_tests_local.bat
```

## Allure Metadata

Static report settings are stored in:

```text
config/allure_config.py
```

Generated metadata files:

```text
reports/allure-results/environment.properties
reports/allure-results/executor.json
reports/allure-results/categories.json
```

`environment.properties` records the final runtime values used during the test run. It is report output, not a configuration source.

## Failure Artifacts

Failed tests can capture:

```text
reports/screenshots/
reports/traces/
reports/videos/
reports/logs/
```

These artifacts are attached to the corresponding Allure test result.

Open a Playwright trace:

```bat
playwright show-trace reports\traces\<trace-file>.zip
```

## Logging

Logs are stored in:

```text
reports/logs/
```

Set the log level:

```bat
set LOG_LEVEL=DEBUG
```

Supported levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

## Jenkins

The `Jenkinsfile` performs:

```text
Checkout
Create virtual environment
Install dependencies
Install Playwright browser
Prepare report folders
Run Pytest
Publish JUnit results
Publish Allure report
Archive failure artifacts
```

Supported Jenkins parameters:

```text
TEST_ENV
TEST_MARKER
BROWSER
HEADLESS
VIDEO
TRACING
SCREENSHOT
```

Jenkins publishes the report from:

```text
reports/allure-results/
```

Access it from:

```text
Jenkins
→ OpenCartAutomationFramework
→ Build Number
→ Allure Report
```

## Test Design Standard

Each test should include:

- Test case ID
- Business-readable title
- Epic
- Feature
- Story
- Severity
- Pytest markers
- Allure steps
- Clear assertion

Example:

```python
@allure.epic("OpenCart Web UI")
@allure.feature("Authentication")
@allure.story("Login")
@allure.title("TC_LOGIN_001 - Verify login using valid credentials")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.login
def test_user_login(pages):
    LoginScenarios(pages).verify_successful_login()
```

## Troubleshooting

### No tests selected

```text
collected 5 items / 5 deselected / 0 selected
```

The selected marker is not assigned to any tests.

### Playwright timeout

```text
Locator.fill: Timeout 30000ms exceeded
```

Check the locator, page navigation, visibility, frames, and application state before increasing the timeout.

### Allure report folder is empty

Pytest creates raw results only. Generate HTML with:

```bat
allure generate reports\allure-results --clean -o reports\allure-reports
```

### Reports created under `tests/reports`

Ensure:

- PyCharm working directory is the project root.
- `--alluredir` is not hardcoded as a relative path in `pytest.ini`.
- Report paths come from `core/paths.py`.

## Author

OpenCart UI Automation Framework  
QA Automation Project
