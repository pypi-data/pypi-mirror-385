import pandas as pd
from . import indicator


@indicator
def RTR(High: pd.Series, Low: pd.Series, Close: pd.Series) -> pd.Series:
    """
    Relative True Range (RTR).

    Calculates the relative true range as a normalized volatility measure.
    The RTR expresses true range as a percentage of the previous close price,
    enabling volatility comparisons across different price levels.

    Returns
    -------
    RTR : pd.Series
        Series containing the relative true range values.

    Notes
    -----
    Requires DataFrame columns: 'High', 'Low', 'Close'.
    
    By normalizing true range relative to price, the RTR provides a scale-independent
    measure of volatility useful for comparing securities at different price levels.

    Examples
    --------
    >>> df.ti.RTR()
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
    rtr = tr / previous_close

    return rtr
