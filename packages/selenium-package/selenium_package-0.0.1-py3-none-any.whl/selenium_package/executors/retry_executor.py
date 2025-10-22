"""
Retry executor implementation.

This executor retries an action until a condition is met or timeout occurs.
"""

from typing import Any
from selenium.webdriver.remote.webelement import WebElement

from ..interfaces.base_executor import BaseExecutor
from ..interfaces.base_action import BaseAction


class RetryExecutor(BaseExecutor):
    """
    Executor that retries an action until a condition is met.
    
    This executor will continuously retry the action until the condition
    to stop is met or the timeout is reached.
    """
    
    def __init__(
        self, 
        action: BaseAction,
        web_element: WebElement | None = None,
        wait_to_verify_condition: int | None = 1,
        timeout: int = 30,
    ):
        """
        Initialize the retry executor.
        
        Args:
            action: The action to be executed and retried
            web_element: Optional web element for the action
            wait_to_verify_condition: Time to wait between attempts
            timeout: Maximum time to wait for all attempts
        """
        super().__init__(action, web_element, wait_to_verify_condition, timeout)
    
    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the condition to stop is met.
        
        This base implementation always returns True to stop after first execution.
        Subclasses should override this method to implement specific conditions.
        
        Args:
            result: The result of the action
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        return True