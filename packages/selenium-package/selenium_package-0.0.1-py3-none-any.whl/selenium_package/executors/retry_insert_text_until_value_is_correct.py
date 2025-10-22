"""
Retry insert text until value is correct executor implementation.

This executor retries an action until an input element contains the correct text value.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *

from selenium.webdriver.remote.webelement import WebElement


class RetryInsertTextUntilValueIsCorrect(BaseExecutor):
    """
    Executor that retries an action until an input element contains the correct text.
    
    This executor will continuously retry the action until the specified
    input element's value exactly matches the desired text.
    """
    
    def __init__(
        self, 
        action: BaseAction, 
        web_element: WebElement,
        desired_text: str,
        wait_to_verify_condition: int = None
    ):
        """
        Initialize the retry insert text until value is correct executor.
        
        Args:
            action: The action to be executed and retried
            web_element: The input element to check the value of
            desired_text: The exact text the input should contain
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If desired_text is not a string
        """
        super().__init__(
            action=action, 
            web_element=web_element,
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(desired_text, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='desired_text'
                )
            )

        self.action = action
        self.desired_text = desired_text

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the input element contains the correct text value.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if input value matches desired text, False otherwise
        """
        actual_text = self.web_element.get_attribute("value") or ""
        return actual_text == self.desired_text

    
            
            
        
        
        