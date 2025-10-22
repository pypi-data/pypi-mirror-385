import pytest

from selenium_package.actions import RedirectToPage

from selenium.webdriver.remote.webdriver import WebDriver

from unittest.mock import MagicMock

from selenium_package.utils.messages import *

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

class TestRedirectToPage:
    def test_if_raises_value_error_if_page_url_is_not_a_string(self):
        with pytest.raises(ValueError) as e:
            RedirectToPage(
                web_instance=mock_webdriver,
                page_url=123
            )

        assert str(e.value) == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='page_url'
        )

    def test_if_execute_action_calls_get_on_web_instance(self):
        mock_webdriver = MagicMock(spec=WebDriver)
        redirect_to_page_instance = RedirectToPage(
            web_instance=mock_webdriver,
            page_url='https://www.google.com'
        )

        redirect_to_page_instance._execute_action()
        mock_webdriver.get.assert_called_once_with('https://www.google.com')