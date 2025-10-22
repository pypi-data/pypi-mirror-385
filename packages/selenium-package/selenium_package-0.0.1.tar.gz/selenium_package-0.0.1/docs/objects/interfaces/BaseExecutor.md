
### Base Executor Object ###

A base executor is an object that defines how to perform some ```BaseAction```.

For example: maybe you want to try to insert a certain text on a input until the value inside the input is the desired one. Then, you can use one of the pre-built executors ```RetryActionUntilElementContainsAPropertyValue``` to execute the action of inserting the text on the input until the input contains the desired value.

### 2. Why This interface has been created? ###

The actions performed by the pure selenium does not always have the same result. Sometimes, you may call selenium native functions to insert a text on a input and it fails on the first attempt. Those executors, then, are created to give more robusteness and confiability on your selenium automations. 

### 3. Pre-built Base Executors Available ###

The pre-built base executors are available on ```selenium_package.executos``` and include some executors such as:

    1. Retry action by max attempts
    2. Retry insert insert until value is correct
    3. Retry action until element has a certain property value
    ...

Check the documentation to see all the executors already implemented.

### 3. How to use a executor ###

First of all, you must define an Action to be executed by the executor:

```python
from selenium_packages.actions import CloseAllTabsExceptThatHasTitle

close_action = CloseAllTabsExceptThatHasTitle(
        web_instance= # pass your webdriver instance,
        desired_tab_title= # desired tab title
    )
```

then, to use the executor:

```python
from selenium_package.executors import RetryActionUntilNumberOfTabsIs

executor = RetryActionUntilNumberOfTabsIs(
    action=close_action,
    desired_number_of_tabs=1
)

executor.run()
```

### 4. How to implement your own custom executors ###

To implement your own actions with the desired logic, you must import the ```BaseExecutor``` interface:

```python
from selenium_packages.interfaces import BaseExecutor
```

Then, you must inherit you custom action from BaseExecutor:

```python
class CustomExecutor(BaseExecutor)
     def __init__(
        self,
        action: BaseAction,
        web_element: WebElement = None,
        wait_to_verify_condition: int = None,
        timeout: int = 30,
        #### Add here any additional argument.
     ):
        super().__init__(
            action=action, 
            web_element=web_element,
            wait_to_verify_condition=wait_to_verify_condition,
            timeout=timeout
        )
        
        ### self.additional_argument = 
```

and implement the function ```_is_condition_to_stop_met()``` to define the condition that indicate that the action can exit the loop and stop its retry execution.

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

    def _is_condition_to_stop_met(self, result: Any = None) -> bool:
        ### DEFINE HERE THE LOGIC TO RETURN TRUE WHEN THE ACTION CAN STOP.
        pass 
```

An Example of a custom executor that is already implemented:

```python
class RetryActionUntilElementContainsAPropertyValue(BaseExecutor):
    def __init__(
        self, 
        action: BaseAction, 
        web_element: WebElement, 
        property_name: str, 
        property_value: str,
        wait_to_verify_condition: int = None
    ):
        super().__init__(
            action=action, 
            web_element=web_element, 
            wait_to_verify_condition=wait_to_verify_condition
        )


        if not isinstance(property_name, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='property_name'
                )
            )

        if not isinstance(property_value, str):
            raise ValueError(
                VARIABLE_MUST_BE_A_STRING.format(
                    variable_name='property_value'
                )
            )

        self.web_element = web_element
        self.property_name = property_name
        self.property_value = property_value

    def _get_property_value(self) -> str:
        return GetPropertyValue(
            web_instance=self.action.web_instance, 
            web_element=self.web_element, 
            property_name=self.property_name
        ).run()

    def _is_condition_to_stop_met(self) -> bool:
        property_value = self._get_property_value()
        return self.property_value in property_value
```




















