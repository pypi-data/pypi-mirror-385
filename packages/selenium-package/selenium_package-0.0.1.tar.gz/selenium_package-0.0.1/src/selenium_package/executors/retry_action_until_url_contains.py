"""
Retry action until URL contains executor implementation.

This executor retries an action until the current URL contains specific text.
"""

from typing import Any

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *


class RetryActionUntilUrlContains(BaseExecutor):
    """
    Executor that retries an action until the URL contains specific text.
    
    This executor will continuously retry the action until the current
    URL contains the desired text.
    """
    
    def __init__(self, action: BaseAction, desired_url: str, wait_to_verify_condition: int = 3):
        """
        Initialize the retry until URL contains executor.
        
        Args:
            action: The action to be executed and retried
            desired_url: Text that should be contained in the URL
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If desired_url is not a string
        """
        super().__init__(
            action=action,
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(desired_url, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='desired_url'
                )
            )

        self.desired_url = desired_url

    def _get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            str: The current page URL
        """
        return self.action.web_instance.current_url

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the URL contains the desired text.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if URL contains the text, False otherwise
        """
        current_url = self._get_current_url()
        return self.desired_url in current_url

    
            
            
        
        
        