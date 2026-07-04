from playwright.sync_api import Page

class RegisterPage:
    """Page Object Model class for the Home Page."""

    def __init__(self, pageManager):
        """
        Constructor that initializes the Playwright Page instance
        and defines all locators used on the Login Page.
        """
        self.page = pageManager.page

        # ===== Locators =====
        # Using selectors to locate elements on the Login page.

        self.firstName = self.page.locator("//div/input[@name='firstname']")
        self.lastName = self.page.locator("//div/input[@name='lastname']")
        self.email = self.page.locator("//div/input[@name='ehg mail']")
        self.telephone = self.page.locator("//div/input[@name='telephone']")
        self.password = self.page.locator("//div/input[@name='password']")
        self.passwordConfirm = self.page.locator("//div/input[@name='confirm']")
        self.btnContinue = self.page.locator("//input[@type='submit']")
        self.checkboxPrivacyPolicy = self.page.locator("//input[@type='checkbox']")







