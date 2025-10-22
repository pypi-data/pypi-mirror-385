Interfaces
==========

This section documents the core interfaces and base classes that form the foundation of the selenium package. These interfaces define the contract for actions and executors, providing a consistent API for extending functionality.

Base Classes
------------

.. autoclass:: selenium_package.interfaces.base_action.BaseAction
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.interfaces.base_executor.BaseExecutor
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

The selenium package defines several custom exceptions that are used throughout the codebase:

.. autoclass:: selenium_package.interfaces.exceptions.exceptions.SeleniumBaseActionException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.interfaces.exceptions.exceptions.SeleniumBaseGetterException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.interfaces.exceptions.exceptions.MaximumAttemptsReachedException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.interfaces.exceptions.exceptions.NoMorePagesException
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Here are some examples of how to use the base interfaces:

**Creating a Custom Action:**

.. code-block:: python

   from selenium_package.interfaces import BaseAction
   from selenium.webdriver.remote.webdriver import WebDriver
   from selenium.webdriver.remote.webelement import WebElement

   class CustomAction(BaseAction):
       def __init__(self, web_instance: WebDriver | WebElement, web_element: WebElement | None = None):
           super().__init__(web_instance, web_element)
       
       def _execute_action(self):
           # Your custom action logic here
           return "Action completed"

**Creating a Custom Executor:**

.. code-block:: python

   from selenium_package.interfaces import BaseExecutor, BaseAction

   class CustomExecutor(BaseExecutor):
       def __init__(self, action: BaseAction, web_element=None, wait_to_verify_condition=None, timeout=30):
           super().__init__(action, web_element, wait_to_verify_condition, timeout)
       
       def _is_condition_to_stop_met(self, result=None):
           # Your custom condition logic here
           return True  # or False based on your condition

**Handling Exceptions:**

.. code-block:: python

   from selenium_package.interfaces import SeleniumBaseActionException

   try:
       action = CustomAction(webdriver)
       result = action.execute_action()
   except SeleniumBaseActionException as e:
       print(f"Action failed: {e.message}")
