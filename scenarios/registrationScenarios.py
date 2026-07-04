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


class RegistrationScenarios:

    def __init__(self, pageManager):
        self.pageManager = pageManager

    @allure.step("TestCase: Validate user register")
    def verify_user_registration(self) -> None:
        log.info(f"TestCase: Validate user register ")

        # ── Action ────────────────────────────────────────────────────────────
        self.pageManager.homePageDao.navigate_to_register_page()
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Register page loaded successfully "):
            confirmationMsg = self.pageManager.homePageDao.getRegisterAccountText()
            expect(confirmationMsg).to_have_text("Register Account")

        self.pageManager.registerPageDao.enterUserRegistrationDetails()
        self.pageManager.registerPageDao.clickOnCheckboxPrivacyPolicy()
        self.pageManager.registerPageDao.clickOnContinue()
        allure.step("User registration successfully")
