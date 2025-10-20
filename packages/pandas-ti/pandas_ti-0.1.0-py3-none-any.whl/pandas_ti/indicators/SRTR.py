import pandas as pd
import numpy as np
from scipy.stats import norm
from statsmodels.tsa.stattools import acovf
from .RTR import RTR
from typing import Literal
from . import indicator


def _SRTR_iid(RTR: pd.Series, N: int = 1000, expand: bool = False, n: int = 14, full: bool = False):
    """
    Standardize rolling mean of log(Relative True Range) under the i.i.d. assumption.
    """
    df = pd.DataFrame({"RTR": RTR})

    # 1. Log-transform
    df['log_RTR'] = np.log(df['RTR'].clip(lower=1e-8))

    # 2. Rolling arithmetic mean of log(RTR)
    df['mu_n'] = df['log_RTR'].rolling(window=n).mean()

    # 3. Historical rolling mu/sigma
    if expand:
        df['mu_N'] = np.nan
        df.loc[df.index[N-1:], 'mu_N'] = df['log_RTR'].iloc[N-1:].expanding().mean()
        df['sigma'] = np.nan
        df.loc[df.index[N-1:], 'sigma'] = df['log_RTR'].iloc[N-1:].expanding().std(ddof=1)
    else:
        df['mu_N'] = df['log_RTR'].rolling(window=N).mean()
        df['sigma'] = df['log_RTR'].rolling(window=N).std(ddof=1)

    # 4. Z-score and percentile
    df['z_score'] = (df['mu_n'] - df['mu_N']) / (df['sigma'] / np.sqrt(n))

    # 5. Map to percentile (p value)
    df['p'] = norm.cdf(df['z_score'])

    if full:
        return df[["RTR", "mu_N", "sigma", "mu_n", "z_score", "p"]]
    else:
        return df["p"]



def _hac_variance(hist: np.ndarray, mu: float, L: int, n: int) -> float:
    """
    Compute the HAC / Newey-West variance estimator for the mean of a series.

    Parameters
    ----------
        hist : np.ndarray
            Historical data window
        mu : float
            Mean of historical data
        L : int
            Truncation lag for autocovariances
        n : int
            Sub-window size for rolling mean

    Returns
    -------
        variance : float
            HAC-adjusted variance of the rolling mean
    """
    # 1. Center data around mean
    diffs = hist - mu

    # 2. Compute autocovariances (use statsmodels for vectorized computation)
    gamma = acovf(diffs, nlag=L, adjusted=False, fft=False)

    # Bartlett weights: W0 = 1, Wk = 1 - k/(L+1)
    weights = np.concatenate([[1], 2 * (1 - np.arange(1, L+1)/(L+1))])

    # 4. Variance
    variance = np.dot(weights, gamma) / n

    return variance


def _SRTR_cluster(RTR: pd.Series, N: int = 1000, expand: bool = False, n: int = 14, L: int = None, full: bool = False):
    """
    Volatility metric using rolling arithmetic mean of log(RTR) with HAC / Newey-West adjustment.

    Notes
    -----
    Compatible with pandas 3.0: Uses .loc indexing to avoid chained assignment warnings.
    """
    if L is None:
        L = n - 1
    if not isinstance(L, int) or L <= 0:
        raise ValueError("L must be a positive integer.")
    if L > N - 1:
        raise ValueError("L must be <= N-1.")

    df = pd.DataFrame({"RTR": RTR})

    # 1. Log-transform
    df['log_RTR'] = np.log(df['RTR'].clip(lower=1e-8))

    # 2. Short-term rolling mean
    df['mu_n'] = df['log_RTR'].rolling(window=n).mean()

    # 3. Long-term mean (rolling or expanding after N)
    if expand:
        df['mu_N'] = np.nan
        df.loc[df.index[N-1:], 'mu_N'] = df['log_RTR'].iloc[N-1:].expanding().mean()

        # Vectorized HAC variance for expanding windows
        temp = df['log_RTR'].iloc[N-1:].expanding(min_periods=n).apply(
            lambda w: np.sqrt(_hac_variance(w.values, np.mean(w.values), L, n))
        )
        df['sigma'] = np.nan
        df.loc[df.index[N-1:], 'sigma'] = temp
    else:
        df['mu_N'] = df['log_RTR'].rolling(window=N).mean()

        # Vectorized HAC variance for rolling windows
        df['sigma'] = df['log_RTR'].rolling(window=N).apply(
            lambda w: np.sqrt(_hac_variance(w.values, np.mean(w.values), L, n))
        )

    # Match original NaN placement for consistency
    start_idx = (N - 1 if expand else N - 1) + (n - 1)
    df.loc[df.index[:start_idx], 'sigma'] = np.nan

    # 4. Z-score where all components are available
    mask = df['mu_n'].notna() & df['mu_N'].notna() & df['sigma'].notna()
    df['z_score'] = np.nan
    df.loc[mask, 'z_score'] = (df.loc[mask, 'mu_n'] - df.loc[mask, 'mu_N']) / df.loc[mask, 'sigma']

    # 5. Percentile
    df['p'] = norm.cdf(df['z_score'])

    if not full:
        return df['p']
    else:
        return df[["RTR", "mu_N", "sigma", "mu_n", "z_score", "p"]]



