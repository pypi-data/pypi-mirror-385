"""
Retry action until number of tabs is executor implementation.

This executor retries an action until the browser has a specific number of tabs.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class RetryActionUntilNumberOfTabsIs(BaseExecutor):
    """
    Executor that retries an action until the number of tabs equals a specific value.
    
    This executor will continuously retry the action until the browser
    has exactly the desired number of tabs open.
    """
    
    def __init__(self, action: BaseAction, desired_number_of_tabs: int):
        """
        Initialize the retry until number of tabs is executor.
        
        Args:
            action: The action to be executed and retried
            desired_number_of_tabs: The exact number of tabs that should be open
            
        Raises:
            ValueError: If desired_number_of_tabs is not a positive integer
        """
        super().__init__(action)

        if not isinstance(desired_number_of_tabs, int) or desired_number_of_tabs < 1:
            raise ValueError(
                VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
                    variable_name='desired_number_of_tabs'
                )
            )

        self.desired_number_of_tabs = desired_number_of_tabs

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the number of tabs equals the desired count.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if number of tabs matches, False otherwise
        """
        web_instance = self.action.web_instance

        try:
            WebDriverWait(web_instance, 3).until(
                lambda driver: len(driver.window_handles) == self.desired_number_of_tabs
            )
            return True
        except TimeoutException:
            return False

    
            
            
        
        
        