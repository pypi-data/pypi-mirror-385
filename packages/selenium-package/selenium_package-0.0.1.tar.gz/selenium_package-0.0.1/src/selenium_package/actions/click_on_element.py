"""
This module contains the ClickOnElement action.
It will simply click on the element passed to the constructor.
"""

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.utils.messages import *

class ClickOnElement(BaseAction):
    """
    Action that clicks on the element passed to the constructor.
    """
    def __init__(self, 
        web_instance: WebDriver | WebElement, 
        web_element: WebElement,
    ):
        """
        This action will click on the element passed to the constructor.
        Args:
            web_instance (WebDriver | WebElement): The webdriver instance or the web element to perform the action on.
            web_element (WebElement): The web element to click on.
        """
        super().__init__(web_instance, web_element)
        
    def _execute_action(self) -> None:
        self.web_element.click()
        

        

