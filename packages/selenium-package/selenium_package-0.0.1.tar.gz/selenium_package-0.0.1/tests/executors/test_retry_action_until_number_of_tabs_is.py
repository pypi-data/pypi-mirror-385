from selenium_package.executors import RetryActionUntilNumberOfTabsIs

from selenium_package.interfaces import BaseAction

from selenium_package.utils.messages import *

from selenium.webdriver.remote.webdriver import WebDriver

import pytest

from unittest.mock import MagicMock

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

@pytest.fixture
def mock_action_instance():
    class InheritedBaseAction(BaseAction):
        def _execute_action(self) -> None:
            pass

    return InheritedBaseAction(
        web_instance=mock_webdriver,
    )

class TestRetryActionUntilNumberOfTabsIs:
    def test_if_raises_value_error_if_desired_number_of_tabs_is_not_an_integer_greater_than_0(
        self, 
        mock_action_instance,
    ):
        with pytest.raises(ValueError):
            RetryActionUntilNumberOfTabsIs(
                action=mock_action_instance,
                desired_number_of_tabs=0
            )

    def test_if_raises_value_error_if_desired_number_of_tabs_is_not_an_integer(
        self, 
        mock_action_instance,
    ):
        with pytest.raises(ValueError):
            RetryActionUntilNumberOfTabsIs(
                action=mock_action_instance,
                desired_number_of_tabs='1'
            )

    def test_if_is_condition_to_stop_met_returns_true_if_desired_number_of_tabs_is_reached(
        self, 
        mock_webdriver,
        mock_action_instance,
    ):
        mock_webdriver.window_handles = ['tab1', 'tab2', 'tab3']

        executor = RetryActionUntilNumberOfTabsIs(
            action=mock_action_instance,
            desired_number_of_tabs=3
        )

        executor.action.web_instance.window_handles = ['tab1', 'tab2', 'tab3']
        result = executor._is_condition_to_stop_met(MagicMock())
        
        assert result is True

    def test_if_is_condition_to_stop_met_returns_false_if_desired_number_of_tabs_is_not_reached(
        self, 
        mock_webdriver,
        mock_action_instance,
    ):

        executor = RetryActionUntilNumberOfTabsIs(
            action=mock_action_instance,
            desired_number_of_tabs=3
        )

        executor.action.web_instance.window_handles = ['tab1', 'tab2']
        result = executor._is_condition_to_stop_met(MagicMock())
        
        assert result is False
    
        