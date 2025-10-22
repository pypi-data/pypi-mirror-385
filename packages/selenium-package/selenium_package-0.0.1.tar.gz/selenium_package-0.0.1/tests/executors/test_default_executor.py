from selenium_package.executors import DefaultExecutor

from unittest.mock import MagicMock

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webelement import WebElement


class TestDefaultExecutor:
    def test_if_is_condition_to_stop_met_returns_true(self):
        executor = DefaultExecutor(
            action=MagicMock(spec=BaseAction),
            web_element=MagicMock(spec=WebElement),
        )
        assert executor.is_condition_to_stop_met() == True