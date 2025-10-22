
import pytest

from unittest.mock import MagicMock

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.remote.webelement import WebElement

from selenium_package.interfaces import (
    BaseAction,
    SeleniumBaseActionException
)

from selenium_package.utils.messages import *

class TestBaseAction:

    @pytest.fixture
    def mock_webdriver(self):
        return MagicMock(spec=WebDriver)

    @pytest.fixture
    def mock_web_element_instance(self):
        return MagicMock(spec=WebElement)

    @pytest.fixture
    def base_action_class(self):
        class InheritedBaseAction(BaseAction):
            def _execute_action(self):
                return 'success'
        
        return InheritedBaseAction

    def test_if_does_not_raise_error_when_web_instance_is_a_webelement_instance(
        self,
        base_action_class,
        mock_web_element_instance
    ):
        base_action_instance = base_action_class(
            web_instance=mock_web_element_instance, 
        )

        assert isinstance(base_action_instance, BaseAction)

    def test_if_does_not_raise_error_when_web_element_is_none(
        self,
        base_action_class,
        mock_webdriver
    ):
        base_action_instance = base_action_class(
            web_instance=mock_webdriver,
        )

        assert isinstance(base_action_instance, BaseAction)

    def test_if_raises_error_when_web_element_is_not_a_web_element_instance(
        self,
        base_action_class,
        mock_webdriver
    ):
        with pytest.raises(ValueError) as e:
            base_action_class(
                web_instance=mock_webdriver,
                web_element='not_a_web_element',
            )

        #assert e.value.args[0] == VARIABLE_MUST_BE_A_WEB_ELEMENT_INSTANCE.format(variable_name='web_element')

    def test_if_raises_selenium_base_action_exception_when_execute_action_raises_exception(
        self,
        base_action_class,
        mock_webdriver
    ):
        base_action_instance = base_action_class(
            web_instance=mock_webdriver,
        )

        base_action_instance._execute_action = MagicMock(side_effect=Exception('test'))

        with pytest.raises(SeleniumBaseActionException) as e:
            base_action_instance.execute_action()

        # #assert e.value.args[0] == BASE_ACTION_FAILED_MESSAGE.format(
        #     action_name='InheritedBaseAction',
        #     error='test'
        # #)

    def test_if_returns_success_when_execute_action_returns_success(
        self,
        base_action_class,
        mock_webdriver
    ):
        base_action_instance = base_action_class(
            web_instance=mock_webdriver,
        )

        result = base_action_instance.run()

        assert result == 'success'
        

    
        