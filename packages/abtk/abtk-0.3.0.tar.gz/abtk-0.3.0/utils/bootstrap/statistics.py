"""
Bootstrap statistical utilities.

This module provides utilities for calculating statistics from bootstrap distributions:
- Confidence intervals (percentile method)
- P-values (empirical distribution method)
- Normality checks
"""

from typing import Tuple, Callable
import numpy as np
import scipy.stats as sps
import logging


def calculate_bootstrap_ci(
    bootstrap_distribution: np.ndarray,
    alpha: float = 0.05
) -> Tuple[float, float, float]:
    """
    Calculate confidence interval from bootstrap distribution using percentile method.

    Parameters
    ----------
    bootstrap_distribution : np.ndarray
        Array of bootstrap statistics (e.g., means, differences, ratios)
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
    >>> boot_dist = np.random.normal(0.05, 0.01, 1000)
    >>> lb, ub, length = calculate_bootstrap_ci(boot_dist, alpha=0.05)
    >>> print(f"95% CI: [{lb:.3f}, {ub:.3f}]")
    95% CI: [0.030, 0.070]

    Notes
    -----
    The percentile method calculates CI as:
        [Q(alpha/2), Q(1 - alpha/2)]

    Where Q is the quantile function of the bootstrap distribution.

    This is the most common method for bootstrap CI and works well when:
    - Bootstrap distribution is approximately symmetric
    - Sample size is large enough (typically n > 30)

    For skewed distributions, consider BCa (bias-corrected and accelerated) method.
    """
    left_bound = np.quantile(bootstrap_distribution, alpha / 2)
    right_bound = np.quantile(bootstrap_distribution, 1 - alpha / 2)
    ci_length = right_bound - left_bound

    return left_bound, right_bound, ci_length


def calculate_bootstrap_pvalue(
    bootstrap_distribution: np.ndarray,
    null_value: float = 0.0
) -> float:
    """
    Calculate two-sided p-value from bootstrap distribution.

    The p-value is calculated as the proportion of bootstrap samples
    that are as extreme or more extreme than the null hypothesis value.

    Parameters
    ----------
    bootstrap_distribution : np.ndarray
        Array of bootstrap statistics
    null_value : float, default=0.0
        Null hypothesis value to test against

    Returns
    -------
    float
        Two-sided p-value

    Examples
    --------
    >>> # Bootstrap distribution centered around 0.05
    >>> boot_dist = np.random.normal(0.05, 0.01, 1000)
    >>> pvalue = calculate_bootstrap_pvalue(boot_dist, null_value=0)
    >>> print(f"P-value: {pvalue:.4f}")
    P-value: 0.0000

    >>> # Bootstrap distribution centered around 0
    >>> boot_dist = np.random.normal(0, 0.01, 1000)
    >>> pvalue = calculate_bootstrap_pvalue(boot_dist, null_value=0)
    >>> print(f"P-value: {pvalue:.4f}")
    P-value: 1.0000

    Notes
    -----
    The two-sided p-value is calculated as:
        p = 2 * min(P(X ≤ null_value), P(X ≥ null_value))

    This is equivalent to:
        p = 2 * min(proportion below null, proportion above null)

    A small p-value indicates that the null hypothesis value is unlikely
    given the observed bootstrap distribution.
    """
    prop_below = np.mean(bootstrap_distribution <= null_value)
    prop_above = np.mean(bootstrap_distribution >= null_value)

    pvalue = 2 * min(prop_below, prop_above)

    return pvalue


def apply_statistic_to_bootstrap_samples(
    bootstrap_samples: np.ndarray,
    stat_func: Callable[[np.ndarray], float] = np.mean,
    axis: int = 1
) -> np.ndarray:
    """
    Apply a statistic function to bootstrap samples.

    Parameters
    ----------
    bootstrap_samples : np.ndarray
        Bootstrap samples array of shape (n_bootstrap, sample_size)
    stat_func : callable, default=np.mean
        Function to apply to each bootstrap sample.
        Should accept 1D array and return a scalar.
    axis : int, default=1
        Axis along which to apply the function
        (1 = apply to each row = each bootstrap sample)

    Returns
    -------
    np.ndarray
        Array of statistics, one per bootstrap sample

    Examples
    --------
    >>> boot_samples = np.random.randn(1000, 100)  # 1000 bootstrap samples of size 100
    >>> boot_means = apply_statistic_to_bootstrap_samples(boot_samples, np.mean)
    >>> boot_means.shape
    (1000,)

    >>> # Custom statistic: 90th percentile
    >>> stat_func = lambda x: np.percentile(x, 90)
    >>> boot_p90 = apply_statistic_to_bootstrap_samples(boot_samples, stat_func)

    Notes
    -----
    Common statistics:
    - np.mean: Bootstrap means
    - np.median: Bootstrap medians
    - np.std: Bootstrap standard deviations
    - lambda x: np.percentile(x, q): Bootstrap percentiles
    """
    return np.apply_along_axis(stat_func, axis, bootstrap_samples)


