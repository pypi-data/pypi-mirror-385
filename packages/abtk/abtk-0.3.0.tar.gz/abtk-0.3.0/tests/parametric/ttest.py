"""
Two-sample t-test for comparing means of continuous data.

This module provides a t-test implementation that supports both absolute
and relative effect sizes, uses Welch's approach (unequal variances),
and leverages shared utilities for validation, effect size calculation,
and power analysis.
"""

from typing import List, Literal, Optional, Tuple
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha, validate_power
from utils.effect_size import (
    calculate_confidence_interval,
    calculate_pvalue_twosided
)


class TTest(BaseTestProcessor):
    """
    Two-sample t-test for comparing means of continuous data.

    Supports both absolute and relative effect size calculations.
    Uses Welch's t-test approach (unequal variances assumed).

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference in means (mean2 - mean1)
        - 'relative': relative difference ((mean2 - mean1) / mean1)
    return_effect_distribution : bool, default=False
        If True, includes the effect distribution in results
    calculate_mde : bool, default=True
        If True, calculates minimum detectable effect for each sample
    power : float, default=0.8
        Target statistical power for MDE calculation
    logger : logging.Logger, optional
        Logger instance for error reporting

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Create samples
    >>> control = SampleData(np.random.normal(100, 15, 1000), name="Control")
    >>> treatment = SampleData(np.random.normal(105, 15, 1000), name="Treatment")
    >>>
    >>> # Run t-test
    >>> ttest = TTest(alpha=0.05, test_type="relative")
    >>> results = ttest.compare([control, treatment])
    >>>
    >>> # Access results
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")
    >>> print(f"Reject null: {result.reject}")
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        return_effect_distribution: bool = False,
        calculate_mde: bool = True,
        power: float = 0.8,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)
        validate_power(power)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Incorrect test type. Use "relative" or "absolute"')

        # Initialize base class
        super().__init__(
            test_name="t-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type,
            calculate_mde=calculate_mde,
            power=power,
            return_effect_distribution=return_effect_distribution
        )

        # Test-specific parameters
        self.test_type = test_type
        self.return_effect_distribution = return_effect_distribution
        self.calculate_mde = calculate_mde
        self.power = power

    @staticmethod
    def _calculate_effect_distribution(
        sample1: SampleData,
        sample2: SampleData,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> Tuple[sps.norm, float]:
        """
        Calculate effect distribution for t-test using delta method.

        For absolute effect:
            effect = mean2 - mean1
            variance = var(mean2) + var(mean1)

        For relative effect:
            effect = (mean2 - mean1) / mean1
            Uses delta method to approximate variance of ratio

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline)
        sample2 : SampleData
            Second sample (treatment/variant)
        test_type : {'relative', 'absolute'}, default='relative'
            Type of effect to calculate

        Returns
        -------
        tuple of (scipy.stats.norm, float)
            - Normal distribution of the effect
            - Point estimate of the effect

        Notes
        -----
        Delta method for variance of ratio:
            Var(X/Y) ≈ (1/μ_Y)² Var(X) + (μ_X/μ_Y²)² Var(Y) - 2(μ_X/μ_Y³) Cov(X,Y)

        For independent samples: Cov(X,Y) = 0, but we use -Var(mean1) for correlation
        correction when both means come from the same underlying process.
        """
        mean_1, mean_2 = sample1.mean, sample2.mean
        var_mean_1 = sample1.variance / sample1.sample_size
        var_mean_2 = sample2.variance / sample2.sample_size

        # Calculate difference statistics
        difference_mean = mean_2 - mean_1
        difference_mean_var = var_mean_1 + var_mean_2

        if test_type == "absolute":
            distribution = sps.norm(
                loc=difference_mean,
                scale=np.sqrt(difference_mean_var)
            )
            effect = difference_mean

        elif test_type == "relative":
            if mean_1 == 0:
                raise ValueError("Cannot calculate relative effect when baseline mean is zero")

            # Delta method for variance of ratio
            # Cov(X,Y) for independent samples, but with correction
            covariance = -var_mean_1
            relative_mu = difference_mean / mean_1
            relative_var = (
                difference_mean_var / (mean_1**2)
                + var_mean_1 * ((difference_mean**2) / (mean_1**4))
                - 2 * (difference_mean / (mean_1**3)) * covariance
            )

            if relative_var < 0:
                # Numerical stability: use simplified formula if negative
                relative_var = difference_mean_var / (mean_1**2)

            distribution = sps.norm(
                loc=relative_mu,
                scale=np.sqrt(relative_var)
            )
            effect = relative_mu

        else:
            raise ValueError(f"Invalid test_type: {test_type}. Use 'relative' or 'absolute'")

        return distribution, effect

    @staticmethod
    def _calculate_mde(
        mean: float,
        std: float,
        n: int,
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
        mean : float
            Sample mean (baseline/control value)
        std : float
            Sample standard deviation
        n : int
            Sample size
        alpha : float, default=0.05
            Significance level (two-sided)
        power : float, default=0.8
            Target statistical power (1 - β)
        ratio : float, default=1.0
            Ratio of the other sample size to this sample size (n2/n1)
        test_type : {'relative', 'absolute'}, default='relative'
            Type of effect to calculate:
            - 'absolute': absolute difference in means
            - 'relative': relative difference (percentage)

        Returns
        -------
        float
            Minimum detectable effect

        Notes
        -----
        The MDE is calculated using the formula:
            MDE = (z_α/2 + z_β) * SE

        Where:
        - z_α/2 is the critical value for significance level α (two-sided)
        - z_β is the critical value for power (1 - β)
        - SE is the pooled standard error: sqrt(σ²/n₁ + σ²/n₂)

        For relative MDE, the absolute MDE is divided by the baseline mean.
        """
        if n <= 0:
            raise ValueError("Sample size must be positive")
        if std < 0:
            raise ValueError("Standard deviation cannot be negative")

        # Z-scores for power and alpha
        z_alpha = sps.norm.ppf(1 - alpha / 2)  # Two-sided test
        z_beta = sps.norm.ppf(power)

        # Pooled standard error
        # SE = sqrt(σ²/n₁ + σ²/n₂) where n₂ = ratio * n₁
        se = std * np.sqrt(1/n + 1/(ratio * n))

        # MDE in absolute terms
        mde_absolute = (z_alpha + z_beta) * se

        if test_type == "relative":
            # Convert to relative MDE
            if mean == 0:
                return 0.0
            return mde_absolute / abs(mean)
        else:
            return mde_absolute

    @staticmethod
    def _calculate_required_sample_size(
        baseline_mean: float,
        std: float,
        mde: float,
        alpha: float = 0.05,
        power: float = 0.8,
        ratio: float = 1.0,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> int:
        """
        Calculate required sample size for t-test to detect a given effect.

        Parameters
        ----------
        baseline_mean : float
            Expected baseline/control mean
        std : float
            Expected standard deviation
        mde : float
            Minimum detectable effect to detect
            - For relative: proportion (e.g., 0.05 for 5%)
            - For absolute: absolute difference
        alpha : float, default=0.05
            Significance level (two-sided)
        power : float, default=0.8
            Target statistical power
        ratio : float, default=1.0
            Ratio of treatment to control sample size (n2/n1)
        test_type : {'relative', 'absolute'}, default='relative'
            Type of effect

        Returns
        -------
        int
            Required sample size per group
        """
        if std <= 0:
            raise ValueError("Standard deviation must be positive")
        if mde <= 0:
            raise ValueError("MDE must be positive")

        # Convert relative MDE to absolute
        if test_type == "relative":
            if baseline_mean == 0:
                raise ValueError("Baseline mean cannot be zero for relative MDE")
            mde_absolute = mde * abs(baseline_mean)
        else:
            mde_absolute = mde

        # Z-scores
        z_alpha = sps.norm.ppf(1 - alpha / 2)
        z_beta = sps.norm.ppf(power)

        # Sample size formula: n = (z_α/2 + z_β)² * σ² * (1 + 1/ratio) / Δ²
        n = ((z_alpha + z_beta) ** 2) * (std ** 2) * (1 + 1/ratio) / (mde_absolute ** 2)

        return int(np.ceil(n))

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise comparisons.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results

        Raises
        ------
        ValueError
            If samples don't pass validation
        """
        if not samples or len(samples) < 2:
            return []

        # Use centralized validation from utils
        validate_samples(samples, min_samples=2)

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using t-test.

        This method calculates the effect size, p-value, confidence interval,
        and optionally the minimum detectable effect using shared utilities.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline)
        sample2 : SampleData
            Second sample (treatment/variant)

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval, etc.

        Raises
        ------
        ValueError
            If effect distribution calculation fails (e.g., division by zero for relative effect)
        """
        try:
            # Calculate effect distribution
            distribution, effect = self._calculate_effect_distribution(
                sample1, sample2, test_type=self.test_type
            )

            # Calculate confidence interval
            left_bound, right_bound, ci_length = calculate_confidence_interval(
                distribution, alpha=self.alpha
            )

            # Calculate two-sided p-value
            pvalue = calculate_pvalue_twosided(distribution, null_value=0.0)
            reject = pvalue < self.alpha

            # Calculate MDE if requested
            mde_1 = mde_2 = 0.0
            if self.calculate_mde:
                mde_1 = self._calculate_mde(
                    mean=sample1.mean,
                    std=sample1.std_dev,
                    n=sample1.sample_size,
                    alpha=self.alpha,
                    power=self.power,
                    ratio=sample2.sample_size / sample1.sample_size,
                    test_type=self.test_type
                )
                mde_2 = self._calculate_mde(
                    mean=sample2.mean,
                    std=sample2.std_dev,
                    n=sample2.sample_size,
                    alpha=self.alpha,
                    power=self.power,
                    ratio=sample1.sample_size / sample2.sample_size,
                    test_type=self.test_type
                )

            # Create result object
            result = TestResult(
                name_1=sample1.name or "sample_1",
                value_1=sample1.mean,
                std_1=sample1.std_dev,
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=sample2.mean,
                std_2=sample2.std_dev,
                size_2=sample2.sample_size,
                method_name=self.test_name,
                method_params=self.test_params,
                alpha=self.alpha,
                pvalue=pvalue,
                effect=effect,
                ci_length=ci_length,
                left_bound=left_bound,
                right_bound=right_bound,
                reject=reject,
                effect_distribution=distribution if self.return_effect_distribution else None,
                mde_1=mde_1,
                mde_2=mde_2,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in TTest compare_samples: {str(e)}", exc_info=True)
            raise
