from selenium_package.executors import RetryActionUntilElementContainsAPropertyValue

from unittest.mock import MagicMock

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.utils.messages import *

from unittest.mock import patch

import pytest

class TestRetryActionUntilElementContainsAPropertyValue:
    def test_if_raises_value_error_when_property_name_is_not_a_string(self):
        with pytest.raises(ValueError) as e:
            RetryActionUntilElementContainsAPropertyValue(
                action=MagicMock(spec=BaseAction),
                web_element=MagicMock(spec=WebElement),
                property_name=123,
                property_value='test',
            )

        assert e.value.args[0] == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='property_name'
        )

    def test_if_raises_value_error_when_property_value_is_not_a_string(self):
        with pytest.raises(ValueError) as e:
            RetryActionUntilElementContainsAPropertyValue(
                action=MagicMock(spec=BaseAction),
                web_element=MagicMock(spec=WebElement),
                property_name='test',
                property_value=123,
            )

        assert e.value.args[0] == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='property_value'
        )

    def test_if_is_condition_to_stop_met_returns_true_when_property_value_contains_desired_value(
        self,
    ):
        executor = RetryActionUntilElementContainsAPropertyValue(
            action=MagicMock(spec=BaseAction),
            web_element=MagicMock(spec=WebElement),
            property_name='test',
            property_value='desired_value',
        )

        executor._get_property_value = MagicMock(return_value='desired_value_and_more_text')

        assert executor._is_condition_to_stop_met() == True

    def test_if_is_condition_to_stop_met_returns_false_when_property_value_does_not_contain_desired_value(
        self,
    ):
        executor = RetryActionUntilElementContainsAPropertyValue(
            action=MagicMock(spec=BaseAction),
            web_element=MagicMock(spec=WebElement),
            property_name='test',
            property_value='desired_value',
        )

        executor._get_property_value = MagicMock(return_value='does_not_contain')

        assert executor._is_condition_to_stop_met() == False