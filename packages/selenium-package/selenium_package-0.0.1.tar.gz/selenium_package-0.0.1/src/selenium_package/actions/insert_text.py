"""
This module contains the InsertText action.
It will insert the text passed to the constructor into the element passed to the constructor.
"""

from selenium_package.interfaces import BaseAction

from selenium_package.utils.messages import *

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

class InsertText(BaseAction):
    """
    Action that inserts the text passed to the constructor into the element passed to the constructor.
    """
    def __init__(
        self, 
        web_instance: WebDriver, 
        web_element: WebElement,
        text: str,
        using_js: bool = False
    ):
        """
        Initialize the InsertText action.
        This action will insert the text passed to the constructor into 
        the element passed to the constructor.
        
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
            web_element (WebElement): The web_element to perform the action on.
            text (str): The text to insert into the element.
            using_js (bool): Whether to use javascript to insert the text.
        """
        super().__init__(web_instance, web_element)

        if not isinstance(text, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='text'
                )
            )

        if not isinstance(using_js, bool):
            raise ValueError(
                VARIABLE_MUST_BE_A_BOOLEAN.format(
                    variable_name='using_js'
                )
            )
        
        self.using_js = using_js
        self.text = text

    def _execute_action_with_js(self) -> None:
        """
        Execute the action using javascript.
        It will insert the text passed to the constructor into 
        the element passed to the constructor.
        """
        self.web_instance.execute_script(
            "arguments[0].value = arguments[1];",
            self.web_element,
            self.text
        )

    def _execute_action_without_js(self) -> None:
        """
        Execute the action without using javascript.
        It will insert the text passed to the constructor into 
        the element passed to the constructor.
        """
        self.web_element.send_keys(self.text)

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will insert the text passed to the constructor into 
        the element passed to the constructor using javascript
        or without using javascript depending on the value of 
        the using_js parameter passed to the constructor.
        """
        if self.using_js:
            self._execute_action_with_js()
        else:
            self._execute_action_without_js()

            
        
        