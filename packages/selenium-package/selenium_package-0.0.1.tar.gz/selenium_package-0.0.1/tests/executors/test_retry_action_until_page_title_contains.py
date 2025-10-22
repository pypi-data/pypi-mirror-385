from selenium_package.executors import RetryActionUntilPageTitleContains

from unittest.mock import MagicMock

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.utils.messages import *

import pytest

class TestRetryActionUntilPageTitleContains:
    def test_if_raises_value_error_when_desired_page_title_is_not_a_string(self):
        with pytest.raises(ValueError) as e:
            RetryActionUntilPageTitleContains(
                action=MagicMock(spec=BaseAction),
                desired_page_title=123,
            )

        assert e.value.args[0] == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='desired_page_title'
        )

    def test_if_is_condition_to_stop_met_returns_true_when_current_page_title_contains_desired_page_title(
        self,
    ):
        executor = RetryActionUntilPageTitleContains(
            action=MagicMock(spec=BaseAction),
            desired_page_title='desired_page_title',
        )

        executor._get_current_page_title = MagicMock(return_value='desired_page_title')

        assert executor._is_condition_to_stop_met() == True

    def test_if_is_condition_to_stop_met_returns_false_when_current_page_title_does_not_contain_desired_page_title(
        self,
    ):
        executor = RetryActionUntilPageTitleContains(
            action=MagicMock(spec=BaseAction),
            desired_page_title='desired_page_title',
        )

        executor._get_current_page_title = MagicMock(return_value='does_not_contain')

        assert executor._is_condition_to_stop_met() == False