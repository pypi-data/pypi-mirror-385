"""
This module contains the GoBackToThePreviousPage action.
It will simply go back to the previous page.
"""

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver


class GoBackToThePreviousPage(BaseAction):
    """
    Action that goes back to the previous page.
    """
    def __init__(
        self,
        web_instance: WebDriver,
    ):
        """
        Initialize the GoBackToThePreviousPage action.
        This action will go back to the previous page.
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
        """
        super().__init__(web_instance)

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will go back to the previous page.
        """
        self.web_instance.back()