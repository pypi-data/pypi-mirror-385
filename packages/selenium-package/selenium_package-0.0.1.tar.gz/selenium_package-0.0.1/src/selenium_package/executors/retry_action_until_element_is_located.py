"""
Retry action until element is located executor implementation.

This executor retries an action until a specific element is located on the page.
"""

from typing import Any, Tuple

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class RetryActionUntilElementIsLocated(BaseExecutor):
    """
    Executor that retries an action until an element is located.
    
    This executor will continuously retry the action until the specified
    element is found on the page using the provided locator.
    """
    
    def __init__(
        self, 
        action: BaseAction, 
        element_locator: Tuple[str, str], 
        wait_to_verify_condition: int = None
    ):
        """
        Initialize the retry until element is located executor.
        
        Args:
            action: The action to be executed and retried
            element_locator: Tuple of (By method, locator value) for the element
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If element_locator is not a tuple of strings
        """
        super().__init__(
            action=action,
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(element_locator, tuple) or len(element_locator) != 2:
            raise ValueError(
                "element_locator must be a tuple of (By method, locator value)"
            )

        self.element_locator = element_locator

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the element is located on the page.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if element is located, False otherwise
        """
        web_instance = self.action.web_instance

        try:
            WebDriverWait(web_instance, 3).until(
                EC.presence_of_element_located(self.element_locator)
            )
            return True
        except TimeoutException:
            return False

    
            
            
        
        
        