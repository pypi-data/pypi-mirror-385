"""
Default executor implementation.

This executor runs an action once and immediately stops.
"""

from typing import Any

from ..interfaces.base_executor import BaseExecutor


class DefaultExecutor(BaseExecutor):
    """
    Default executor that runs an action once and stops.
    
    This is the simplest executor implementation that executes the action
    once and immediately considers the condition to stop as met.
    """
    
    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Always return True to stop after first execution.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: Always True to stop execution after first run
        """
        return True
