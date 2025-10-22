
"""
Retry action until element contains a property value executor implementation.

This executor retries an action until a web element's property contains a specific value.
"""

from typing import Any

from ..interfaces.base_executor import BaseExecutor
from ..interfaces.base_action import BaseAction
from selenium.webdriver.remote.webelement import WebElement
from selenium_package.utils.messages import *


class RetryActionUntilElementContainsAPropertyValue(BaseExecutor):
    """
    Executor that retries an action until an element's property contains a value.
    
    This executor will continuously retry the action until the specified
    web element's property contains the expected value.
    """
    
    def __init__(
        self, 
        action: BaseAction, 
        web_element: WebElement, 
        property_name: str, 
        property_value: str,
        wait_to_verify_condition: int = None
    ):
        """
        Initialize the retry until element contains property value executor.
        
        Args:
            action: The action to be executed and retried
            web_element: The web element to check the property of
            property_name: Name of the property to check
            property_value: Value that should be contained in the property
            wait_to_verify_condition: Time to wait between condition checks
            
        Raises:
            ValueError: If property_name or property_value are not strings
        """
        super().__init__(
            action=action, 
            web_element=web_element, 
            wait_to_verify_condition=wait_to_verify_condition
        )

        if not isinstance(property_name, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='property_name'
                )
            )

        if not isinstance(property_value, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='property_value'
                )
            )

        self.web_element = web_element
        self.property_name = property_name
        self.property_value = property_value

    def _get_property_value(self) -> str:
        """
        Get the current value of the element's property.
        
        Returns:
            str: The current property value
        """
        return self.web_element.get_attribute(self.property_name) or ""

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        """
        Check if the element's property contains the expected value.
        
        Args:
            result: The result of the action (unused)
            
        Returns:
            bool: True if property contains the value, False otherwise
        """
        property_value = self._get_property_value()
        return self.property_value in property_value