# OpenCart UI Automation Framework

Enterprise-style UI automation framework built with Python, Playwright, Pytest, Allure, TestRail, and Jenkins.

## Tech Stack

- Python
- Playwright
- Pytest
- Page Object Model
- DAO and Scenario layers
- Allure Reports
- TestRail
- Jenkins


## Application Under Test

```text
https://tutorialsninja.com/demo/index.php?route=common/home
```

---

## Project Structure

```text
OpenCartAutomationFramework/
│
├── config/
│   ├── __init__.py
│   ├── qa_config.py
│   ├── uat_config.py
│   ├── prod_config.py
│   ├── config_manager.py
│   └── testrail_config.py
│
├── core/
│   ├── __init__.py
│   ├── actions.py
│   ├── allure_report.py
│   ├── logger.py
│   ├── pageManager.py
│   ├── paths.py
│   │
│   └── testrail/
│       ├── __init__.py
│       ├── client.py
│       ├── reporter.py
│       └── pytest_plugin.py
│
├── pageObjectLocators/
├── dao/
├── scenarios/
├── tests/
│
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
├── .gitignore
└── README.md
```

---

## Framework Layers

| Layer | Responsibility |
|---|---|
| `tests` | Test entry points, Allure metadata, Pytest markers, TestRail case mapping |
| `scenarios` | Business workflows, assertions, and Allure steps |
| `dao` | Page-level actions such as click, fill, select, and read text |
| `pageObjectLocators` | Playwright locators only |
| `core/actions.py` | Reusable Playwright actions |
| `core/pageManager.py` | Creates and manages DAO objects |
| `core/paths.py` | Central project and report paths |
| `core/allure_report.py` | Generates Allure metadata |
| `core/testrail` | Creates TestRail runs and publishes execution results |
| `conftest.py` | Browser, page, environment, reporting, and artifact fixtures |

---

## Execution Flow

```text
Pytest Test
    ↓
Scenario
    ↓
DAO
    ↓
Core Actions
    ↓
Playwright Browser
```

Reporting flow:

```text
Pytest execution
    ├── Allure detailed report
    ├── JUnit Jenkins summary
    └── TestRail execution results
```

---

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
QA / UAT / PROD config
        ↓
OS or Jenkins environment-variable overrides
        ↓
Final runtime configuration
        ↓
conftest.py fixtures
```

Supported execution overrides:

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

---

## Timeout Design

### Pytest timeout

Configured in `pytest.ini`:

```ini
--timeout=300
--timeout-method=thread
```

Controls the maximum duration of the complete test.

### Playwright timeout

Configured in the environment files:

```python
"playwright_timeout": 30000
```

Controls how long Playwright waits for locators, clicks, fills, and navigation.

---

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

Install Chromium:

```bat
python -m playwright install chromium
```

Install all supported browsers:

```bat
python -m playwright install
```

---

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

---

## Pytest Markers

Markers are registered in `pytest.ini`.

```text
smoke
sanity
regression
login
register
search
product
testrail
```

Example:

```python
@pytest.mark.smoke
@pytest.mark.login
@pytest.mark.testrail(case_id=108)
def test_userLogin(pages):
    LoginScenarios(pages).verify_successful_login()
```

`case_id=108` links the test to TestRail case `C108`.

Tests without the TestRail marker still execute normally but are not published to TestRail.

---

## Allure Reporting

Raw Allure results are generated in:

```text
reports/allure-results/
```

Run tests with Allure:

```bat
python -m pytest --env=qa --alluredir=reports\allure-results
```

Generate the HTML report:

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
<img width="1855" height="881" alt="Screenshot 2026-07-15 202910" src="https://github.com/user-attachments/assets/492c3dae-f4c2-420c-9276-4f71752dd5bc" />


```

---

## Allure Metadata

Static Allure settings are stored in:

```text
config/allure_config.py
```

Generated metadata files:

```text
reports/allure-results/environment.properties
reports/allure-results/executor.json
reports/allure-results/categories.json
```

`environment.properties` records the final runtime configuration used during the execution. It is report output, not a configuration source.

---

## TestRail Integration

TestRail configuration is loaded from:

```text
config/testrail_config.py
```

TestRail implementation:

```text
core/testrail/client.py
core/testrail/reporter.py
core/testrail/pytest_plugin.py
```

### Responsibilities

| File | Responsibility |
|---|---|
| `testrail_config.py` | Reads and validates TestRail environment variables |
| `client.py` | Handles TestRail API requests |
| `reporter.py` | Creates runs and publishes results |
| `pytest_plugin.py` | Captures Pytest results and maps them to TestRail cases |

### TestRail flow

```text
@pytest.mark.testrail(case_id=108)
        ↓
Pytest executes the test
        ↓
Plugin captures setup, call, and teardown results
        ↓
Reporter creates or reuses a TestRail run
        ↓
Results are uploaded in bulk
        ↓
Run is optionally closed
```

### Status mapping

```text
Pytest Passed  → TestRail Passed
Pytest Failed  → TestRail Failed
Pytest Skipped → TestRail Blocked
```

### Required TestRail variables