def check_bootstrap_normality(
    bootstrap_distribution: np.ndarray,
    alpha: float = 0.05,
    logger: logging.Logger = None
) -> Tuple[float, bool]:
    """
    Check if bootstrap distribution is approximately normal using Kolmogorov-Smirnov test.

    Parameters
    ----------
    bootstrap_distribution : np.ndarray
        Array of bootstrap statistics
    alpha : float, default=0.05
        Significance level for normality test
    logger : logging.Logger, optional
        Logger to log warnings if distribution is non-normal

    Returns
    -------
    tuple of (float, bool)
        - P-value from KS test
        - Whether distribution appears normal (pvalue >= alpha)

    Examples
    --------
    >>> boot_dist = np.random.normal(0, 1, 1000)
    >>> pvalue, is_normal = check_bootstrap_normality(boot_dist)
    >>> print(f"Normal: {is_normal}")
    Normal: True

    >>> boot_dist = np.random.exponential(1, 1000)
    >>> pvalue, is_normal = check_bootstrap_normality(boot_dist)
    >>> print(f"Normal: {is_normal}")
    Normal: False

    Notes
    -----
    The Kolmogorov-Smirnov test compares the bootstrap distribution
    to a normal distribution with the same mean and standard deviation.

    If the distribution is not normal:
    - Bootstrap CI (percentile method) is still valid
    - But parametric assumptions may not hold
    - Consider using more bootstrap samples for better accuracy

    Bootstrap distributions tend to be approximately normal due to
    Central Limit Theorem, especially for means and large sample sizes.
    """
    mean = np.mean(bootstrap_distribution)
    std = np.std(bootstrap_distribution)

    # Kolmogorov-Smirnov test against normal distribution
    _, pvalue = sps.kstest(bootstrap_distribution, 'norm', args=(mean, std))

    is_normal = pvalue >= alpha

    if not is_normal and logger:
        logger.warning(
            f"Bootstrap distribution may not be normal (KS test p-value = {pvalue:.4f}). "
            "This doesn't invalidate bootstrap CI, but parametric assumptions may not hold."
        )

    return pvalue, is_normal


def calculate_bootstrap_variance_reduction(
    boot_values: np.ndarray,
    boot_covariates: np.ndarray,
    stat_func: Callable[[np.ndarray], float] = np.mean
) -> float:
    """
    Calculate variance reduction from using covariates in bootstrap.

    This is used in post-normed bootstrap to assess how much variance
    reduction is achieved by normalizing with covariates.

    Parameters
    ----------
    boot_values : np.ndarray
        Bootstrap samples of main metric
    boot_covariates : np.ndarray
        Bootstrap samples of covariate
    stat_func : callable, default=np.mean
        Statistic function applied to samples

    Returns
    -------
    float
        Variance reduction ratio (1 - var_normed/var_original)

    Examples
    --------
    >>> boot_values = np.random.randn(1000, 100)
    >>> boot_cov = 0.7 * boot_values + 0.3 * np.random.randn(1000, 100)
    >>> reduction = calculate_bootstrap_variance_reduction(boot_values, boot_cov)
    >>> print(f"Variance reduction: {reduction:.1%}")
    Variance reduction: 40%

    Notes
    -----
    Variance reduction is similar to R² in regression:
    - 0 = no reduction (covariate uncorrelated)
    - 1 = perfect reduction (covariate perfectly predicts outcome)
    - Typical values: 0.2-0.5 (20-50% reduction)
    """
    # Apply stat function to bootstrap samples
    boot_stats = apply_statistic_to_bootstrap_samples(boot_values, stat_func)
    boot_cov_stats = apply_statistic_to_bootstrap_samples(boot_covariates, stat_func)

    # Calculate correlation
    correlation = np.corrcoef(boot_stats, boot_cov_stats)[0, 1]

    # Variance reduction = R²
    variance_reduction = correlation ** 2

    return variance_reduction
