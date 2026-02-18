"""
SmartWebSearch.ChromeDriver
~~~~~~~~~~~~

This module implements the ChromeDriver.
"""

# Import the required modules
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# The ChromeDriver class
class ChromeDriver:
    """
    A class for interacting with a ChromeDriver.
    """

    def __init__(self) -> None:
        """
        Initialize the ChromeDriver object.

        Returns:
            None
        """

        # Create a headless Chrome browser
        self.chrome_options: Options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")

        self.driver: Chrome = Chrome(options = self.chrome_options)
        self.driver.set_page_load_timeout(60)

    def quit(self) -> None:
        """
        Quit the ChromeDriver object.

        Returns:
            None
        """

        self.driver.quit()