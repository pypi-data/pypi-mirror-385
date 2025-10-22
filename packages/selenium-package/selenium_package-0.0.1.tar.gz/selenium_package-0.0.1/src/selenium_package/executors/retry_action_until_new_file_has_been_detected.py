"""
Retry action until new file has been detected executor implementation.

This executor retries an action until a new file is detected in a specified directory.
"""

from typing import Any
from pathlib import Path

from ..interfaces.base_action import BaseAction
from ..interfaces.base_executor import BaseExecutor
from selenium_package.utils.messages import *

import time


class RetryActionUntilNewFileHasBeenDetected(BaseExecutor):
    """
    Executor that retries an action until a new file is detected in a directory.
    
    This executor will continuously retry the action until a new file
    appears in the specified directory.
    """
    
    def __init__(self, action: BaseAction, path: Path, file_extension: str = None):
        """
        Initialize the retry until new file detected executor.
        
        Args:
            action: The action to be executed and retried
            path: Directory path to monitor for new files
            file_extension: Optional file extension to filter by (e.g., '.pdf', '.txt')
            
        Raises:
            ValueError: If path is not a Path instance
        """
        super().__init__(action)

        if not isinstance(path, Path):
            raise ValueError(
                VARIABLE_MUST_BE_A_PATH_INSTANCE.format(variable_name="path")
            )

        self.path = path
        self.file_extension = file_extension
        self.old_files_count = self._get_current_files_count()

    def _get_current_files_count(self) -> int:
        """
        Get the current count of files in the monitored directory.
        
        Returns:
            int: Number of files in the directory
        """
        if self.file_extension:
            return len(list(self.path.glob(f"*{self.file_extension}")))
        else:
            return len(list(self.path.glob("*")))
    
    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if a new file has been detected in the directory.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if new file detected, False otherwise
        """
        timeout = 5  # seconds
        interval = 0.5
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._get_current_files_count() > self.old_files_count:
                return True
            time.sleep(interval)

        return False
    
