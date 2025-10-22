# Selenium Package

A Python package for Selenium automation with action and executor patterns.

## Features

- **BaseAction**: Abstract base class for creating Selenium actions
- **BaseExecutor**: Abstract base class for executing actions with conditions and timeouts
- **Exception Handling**: Custom exceptions for better error handling
- **Type Hints**: Full type annotation support

## Installation

```bash
pip install selenium-package
```

## Usage

### Basic Action

```python
from selenium_package import BaseAction
from selenium.webdriver import Chrome

class ClickAction(BaseAction):
    def _execute_action(self):
        element = self.web_instance.find_element("id", "my-button")
        element.click()
        return "Button clicked successfully"

# Usage
driver = Chrome()
action = ClickAction(web_instance=driver)
result = action.run()
```

### Basic Executor

```python
from selenium_package import BaseExecutor

class ClickExecutor(BaseExecutor):
    def _is_condition_to_stop_met(self, result=None):
        return result == "Button clicked successfully"

# Usage
executor = ClickExecutor(
    action=ClickAction(web_instance=driver),
    timeout=30,
    wait_to_verify_condition=1
)
result = executor.run()
```

## Development

### Setup

```bash
git clone https://github.com/jgabrielsb/selenium-package.git
cd selenium-package
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black selenium_package tests
isort selenium_package tests
```

## License

MIT License - see LICENSE file for details.
