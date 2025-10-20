import pandas as pd
from .TR import TR
from . import indicator


@indicator
def ATR(High: pd.Series, Low: pd.Series, Close: pd.Series, length: int = 14) -> pd.Series:
    """
    Average True Range (ATR).

    Calculates the average of the true range over a specified window of time.
    Useful for measuring volatility and normalizing price movements.

    Parameters
    ----------
    length : int, optional
        Length of the ATR window. Default is 14.

    Returns
    -------
    ATR : pd.Series
        Series containing the ATR values.

    Notes
    -----
    Requires DataFrame columns: 'High', 'Low', 'Close'.
    
    The ATR is a volatility indicator that expands when price movement increases
    and contracts during low volatility.

    Examples
    --------
    >>> df.ti.ATR(length=14)
    """
    tr = TR(High, Low, Close)
    atr = tr.rolling(window=length).mean()

    return atr