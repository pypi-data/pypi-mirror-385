# robotframework-NestedLogger

The goal of this library is to enable the registration of keywords so that they are visible at the HTML level as individual keywords, while their implementation is nested in python.

## Description

The `NestedLogger` library allows Robot Framework test libraries to dynamically log keywords during test execution. This is particularly useful when you want to break down complex operations into smaller inside of python

## Installation

### Install from source

```bash
pip install .
```

### Install in development mode

```bash
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install robotframework-nestedlogger
```

## Usage

### Basic Example

```python
from NestedLogger import NestedLogger
from robot.api.deco import keyword

class MyLibrary:
    
    @keyword("Process Multiple Items")
    def process_items(self, *items):
        logger = NestedLogger()
        lib_name = self.__class__.__name__
        
        for item in items:
            kw_name = f"Process Item: {item}"
            logger.start_keyword(kw_name, lib_name)
            
            try:
                # Your processing logic here
                self._process_single_item(item)
                logger.end_keyword(kw_name, lib_name, 'PASS')
            except Exception as e:
                logger.end_keyword(kw_name, lib_name, 'FAIL')
                raise e
    
    def _process_single_item(self, item):
        # Implementation
        print(f"Processing: {item}")
```

### In Robot Framework Test

```robotframework
*** Settings ***
Library    MyLibrary

*** Test Cases ***
Test Processing
    Process Multiple Items    item1    item2    item3
```

Each item will appear as a separate keyword in the log.html report with its own pass/fail status.

## API

### NestedLogger Class

#### `start_keyword(kwname, libname, status='FAIL')`
Starts logging a new nested keyword.

**Arguments:**
- `kwname` (str): Name of the keyword to log
- `libname` (str): Name of the library owning the keyword
- `status` (str): Initial status (default: 'FAIL')

#### `end_keyword(kwname, libname, status)`
Ends logging of a nested keyword.

**Arguments:**
- `kwname` (str): Name of the keyword to log
- `libname` (str): Name of the library owning the keyword
- `status` (str): Final status ('PASS' or 'FAIL')

## Requirements

- Python >= 3.10
- robotframework >= 7.3.0

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
