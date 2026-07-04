# dao/homeDAO.py
import allure
from core.actions import Actions
from core.logger import get_logger
from pageObjectLocators.myAccountPageLocators import MyAccountPage

log = get_logger(__name__)


class MyAccountPageDAO(Actions):
    """
    Data Access Object for MyAccountPage.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, pageManager):
        super().__init__(pageManager)

        self.pageManager = pageManager
        self.myAccountPageLocators = MyAccountPage(pageManager)

    @allure.step("Confirmed Log-In")
    def getMyAccountText(self):
        return self.myAccountPageLocators.myAccountText


