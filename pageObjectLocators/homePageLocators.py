class HomePage:
    """Page Object Model class for the Home Page."""

    def __init__(self, pageManager):
        """
        Constructor that initializes the Playwright Page instance
        and defines all locators used on the Login Page.
        """
        self.page = pageManager.page

        # ===== Locators =====
        # Using selectors to locate elements on the Login page.
        self.myAccountDropdownHomepage = self.page.locator("//span[text()='My Account']")
        self.registerButtonHomepage = self.page.locator("//a[text()='Register']")
        self.loginButtonHomepage = self.page.locator("//a[text()='Login']")
        self.txtRegisterAccount = self.page.locator("//h1[text()='Register Account']")
        self.wrntxtRegisterAccount = self.page.locator("//h1[text()='EfRegister Account']")
        self.logoutButtonHomepage = self.page.locator("//div/a[text()='Logout']")
        self.logoutConfirmationText = self.page.locator("//h1[text()='Account Logout']")
        self.homePage = self.page.locator("//a[text()='Qafox.com']")


