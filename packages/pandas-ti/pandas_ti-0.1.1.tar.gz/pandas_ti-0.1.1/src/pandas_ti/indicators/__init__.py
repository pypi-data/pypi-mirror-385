"""
Automatic Technical Indicator Registration System.

How it works:
-------------
To create a new indicator, simply:
1. Create a new `.py` file in this folder.
2. Define your function with the `@indicator` decorator.
3. That’s it! It will be automatically registered in the accessor.

Example:
--------
```python
from pandas_ti.indicators import indicator
import pandas as pd

@indicator
def MY_INDICATOR(High: pd.Series, Low: pd.Series, Close: pd.Series, length: int = 14) -> pd.Series:
    '''Documentation for my indicator.'''
    # Your implementation here
    return result
"""

import pkgutil
import importlib

# Dictionary to hold all registered indicators
_INDICATORS = {}

def indicator(func):
    """
    Decorator to automatically register a technical indicator.
    Extracts metadata from the first line of the docstring.
    
    Example
    -------
        >>> @indicator
        >>> def ATR(High, Low, Close, length=14):
            >>> '''Average True Range (ATR) - Calculates the average of the true range.'''
            >>> ...
            >>> return atr
    """
    # Extract metadata from docstring
    if func.__doc__:
        first_line = func.__doc__.strip().split('\n')[0]
        if ' - ' in first_line:
            full_name, description = first_line.split(' - ', 1)
            func._indicator_full_name = full_name.strip()
            func._indicator_description = description.strip()
        else:
            func._indicator_full_name = first_line.strip()
            func._indicator_description = ""
    else:
        func._indicator_full_name = func.__name__
        func._indicator_description = ""
    
    _INDICATORS[func.__name__] = func
    return func


# Import all modules in the current package to register their indicators
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if module_name.startswith('_'):  # Skip __init__ and other private modules
        continue
    
    try:
        importlib.import_module(f"{__name__}.{module_name}")
    except Exception as e:
        print(f"Warning: Could not import {module_name}: {e}")

# Export all registered indicators
__all__ = sorted(_INDICATORS.keys())

# Make indicators accessible directly from the module
globals().update(_INDICATORS)
