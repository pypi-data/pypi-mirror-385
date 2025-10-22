"""
Z-test for comparing proportions.

Z-test is used to compare proportions between two groups, typically for conversion rates,
click-through rates, or other binary outcomes.

This test uses the normal approximation to the binomial distribution, which is valid
when sample sizes are large enough (np > 5 and n(1-p) > 5).
"""

from typing import List, Literal, Optional, Tuple
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import ProportionData
from core.test_result import TestResult
from utils.data_validation import validate_alpha, validate_power
from utils.effect_size import calculate_confidence_interval, calculate_pvalue_twosided


class ZTest(BaseTestProcessor):
    """
    Z-test for comparing proportions.

    Use Z-test when:
    - Comparing conversion rates, click-through rates, or other binary outcomes
    - Sample sizes are large enough (np > 5 and n(1-p) > 5)
    - You have count data (successes/failures)

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference in proportions (p2 - p1)
        - 'relative': relative difference ((p2 - p1) / p1)
    calculate_mde : bool, default=True
        If True, calculates minimum detectable effect for each sample
    power : float, default=0.8
        Target statistical power for MDE calculation
    logger : logging.Logger, optional
        Logger instance for error reporting

    Examples
    --------
    >>> from core.data_types import ProportionData
    >>>
    >>> # Create proportion samples
    >>> control = ProportionData(successes=100, nobs=1000, name="Control")
    >>> treatment = ProportionData(successes=120, nobs=1000, name="Treatment")
    >>>
    >>> # Run Z-test
    >>> ztest = ZTest(alpha=0.05, test_type="relative")
    >>> results = ztest.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")
    >>> print(f"Reject null: {result.reject}")

    Notes
    -----
    Z-test assumptions:
    - Large sample sizes (rule of thumb: np > 5 and n(1-p) > 5)
    - Independent observations
    - Binary outcomes

    For small samples, consider using Fisher's exact test or Barnard's test instead.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
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
            test_name="z-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type,
            calculate_mde=calculate_mde,
            power=power
        )

        # Test-specific parameters
        self.test_type = test_type
        self.calculate_mde = calculate_mde
        self.power = power

    @staticmethod
    def _calculate_effect_distribution(
        prop1: ProportionData,
        prop2: ProportionData,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> Tuple[sps.norm, float]:
        """
        Calculate effect distribution for Z-test.

        Uses pooled proportion for standard error calculation.

        Parameters
        ----------
        prop1 : ProportionData
            First proportion sample (control/baseline)
        prop2 : ProportionData
            Second proportion sample (treatment/variant)
        test_type : {'relative', 'absolute'}, default='relative'
            Type of effect to calculate

        Returns
        -------
        tuple of (scipy.stats.norm, float)
            - Normal distribution of the effect
            - Point estimate of the effect
        """
        p1 = prop1.prop
        p2 = prop2.prop
        n1 = prop1.nobs
        n2 = prop2.nobs

        # Pooled proportion for standard error
        p_combined = (prop1.successes + prop2.successes) / (n1 + n2)

        # Standard error using pooled proportion
        se = np.sqrt(p_combined * (1 - p_combined) * (1/n1 + 1/n2))

        if test_type == "absolute":
            # Absolute effect: difference in proportions
            effect = p2 - p1
            distribution = sps.norm(loc=effect, scale=se)

        elif test_type == "relative":
            # Relative effect
            if p1 == 0:
                raise ValueError("Cannot calculate relative effect when baseline proportion is zero")

            effect = (p2 - p1) / p1
            # Delta method for relative effect standard error
            se_relative = se / p1
            distribution = sps.norm(loc=effect, scale=se_relative)

        else:
            raise ValueError(f"Invalid test_type: {test_type}. Use 'relative' or 'absolute'")

        return distribution, effect

    @staticmethod
    def _calculate_mde(
        prop: float,
        n: int,
        alpha: float = 0.05,
        power: float = 0.8,
        ratio: float = 1.0,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> float:
        """
        Calculate Minimum Detectable Effect (MDE) for Z-test (proportions).

        Parameters
        ----------
        prop : float
            Baseline proportion (between 0 and 1)
        n : int
            Sample size
        alpha : float, default=0.05
            Significance level (two-sided)
        power : float, default=0.8
            Target statistical power
        ratio : float, default=1.0
            Ratio of the other sample size to this sample size (n2/n1)
        test_type : {'relative', 'absolute'}, default='relative'
            Type of effect to calculate

        Returns
        -------
        float
            Minimum detectable effect
        """
        if not 0 < prop < 1:
            raise ValueError(f"Proportion must be between 0 and 1, got {prop}")
        if n <= 0:
            raise ValueError("Sample size must be positive")

        # Standard deviation for proportion
        std = np.sqrt(prop * (1 - prop))

        # Z-scores
        z_alpha = sps.norm.ppf(1 - alpha / 2)
        z_beta = sps.norm.ppf(power)

        # Standard error
        se = std * np.sqrt(1/n + 1/(ratio * n))

        # MDE in absolute terms
        mde_absolute = (z_alpha + z_beta) * se

        if test_type == "relative":
            return mde_absolute / prop
        else:
            return mde_absolute

    def compare(self, proportions: List[ProportionData]) -> List[TestResult]:
        """
        Compare multiple proportion samples and perform pairwise comparisons.

        Parameters
        ----------
        proportions : List[ProportionData]
            List of proportion samples to compare

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results

        Raises
        ------
        ValueError
            If proportions don't pass validation
        """
        if not proportions or len(proportions) < 2:
            return []

        # Validate proportions
        self._validate_proportions(proportions)

        results = []
        for prop1, prop2 in combinations(proportions, 2):
            results.append(self.compare_samples(prop1, prop2))

        return results

    def compare_samples(self, prop1: ProportionData, prop2: ProportionData) -> TestResult:
        """
        Compare two proportion samples using Z-test.

        Parameters
        ----------
        prop1 : ProportionData
            First proportion sample (control/baseline)
        prop2 : ProportionData
            Second proportion sample (treatment/variant)

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval, etc.

        Raises
        ------
        ValueError
            If effect distribution calculation fails
        """
        try:
            # Calculate effect distribution
            distribution, effect = self._calculate_effect_distribution(
                prop1, prop2, test_type=self.test_type
            )

            # Calculate confidence interval using shared utility
            left_bound, right_bound, ci_length = calculate_confidence_interval(
                distribution, alpha=self.alpha
            )

            # Calculate two-sided p-value using shared utility
            pvalue = calculate_pvalue_twosided(distribution, null_value=0.0)
            reject = pvalue < self.alpha

            # Calculate MDE if requested
            mde_1 = mde_2 = 0.0
            if self.calculate_mde:
                mde_1 = self._calculate_mde(
                    prop=prop1.prop,
                    n=prop1.nobs,
                    alpha=self.alpha,
                    power=self.power,
                    ratio=prop2.nobs / prop1.nobs,
                    test_type=self.test_type
                )
                mde_2 = self._calculate_mde(
                    prop=prop2.prop,
                    n=prop2.nobs,
                    alpha=self.alpha,
                    power=self.power,
                    ratio=prop1.nobs / prop2.nobs,
                    test_type=self.test_type
                )

            # Create result object
            result = TestResult(
                name_1=prop1.name or "sample_1",
                value_1=prop1.prop,
                std_1=prop1.std,
                size_1=prop1.nobs,
                name_2=prop2.name or "sample_2",
                value_2=prop2.prop,
                std_2=prop2.std,
                size_2=prop2.nobs,
                method_name=self.test_name,
                method_params=self.test_params,
                alpha=self.alpha,
                pvalue=pvalue,
                effect=effect,
                ci_length=ci_length,
                left_bound=left_bound,
                right_bound=right_bound,
                reject=reject,
                effect_distribution=distribution,
                mde_1=mde_1,
                mde_2=mde_2,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in ZTest compare_samples: {str(e)}", exc_info=True)
            raise

    def _validate_proportions(self, proportions: List[ProportionData]) -> None:
        """
        Validate proportion samples for Z-test.

        Parameters
        ----------
        proportions : List[ProportionData]
            Proportion samples to validate

        Raises
        ------
        ValueError
            If validation fails
        """
        if len(proportions) < 2:
            raise ValueError("At least two proportion samples are required for comparison")

        for i, prop in enumerate(proportions):
            prop_name = prop.name or f"proportion_{i}"

            # Check sample size
            if prop.nobs == 0:
                raise ValueError(f"Number of observations for '{prop_name}' cannot be zero")

            # Check for large sample assumption
            if prop.successes < 5 or (prop.nobs - prop.successes) < 5:
                self.logger.warning(
                    f"Sample '{prop_name}' may not meet large sample assumption. "
                    f"Successes: {prop.successes}, Failures: {prop.nobs - prop.successes}. "
                    "Z-test assumes np > 5 and n(1-p) > 5. Consider using exact tests for small samples."
                )

        # Check for duplicate names
        names = [prop.name for prop in proportions if prop.name is not None]
        if len(names) != len(set(names)):
            self.logger.warning(
                "Some proportion samples have duplicate names. "
                "This might lead to confusion in results interpretation."
            )
