"""
This module contains the GoToTabThatContainsUrl action.
It will go to the tab that contains the url passed to the constructor.
"""

from selenium_package.interfaces import BaseAction

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_package.utils.messages import *

class GoToTabThatContainsUrl(BaseAction):
    """
    Action that goes to the tab that contains the url passed to the constructor.
    """
    def __init__(
        self,
        web_instance: WebDriver,
        desired_url: str
    ):
        """
        Initialize the GoToTabThatContainsUrl action.
        This action will go to the tab that contains the url passed to the constructor.
        Args:
            web_instance (WebDriver): The webdriver instance to perform the action on.
            desired_url (str): The url of the desired tab.
        """
        super().__init__(web_instance)

        if not isinstance(desired_url, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='desired_url'
                )
            )
        
        self.desired_url = desired_url

    def _return_desired_tab_id_by_url(self) -> str:
        """
        Return the id of the tab that contains the url passed to 
        the constructor.

        Raises:
            ValueError: If the desired url is not found.
        """
        tabs_id = self.web_instance.window_handles
        desired_url = self.desired_url

        for tab_id in tabs_id:
            self.web_instance.switch_to.window(tab_id)
            if desired_url in self.web_instance.current_url:
                desired_tab_id = tab_id
                return desired_tab_id

        raise ValueError(
            DESIRED_URL_NOT_FOUND_MESSAGE.format(
                desired_url=desired_url
            )
        )

    def _execute_action(self) -> None:
        """
        Execute the action.
        It will go to the tab that contains the url passed to 
        the constructor.
        """
        desired_tab_id = self._return_desired_tab_id_by_url()
        self.web_instance.switch_to.window(desired_tab_id)