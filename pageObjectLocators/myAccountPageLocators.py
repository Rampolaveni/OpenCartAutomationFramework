from playwright.sync_api import Page

class MyAccountPage:
    """Page Object Model class for the Home Page."""

    def __init__(self, pageManager):
        """
        Constructor that initializes the Playwright Page instance
        and defines all locators used on the Login Page.
        """
        self.page = pageManager.page

        # ===== Locators =====
        # Using selectors to locate elements on the Login page.
        self.myAccountText = self.page.locator("//h2[text()='My Account']")

