"""
This module contains the GoToTabThatContainsTitle action.
It will go to the tab that contains the title passed to the constructor.
"""
from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.utils.messages import *

class GoToTabThatContainsTitle(BaseAction):
    """
    Action that goes to the tab that contains the title passed to the constructor.
    """
    def __init__(
        self,
        web_instance: WebDriver,
        desired_tab_title: str
    ):
        """
        Initialize the GoToTabThatContainsTitle action.
        This action will go to the tab that contains the title passed to the constructor.
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
            desired_tab_title (str): The title of the desired tab.
        """
        super().__init__(web_instance)

        if not isinstance(desired_tab_title, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='desired_tab_title'
                )
            )
        
        self.desired_tab_title = desired_tab_title

    def _return_desired_tab_id_by_title(self) -> str:
        """
        Return the id of the tab that contains the title passed 
        to the constructor.

        Raises:
            ValueError: If the desired tab title is not found.
        """
        tabs_id = self.web_instance.window_handles
        desired_table_title = self.desired_tab_title

        for tab_id in tabs_id:
            self.web_instance.switch_to.window(tab_id)
            if desired_table_title in self.web_instance.title:
                desired_tab_id = tab_id
                return desired_tab_id

        raise ValueError(
            DESIRED_TAB_TITLE_NOT_FOUND_MESSAGE.format(
                desired_tab_title=desired_table_title
            )
        )

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will go to the tab that contains the title passed to 
        the constructor.
        """
        desired_tab_id = self._return_desired_tab_id_by_title()
        self.web_instance.switch_to.window(desired_tab_id)