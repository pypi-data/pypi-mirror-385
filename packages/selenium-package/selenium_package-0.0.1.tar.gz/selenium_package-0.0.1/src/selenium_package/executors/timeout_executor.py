"""
Timeout executor implementation.

This executor runs an action with a specific timeout.
"""

from typing import Any
from selenium.webdriver.remote.webelement import WebElement

from ..interfaces.base_executor import BaseExecutor
from ..interfaces.base_action import BaseAction


class TimeoutExecutor(BaseExecutor):
    """
    Executor that runs an action with a specific timeout.
    
    This executor will run the action once and stop, with the timeout
    being handled by the base executor class.
    """
    
    def __init__(
        self, 
        action: BaseAction,
        web_element: WebElement | None = None,
        wait_to_verify_condition: int | None = None,
        timeout: int = 30,
    ):
        """
        Initialize the timeout executor.
        
        Args:
            action: The action to be executed
            web_element: Optional web element for the action
            wait_to_verify_condition: Not used for timeout execution
            timeout: Maximum time to wait for action completion
        """
        super().__init__(action, web_element, wait_to_verify_condition, timeout)
    
    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Always stop after first execution (timeout is handled by base class).
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: Always True to stop execution after first run
        """
        return True
