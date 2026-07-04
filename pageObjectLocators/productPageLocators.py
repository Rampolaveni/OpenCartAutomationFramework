from playwright.sync_api import Page


class ProductPage:
    """Page Object Model class for the Home Page."""

    def __init__(self, pageManager):
        """
        Constructor that initializes the Playwright Page instance
        and defines all locators used on the Login Page.
        """
        self.page = pageManager.page

        # ===== Locators =====
        # Using selectors to locate elements on the Product page.
        self.searchBar = self.page.locator("//input[@name='search']")
        self.searchButton = self.page.locator("//input[@name='search']/parent::div/span/button")
        self.productSearchResults = self.page.locator("//h4/a")
        self.getProductComparisonSuccessMessage = self.page.locator("//div/div[contains(.,'You have added') and contains(.,'product comparison')]")
