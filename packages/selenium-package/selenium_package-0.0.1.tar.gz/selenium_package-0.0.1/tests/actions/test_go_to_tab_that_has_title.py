import pytest

from selenium_package.actions import GoToTabThatHasTitle

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from unittest.mock import MagicMock, patch

from selenium_package.utils.messages import *

@pytest.fixture
def mock_webdriver():
    return MagicMock(spec=WebDriver)

@pytest.fixture
def mock_webelement_instance():
    return MagicMock(spec=WebElement)

class TestGoToTabThatContainsTitle:
    def test_if_raises_value_error_if_desired_tab_title_is_not_a_string(self):
        with pytest.raises(ValueError) as e:
            GoToTabThatHasTitle(
                web_instance=mock_webdriver,
                desired_tab_title=123
            )

        assert str(e.value) == VARIABLE_MUST_BE_A_STRING.format(
            variable_name='desired_tab_title'
        )

    def test_if_returns_desired_tab_id_when_desired_tab_title_is_found(
        self,
    ):
        class MockWebDriver:
            class _SwitchTo:
                def __init__(self, driver):
                    self._driver = driver

                def window(self, handle: str):
                    if handle not in self._driver.titles_for_window_handles:
                        raise ValueError(f"Unknown handle: {handle}")
                    self._driver.current_window_handle = handle
                    self._driver.title = self._driver.titles_for_window_handles[handle]

            def __init__(self):
                self.titles_for_window_handles = {
                    "tab_1": "tab_1_title",
                    "tab_2": "desired title",
                    "tab_3": "tab_3_title",
                }
                self.window_handles = list(self.titles_for_window_handles.keys())
                self.current_window_handle = "tab_1"
                self.title = self.titles_for_window_handles[self.current_window_handle]
                self.switch_to = MockWebDriver._SwitchTo(self)

        mock_webdriver = MockWebDriver()
        
        go_to_tab_that_has_title_instance = GoToTabThatHasTitle(
            web_instance=mock_webdriver,
            desired_tab_title='desired title'
        )
        
        desired_tab_id = go_to_tab_that_has_title_instance._return_desired_tab_id_by_title()
        
        assert desired_tab_id == 'tab_2'

    def test_if_raises_value_error_if_desired_tab_is_not_found(
        self,
    ):
        class MockWebDriver:
            class _SwitchTo:
                def __init__(self, driver):
                    self._driver = driver

                def window(self, handle: str):
                    if handle not in self._driver.titles_for_window_handles:
                        raise ValueError(f"Unknown handle: {handle}")
                    self._driver.current_window_handle = handle
                    self._driver.title = self._driver.titles_for_window_handles[handle]

            def __init__(self):
                self.titles_for_window_handles = {
                    "tab_1": "tab_1_title",
                    "tab_2": "tab_2_title",
                    "tab_3": "tab_3_title",
                }
                self.window_handles = list(self.titles_for_window_handles.keys())
                self.current_window_handle = "tab_1"
                self.title = self.titles_for_window_handles[self.current_window_handle]
                self.switch_to = MockWebDriver._SwitchTo(self)

        mock_webdriver = MockWebDriver()
        
        go_to_tab_that_has_title_instance = GoToTabThatHasTitle(
            web_instance=mock_webdriver,
            desired_tab_title='desired title'
        )
        
        with pytest.raises(ValueError) as e:
            go_to_tab_that_has_title_instance._return_desired_tab_id_by_title()
        
        assert str(e.value) == DESIRED_TAB_TITLE_NOT_FOUND_MESSAGE.format(
            desired_tab_title='desired title'
        )

    
        
        

        

    