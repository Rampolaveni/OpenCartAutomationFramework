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


class LogoutScenarios:

    def __init__(self, pageManager):
        self.pageManager = pageManager

    @allure.step("TestCase: Validate user logout")
    def verify_user_logout(self) -> None:
        """
        Full login scenario:
        1. Navigate to login page
        2. Enter credentials
        3. Submit.
        4. Assert user logout
        """
        log.info(f"Scenario: Verify user logout ")

        # ── Action ────────────────────────────────────────────────────────────
        self.pageManager.homePageDao.navigate_to_login_page()
        self.pageManager.loginPageDao.enterUserEmailAndPassword()
        self.pageManager.loginPageDao.clickOnLoginButton()

        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Assert: User login successfully"):
            confirmation_msg = self.pageManager.myAccountPageDao.getMyAccountText()
            expect(confirmation_msg).to_have_text("My Account")
            log.info("Assertion passed: User login successfully")

        self.pageManager.homePageDao.clickOnLogoutButton()

        with allure.step("Assert: User logout successfully"):
            confirmAccountLogoutText = self.pageManager.homePageDao.getLogoutAccountText()
            expect(confirmAccountLogoutText).to_have_text("Account Logout")
            log.info("Assertion passed: User logout successfully")