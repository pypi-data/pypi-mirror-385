import pytest

from unittest.mock import MagicMock, patch

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.actions import ClickOnElement

from selenium_package.utils.messages import *


@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

@pytest.fixture
def mock_webelement_instance():
    return MagicMock(spec=WebElement)

class TestClickOnElement:
    def test_if_execute_action_calls_click_on_element(
        self,
        mock_webdriver,
        mock_webelement_instance
    ):
        click_on_element_instance = ClickOnElement(
            web_instance=mock_webdriver,
            web_element=mock_webelement_instance
        )

        with patch.object(mock_webelement_instance, 'click', return_value=None):
            click_on_element_instance._execute_action()
            mock_webelement_instance.click.assert_called_once()
    