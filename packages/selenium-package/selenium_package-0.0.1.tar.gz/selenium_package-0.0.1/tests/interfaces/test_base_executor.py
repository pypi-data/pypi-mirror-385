import pytest

from unittest.mock import (
    MagicMock, 
    patch
)

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.interfaces.base_executor import BaseExecutor
from selenium_package.interfaces.base_action import BaseAction
from selenium_package.interfaces.exceptions.exceptions import (
    SeleniumBaseActionException, 
    MaximumAttemptsReachedException
)
from selenium_package.utils.messages import *

from typing import Any

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

@pytest.fixture
def executor_class_that_always_returns_true():
    class InheritedBaseExecutor(BaseExecutor):
        def _is_condition_to_stop_met(self, result: Any = None) -> bool:
            return True

    return InheritedBaseExecutor

@pytest.fixture
def action_class_that_sums_one():
    class ActionClassThatSumsOne(BaseAction):
        def _execute_action(self, result: int = 0) -> Any:
            if result < 3:
                return result + 1
    
    return ActionClassThatSumsOne


class TestBaseExecutor:
    def test_if_raises_value_error_when_action_is_not_a_base_action_instance(
        self,
        executor_class_that_always_returns_true
    ):
        with pytest.raises(ValueError) as e:
            executor_class_that_always_returns_true(action='not_a_base_action_instance')

        assert e.value.args[0] == VARIABLE_MUST_BE_A_BASE_ACTION_INSTANCE.format(
            variable_name='action'
        )

    def test_if_raises_value_error_when_web_element_is_not_a_web_element_instance(
        self,
        action_class_that_sums_one,
        executor_class_that_always_returns_true
    ):
        with pytest.raises(ValueError) as e:
            executor_class_that_always_returns_true(
                action=action_class_that_sums_one(web_instance=mock_webdriver),
                web_element='not_a_web_element_instance'
            )

    def test_if_raises_value_error_when_wait_to_verify_condition_is_not_an_integer(
        self,
        action_class_that_sums_one,
        executor_class_that_always_returns_true
    ):
        with pytest.raises(ValueError) as e:
            executor_class_that_always_returns_true(
                action=action_class_that_sums_one(web_instance=mock_webdriver),
                wait_to_verify_condition='not_an_integer'
            )

        assert e.value.args[0] == VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
            variable_name='wait_to_verify_condition'
        )

    def test_if_raises_value_error_when_wait_to_verify_condition_is_not_greater_than_0(
        self,
        action_class_that_sums_one,
        executor_class_that_always_returns_true
    ):
        with pytest.raises(ValueError) as e:
            executor_class_that_always_returns_true(
                action=action_class_that_sums_one(web_instance=mock_webdriver),
                wait_to_verify_condition=0
            )

        assert e.value.args[0] == VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
            variable_name='wait_to_verify_condition'
        )

    def test_if_run_return_action_result_when_condition_is_met(
        self,
        mock_webdriver,
        executor_class_that_always_returns_true,
        action_class_that_sums_one,
    ):
        action_instance = action_class_that_sums_one(web_instance=mock_webdriver)
        action_instance.run = MagicMock(return_value=1)

        executor_instance = executor_class_that_always_returns_true(
            action=action_instance
        )

        with patch.object(
            executor_instance, 
            'is_condition_to_stop_met', 
            return_value=True
        ) as mock_is_condition_to_stop_met:

            result = executor_instance.run()

            assert result == 1
            assert mock_is_condition_to_stop_met.call_count == 1
            assert action_instance.run.call_count == 1