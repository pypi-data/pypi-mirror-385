import pytest

from unittest.mock import MagicMock, patch

from selenium_package.actions import InsertText

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.utils.messages import *

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

@pytest.fixture
def mock_webelement_instance():
    return MagicMock(spec=WebElement)

class TestInsertText:
    def test_if_raises_value_error_if_text_is_not_a_string(
        self,
        mock_webdriver,
        mock_webelement_instance
    ):
        with pytest.raises(ValueError) as e:
            InsertText(
                web_instance=mock_webdriver,
                web_element=mock_webelement_instance,
                text=123
            )

        assert str(e.value) == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='text'
        )

    def test_if_raises_value_error_if_using_js_is_not_a_boolean(
        self,
        mock_webdriver,
        mock_webelement_instance
    ):
        with pytest.raises(ValueError) as e:
            InsertText(
                web_instance=mock_webdriver,
                web_element=mock_webelement_instance,
                text='test',
                using_js=123
            )

        assert str(e.value) == VARIABLE_MUST_BE_A_BOOLEAN.format(
            variable_name='using_js'
        )

    def test_if_execute_action_calls_execute_action_with_js_when_using_js_is_true(
        self,
        mock_webdriver,
        mock_webelement_instance
    ):
        insert_text_instance = InsertText(
            web_instance=mock_webdriver,
            web_element=mock_webelement_instance,
            text='test',
            using_js=True)

        with patch.object(insert_text_instance, '_execute_action_with_js', return_value=None):
            insert_text_instance._execute_action()
            insert_text_instance._execute_action_with_js.assert_called_once()

    def test_if_execute_action_calls_execute_action_without_js_when_using_js_is_false(
        self,
        mock_webdriver,
        mock_webelement_instance
    ):
        insert_text_instance = InsertText(
            web_instance=mock_webdriver,
            web_element=mock_webelement_instance,
            text='test',
            using_js=False)

        with patch.object(insert_text_instance, '_execute_action_without_js', return_value=None):
            insert_text_instance._execute_action()
            insert_text_instance._execute_action_without_js.assert_called_once()