"""
Message constants for the selenium package.
"""

# Base action messages
BASE_ACTION_FAILED_MESSAGE = "Action {action_name} failed: {error}"
DESIRED_URL_NOT_FOUND_MESSAGE = "Desired url '{desired_url}' not found"
DESIRED_TAB_TITLE_NOT_FOUND_MESSAGE = "Desired tab title '{desired_tab_title}' not found"

# Variable validation messages
VARIABLE_MUST_BE_A_WEB_ELEMENT_INSTANCE = "Variable '{variable_name}' must be a WebElement instance"
VARIABLE_MUST_BE_A_BASE_ACTION_INSTANCE = "Variable '{variable_name}' must be a BaseAction instance"
VARIABLE_MUST_BE_AN_INTEGER_GREATER_THAN_0 = "Variable '{variable_name}' must be an integer greater than 0"
VARIABLE_MUST_BE_A_BOOLEAN = "Variable '{variable_name}' must be a boolean"
VARIABLE_MUST_BE_A_STRING = "Variable '{variable_name}' must be a string"
VARIABLE_MUST_BE_A_PATH_INSTANCE = "Variable '{variable_name}' must be a Path instance"

MAXIMUM_ATTEMPTS_REACHED_MESSAGE = "Maximum attempts reached. Exceptions raised:\n{exceptions}"
