Pre-built Objects
=================

This section documents all the pre-built actions and executors available in the selenium package. These ready-to-use classes provide common functionality for web automation tasks.

Actions
-------

Actions are concrete implementations of the `BaseAction` interface that perform specific operations on web elements or the browser.

Click Actions
~~~~~~~~~~~~~

.. autoclass:: selenium_package.actions.click_on_element.ClickOnElement
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.click_on_the_screen.ClickOnTheScreen
   :members:
   :undoc-members:
   :show-inheritance:

Text Input Actions
~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.actions.insert_text.InsertText
   :members:
   :undoc-members:
   :show-inheritance:

Navigation Actions
~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.actions.redirect_to_page.RedirectToPage
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.go_back_to_the_previous_page.GoBackToThePreviousPage
   :members:
   :undoc-members:
   :show-inheritance:

Tab Management Actions
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.actions.go_to_tab_that_has_title.GoToTabThatHasTitle
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.go_to_tab_that_contains_title.GoToTabThatContainsTitle
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.go_to_tab_that_contains_url.GoToTabThatContainsUrl
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.close_all_tabs_except_that_has_title.CloseAllTabsExceptThatHasTitle
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.actions.close_all_tabs_except_that_contains_title.CloseAllTabsExceptThatContainsTitle
   :members:
   :undoc-members:
   :show-inheritance:

Executors
---------

Executors are concrete implementations of the `BaseExecutor` interface that control how actions are executed, including retry logic and conditional execution.

Basic Executors
~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.default_executor.DefaultExecutor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.timeout_executor.TimeoutExecutor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_executor.RetryExecutor
   :members:
   :undoc-members:
   :show-inheritance:

Retry Executors
~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_action_by_max_attempts.RetryActionByMaxAttempts
   :members:
   :undoc-members:
   :show-inheritance:

Element-based Retry Executors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_action_until_element_is_located.RetryActionUntilElementIsLocated
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_action_until_element_has_a_property_value.RetryActionUntilElementHasAPropertyValue
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_action_until_element_contains_a_property_value.RetryActionUntilElementContainsAPropertyValue
   :members:
   :undoc-members:
   :show-inheritance:

Page-based Retry Executors
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_action_until_page_title_is.RetryActionUntilPageTitleIs
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_action_until_page_title_contains.RetryActionUntilPageTitleContains
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_action_until_url_contains.RetryActionUntilUrlContains
   :members:
   :undoc-members:
   :show-inheritance:

Tab-based Retry Executors
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_action_until_another_tab_is_opened.RetryActionUntilAnotherTabIsOpened
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: selenium_package.executors.retry_action_until_number_of_tabs_is.RetryActionUntilNumberOfTabsIs
   :members:
   :undoc-members:
   :show-inheritance:

File-based Retry Executors
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_action_until_new_file_has_been_detected.RetryActionUntilNewFileHasBeenDetected
   :members:
   :undoc-members:
   :show-inheritance:

Text Input Retry Executors
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: selenium_package.executors.retry_insert_text_until_value_is_correct.RetryInsertTextUntilValueIsCorrect
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Here are some practical examples of how to use the pre-built actions and executors:

**Basic Action Usage:**

.. code-block:: python

   from selenium_package.actions import ClickOnElement, InsertText, RedirectToPage
   from selenium.webdriver.common.by import By
   from selenium import webdriver

   driver = webdriver.Chrome()
   
   # Navigate to a page
   redirect_action = RedirectToPage(driver, "https://example.com")
   redirect_action.execute_action()
   
   # Find an element and click it
   element = driver.find_element(By.ID, "submit-button")
   click_action = ClickOnElement(driver, element)
   click_action.execute_action()
   
   # Insert text into an input field
   input_element = driver.find_element(By.NAME, "username")
   insert_action = InsertText(driver, input_element, "myusername")
   insert_action.execute_action()

**Using Executors for Retry Logic:**

.. code-block:: python

   from selenium_package.executors import RetryActionUntilElementIsLocated, RetryActionByMaxAttempts
   from selenium.webdriver.common.by import By
   
   # Retry clicking until an element appears
   click_action = ClickOnElement(driver, some_element)
   retry_executor = RetryActionUntilElementIsLocated(
       click_action, 
       (By.ID, "success-message")
   )
   retry_executor.run()
   
   # Retry an action up to 3 times
   retry_max_executor = RetryActionByMaxAttempts(click_action, max_attempts=3)
   retry_max_executor.run()

**Combining Actions and Executors:**

.. code-block:: python

   from selenium_package.executors import RetryActionUntilUrlContains
   
   # Navigate and wait for URL change
   redirect_action = RedirectToPage(driver, "https://example.com/login")
   url_retry_executor = RetryActionUntilUrlContains(redirect_action, "login")
   url_retry_executor.run()
