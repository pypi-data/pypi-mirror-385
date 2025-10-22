"""robotframework-NestedLogger package.

A Robot Framework library that enables the registration of keywords so that they 
are visible at the HTML level as individual keywords, while their implementation 
is nested in Python.
"""

from .nested_logger import NestedLogger

__version__ = '1.0.1'
__all__ = ['NestedLogger']
