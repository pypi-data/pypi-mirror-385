"""
Retry action until page title is executor implementation.

This executor retries an action until the page title exactly matches a specific text.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *


class RetryActionUntilPageTitleIs(BaseExecutor):
    """
    Executor that retries an action until the page title exactly matches specific text.
    
    This executor will continuously retry the action until the current
    page title exactly matches the desired text.
    """
    
    def __init__(self, action: BaseAction, desired_page_title: str, wait_to_verify_condition: int = None):
        """
        Initialize the retry until page title is executor.
        
        Args:
            action: The action to be executed and retried
            desired_page_title: Exact text the page title should match
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If desired_page_title is not a string
        """
        super().__init__(
            action=action,
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(desired_page_title, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='desired_page_title'
                )
            )

        self.desired_page_title = desired_page_title

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the page title exactly matches the desired text.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if page title matches exactly, False otherwise
        """
        webdriver_instance = self.action.web_instance
        current_page_title = webdriver_instance.title
        is_condition_to_stop_met = (current_page_title == self.desired_page_title)
        return is_condition_to_stop_met

    
            
            
        
        
        