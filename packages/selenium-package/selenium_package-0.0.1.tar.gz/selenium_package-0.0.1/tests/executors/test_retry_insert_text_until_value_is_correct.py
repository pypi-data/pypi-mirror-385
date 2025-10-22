from unittest.mock import patch

from unittest.mock import MagicMock

import pytest

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.interfaces import BaseAction

from selenium_package.executors import RetryInsertTextUntilValueIsCorrect

from selenium_package.utils.messages import *

DESIRED_TEXT = 'test'

@pytest.fixture
def mock_base_action_instance():
    class MockBaseAction(BaseAction):
        def _execute_action(self) -> None:
            return 'SUCCESS'

    return MockBaseAction(
        web_instance=MagicMock(spec=WebDriver)
    )

class TestRetryInsertTextUntilValueIsCorrect:

    def test_if_raises_value_error_if_desired_text_is_not_a_string(
        self,
        mock_base_action_instance
    ):
        with pytest.raises(ValueError) as e:
            RetryInsertTextUntilValueIsCorrect(
                action=mock_base_action_instance,
                web_element=MagicMock(spec=WebElement),
                desired_text=1
            )

        assert str(e.value) == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='desired_text'
        )


        
    