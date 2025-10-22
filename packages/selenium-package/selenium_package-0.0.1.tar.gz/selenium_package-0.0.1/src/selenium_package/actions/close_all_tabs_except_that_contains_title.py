"""
This module contains the CloseAllTabsExceptThatContainsTitle action.
It will close all tabs except the one that contains the title passed to the constructor.
"""
from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.utils.messages import *

class CloseAllTabsExceptThatContainsTitle(BaseAction):
    """
    Action that closes all tabs except the one that contains the title passed to the constructor.
    """
    def __init__(
        self,
        web_instance: WebDriver,
        desired_tab_title: str
    ):
        """
        Initialize the CloseAllTabsExceptThatContainsTitle action.
        This action will close all tabs except the one that contains the title 
        passed to the constructor.
        Args:
            web_instance (WebDriver): The webdriver instance.
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

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will change to all tabs and close the ones that do 
        not contain the desired title.
        """
        tabs_id = self.web_instance.window_handles
        
        for tab_id in tabs_id:
            self.web_instance.switch_to.window(tab_id)
            if self.desired_tab_title not in self.web_instance.title:
                self.web_instance.close()

    
            
                