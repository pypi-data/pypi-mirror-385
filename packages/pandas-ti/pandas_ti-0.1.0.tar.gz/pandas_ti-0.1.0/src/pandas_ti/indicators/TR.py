import pandas as pd
from . import indicator


@indicator
def TR(High: pd.Series, Low: pd.Series, Close: pd.Series) -> pd.Series:
    """
    True Range (TR).

    Calculates the true range as a measure of price movement volatility.
    The TR is the maximum of three values: the difference between the current
    high and low, the absolute difference between the current high and previous
    close, or the absolute difference between the current low and previous close.

    Returns
    -------
    TR : pd.Series
        Series of true range values.

    Notes
    -----
    Requires DataFrame columns: 'High', 'Low', 'Close'.
    
    The TR captures the full range of price movement, including potential gaps
    between periods, making it a foundational component for volatility indicators.

    Examples
    --------
    >>> df.ti.TR()
    """
    High = High.astype(float)
    Low = Low.astype(float)
    Close = Close.astype(float)

    previous_close = Close.shift(1)
    previous_close.iloc[0] = Close.iloc[0]  # handle first value

    tr1 = (High - Low).abs()
    tr2 = (High - previous_close).abs()
    tr3 = (previous_close - Low).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr
