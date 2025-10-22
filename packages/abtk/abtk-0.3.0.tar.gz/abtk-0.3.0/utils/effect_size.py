"""
Effect size calculations for statistical tests.

This module provides general utilities for effect size calculations
that are shared across different test types.

Test-specific effect calculations have been moved to their respective test classes:
- TTest._calculate_effect_distribution() for regular t-test
- CupedTTest._calculate_effect_distribution() for CUPED t-test
- PairedTTest._calculate_effect_distribution() for paired t-test
"""

import numpy as np
import scipy.stats as sps
from typing import Tuple


def cohens_d(mean1: float, mean2: float, std1: float, std2: float, n1: int, n2: int) -> float:
    """
    Calculate Cohen's d effect size.

    Cohen's d is a standardized measure of effect size that represents
    the difference between two means in terms of standard deviation units.

    Parameters
    ----------
    mean1 : float
        Mean of first sample
    mean2 : float
        Mean of second sample
    std1 : float
        Standard deviation of first sample
    std2 : float
        Standard deviation of second sample
    n1 : int
        Sample size of first sample
    n2 : int
        Sample size of second sample

    Returns
    -------
    float
        Cohen's d effect size

    Notes
    -----
    Cohen's d is calculated as:
        d = (mean2 - mean1) / pooled_std

    Where pooled_std is:
        pooled_std = sqrt(((n1-1)*std1² + (n2-1)*std2²) / (n1 + n2 - 2))

    Interpretation guidelines:
    - Small effect: |d| = 0.2
    - Medium effect: |d| = 0.5
    - Large effect: |d| = 0.8

    Examples
    --------
    >>> cohens_d(100, 105, 15, 15, 1000, 1000)
    0.333
    """
    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (mean2 - mean1) / pooled_std


def calculate_confidence_interval(
    distribution: sps.norm,
    alpha: float = 0.05
) -> Tuple[float, float, float]:
    """
    Calculate confidence interval from effect distribution.

    Parameters
    ----------
    distribution : scipy.stats.norm
        Normal distribution of the effect
    alpha : float, default=0.05
        Significance level (for 95% CI, use alpha=0.05)

    Returns
    -------
    tuple of (float, float, float)
        - Lower bound of confidence interval
        - Upper bound of confidence interval
        - Length of confidence interval

    Examples
    --------
    >>> dist = sps.norm(loc=0.05, scale=0.01)
    >>> lb, ub, length = calculate_confidence_interval(dist, alpha=0.05)
    >>> print(f"95% CI: [{lb:.3f}, {ub:.3f}], length: {length:.3f}")
    95% CI: [0.030, 0.070], length: 0.040
    """
    left_bound = distribution.ppf(alpha / 2)
    right_bound = distribution.ppf(1 - alpha / 2)
    ci_length = right_bound - left_bound

    return left_bound, right_bound, ci_length


def calculate_pvalue_twosided(distribution: sps.norm, null_value: float = 0.0) -> float:
    """
    Calculate two-sided p-value from effect distribution.

    Parameters
    ----------
    distribution : scipy.stats.norm
        Normal distribution of the effect
    null_value : float, default=0.0
        Null hypothesis value to test against

    Returns
    -------
    float
        Two-sided p-value

    Notes
    -----
    The two-sided p-value is calculated as:
        p = 2 * min(P(X ≤ null_value), P(X ≥ null_value))

    Examples
    --------
    >>> dist = sps.norm(loc=0.05, scale=0.01)
    >>> pvalue = calculate_pvalue_twosided(dist, null_value=0)
    >>> print(f"p-value: {pvalue:.4f}")
    p-value: 0.0000
    """
    return 2 * min(distribution.cdf(null_value), distribution.sf(null_value))


def relative_to_absolute(relative_effect: float, baseline_mean: float) -> float:
    """
    Convert relative effect to absolute effect.

    Parameters
    ----------
    relative_effect : float
        Relative effect (e.g., 0.05 for 5% increase)
    baseline_mean : float
        Baseline mean value

    Returns
    -------
    float
        Absolute effect

    Examples
    --------
    >>> relative_to_absolute(0.05, 100)
    5.0
    """
    return relative_effect * baseline_mean


def absolute_to_relative(absolute_effect: float, baseline_mean: float) -> float:
    """
    Convert absolute effect to relative effect.

    Parameters
    ----------
    absolute_effect : float
        Absolute effect
    baseline_mean : float
        Baseline mean value

    Returns
    -------
    float
        Relative effect

    Raises
    ------
    ValueError
        If baseline_mean is zero

    Examples
    --------
    >>> absolute_to_relative(5, 100)
    0.05
    """
    if baseline_mean == 0:
        raise ValueError("Cannot convert to relative effect when baseline mean is zero")

    return absolute_effect / baseline_mean
