"""
This module contains the base class for all selenium actions.
You can extend this class to perform selenium actions on a page and use it with an executor.
"""

from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from abc import ABC, abstractmethod

from .exceptions.exceptions import SeleniumBaseActionException

from selenium_package.utils.messages import *

class BaseAction(ABC):
    def __init__(
        self, 
        web_instance: WebDriver | WebElement, 
        web_element: WebElement | None = None
    ):
        """
        Initialize the base action.
        You must pass the webdriver itself or you can pass a web_element to 
        perform the action on.

        Args:
            web_instance (WebDriver | WebElement): The webdriver instance or the web_element to perform the action on.
            web_element (WebElement | None): The web_element to perform the action on.
        """
        if web_element and not isinstance(web_element, WebElement):
            raise ValueError(
                VARIABLE_MUST_BE_A_WEB_ELEMENT_INSTANCE.format(
                    variable_name='web_element'
                )
            )

        self.web_element = web_element
        self.web_instance = web_instance

    @abstractmethod
    def _execute_action(self) -> Any:
        pass

    def execute_action(self) -> Any:
        """
        Execute the action by calling the _execute_action method.
        It will wrap the exception in a SeleniumBaseActionException.

        Returns:
            Any: The result of the action.
        """
        try:
            return self._execute_action()
        except Exception as e:
            raise SeleniumBaseActionException(
                message=BASE_ACTION_FAILED_MESSAGE.format(
                    action_name=self.__class__.__name__,
                    error=str(e) # str(e) to get the error message
                )
            )

    def run(self) -> Any:
        """
        Just a wrapper to execute the action and return the result.
        """
        result = self.execute_action()
        return result
            


        
            



        
            
        
        
