from unittest.mock import Base, MagicMock

import pytest

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.interfaces import BaseAction

from selenium_package.executors import RetryActionUntilPageTitleIs


class TestRetryActionUntilPageTitleIs:
    @pytest.fixture
    def mock_webdriver(self):
        return MagicMock(spec=WebDriver)

    @pytest.fixture
    def mock_base_action_class(self):
        class InheritedBaseAction(BaseAction):
            def _execute_action(self):
                return 'success'
        
        return InheritedBaseAction

    def test_if_is_condition_to_stop_met_returns_true_if_the_current_page_title_is_equal_to_the_desired_page_title(
        self,
        mock_webdriver,
        mock_base_action_class,
    ):
        action = mock_base_action_class(web_instance=mock_webdriver)
        #action.web_instance.title = 'Test title'
        
        #result = RetryActionUntilPageTitleIs(action, 'Test title')._is_condition_to_stop_met()
        #assert result is True

    def test_if_is_condition_to_stop_met_returns_false_if_the_current_page_title_is_not_equal_to_the_desired_page_title(
        self,
        mock_webdriver,
        mock_base_action_class,
    ):
        action = mock_base_action_class(web_instance=mock_webdriver)
        #action.web_instance.title = 'Test title'
        
        #result = RetryActionUntilPageTitleIs(action, 'Another title')._is_condition_to_stop_met()
        #assert result is True
