"""
Retry action by maximum attempts executor implementation.

This executor retries an action a specified number of times before giving up.
"""

import time
from typing import Any

from ..interfaces.base_executor import BaseExecutor
from ..interfaces.base_action import BaseAction
from ..interfaces.exceptions.exceptions import (
    MaximumAttemptsReachedException,
    SeleniumBaseActionException
)
from selenium_package.utils.messages import *

class RetryActionByMaxAttempts(BaseExecutor):
    """
    Executor that retries an action a specified number of times.
    
    This executor will attempt to run the action up to max_attempts times.
    If the action fails after all attempts, it raises MaximumAttemptsReachedException.
    """
    
    def __init__(self, action: BaseAction, max_attempts: int = 1):
        """
        Initialize the retry executor.
        
        Args:
            action: The action to be executed and retried
            max_attempts: Maximum number of attempts before giving up (default: 1)
            
        Raises:
            ValueError: If max_attempts is not a positive integer
        """
        super().__init__(action)

        if not isinstance(max_attempts, int) or max_attempts < 1:
            raise ValueError(
                VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
                    variable_name='max_attempts'
                )
            )

        self.max_attempts = max_attempts

    def _is_condition_to_stop_met(self, attempt_index: int) -> bool:
        """
        Check if maximum attempts have been reached.
        
        Args:
            attempt_index: Current attempt number (0-based)
            
        Returns:
            bool: True if max attempts reached, False otherwise
        """
        return attempt_index >= self.max_attempts

    def run(self) -> Any:
        """
        Execute the action with retry logic.
        
        This method will attempt to run the action up to max_attempts times.
        If the action succeeds, it returns the result. If it fails after all
        attempts, it raises MaximumAttemptsReachedException.
        
        Returns:
            Any: The result of the action if successful
            
        Raises:
            MaximumAttemptsReachedException: If all attempts failed
        """
        attempt_index = 0

        is_max_attempts_reached = False
        action_runnned_successfully = False

        exceptions_raised = []

        while (
            not action_runnned_successfully and
            not is_max_attempts_reached
        ):
            try:
                action_result = self.action.run()
                action_runnned_successfully = True
            except SeleniumBaseActionException as e:
                time.sleep(3)
                exceptions_raised.append(e)
                
                attempt_index += 1
                is_max_attempts_reached = self._is_condition_to_stop_met(
                    attempt_index=attempt_index
                )

            
        if not action_runnned_successfully:
            unique_exceptions_raised = list( # getting the unique str exceptions to get a better message
                set(
                    [str(exception) for exception in exceptions_raised]
                )
            )
            
            exceptions_raised_str = '\n'.join(
                [str(exception) for exception in unique_exceptions_raised]
            )

            raise MaximumAttemptsReachedException(
                message=MAXIMUM_ATTEMPTS_REACHED_MESSAGE.format(
                    exceptions=exceptions_raised_str
                )
            )
        
        return action_result