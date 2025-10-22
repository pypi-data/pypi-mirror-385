"""
Executor implementations for common Selenium operations.

This module contains concrete implementations of BaseExecutor for various
execution patterns like retry logic, conditional execution, etc.
"""

# Import all executor classes
from .default_executor import DefaultExecutor
from .retry_action_by_max_attempts import RetryActionByMaxAttempts
from .retry_action_until_another_tab_is_opened import RetryActionUntilAnotherTabIsOpened
from .retry_action_until_element_contains_a_property_value import RetryActionUntilElementContainsAPropertyValue
from .retry_action_until_element_has_a_property_value import RetryActionUntilElementHasAPropertyValue
from .retry_action_until_element_is_located import RetryActionUntilElementIsLocated
from .retry_action_until_new_file_has_been_detected import RetryActionUntilNewFileHasBeenDetected
from .retry_action_until_number_of_tabs_is import RetryActionUntilNumberOfTabsIs
from .retry_action_until_page_title_contains import RetryActionUntilPageTitleContains
from .retry_action_until_page_title_is import RetryActionUntilPageTitleIs
from .retry_action_until_url_contains import RetryActionUntilUrlContains
from .retry_executor import RetryExecutor
from .retry_insert_text_until_value_is_correct import RetryInsertTextUntilValueIsCorrect
from .timeout_executor import TimeoutExecutor

__all__ = [
    "DefaultExecutor",
    "RetryActionByMaxAttempts",
    "RetryActionUntilAnotherTabIsOpened",
    "RetryActionUntilElementContainsAPropertyValue",
    "RetryActionUntilElementHasAPropertyValue",
    "RetryActionUntilElementIsLocated",
    "RetryActionUntilNewFileHasBeenDetected",
    "RetryActionUntilNumberOfTabsIs",
    "RetryActionUntilPageTitleContains",
    "RetryActionUntilPageTitleIs",
    "RetryActionUntilUrlContains",
    "RetryExecutor",
    "RetryInsertTextUntilValueIsCorrect",
    "TimeoutExecutor",
]
