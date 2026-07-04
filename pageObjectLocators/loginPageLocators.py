class LoginPage:
    """Page Object Model class for the Login Page."""

    def __init__(self, pageManager):
        """
        Constructor that initializes the Playwright Page instance
        and defines all locators used on the Login Page.
        """
        self.page = pageManager.page

        # ===== Locators =====
        # Using selectors to locate elements on the Login page.
        self.userEmail = self.page.locator("//input[@name='email']")
        self.userPassword = self.page.locator("//input[@name='password']")
        self.loginButton = self.page.locator("//input[@type='submit']")



