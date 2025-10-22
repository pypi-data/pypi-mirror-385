
### Base Action Object ###

A base action is, as the name says, a wrapper or a interface that must be implemented to define some kind of selenium action.

### 1. Why This interface has been created? ###
Maybe you have asked: 'why shouldn't I use the basic selenium functions to performs actions such click on a certain element?'.  

The answer is that this interface is created to define conditions and funcionalities that must be implemented to allow it's compatibilitie with another objects of this package such as ***Executors*** .

Additionally, an action can be more complex than those defined by the functions defined by selenium. For example: one of the pre built base actions is ```CloseCloseAllTabsExceptThatContainsTitle```. That action receices the selenium webdriver and the tab title. Then, it contains all the logic to close all the tabs except the ones that contains a certain title. 

Then, you can reutilize that logic whenever is necessary.


### 2. Pre-built Base Actions Available ###

The pre-built base actions are available on ```selenium_package.actions``` and include some actions such as:

    1. Click on element
    2. Click on the screen
    3. Go back to the previous page
    4. Close all tabs that contains title
    5. Close all tabs that has title
    6. Insert text
    7. Go to tab that contains url
    ...

Check the documentation to see all the actions already implemented.

### 3. How to use a base action ###

Here is an example of usage:

```python
from selenium_packages.actions import CloseAllTabsExceptThatHasTitle

action = CloseAllTabsExceptThatHasTitle(
        web_instance= # pass your webdriver instance,
        desired_tab_title= # desired tab title
    )

# execute the action by calling the run method
action.run()
```


### 4. How to implement your own custom actions ###

To implement your own actions with the desired logic, you must import the ```BaseAction``` interface:

```python
from selenium_packages.interfaces import BaseAction
```

Then, you must inherit you custom action from BaseAction:

```python
class CustomAction(BaseAction)
     def __init__(
        self,
        web_instance: Webdriver | WebElement,
        web_element: WebElement | None,
        #### Add here any additional argument.
     ):
        super().__init__(web_instance, web_element)
        
        ### self.additional_argument = 
```

and implement the function ```_execute_action()``` to define the action execution logic

```python
class CustomAction(BaseAction)
     def __init__(
        self,
        web_instance: Webdriver | WebElement,
        web_element: WebElement | None,
        #### Add here any additional argument.
     ):
        super().__init__(web_instance, web_element)
        
        ### self.additional_argument = 

    def _execute_action(self):
        #### DEFINE THE LOGIC HERE
        pass    
```

An Example of a custom action that is already implemented:

```python
class GoToTabThatHasTitle(BaseAction):
    def __init__(
        self,
        web_instance: WebDriver,
        desired_tab_title: str = ''
    ):
        """
        Initialize the GoToTabThatHasTitle action.
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
        Return the id of the tab that has the exact same title 
        passed to the constructor.

        Raises:
            ValueError: If the desired tab title is not found.
        """
        tabs_id = self.web_instance.window_handles
        desired_table_title = self.desired_tab_title

        for tab_id in tabs_id:
            self.web_instance.switch_to.window(tab_id)
            if desired_table_title == self.web_instance.title:
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
        It will go to the tab that has the exact same title passed to 
        the constructor.
        """
        desired_tab_id = self._return_desired_tab_id_by_title()
        self.web_instance.switch_to.window(desired_tab_id)
```




















