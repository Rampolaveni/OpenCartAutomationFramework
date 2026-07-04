# scenarios/loginScenario.py
# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCENARIO
# Contains all assertions for Login functionality
# Calls DAO for actions, then asserts on results
# ─────────────────────────────────────────────────────────────────────────────

import allure
from playwright.sync_api import expect
from core.logger import get_logger

log = get_logger(__name__)


class LoginScenarios:

    def __init__(self, pageManager):
        self.pageManager = pageManager

    @allure.step("TestCase: Validate user login")
    def verify_successful_login(self) -> None:
        """
        Full login scenario:
        1. Navigate to login page
        2. Enter credentials
        3. Submit.
        4. Assert My Account page is displayed
        """
        log.info(f"Scenario: Verify successful login ")

        # ── Action ────────────────────────────────────────────────────────────
        self.pageManager.homePageDao.navigate_to_login_page()
        self.pageManager.loginPageDao.enterUserEmailAndPassword()
        self.pageManager.loginPageDao.clickOnLoginButton()

        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Assert: My Account page is displayed"):
            confirmation_msg = self.pageManager.myAccountPageDao.getMyAccountText()
            expect(confirmation_msg).to_have_text("My Account")
            log.info("Assertion passed: My Account heading visible")
