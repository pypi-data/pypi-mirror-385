import pandas as pd
from .RTR import RTR
from . import indicator


@indicator
def ARTR(High: pd.Series, Low: pd.Series, Close: pd.Series, length: int = 14) -> pd.Series:
    """
    Average Relative True Range (ARTR).

    Calculates the average relative true range over a specified window.
    This normalized volatility measure is useful for comparing volatility
    across different price levels and securities.

    Parameters
    ----------
    length : int, optional
        Length of the ARTR window. Default is 14.

    Returns
    -------
    ARTR : pd.Series
        Series containing the ARTR values.

    Notes
    -----
    Requires DataFrame columns: 'High', 'Low', 'Close'.
    
    The ARTR normalizes volatility by expressing it relative to price levels,
    making it suitable for cross-asset volatility comparisons.

    Examples
    --------
    >>> df.ti.ARTR(length=14)
    """
    rtr = RTR(High, Low, Close)
    artr = rtr.rolling(window=length).mean()

    return artr