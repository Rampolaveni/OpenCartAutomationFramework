from playwright.sync_api import Page
from core.logger import get_logger
from dao.loginPageDao import LoginPageDAO
from dao.homePageDao import HomePageDAO
from dao.myAccountPageDao import MyAccountPageDAO
from dao.registerPageDao import RegisterPageDAO
from dao.productPageDao import ProductPageDAO

log = get_logger(__name__)

class PageManager:
    def __init__(self, page):
        log.debug("Initialising PageManager")
        self._page = page

        # ── DAO layer ─────────────────────────────────────────────────────────
        self.loginPageDao = LoginPageDAO(self)
        self.homePageDao = HomePageDAO(self)
        self.myAccountPageDao = MyAccountPageDAO(self)
        self.registerPageDao = RegisterPageDAO(self)
        self.productPageDao = ProductPageDAO(self)

    @property
    def page(self) -> Page:
        return self._page