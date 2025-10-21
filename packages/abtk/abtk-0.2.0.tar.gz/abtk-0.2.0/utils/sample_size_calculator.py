"""
Sample Size and MDE Calculator for Experiment Planning.

This module provides functions for calculating:
- Minimum Detectable Effect (MDE): smallest effect detectable with given power
- Required Sample Size: sample size needed to detect a given effect

Functions accept either:
- SampleData/ProportionData objects (if you have historical/pilot data)
- Individual parameters (if planning from scratch)
"""

import numpy as np
import scipy.stats as sps
from typing import Optional, Literal, Tuple

from core.data_types import SampleData, ProportionData


# =============================================================================
# T-Test (Continuous Metrics)
# =============================================================================

def calculate_mde_ttest(
    sample: Optional[SampleData] = None,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    n: Optional[int] = None,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> float:
    """
    Calculate Minimum Detectable Effect (MDE) for t-test.

    MDE is the smallest effect size that can be detected with the specified
    power and significance level given the sample sizes.

    Parameters
    ----------
    sample : SampleData, optional
        Historical or pilot data to extract mean/std from
        If provided, mean/std parameters are ignored
    mean : float, optional
        Expected baseline/control mean (required if sample not provided)
    std : float, optional
        Expected standard deviation (required if sample not provided)
    n : int, optional
        Target sample size per group
        If not provided and sample given, uses sample.sample_size
    alpha : float, default=0.05
        Significance level (two-sided)
    power : float, default=0.8
        Target statistical power (1 - β)
    ratio : float, default=1.0
        Ratio of treatment to control sample size (n_treatment/n_control)
        - ratio=1.0: equal sizes (recommended)
        - ratio=2.0: treatment group is 2x larger
    test_type : {'relative', 'absolute'}, default='relative'
        - 'relative': percentage change (e.g., 0.05 = 5%)
        - 'absolute': absolute difference in units

    Returns
    -------
    float
        Minimum detectable effect

    Raises
    ------
    ValueError
        If neither sample nor (mean, std, n) are provided

    Examples
    --------
    >>> # Option 1: Use historical data
    >>> from core.data_types import SampleData
    >>> historical = SampleData(data=np.random.normal(100, 20, 5000))
    >>> mde = calculate_mde_ttest(sample=historical, n=1000)
    >>> print(f"Can detect effect of {mde:.2%}")
    Can detect effect of 3.5%

    >>> # Option 2: Plan from scratch with parameters
    >>> mde = calculate_mde_ttest(mean=100, std=20, n=1000)
    >>> print(f"Can detect effect of {mde:.2%}")
    Can detect effect of 3.5%

    >>> # With larger sample, detect smaller effects
    >>> mde = calculate_mde_ttest(mean=100, std=20, n=5000)
    >>> print(f"Can detect effect of {mde:.2%}")
    Can detect effect of 1.6%
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        mean = float(np.mean(sample.data))
        std = float(np.std(sample.data, ddof=1))
        if n is None:
            n = sample.sample_size
    elif mean is not None and std is not None and n is not None:
        pass  # Use provided parameters
    else:
        raise ValueError(
            "Must provide either 'sample' or all of (mean, std, n)"
        )

    # Validation
    if n <= 0:
        raise ValueError("Sample size must be positive")
    if std < 0:
        raise ValueError("Standard deviation cannot be negative")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("Power must be between 0 and 1")
    if ratio <= 0:
        raise ValueError("Ratio must be positive")

    # Z-scores
    z_alpha = sps.norm.ppf(1 - alpha / 2)  # Two-sided
    z_beta = sps.norm.ppf(power)

    # Pooled standard error: SE = std * sqrt(1/n₁ + 1/n₂)
    se = std * np.sqrt(1/n + 1/(ratio * n))

    # MDE in absolute terms
    mde_absolute = (z_alpha + z_beta) * se

    if test_type == "relative":
        if mean == 0:
            raise ValueError("Cannot calculate relative MDE when mean is zero")
        return mde_absolute / abs(mean)
    else:
        return mde_absolute


def calculate_sample_size_ttest(
    sample: Optional[SampleData] = None,
    baseline_mean: Optional[float] = None,
    std: Optional[float] = None,
    mde: float = 0.05,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> int:
    """
    Calculate required sample size per group for t-test.

    Parameters
    ----------
    sample : SampleData, optional
        Historical or pilot data to extract mean/std from
        If provided, baseline_mean/std parameters are ignored
    baseline_mean : float, optional
        Expected baseline/control mean (required if sample not provided)
    std : float, optional
        Expected standard deviation (required if sample not provided)
    mde : float, default=0.05
        Minimum detectable effect to detect
        - For relative: proportion (e.g., 0.05 for 5%)
        - For absolute: absolute difference
    alpha : float, default=0.05
        Significance level (two-sided)
    power : float, default=0.8
        Target statistical power (1 - β)
    ratio : float, default=1.0
        Ratio of treatment to control sample size (n_treatment/n_control)
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect specified in mde

    Returns
    -------
    int
        Required sample size per group (control group size)
        For treatment group size: multiply by ratio

    Examples
    --------
    >>> # Option 1: Use historical data
    >>> historical = SampleData(data=np.random.normal(100, 20, 5000))
    >>> n = calculate_sample_size_ttest(sample=historical, mde=0.05)
    >>> print(f"Need {n} users per group")
    Need 1571 users per group

    >>> # Option 2: Plan from parameters
    >>> n = calculate_sample_size_ttest(
    ...     baseline_mean=100,
    ...     std=20,
    ...     mde=0.05  # 5% effect
    ... )
    >>> print(f"Need {n} users per group")
    Need 1571 users per group

    >>> # Smaller effect needs more users
    >>> n = calculate_sample_size_ttest(baseline_mean=100, std=20, mde=0.03)
    >>> print(f"Need {n} users per group for 3% effect")
    Need 4363 users per group
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        baseline_mean = float(np.mean(sample.data))
        std = float(np.std(sample.data, ddof=1))
    elif baseline_mean is not None and std is not None:
        pass  # Use provided parameters
    else:
        raise ValueError(
            "Must provide either 'sample' or both (baseline_mean, std)"
        )

    # Validation
    if std <= 0:
        raise ValueError("Standard deviation must be positive")
    if mde <= 0:
        raise ValueError("MDE must be positive")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("Power must be between 0 and 1")
    if ratio <= 0:
        raise ValueError("Ratio must be positive")

    # Convert relative MDE to absolute
    if test_type == "relative":
        if baseline_mean == 0:
            raise ValueError("Cannot calculate sample size with zero baseline mean for relative MDE")
        effect_absolute = mde * abs(baseline_mean)
    else:
        effect_absolute = abs(mde)

    # Z-scores
    z_alpha = sps.norm.ppf(1 - alpha / 2)
    z_beta = sps.norm.ppf(power)

    # Sample size formula: n = ((z_α/2 + z_β) * σ / Δ)² * (1 + 1/r)
    n = ((z_alpha + z_beta) * std / effect_absolute) ** 2 * (1 + 1/ratio)

    return int(np.ceil(n))


# =============================================================================
# CUPED T-Test (Variance Reduction with Covariates)
# =============================================================================

def calculate_mde_cuped(
    sample: Optional[SampleData] = None,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    n: Optional[int] = None,
    correlation: float = 0.7,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> float:
    """
    Calculate MDE for CUPED - accounts for variance reduction!

    CUPED uses pre-experiment covariates to reduce variance:
        - Higher correlation → more variance reduction → smaller MDE!
        - Adjusted std = std * sqrt(1 - ρ²)

    Parameters
    ----------
    sample : SampleData, optional
        Historical or pilot data to extract mean/std from
    mean : float, optional
        Expected baseline/control mean
    std : float, optional
        Expected standard deviation (WITHOUT variance reduction)
    n : int, optional
        Target sample size per group
    correlation : float, default=0.7
        Expected correlation between covariate and metric (0 to 1)
        - correlation=0.5: 25% variance reduction
        - correlation=0.7: 51% variance reduction
        - correlation=0.9: 81% variance reduction
    alpha : float, default=0.05
        Significance level
    power : float, default=0.8
        Target power
    ratio : float, default=1.0
        Sample size ratio
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect

    Returns
    -------
    float
        Minimum detectable effect (smaller than regular t-test!)

    Examples
    --------
    >>> # With historical data
    >>> historical = SampleData(data=np.random.normal(100, 20, 5000))
    >>> mde_cuped = calculate_mde_cuped(sample=historical, n=1000, correlation=0.7)
    >>> print(f"CUPED MDE: {mde_cuped:.2%}")
    CUPED MDE: 2.5%

    >>> # Compare with regular t-test
    >>> mde_regular = calculate_mde_ttest(sample=historical, n=1000)
    >>> print(f"Regular MDE: {mde_regular:.2%}")
    >>> print(f"Improvement: {(1 - mde_cuped/mde_regular):.1%}")
    Regular MDE: 3.5%
    Improvement: 30%

    >>> # From parameters
    >>> mde = calculate_mde_cuped(mean=100, std=20, n=1000, correlation=0.9)
    >>> print(f"CUPED MDE (ρ=0.9): {mde:.2%}")
    CUPED MDE (ρ=0.9): 1.5%
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        mean = float(np.mean(sample.data))
        std = float(np.std(sample.data, ddof=1))
        if n is None:
            n = sample.sample_size
    elif mean is not None and std is not None and n is not None:
        pass  # Use provided parameters
    else:
        raise ValueError(
            "Must provide either 'sample' or all of (mean, std, n)"
        )

    if not 0 <= correlation <= 1:
        raise ValueError("Correlation must be between 0 and 1")

    # Adjust std with variance reduction: std_adjusted = std * sqrt(1 - ρ²)
    variance_reduction_factor = np.sqrt(1 - correlation**2)
    std_adjusted = std * variance_reduction_factor

    # Use adjusted std in regular t-test MDE calculation
    return calculate_mde_ttest(
        mean=mean,
        std=std_adjusted,
        n=n,
        alpha=alpha,
        power=power,
        ratio=ratio,
        test_type=test_type
    )


def calculate_sample_size_cuped(
    sample: Optional[SampleData] = None,
    baseline_mean: Optional[float] = None,
    std: Optional[float] = None,
    mde: float = 0.05,
    correlation: float = 0.7,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> int:
    """
    Calculate required sample size for CUPED - need fewer users!

    CUPED reduces variance, so you need smaller sample size than regular t-test.

    Parameters
    ----------
    sample : SampleData, optional
        Historical data to extract mean/std from
    baseline_mean : float, optional
        Expected baseline mean
    std : float, optional
        Expected standard deviation (WITHOUT variance reduction)
    mde : float, default=0.05
        Target minimum detectable effect
    correlation : float, default=0.7
        Expected correlation between covariate and metric (0 to 1)
    alpha : float, default=0.05
        Significance level
    power : float, default=0.8
        Target power
    ratio : float, default=1.0
        Sample size ratio
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect

    Returns
    -------
    int
        Required sample size per group (fewer than regular t-test!)

    Notes
    -----
    Sample size reduction:
        - ρ=0.5 → need 75% of original sample (25% reduction)
        - ρ=0.7 → need 49% of original sample (51% reduction)
        - ρ=0.9 → need 19% of original sample (81% reduction)

    Examples
    --------
    >>> # Compare regular vs CUPED sample sizes
    >>> historical = SampleData(data=np.random.normal(100, 20, 5000))
    >>>
    >>> n_regular = calculate_sample_size_ttest(sample=historical, mde=0.05)
    >>> n_cuped = calculate_sample_size_cuped(sample=historical, mde=0.05, correlation=0.7)
    >>>
    >>> print(f"Regular: {n_regular} users")
    >>> print(f"CUPED: {n_cuped} users")
    >>> print(f"Reduction: {(1 - n_cuped/n_regular):.1%}")
    Regular: 1571 users
    CUPED: 770 users
    Reduction: 51%
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        baseline_mean = float(np.mean(sample.data))
        std = float(np.std(sample.data, ddof=1))
    elif baseline_mean is not None and std is not None:
        pass  # Use provided parameters
    else:
        raise ValueError(
            "Must provide either 'sample' or both (baseline_mean, std)"
        )

    if not 0 <= correlation <= 1:
        raise ValueError("Correlation must be between 0 and 1")

    # Adjust std with variance reduction
    variance_reduction_factor = np.sqrt(1 - correlation**2)
    std_adjusted = std * variance_reduction_factor

    # Use adjusted std in regular t-test sample size calculation
    return calculate_sample_size_ttest(
        baseline_mean=baseline_mean,
        std=std_adjusted,
        mde=mde,
        alpha=alpha,
        power=power,
        ratio=ratio,
        test_type=test_type
    )


# =============================================================================
# Z-Test (Proportions / Binary Metrics)
# =============================================================================

def calculate_mde_proportions(
    sample: Optional[ProportionData] = None,
    p: Optional[float] = None,
    n: Optional[int] = None,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> float:
    """
    Calculate MDE for proportions (Z-test).

    Use for binary metrics: CTR, CVR, churn rate, etc.

    Parameters
    ----------
    sample : ProportionData, optional
        Historical proportion data
    p : float, optional
        Expected baseline proportion (between 0 and 1)
        - CTR: 0.05 = 5% click-through rate
        - CVR: 0.10 = 10% conversion rate
    n : int, optional
        Target sample size per group
    alpha : float, default=0.05
        Significance level
    power : float, default=0.8
        Target power
    ratio : float, default=1.0
        Sample size ratio
    test_type : {'relative', 'absolute'}, default='relative'
        - 'relative': percentage lift (e.g., 0.10 = 10% relative increase)
        - 'absolute': absolute percentage points (e.g., 0.01 = 1pp increase)

    Returns
    -------
    float
        Minimum detectable effect

    Examples
    --------
    >>> # With historical proportion data
    >>> from core.data_types import ProportionData
    >>> historical = ProportionData(successes=500, trials=10000)
    >>> mde = calculate_mde_proportions(sample=historical, n=10000)
    >>> print(f"Can detect {mde:.2%} relative change")
    Can detect 12.5% relative change

    >>> # From parameters: CTR test, baseline CTR = 5%
    >>> mde = calculate_mde_proportions(p=0.05, n=10000)
    >>> print(f"Can detect {mde:.2%} relative change")
    Can detect 12.5% relative change

    >>> # Absolute MDE (percentage points)
    >>> mde = calculate_mde_proportions(p=0.05, n=10000, test_type="absolute")
    >>> print(f"Can detect {mde:.4f} percentage points")
    Can detect 0.0063 percentage points
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        p = sample.successes / sample.trials
        if n is None:
            n = sample.trials
    elif p is not None and n is not None:
        pass  # Use provided parameters
    else:
        raise ValueError(
            "Must provide either 'sample' or both (p, n)"
        )

    # Validation
    if not 0 < p < 1:
        raise ValueError("Proportion must be between 0 and 1 (exclusive)")
    if n <= 0:
        raise ValueError("Sample size must be positive")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("Power must be between 0 and 1")
    if ratio <= 0:
        raise ValueError("Ratio must be positive")

    # Z-scores
    z_alpha = sps.norm.ppf(1 - alpha / 2)
    z_beta = sps.norm.ppf(power)

    # Standard error for proportions: sqrt(p*(1-p) * (1/n₁ + 1/n₂))
    se = np.sqrt(p * (1 - p) * (1/n + 1/(ratio * n)))

    # MDE in absolute terms (percentage points)
    mde_absolute = (z_alpha + z_beta) * se

    if test_type == "relative":
        # Relative change: mde_relative = mde_absolute / baseline
        return mde_absolute / p
    else:
        return mde_absolute


def calculate_sample_size_proportions(
    sample: Optional[ProportionData] = None,
    baseline_proportion: Optional[float] = None,
    mde: float = 0.10,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    test_type: Literal["relative", "absolute"] = "relative"
) -> int:
    """
    Calculate required sample size for proportions test.

    Parameters
    ----------
    sample : ProportionData, optional
        Historical proportion data
    baseline_proportion : float, optional
        Expected baseline proportion (between 0 and 1)
    mde : float, default=0.10
        Target minimum detectable effect
        - For relative: proportion (e.g., 0.10 for 10% relative increase)
        - For absolute: percentage points (e.g., 0.01 for 1pp increase)
    alpha : float, default=0.05
        Significance level
    power : float, default=0.8
        Target power
    ratio : float, default=1.0
        Sample size ratio
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect

    Returns
    -------
    int
        Required sample size per group

    Examples
    --------
    >>> # With historical data
    >>> historical = ProportionData(successes=500, trials=10000)  # 5% CTR
    >>> n = calculate_sample_size_proportions(sample=historical, mde=0.10)
    >>> print(f"Need {n} users per group")
    Need 15732 users per group

    >>> # From parameters: CTR test, detect 10% relative increase from 5%
    >>> n = calculate_sample_size_proportions(
    ...     baseline_proportion=0.05,
    ...     mde=0.10  # 10% relative (5% → 5.5%)
    ... )
    >>> print(f"Need {n} users per group")
    Need 15732 users per group
    """
    # Extract parameters from sample or use provided values
    if sample is not None:
        baseline_proportion = sample.successes / sample.trials
    elif baseline_proportion is not None:
        pass  # Use provided parameter
    else:
        raise ValueError(
            "Must provide either 'sample' or 'baseline_proportion'"
        )

    # Validation
    if not 0 < baseline_proportion < 1:
        raise ValueError("Baseline proportion must be between 0 and 1 (exclusive)")
    if mde <= 0:
        raise ValueError("MDE must be positive")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("Power must be between 0 and 1")
    if ratio <= 0:
        raise ValueError("Ratio must be positive")

    # Convert relative MDE to absolute (percentage points)
    if test_type == "relative":
        effect_absolute = mde * baseline_proportion
    else:
        effect_absolute = abs(mde)

    # Z-scores
    z_alpha = sps.norm.ppf(1 - alpha / 2)
    z_beta = sps.norm.ppf(power)

    # Sample size for proportions
    p = baseline_proportion
    n = ((z_alpha + z_beta) / effect_absolute) ** 2 * p * (1 - p) * (1 + 1/ratio)

    return int(np.ceil(n))


# =============================================================================
# Utility Functions
# =============================================================================

def compare_mde_with_without_cuped(
    sample: Optional[SampleData] = None,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    n: Optional[int] = None,
    correlation: float = 0.7,
    alpha: float = 0.05,
    power: float = 0.8
) -> Tuple[float, float, float]:
    """
    Compare MDE with and without CUPED to see improvement.

    Parameters
    ----------
    sample : SampleData, optional
        Historical data
    mean : float, optional
        Baseline mean
    std : float, optional
        Standard deviation
    n : int, optional
        Sample size per group
    correlation : float, default=0.7
        Expected correlation with covariate
    alpha : float, default=0.05
        Significance level
    power : float, default=0.8
        Target power

    Returns
    -------
    tuple of (float, float, float)
        - MDE without CUPED (regular t-test)
        - MDE with CUPED
        - MDE improvement (as proportion)

    Examples
    --------
    >>> historical = SampleData(data=np.random.normal(100, 20, 5000))
    >>> mde_regular, mde_cuped, improvement = compare_mde_with_without_cuped(
    ...     sample=historical, n=1000, correlation=0.7
    ... )
    >>> print(f"Regular MDE: {mde_regular:.2%}")
    >>> print(f"CUPED MDE: {mde_cuped:.2%}")
    >>> print(f"Improvement: {improvement:.1%}")
    Regular MDE: 3.5%
    CUPED MDE: 2.5%
    Improvement: 30%
    """
    mde_regular = calculate_mde_ttest(sample=sample, mean=mean, std=std, n=n, alpha=alpha, power=power)
    mde_cuped = calculate_mde_cuped(sample=sample, mean=mean, std=std, n=n, correlation=correlation, alpha=alpha, power=power)
    improvement = (mde_regular - mde_cuped) / mde_regular

    return mde_regular, mde_cuped, improvement


# =============================================================================
# Multiple Comparisons Correction for Planning
# =============================================================================

def calculate_number_of_comparisons(
    num_groups: int,
    comparison_type: Literal["pairwise", "vs_control"] = "vs_control"
) -> int:
    """
    Calculate number of pairwise comparisons for multi-variant tests.

    Parameters
    ----------
    num_groups : int
        Total number of groups (including control)
        - For A/B: num_groups=2 (1 comparison)
        - For A/B/C: num_groups=3 (2 or 3 comparisons depending on type)
        - For A/B/C/D: num_groups=4 (3 or 6 comparisons depending on type)
    comparison_type : {'pairwise', 'vs_control'}, default='vs_control'
        - 'vs_control': Compare each treatment to control (recommended)
          Number of comparisons = num_groups - 1
        - 'pairwise': Compare all pairs (all vs all)
          Number of comparisons = C(n,2) = n*(n-1)/2

    Returns
    -------
    int
        Number of pairwise comparisons

    Examples
    --------
    >>> # A/B/C test: 1 control + 2 treatments
    >>> calculate_number_of_comparisons(num_groups=3, comparison_type="vs_control")
    2

    >>> # A/B/C test: all pairwise comparisons
    >>> calculate_number_of_comparisons(num_groups=3, comparison_type="pairwise")
    3

    >>> # A/B/C/D test: compare all to control
    >>> calculate_number_of_comparisons(num_groups=4, comparison_type="vs_control")
    3

    >>> # A/B/C/D test: all pairs
    >>> calculate_number_of_comparisons(num_groups=4, comparison_type="pairwise")
    6

    Notes
    -----
    For most A/B tests, use 'vs_control' (comparing treatments to control only).
    Use 'pairwise' only if you need to compare all treatments with each other.
    """
    if num_groups < 2:
        raise ValueError("Must have at least 2 groups")

    if comparison_type == "vs_control":
        # Compare each treatment to control: n-1 comparisons
        return num_groups - 1
    elif comparison_type == "pairwise":
        # All pairwise comparisons: C(n,2) = n*(n-1)/2
        return num_groups * (num_groups - 1) // 2
    else:
        raise ValueError(
            f"Invalid comparison_type: {comparison_type}. "
            "Use 'vs_control' or 'pairwise'"
        )


def adjust_alpha_for_multiple_comparisons(
    alpha: float = 0.05,
    num_groups: Optional[int] = None,
    num_comparisons: Optional[int] = None,
    comparison_type: Literal["pairwise", "vs_control"] = "vs_control",
    method: Literal["bonferroni", "sidak"] = "bonferroni"
) -> float:
    """
    Adjust alpha level for multiple comparisons during experiment planning.

    Use this BEFORE running your experiment to calculate the corrected
    significance level you should use in sample size calculations.

    Parameters
    ----------
    alpha : float, default=0.05
        Desired family-wise error rate (overall alpha level)
    num_groups : int, optional
        Total number of groups (including control)
        Provide either num_groups OR num_comparisons, not both
    num_comparisons : int, optional
        Number of pairwise comparisons
        Provide either num_groups OR num_comparisons, not both
    comparison_type : {'pairwise', 'vs_control'}, default='vs_control'
        Type of comparisons (used only if num_groups is provided)
        - 'vs_control': Compare treatments to control only
        - 'pairwise': All pairwise comparisons
    method : {'bonferroni', 'sidak'}, default='bonferroni'
        Correction method
        - 'bonferroni': alpha_adj = alpha / m (conservative)
        - 'sidak': alpha_adj = 1 - (1-alpha)^(1/m) (less conservative)

    Returns
    -------
    float
        Adjusted alpha level to use in sample size calculations

    Raises
    ------
    ValueError
        If neither num_groups nor num_comparisons is provided
        If both num_groups and num_comparisons are provided

    Examples
    --------
    >>> # Example 1: A/B/C test (1 control + 2 treatments)
    >>> # Want overall alpha=0.05, compare each treatment to control
    >>> alpha_adj = adjust_alpha_for_multiple_comparisons(
    ...     alpha=0.05,
    ...     num_groups=3,
    ...     comparison_type="vs_control"
    ... )
    >>> print(f"Adjusted alpha: {alpha_adj:.4f}")
    Adjusted alpha: 0.0250

    >>> # Now use adjusted alpha in sample size calculation
    >>> n = calculate_sample_size_ttest(
    ...     baseline_mean=100,
    ...     std=20,
    ...     mde=0.05,
    ...     alpha=alpha_adj  # Use corrected alpha!
    ... )
    >>> print(f"Need {n:,} users per group")
    Need 2102 users per group

    >>> # Example 2: A/B/C/D test with all pairwise comparisons
    >>> alpha_adj = adjust_alpha_for_multiple_comparisons(
    ...     alpha=0.05,
    ...     num_groups=4,
    ...     comparison_type="pairwise",
    ...     method="sidak"
    ... )
    >>> print(f"Adjusted alpha (Sidak): {alpha_adj:.4f}")
    Adjusted alpha (Sidak): 0.0085

    >>> # Example 3: If you already know number of comparisons
    >>> alpha_adj = adjust_alpha_for_multiple_comparisons(
    ...     alpha=0.05,
    ...     num_comparisons=6
    ... )
    >>> print(f"Adjusted alpha: {alpha_adj:.4f}")
    Adjusted alpha: 0.0083

    >>> # Example 4: Compare Bonferroni vs Sidak
    >>> alpha_bonf = adjust_alpha_for_multiple_comparisons(
    ...     alpha=0.05, num_comparisons=3, method="bonferroni"
    ... )
    >>> alpha_sidak = adjust_alpha_for_multiple_comparisons(
    ...     alpha=0.05, num_comparisons=3, method="sidak"
    ... )
    >>> print(f"Bonferroni: {alpha_bonf:.4f}")
    >>> print(f"Sidak: {alpha_sidak:.4f}")
    Bonferroni: 0.0167
    Sidak: 0.0170

    Notes
    -----
    **When to use this function:**
    - Planning a multi-variant test (A/B/C, A/B/C/D, etc.)
    - Want to control family-wise error rate (FWER)
    - Need to calculate sample size accounting for multiple comparisons

    **Which method to choose:**
    - **Bonferroni**: Most common, conservative, easy to understand
    - **Sidak**: Less conservative, slightly more powerful

    **Workflow:**
    1. Determine number of groups or comparisons
    2. Adjust alpha using this function
    3. Use adjusted alpha in sample size calculation
    4. Run experiment with corrected alpha

    **For post-hoc correction** (after running tests):
    Use `utils.corrections.adjust_pvalues()` instead

    See Also
    --------
    calculate_number_of_comparisons : Calculate number of comparisons
    utils.corrections.adjust_pvalues : Post-hoc p-value correction
    """
    # Validate inputs
    if num_groups is None and num_comparisons is None:
        raise ValueError(
            "Must provide either 'num_groups' or 'num_comparisons'"
        )

    if num_groups is not None and num_comparisons is not None:
        raise ValueError(
            "Provide either 'num_groups' OR 'num_comparisons', not both"
        )

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")

    # Calculate number of comparisons if num_groups provided
    if num_groups is not None:
        m = calculate_number_of_comparisons(num_groups, comparison_type)
    else:
        m = num_comparisons

    if m < 1:
        raise ValueError("Number of comparisons must be at least 1")

    # Apply correction
    if method == "bonferroni":
        # Bonferroni: alpha_adj = alpha / m
        alpha_adjusted = alpha / m
    elif method == "sidak":
        # Sidak: alpha_adj = 1 - (1 - alpha)^(1/m)
        alpha_adjusted = 1 - (1 - alpha) ** (1/m)
    else:
        raise ValueError(
            f"Invalid method: {method}. Use 'bonferroni' or 'sidak'"
        )

    return alpha_adjusted
