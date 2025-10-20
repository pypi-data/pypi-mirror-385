"""
pandas_ti - Technical Indicators for pandas DataFrames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A lightweight, extensible technical indicators library with automatic
OHLCV column detection and mapping.

Basic usage:

   >>> import pandas as pd
   >>> import pandas_ti
   >>> df = pd.read_csv('data.csv')
   >>> df['ATR'] = df.ti.ATR(length=14)
   >>> df.ti.help()

:copyright: (c) 2025 by Javier Calzada Espuny.
:license: MIT, see LICENSE for more details.
"""

import os
import sys
import pydoc

__version__ = "0.1.0"
__author__ = "Javier Calzada Espuny"
__license__ = "MIT"

# Fix for Windows: Prevent help() from trying to use the 'more' pager
# This makes help() work seamlessly on Windows systems
if sys.platform == 'win32':
    os.environ['PAGER'] = ''
    # Also override pydoc's pager directly
    pydoc.pager = pydoc.plainpager

from .accessor import TechnicalIndicatorsAccessor

__all__ = ["TechnicalIndicatorsAccessor", "__version__"]