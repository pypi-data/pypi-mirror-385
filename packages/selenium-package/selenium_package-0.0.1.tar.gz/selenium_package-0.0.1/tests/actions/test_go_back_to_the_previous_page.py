from selenium_package.actions import GoBackToThePreviousPage

from selenium.webdriver.remote.webdriver import WebDriver

from unittest.mock import MagicMock, patch


class TestGoBackToThePreviousPage:

    def test_if_execute_action_calls_back_on_web_instance(self):
        mock_webdriver = MagicMock(spec=WebDriver)
        go_back_to_the_previous_page_instance = GoBackToThePreviousPage(
            web_instance=mock_webdriver
        )

        with patch.object(mock_webdriver, 'back') as mock_back:
            go_back_to_the_previous_page_instance._execute_action()
            mock_back.assert_called_once()