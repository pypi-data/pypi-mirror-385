"""
This module contains the RedirectToPage action.
It will redirect the webdriver to the page passed to the constructor.
"""
from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.utils.messages import *

class RedirectToPage(BaseAction):
    """
    Action that redirects the webdriver to the page passed to the constructor.
    """
    def __init__(self, 
        web_instance: WebDriver, 
        page_url: str,
    ):
        """
        Initialize the RedirectToPage action.
        This action will redirect the webdriver to the page url passed
        to the constructor.
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
            page_url (str): The url to redirect the webdriver to.
        """
        super().__init__(web_instance)
        
        if not isinstance(page_url, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='page_url'
                )
            )
        
        self.page_url = page_url

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will redirect the webdriver to the page passed to 
        the constructor.
        """
        self.web_instance.get(self.page_url)
        

        

