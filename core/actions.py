# core/actions.py

# ============================================================================
# ACTIONS CLASS
# ============================================================================
# Wraps all Playwright interactions with:
# 1. Logging — every action logged at DEBUG level
# 2. Exception handling — clear error messages with locator context
# 3. Allure steps — every action appears in Allure report timeline
# 4. Consistent interface — all page object methods go through here
# ============================================================================

import allure
from playwright.sync_api import Page
from core.logger import get_logger

log = get_logger(__name__)


class Actions:
    """
    Base actions class — wraps all Playwright interactions.
    All page object classes inherit from this.

    Usage:
        class LoginPage(Actions):
            EMAIL_FIELD    = "#input-email"
            PASSWORD_FIELD = "#input-password"
            LOGIN_BUTTON   = "input[value='Login']"

            def login(self, email, password):
                self.fill(self.EMAIL_FIELD, email)
                self.fill(self.PASSWORD_FIELD, password)
                self.click(self.LOGIN_BUTTON)
    """

    def __init__(self, pageManager):
        self.page = pageManager.page

    # ─────────────────────────────────────────────────────────────────────────
    # CLICK
    # ─────────────────────────────────────────────────────────────────────────
    def click(self, locator) -> None:
        """Click an element identified by locator."""
        with allure.step(f"Click: {locator}"):
            try:
                log.debug(f"Click → {locator}")
                locator.click()
                log.debug(f"Click ✅ → {locator}")
            except Exception as e:
                log.error(f"Click FAILED → {locator} | Error: {e}")
                raise

    # ─────────────────────────────────────────────────────────────────────────
    # FILL / TYPE / CLEAR
    # ─────────────────────────────────────────────────────────────────────────
    def fill(self, locator, value: str) -> None:
        """Clear and fill an input field."""
        with allure.step(f"Fill: {locator}"):
            try:
                log.debug(f"Fill → {locator} | value: {value}")
                locator.fill("")
                locator.fill(value)
                log.debug(f"Fill ✅ → {locator}")
            except Exception as e:
                log.error(f"Fill FAILED → {locator} | Error: {e}")

                raise

    def click_by_selector(self, selector: str) -> None:
        """Click an element identified by selector string."""
        with allure.step(f"Click by selector: {selector}"):
            try:
                log.debug(f"Click → {selector}")

                locator = self.page.locator(selector)
                locator.click()

                log.debug(f"Click ✅ → {selector}")

            except Exception as e:
                log.error(f"Click FAILED → {selector} | Error: {e}")
                raise

    def get_text_by_selector(self, selector: str) -> str:
        """Get visible text of an element using selector string."""
        with allure.step(f"Get text: {selector}"):
            try:
                log.debug(f"Get text → {selector}")

                locator = self.page.locator(selector)
                locator.wait_for(state="visible")

                text = locator.inner_text().strip()

                log.debug(f"Get text ✅ → {selector} | text: {text}")

                return text

            except Exception as e:
                log.error(f"Get text FAILED → {selector} | Error: {e}")
                raise

    def clear(self, locator) -> None:
        """Clear an input field."""
        with allure.step(f"Clear: {locator}"):
            try:
                log.debug(f"Clear → {locator}")
                locator.fill("")
                log.debug(f"Clear ✅ → {locator}")
            except Exception as e:
                log.error(f"Clear FAILED → {locator} | Error: {e}")

                raise

    def check(self, locator) -> None:
        """Check a checkbox."""
        with allure.step(f"Check: {locator}"):
            try:
                log.debug(f"Check → {locator}")

                locator.check()

                log.debug(f"Check ✅ → {locator}")

            except Exception as e:
                log.error(f"Check FAILED → {locator} | Error: {e}")
                raise

    def uncheck(self, locator) -> None:
        """Uncheck a checkbox."""
        with allure.step(f"Uncheck: {locator}"):
            try:
                log.debug(f"Uncheck → {locator}")
                locator.uncheck(locator)
                log.debug(f"Uncheck ✅ → {locator}")
            except Exception as e:
                log.error(f"Uncheck FAILED → {locator} | Error: {e}")

                raise

    # ─────────────────────────────────────────────────────────────────────────
    # NAVIGATION
    # ─────────────────────────────────────────────────────────────────────────
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        with allure.step(f"Navigate to: {url}"):
            try:
                log.debug(f"Navigate → {url}")
                self.page.goto(url)
                log.debug(f"Navigate ✅ → {url}")
            except Exception as e:
                log.error(f"Navigate FAILED → {url} | Error: {e}")

                raise

    def go_back(self) -> None:
        """Navigate back."""
        with allure.step("Navigate back"):
            try:
                log.debug("Navigate back")
                self.page.go_back()
                log.debug("Navigate back ✅")
            except Exception as e:
                log.error(f"Navigate back FAILED | Error: {e}")

                raise

    def refresh(self) -> None:
        """Refresh the page."""
        with allure.step("Refresh page"):
            try:
                log.debug("Refresh page")
                self.page.reload()
                log.debug("Refresh ✅")
            except Exception as e:
                log.error(f"Refresh FAILED | Error: {e}")

                raise

    # ─────────────────────────────────────────────────────────────────────────
    # GET / READ
    # ─────────────────────────────────────────────────────────────────────────
    def get_text(self, locator) -> str:
        """Get visible text of an element."""
        with allure.step(f"Get text: {locator}"):
            try:
                log.debug(f"Get text → {locator}")
                text = locator.text_content()
                log.debug(f"Get text ✅ → {locator} | text: {text}")

                return text

            except Exception as e:
                log.error(f"Get text FAILED → {locator} | Error: {e}")
                raise

    def get_attribute(self, locator, attribute: str) -> str:
        """Get a specific attribute of an element."""
        with allure.step(f"Get attribute '{attribute}': {locator}"):
            try:
                log.debug(f"Get attribute → {locator} | attribute: {attribute}")
                value = self.page.get_attribute(locator, attribute)
                log.debug(f"Get attribute ✅ → {attribute}: {value}")
                return value
            except Exception as e:
                log.error(f"Get attribute FAILED → {locator} | Error: {e}")

                raise

    def get_title(self) -> str:
        """Get the page title."""
        with allure.step("Get page title"):
            try:
                title = self.page.title()
                log.debug(f"Page title: {title}")
                return title
            except Exception as e:
                log.error(f"Get title FAILED | Error: {e}")

                raise

    def get_current_url(self) -> str:
        """Get the current page URL."""
        with allure.step("Get current URL"):
            url = self.page.url
            log.debug(f"Current URL: {url}")

            return url

    # ─────────────────────────────────────────────────────────────────────────
    # SCREENSHOT
    # ─────────────────────────────────────────────────────────────────────────
    def take_screenshot(self, name: str) -> None:
        """Take a screenshot and attach to Allure report."""
        try:
            screenshot = self.page.screenshot()
            allure.attach(
                screenshot,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
            log.debug(f"Screenshot attached: {name}")
        except Exception as e:
            log.error(f"Screenshot FAILED | Error: {e}")
