import pytest

from selenium_package.actions import ClickOnTheScreen

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.common.action_chains import ActionChains

from unittest.mock import (
    MagicMock,
    patch
)

from selenium_package.utils.messages import *

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

class TestClickOnTheScreen:
    def test_if_raises_value_error_if_click_on_point_is_not_a_point_2d(self):
        with pytest.raises(ValueError) as e:
            ClickOnTheScreen(
                web_instance=mock_webdriver,
                x_coordinate=None,
                y_coordinate=456
            )

        assert str(e.value) == VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
            variable_name='x_coordinate'
        )

    def test_if_execute_action_calls_move_by_offset(self):
        mock_webdriver = MagicMock(spec=WebDriver)
        click_on_the_screen_instance = ClickOnTheScreen(
            web_instance=mock_webdriver,
            x_coordinate=100,
            y_coordinate=200
        )

        with patch.object(ActionChains, 'move_by_offset') as mock_move_by_offset:
            click_on_the_screen_instance._execute_action()
            mock_move_by_offset.assert_called_once_with(100, 200)