```text
TESTRAIL_ENABLED
TESTRAIL_URL
TESTRAIL_USER
TESTRAIL_API_KEY
TESTRAIL_PROJECT_ID
TESTRAIL_RUN_ID
TESTRAIL_CLOSE_RUN
TESTRAIL_FAIL_ON_ERROR
TESTRAIL_VERSION
```

`TESTRAIL_RUN_ID` is optional.

When it is not supplied, the framework creates a new TestRail run.

---

## Local TestRail Execution

Set TestRail values as environment variables.

PowerShell example:

```powershell
$env:TESTRAIL_ENABLED = "true"
$env:TESTRAIL_URL = "https://opencart.testrail.io"
$env:TESTRAIL_USER = "your-testrail-email"
$env:TESTRAIL_API_KEY = "your-api-key"
$env:TESTRAIL_PROJECT_ID = "2"
$env:TESTRAIL_CLOSE_RUN = "false"
$env:TESTRAIL_FAIL_ON_ERROR = "false"
```

Run the tests:

```powershell
python -m pytest tests --env=qa -s
```

Expected result:

```text
One TestRail run created
Linked cases added
Execution results uploaded
Passed, Failed, or Blocked status displayed
```

Do not store the TestRail API key in:

```text
GitHub
README.md
Jenkinsfile
qa_config.py
testrail_config.py
```
<img width="1885" height="840" alt="Screenshot 2026-07-15 203024" src="https://github.com/user-attachments/assets/3cde0664-b075-4507-9ea6-9994b6b00996" />


---

## Failure Artifacts

Failed tests can capture:

```text
reports/screenshots/
reports/traces/
reports/videos/
reports/logs/
```

These artifacts are attached to the corresponding Allure result.

Open a Playwright trace:

```bat
playwright show-trace reports\traces\<trace-file>.zip
```

---

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

---

## Jenkins Pipeline

The `Jenkinsfile` performs:

```text
Checkout source code
Create virtual environment
Install dependencies
Install Playwright browser
Prepare report folders
Load TestRail credentials
Run Pytest
Publish TestRail results
Publish JUnit results
Publish Allure report
Archive failure artifacts
```

### Jenkins parameters

```text
TEST_ENV
TEST_MARKER
BROWSER
HEADLESS
VIDEO
TRACING
SCREENSHOT
TESTRAIL_ENABLED
TESTRAIL_CLOSE_RUN
TESTRAIL_FAIL_ON_ERROR
```

### TestRail Jenkins credential

Create a Jenkins credential:

```text
Kind: Username with password
ID: testrail-api
Username: TestRail login email
Password: TestRail API key
```

The Jenkins pipeline exposes the credentials temporarily as:

```text
TESTRAIL_USER
TESTRAIL_API_KEY
```

The secrets are not stored in the repository.

### Jenkins output

One Jenkins build produces:

```text
JUnit test summary
Allure detailed report
TestRail execution run
Screenshots
Traces
Videos
Logs
```

Access the Allure report from:

```text
Jenkins
→ OpenCartAutomationFramework
→ Build Number
→ Allure Report
```

Access TestRail results from:

```text
OpenCart Web Automation
→ Test Runs & Results
```
<img width="1888" height="893" alt="Screenshot 2026-07-15 203117" src="https://github.com/user-attachments/assets/ae0ae996-570d-4a40-a49b-babde0f1317e" />

---

## Test Design Standard

Each automated test should include:

- Test case ID
- Business-readable title
- Epic
- Feature
- Story
- Severity
- Pytest markers
- TestRail case ID
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
@pytest.mark.testrail(case_id=108)
def test_userLogin(pages):
    LoginScenarios(pages).verify_successful_login()
```

---

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

Check:

- Locator correctness
- Page navigation
- Element visibility
- Frames or popups
- Application state

Do not increase the timeout to hide an incorrect locator.

### Allure report folder is empty

Pytest creates raw results only.

Generate the HTML report:

```bat
allure generate reports\allure-results --clean -o reports\allure-reports
```

### Reports created under `tests/reports`

Ensure:

- PyCharm working directory is the project root.
- `--alluredir` is not hardcoded incorrectly in `pytest.ini`.
- Report paths come from `core/paths.py`.

### TestRail authentication failed

```text
HTTP 401
Authentication failed
```

Check:

- TestRail email
- API key
- API access
- Jenkins credential ID

### TestRail project error

```text
Field :project is not a valid or accessible project
```

Check:

```text
TESTRAIL_PROJECT_ID
User access to the project
```

### Unrecognized TestRail case IDs

```text
Field :case_ids contains unrecognized case IDs
```

Ensure the case:

- Exists in TestRail
- Belongs to the configured project
- Uses the correct numeric ID in the marker

Example:

```python
@pytest.mark.testrail(case_id=108)
```

### Jenkins does not create a TestRail run

Check the Jenkins console for:

```text
TestRail integration is disabled
No TestRail-linked test results were found
TestRail publishing failed
TESTRAIL_USER loaded: False
TESTRAIL_API_KEY loaded: False
```

Confirm:

```text
TESTRAIL_ENABLED=true
TESTRAIL_PROJECT_ID=2
Credential ID=testrail-api
Tests contain @pytest.mark.testrail
```

---

## Author

OpenCart UI Automation Framework  
QA Automation Project
