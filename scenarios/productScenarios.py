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


class ProductScenarios:

    def __init__(self, pageManager):
        self.pageManager = pageManager

    @allure.step("TestCase: Validate product comparison")
    def verify_product_comparison(self) -> None:
        log.info(f"TestCase: Validate product comparison ")
        # ── Action ────────────────────────────────────────────────────────────
        self.pageManager.homePageDao.navigate_to_login_page()
        self.pageManager.loginPageDao.enterUserEmailAndPassword()
        self.pageManager.loginPageDao.clickOnLoginButton()
        self.pageManager.homePageDao.navigateToHomePage()
        self.pageManager.productPageDao.searchProductWithName("iMac")
        self.pageManager.productPageDao.clickOnSearchButton()
        self.pageManager.productPageDao.selectProductByName("iMac")
        self.pageManager.productPageDao.compareProductWithName("iMac")
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Product comparison assertion"):
            productComparisonSuccessMessage =  self.pageManager.productPageDao.getProductComparisonSuccessMessage()
            assert "Success: You have added iMac to your product comparison!" in productComparisonSuccessMessage
            log.info("Product Comparison Successful")

    @allure.step("TestCase: Validate product search")
    def verify_product_search(self) -> None:
        log.info(f"TestCase: Validate product search ")
        # ── Action ────────────────────────────────────────────────────────────
        self.pageManager.homePageDao.navigate_to_login_page()
        self.pageManager.loginPageDao.enterUserEmailAndPassword()
        self.pageManager.loginPageDao.clickOnLoginButton()
        self.pageManager.homePageDao.navigateToHomePage()
        self.pageManager.productPageDao.searchProductWithName("iMac")
        self.pageManager.productPageDao.clickOnSearchButton()
        productsList = self.pageManager.productPageDao.getProductSearchResults()
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Validating product in search results"):
            assert "iMacv" in productsList, "iMac product not found in search results"

