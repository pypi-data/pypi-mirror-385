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
        df.loc[df.index[N-1:], 'sigma'] = df['log_RTR'].iloc[N-1:].expanding().std()
    else:
        df['mu_N'] = df['log_RTR'].rolling(window=N).mean()
        df['sigma'] = df['log_RTR'].rolling(window=N).std()

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


def _SRTR_cluster(RTR: pd.Series, n: int, N: int = 1000, expand: bool = True, L: int = None, full: bool = False):
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
        # Expansive window after initial N periods
        df['mu_N'] = df['log_RTR'].expanding(min_periods=N).mean()
        df['sigma'] = df['log_RTR'].expanding(min_periods=N).apply(
            lambda w: np.sqrt(_hac_variance(w.values, np.mean(w.values), L, n))
        )
    else:
        # Fixed-size rolling window of N
        df['mu_N'] = df['log_RTR'].rolling(window=N, min_periods=N).mean()
        df['sigma'] = df['log_RTR'].rolling(window=N, min_periods=N).apply(
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
    n: int,
    N: int = 1000,
    method: Literal['iid', 'cluster'] = "cluster",
    expand: bool = True,
    full: bool = False
    ):
    """
    Standardized Relative True Range (SRTR).

    Transforms RTR into percentiles by standardizing short-term rolling mean 
    against long-term historical mean and standard deviation of log(RTR).

    Parameters
    ----------
    High : pd.Series
        High prices.
    Low : pd.Series
        Low prices.
    Close : pd.Series
        Close prices.
    n : int
        Short-term window for rolling mean (typical: 7-30).
    N : int, default 1000
        Long-term window for historical mean/std. Should be >> n.
    method : {'iid', 'cluster'}, default 'cluster'
        - 'iid': Assumes i.i.d., uses sigma/sqrt(n). Faster but less accurate.
        - 'cluster': HAC/Newey-West variance estimator. Accounts for autocorrelation.
    expand : bool, default True
        If True, use expanding window after N periods.
        If False, fixed rolling window.
    full : bool, default False
        If True, return DataFrame with all calculations.
        If False, return percentile Series.

    Returns
    -------
    pd.Series or pd.DataFrame
        If full=False: Series of percentiles (0-1).
        If full=True: DataFrame with columns ['RTR', 'mu_N', 'sigma', 'mu_n', 'z_score', 'p'].

    Examples
    --------
    >>> df['SRTR_14'] = df.ti.SRTR(n=14)
    >>> df['SRTR_14'] = df.ti.SRTR(n=14, N=500)
    >>> df['SRTR_14_iid'] = df.ti.SRTR(n=14, method='iid')


    Notes
    -----
    Computes z-scores: z = (μₙ - μₙ) / σ, then maps to percentiles via norm.cdf().
    Requires series length > N. Method 'cluster' recommended for financial data.
    """
    if len(rtr) <= N:
        raise ValueError("Length of series must be >= N.")
    if N <= n:
        raise ValueError("N must be greater than n.") 
    if method not in ["iid", "cluster"]:
        raise ValueError("Method must be either 'iid' or 'cluster'.")
    
    rtr = RTR(High, Low, Close)

    if n == 1 or method == "iid":
        return _SRTR_iid(rtr, n, N, expand, full)
    elif method == "cluster":
        return _SRTR_cluster(rtr, n, N, expand, full)


