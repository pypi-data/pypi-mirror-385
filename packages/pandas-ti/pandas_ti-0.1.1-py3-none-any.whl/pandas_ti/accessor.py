"""
Pandas DataFrame accessor for technical indicators.

Fully automated system:
- Add @indicator on top of any function in indicators/
- Automatically registers it as an accessor method
- Automatically maps OHLCV columns
- Preserves docstrings for help()
"""

import pandas as pd
from pandas.api.extensions import register_dataframe_accessor
from typing import Optional, Dict
import inspect
from functools import wraps
import textwrap
from . import indicators

# Possible variations of OHLCV column names
COLUMN_VARIATIONS = {
    'Open': ['Open', 'OPEN', 'open', 'O', 'o'],
    'High': ['High', 'HIGH', 'high', 'H', 'h'],
    'Low': ['Low', 'LOW', 'low', 'L', 'l'],
    'Close': ['Close', 'CLOSE', 'close', 'C', 'c'],
    'Volume': ['Volume', 'VOLUME', 'volume', 'Vol', 'vol', 'V', 'v']
}

# Mapping of function parameters to OHLCV columns
OHLCV_PARAMS = {'Open', 'High', 'Low', 'Close', 'Volume'}


def _create_method(indicator_func):
    """Creates a method that automatically maps OHLCV columns."""
    sig = inspect.signature(indicator_func)
    ohlcv_in_func = {name for name in sig.parameters if name in OHLCV_PARAMS}
    
    @wraps(indicator_func)
    def method(self, **kwargs):
        # Map OHLCV columns from the accessor to the function
        call_kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name in ohlcv_in_func:
                call_kwargs[param_name] = getattr(self, param_name)
            elif param_name in kwargs:
                call_kwargs[param_name] = kwargs[param_name]
            elif param.default != inspect.Parameter.empty:
                call_kwargs[param_name] = param.default
        
        return indicator_func(**call_kwargs)
    
    # Create a signature without OHLCV parameters for help()
    new_params = [inspect.Parameter('self', inspect.Parameter.POSITIONAL_OR_KEYWORD)]
    new_params.extend(p for name, p in sig.parameters.items() if name not in ohlcv_in_func)
    method.__signature__ = inspect.Signature(new_params)
    
    # Clean docstring to remove OHLCV parameters
    if indicator_func.__doc__:
        import re
        doc = indicator_func.__doc__
        
        # Remove OHLCV parameters from the Parameters section
        for param_name in ohlcv_in_func:
            # Pattern: parameter name, type annotation, and description (multi-line)
            pattern = rf'^\s+{param_name}\s*:.*?(?=^\s+\w+\s*:|^\s*Returns|^\s*Raises|^\s*Examples|^\s*Notes|^\s*$)'
            doc = re.sub(pattern, '', doc, flags=re.MULTILINE | re.DOTALL)
        
        method.__doc__ = doc
    
    return method


@register_dataframe_accessor("ti")
class TechnicalIndicatorsAccessor:
    """
    Accessor for technical indicators in pandas DataFrames.
    
    Examples
    --------
    >>> import pandas_ti
    >>> df.ti.TR()
    >>> df.ti.ATR(length=14)
    >>> help(df.ti.ATR)  # View documentation for any indicator
    >>> df.ti.available_indicators  # List all available indicators
    """
    
    def __init__(self, pandas_obj: pd.DataFrame, column_mapping: Optional[Dict[str, str]] = None):
        self._df = pandas_obj
        self._column_mapping = self._init_mapping(column_mapping)
        self._validate_columns()
        
        # Shortcuts to columns
        self.Open = self._df[self._column_mapping['Open']]
        self.High = self._df[self._column_mapping['High']]
        self.Low = self._df[self._column_mapping['Low']]
        self.Close = self._df[self._column_mapping['Close']]
        self.Volume = self._df[self._column_mapping['Volume']] if self._column_mapping.get('Volume') else None
        
        # Automatically register all indicators
        self._register_all_indicators()

    def _init_mapping(self, column_mapping=None):
        """Automatically detects OHLCV columns in the DataFrame."""
        if column_mapping:
            return {k: v for k, v in column_mapping.items()}
        
        mapping = {}
        for key, variations in COLUMN_VARIATIONS.items():
            for name in variations:
                if name in self._df.columns:
                    mapping[key] = name
                    break
            else:
                mapping[key] = None
        return mapping

    def _validate_columns(self):
        """Validates that the required columns exist."""
        missing = [k for k in COLUMN_VARIATIONS if self._column_mapping.get(k) is None]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def _register_all_indicators(self):
        """Automatically registers all indicators as methods."""
        for name in indicators.__all__:
            if hasattr(indicators, name):
                func = getattr(indicators, name)
                method = _create_method(func)
                setattr(self, name, method.__get__(self, type(self)))

    @property
    def available_indicators(self):
        """List of all available indicators."""
        return sorted(indicators.__all__)
    
    def help(self, indicator_name=None):
        """
        Show help for indicators with clean formatting.
        
        Parameters
        ----------
        indicator_name : str, optional
            Name of the indicator. If None, shows all available indicators.
        
        Examples
        --------
        >>> df.ti.help()  # List all indicators
        >>> df.ti.help('ATR')  # Show help for ATR
        """
        if indicator_name is None:
            print("Available Technical Indicators:")
            print("=" * 80)
            for name in self.available_indicators:
                func = getattr(indicators, name, None)
                if func:
                    desc = getattr(func, '_indicator_description', '')
                    print(f"  {name:10} {('- ' + desc) if desc else ''}")
            print("-" * 80)
            print("Use: df.ti.help('INDICATOR_NAME') for details")
            print("=" * 80)
            return

        if not hasattr(self, indicator_name):
            print(f"Indicator '{indicator_name}' not found.")
            return

        method = getattr(self, indicator_name)
        doc = getattr(method, "__doc__", "")
        if not doc:
            print(f"No documentation available for '{indicator_name}'.")
            return

        print(f"{indicator_name}() — Technical Indicator")
        print("=" * 80)
        print(textwrap.dedent(doc).strip())
        print("=" * 80)
