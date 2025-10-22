"""
This module contains the ClickOnTheScreen action.
It will simply click on the screen at the point passed to the constructor.
"""
from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.interfaces import BaseAction

from selenium.webdriver.common.action_chains import ActionChains

from selenium_package.utils.messages import *

class ClickOnTheScreen(BaseAction):
    """
    Action that clicks on the screen at the point passed to the constructor.
    """
    def __init__(
        self, 
        web_instance: WebDriver, 
        x_coordinate: int,
        y_coordinate: int,
    ):
        """
        This action will click on the screen at the point passed to the constructor.
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
            x_coordinate (int): The x coordinate to click on.
            y_coordinate (int): The y coordinate to click on.
        """
        super().__init__(web_instance)

        if not isinstance(x_coordinate, int) or not isinstance(y_coordinate, int):
            raise ValueError(
                VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
                    variable_name='x_coordinate'
                )
            )
            raise ValueError(
                VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0.format(
                    variable_name='y_coordinate'
                )
            )

        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def _execute_action(self) -> None:
        action_chains = ActionChains(self.web_instance)
        action_chains.move_by_offset(
            self.x_coordinate, 
            self.y_coordinate
        ).click().perform()
        