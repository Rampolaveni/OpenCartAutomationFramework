# dao/registerPageDAO.py
import allure
from core.actions import Actions
from core.logger import get_logger
from pageObjectLocators.registerPageLocators import RegisterPage

log = get_logger(__name__)


class RegisterPageDAO(Actions):
    """
       Data Access Object for Register Page.
       Contains all actions methods for the home page.
       No assertions allowed here.
       """

    def __init__(self, pageManager):
        super().__init__(pageManager)
        self.registerPageLocators = RegisterPage(pageManager)

    # ===== Actions / Methods =====
    @allure.step("Entering user details for registration.")
    def enterUserRegistrationDetails(self):
        self.fill(self.registerPageLocators.firstName, "Ram")
        self.fill(self.registerPageLocators.lastName, "Polaveni")
        self.fill(self.registerPageLocators.email, "rpolaveni@gmail.com")
        self.fill(self.registerPageLocators.telephone, "0404441536")
        self.fill(self.registerPageLocators.password, "test@123")
        self.fill(self.registerPageLocators.passwordConfirm, "test@123")

    @allure.step("Privacy policy checkbox checked.")
    def clickOnCheckboxPrivacyPolicy(self):
        self.check(self.registerPageLocators.checkboxPrivacyPolicy)

    @allure.step("Continued to next.")
    def clickOnContinue(self):
        self.click(self.registerPageLocators.btnContinue)
