"""
Retry action until page title contains executor implementation.

This executor retries an action until the page title contains a specific text.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *


class RetryActionUntilPageTitleContains(BaseExecutor):
    """
    Executor that retries an action until the page title contains specific text.
    
    This executor will continuously retry the action until the current
    page title contains the desired text.
    """
    
    def __init__(self, action: BaseAction, desired_page_title: str, wait_to_verify_condition: int = 3):
        """
        Initialize the retry until page title contains executor.
        
        Args:
            action: The action to be executed and retried
            desired_page_title: Text that should be contained in the page title
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

    def _get_current_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            str: The current page title
        """
        return self.action.web_instance.title

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the page title contains the desired text.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if page title contains the text, False otherwise
        """
        current_page_title = self._get_current_page_title()
        return self.desired_page_title in current_page_title

    
            
            
        
        
        