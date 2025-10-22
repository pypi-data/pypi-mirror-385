"""
Retry action until another tab is opened executor implementation.

This executor retries an action until a new tab is opened in the browser.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class RetryActionUntilAnotherTabIsOpened(BaseExecutor):
    """
    Executor that retries an action until another tab is opened.
    
    This executor will continuously retry the action until the number of
    browser tabs increases beyond the initial count.
    """
    
    def __init__(self, action: BaseAction, current_tabs_count: int, wait_to_verify_condition: int = 3):
        """
        Initialize the retry until another tab is opened executor.
        
        Args:
            action: The action to be executed and retried
            current_tabs_count: Initial number of tabs in the browser
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If current_tabs_count is not a positive integer
        """
        super().__init__(
            action=action,
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(current_tabs_count, int) or current_tabs_count < 1:
            raise ValueError(
                VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
                    variable_name='current_tabs_count'
                )
            )

        self.current_tabs_count = current_tabs_count

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if another tab has been opened.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if another tab is opened, False otherwise
        """
        web_instance = self.action.web_instance

        try:
            WebDriverWait(web_instance, 3).until(
                lambda driver: len(driver.window_handles) > self.current_tabs_count
            )
            return True
        except TimeoutException:
            return False

    
            
            
        
        
        