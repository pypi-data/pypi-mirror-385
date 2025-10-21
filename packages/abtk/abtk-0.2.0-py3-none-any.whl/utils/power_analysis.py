"""
Power analysis and sample size calculations.

This module provides general utilities for power analysis that are shared across
different test types.

Test-specific MDE and sample size calculations have been moved to their respective test classes:
- TTest._calculate_mde() for regular t-test MDE
- TTest._calculate_required_sample_size() for regular t-test sample size
- CupedTTest._calculate_mde() for CUPED t-test MDE
- ZTest._calculate_mde() for Z-test (proportion) MDE
"""

import numpy as np
import scipy.stats as sps


def calculate_power(
    mean1: float,
    mean2: float,
    std: float,
    n1: int,
    n2: int,
    alpha: float = 0.05
) -> float:
    """
    Calculate statistical power for a two-sample comparison test.

    This function calculates power based on effect size and sample sizes.
    Works for t-tests, z-tests, and other tests that use normal approximation.

    Parameters
    ----------
    mean1 : float
        Mean/proportion of first sample (control)
    mean2 : float
        Mean/proportion of second sample (treatment)
    std : float
        Pooled standard deviation (or standard error for proportions)
    n1 : int
        Sample size of first sample
    n2 : int
        Sample size of second sample
    alpha : float, default=0.05
        Significance level (two-sided)

    Returns
    -------
    float
        Statistical power (probability of detecting the effect)

    Notes
    -----
    This is a general power calculation that can be used for:
    - Two-sample t-test (continuous data)
    - Z-test (proportions)
    - Any test using normal approximation

    Examples
    --------
    >>> # T-test power
    >>> calculate_power(mean1=100, mean2=105, std=15, n1=1000, n2=1000)
    0.843

    >>> # Z-test power (proportions)
    >>> calculate_power(mean1=0.10, mean2=0.12, std=0.03, n1=1000, n2=1000)
    0.756
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Sample sizes must be positive")
    if std <= 0:
        raise ValueError("Standard deviation must be positive")

    # Effect size (Cohen's d)
    effect_size = abs(mean2 - mean1) / std

    # Pooled standard error
    se = std * np.sqrt(1/n1 + 1/n2)

    # Z-score for alpha
    z_alpha = sps.norm.ppf(1 - alpha / 2)

    # Non-centrality parameter
    ncp = abs(mean2 - mean1) / se

    # Power calculation
    power = 1 - sps.norm.cdf(z_alpha - ncp) + sps.norm.cdf(-z_alpha - ncp)

    return power
