# dao/homeDAO.py
import allure
from core.actions import Actions
from core.logger import get_logger
from pageObjectLocators.loginPageLocators import LoginPage

log = get_logger(__name__)


class LoginPageDAO(Actions):
    """
    Data Access Object for Home Page.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, pageManager):
        super().__init__(pageManager)
        self.loginPageLocators = LoginPage(pageManager)

    @allure.step("Entering user credentials")
    def enterUserEmailAndPassword(self):
        self.fill(self.loginPageLocators.userEmail, "rpolaveni@gmail.com")
        self.fill(self.loginPageLocators.userPassword, "test@123")

    @allure.step("Clicked on login button")
    def clickOnLoginButton(self):
        self.click(self.loginPageLocators.loginButton)




