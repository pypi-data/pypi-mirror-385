from unittest.mock import MagicMock

import pytest

from selenium_package.interfaces import BaseAction

from selenium_package.executors import RetryActionByMaxAttempts

from selenium_package.interfaces.exceptions.exceptions import (
    MaximumAttemptsReachedException,
    SeleniumBaseActionException
)

from selenium_package.utils.messages import *

from selenium.webdriver.chrome.webdriver import WebDriver

@pytest.fixture
def mock_base_action_that_always_returns_true_class():
    class MockBaseActionThatAlwaysReturnsTrue(BaseAction):
        def _execute_action(self):
            return 'success'
    
    return MockBaseActionThatAlwaysReturnsTrue

@pytest.fixture
def mock_base_action_that_always_raises_exception_class():
    class MockBaseActionThatAlwaysRaisesException(BaseAction):
        def _execute_action(self):
            raise Exception('test')
    
    return MockBaseActionThatAlwaysRaisesException

@pytest.fixture
def mock_base_action_that_runs_succesfully_just_on_second_attempt_class():
    class ActionSucceedsOnSecondAttempt(BaseAction):
        def __init__(self, web_instance):
            super().__init__(web_instance)
            self._calls = 0

        def _execute_action(self):
            self._calls += 1
            if self._calls == 1:
                # first attempt raises a real exception object
                raise SeleniumBaseActionException("first attempt failed")
            return "success"

    return ActionSucceedsOnSecondAttempt

class TestRetryActionByMaxAttempts:
    def test_if_raises_error_when_max_attempts_is_not_an_integer(
        self,
        mock_base_action_that_always_returns_true_class
    ):
        action_instance = mock_base_action_that_always_returns_true_class(  
            web_instance=MagicMock(spec=WebDriver)
        )

        with pytest.raises(ValueError) as e:
            RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts='not_an_integer'
        )

        assert e.value.args[0] == VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
            variable_name='max_attempts'
        )

    def test_if_raises_error_when_max_attempts_is_less_than_1(
        self,
        mock_base_action_that_always_returns_true_class
    ):
        action_instance = mock_base_action_that_always_returns_true_class(  
            web_instance=MagicMock(spec=WebDriver)
        )

        with pytest.raises(ValueError) as e:
            RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=0
        )

        assert e.value.args[0] == VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
            variable_name='max_attempts'
        )

    def test_if_is_condition_to_stop_met_returns_true_when_attempt_index_is_greater_than_max_attempts(
        self,
        mock_base_action_that_always_returns_true_class
    ):
        action_instance = mock_base_action_that_always_returns_true_class(  
            web_instance=MagicMock(spec=WebDriver)
        )

        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=3
        )

        is_condition_to_stop_met = retry_action_by_max_attempts_instance._is_condition_to_stop_met(attempt_index=4)

        assert is_condition_to_stop_met

    def test_if_is_condition_to_stop_met_returns_false_when_attempt_index_is_less_than_max_attempts(
        self,
        mock_base_action_that_always_returns_true_class
    ):
        action_instance = mock_base_action_that_always_returns_true_class(  
            web_instance=MagicMock(spec=WebDriver)
        )

        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=3
        )

        is_condition_to_stop_met = retry_action_by_max_attempts_instance._is_condition_to_stop_met(attempt_index=1)

        assert not is_condition_to_stop_met

    def test_if_run_returns_action_result_when_action_runs_successfully(
        self,
        mock_base_action_that_always_returns_true_class
    ):
        action_instance = mock_base_action_that_always_returns_true_class(  
            web_instance=MagicMock(spec=WebDriver)
        )

        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=3
        )

        result = retry_action_by_max_attempts_instance.run()

        assert result == 'success'
    
    def test_if_run_raises_error_when_action_raises_exception_until_max_attempts_is_reached(
        self,
        mock_base_action_that_always_raises_exception_class
    ):
        action_instance = mock_base_action_that_always_raises_exception_class(  
            web_instance=MagicMock(spec=WebDriver)
        )
        
        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=3
        )

        with pytest.raises(MaximumAttemptsReachedException) as e:
            retry_action_by_max_attempts_instance.run()

    def test_if_run_returns_action_result_when_action_runs_successfully_before_max_attempts_is_reached(
        self,
        mock_base_action_that_runs_succesfully_just_on_second_attempt_class
    ):
        action_instance = mock_base_action_that_runs_succesfully_just_on_second_attempt_class(
            web_instance=MagicMock(spec=WebDriver)
        )

        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=2,
        )

        result = retry_action_by_max_attempts_instance.run()

        assert result == "success"

        # optional sanity check: ensure it actually took two calls
        assert action_instance._calls == 2

    def test_if_run_raises_maximum_attempts_reached_exception_when_max_attempts_is_reached(
        self,
        mock_base_action_that_runs_succesfully_just_on_second_attempt_class
    ):
        action_instance = mock_base_action_that_runs_succesfully_just_on_second_attempt_class(
            web_instance=MagicMock(spec=WebDriver)
        )

        retry_action_by_max_attempts_instance = RetryActionByMaxAttempts(
            action=action_instance,
            max_attempts=1,
        )

        with pytest.raises(MaximumAttemptsReachedException) as e:
            retry_action_by_max_attempts_instance.run()

    
        