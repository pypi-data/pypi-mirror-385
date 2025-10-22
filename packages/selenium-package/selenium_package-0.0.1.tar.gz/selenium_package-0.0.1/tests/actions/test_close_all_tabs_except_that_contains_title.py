import pytest
from unittest.mock import MagicMock
from selenium_package.actions import CloseAllTabsExceptThatContainsTitle

from selenium.webdriver.remote.webdriver import WebDriver

import pytest

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

class TestCloseAllTabsExceptThatHasTitle:
    def test_if_raises_value_error_if_title_is_not_str(self):
        with pytest.raises(ValueError):
            CloseAllTabsExceptThatContainsTitle(
                web_instance=MagicMock(),
                desired_tab_title=123  # invalid
            )
            
    def test_if_closes_all_tabs_except_the_one_with_desired_title(
        self,
        mock_webdriver
    ):
        # Simulate three tabs, only one has the desired title
        tabs_with_titles = {
            'id_1': 'not desired title',
            'id_2': 'desired title CLOSE',
            'id_3': 'not desired title'
        }

        mock_webdriver.window_handles = list(tabs_with_titles.keys())

        # This will track which tabs were switched to
        switched_tabs = []

        # This will simulate the current tab title after switching
        def switch_to_window_side_effect(tab_id):
            switched_tabs.append(tab_id)
            mock_webdriver.title = tabs_with_titles[tab_id]

        # Assign side effect
        mock_webdriver.switch_to.window.side_effect = switch_to_window_side_effect

        # Mock `close()` to track how many times it's called
        mock_webdriver.close = MagicMock()

        # Run the action
        action = CloseAllTabsExceptThatContainsTitle(
            web_instance=mock_webdriver,
            desired_tab_title='CLOSE'
        )

        action.run()

        # Check that it switched to all tabs
        assert switched_tabs == ['id_1', 'id_2', 'id_3']

        # It should close the two tabs that don’t have the desired title
        assert mock_webdriver.close.call_count == 2

        
        