@indicator
def SRTR(
    High: pd.Series,
    Low: pd.Series,
    Close: pd.Series,
    N: int = 1000,
    expand: bool = False,
    n: int = 14,
    method: Literal['iid', 'cluster'] = "cluster",
    L: int = None,
    full: bool = False
    ):
    """
    Standardized Relative True Range (SRTR).

    Calculates a standardized volatility metric of the relative true range.
    Standardizes the short-term rolling mean against long-term historical mean
    and standard deviation of log(Relative True Range) using either the i.i.d.
    assumption or a HAC/Newey-West estimator.

    Parameters
    ----------
    expand : bool, optional
        If True, use expanding window after initial N periods for long-term mean and std, 
        allowing adaptation to changing volatility. If False, use fixed rolling window of size N. Default is False.
    n : int, optional
        Window size for short-term rolling mean. Default is 14.
    method : {'iid', 'cluster'}, optional
        Method for variance estimation. 'iid' for independent assumption,
        'cluster' for HAC/Newey-West adjustment. Default is 'cluster'.
    L : int, optional
        Truncation lag for HAC estimator (only used if method='cluster').
        Default is None (uses n-1).
    full : bool, optional
        If True, return full DataFrame with all intermediate calculations (RTR, mu_N, sigma, mu_n, z_score, p); 
        if False, return only the percentile series. Default is False.

    Returns
    -------
    SRTR : pd.Series or pd.DataFrame
        If full is False, returns pd.Series of percentiles.
        If full is True, returns pd.DataFrame with columns: RTR, mu_N, sigma, mu_n, z_score, p.

    Notes
    -----
    Requires DataFrame columns: 'High', 'Low', 'Close'.
    
    The SRTR standardizes volatility by computing z-scores of short-term volatility
    relative to long-term historical levels. The method parameter controls how
    autocorrelation in the data is handled:
    
    - 'iid': Assumes independent observations, rescales sigma by sqrt(n)
    - 'cluster': Uses HAC/Newey-West estimator to account for autocorrelation
    
    The function maps z-scores to percentiles under the standard normal distribution,
    providing a normalized volatility measure comparable across different time periods.

    Examples
    --------
    >>> df.ti.SRTR(N=1000, n=14, method='cluster')
    >>> df.ti.SRTR(N=500, expand=True, full=True)
    """
    rtr = RTR(High, Low, Close)

    if len(rtr) <= N:
        raise ValueError("Length of series must be >= N.")
    if N <= n:
        raise ValueError("N must be greater than n.") 
    if method not in ["iid", "cluster"]:
        raise ValueError("Method must be either 'iid' or 'cluster'.")

    if n == 1 or method == "iid":
        return _SRTR_iid(rtr, N, expand, n, full)

    elif method == "cluster":
        return _SRTR_cluster(rtr, N, expand, n, L, full)
        


