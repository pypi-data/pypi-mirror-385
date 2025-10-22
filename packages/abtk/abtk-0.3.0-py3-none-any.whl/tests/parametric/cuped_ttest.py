"""
CUPED t-test for variance-reduced comparison of means.

CUPED (Controlled-experiment Using Pre-Experiment Data) is a variance reduction
technique that uses pre-experiment data (covariates) to reduce noise and increase
the sensitivity of A/B tests.

This implementation follows the methodology from:
Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013).
"Improving the Sensitivity of Online Controlled Experiments by Utilizing
Pre-Experiment Data". WSDM '13.
"""

from typing import List, Literal, Optional, Tuple
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples_with_covariates, validate_alpha, validate_power
from utils.effect_size import (
    calculate_confidence_interval,
    calculate_pvalue_twosided
)


class CupedTTest(BaseTestProcessor):
    """
    CUPED t-test for variance-reduced comparison of means.

    CUPED reduces variance by adjusting the metric using pre-experiment data (covariates).
    This allows detection of smaller effects with the same sample size, or requires
    smaller samples to detect the same effect.

    The variance reduction factor is (1 - ρ²) where ρ is the correlation between
    the metric and the covariate. For example, with ρ=0.7, variance is reduced by 51%!

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
    min_correlation : float, default=0.5
        Minimum acceptable correlation between metric and covariate.
        If correlation is below this threshold, a warning is issued.
        CUPED is most effective with correlation > 0.5.
    logger : logging.Logger, optional
        Logger instance for error reporting

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Create samples with covariates (pre-experiment data)
    >>> control = SampleData(
    ...     data=np.random.normal(100, 15, 1000),
    ...     covariates=np.random.normal(95, 15, 1000),  # Pre-experiment metric
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=np.random.normal(105, 15, 1000),
    ...     covariates=np.random.normal(96, 15, 1000),
    ...     name="Treatment"
    ... )
    >>>
    >>> # Run CUPED t-test
    >>> cuped_test = CupedTTest(alpha=0.05, test_type="relative")
    >>> results = cuped_test.compare([control, treatment])
    >>>
    >>> # Compare with regular t-test
    >>> from tests.parametric.ttest import TTest
    >>> regular_test = TTest(alpha=0.05, test_type="relative")
    >>> regular_results = regular_test.compare([control, treatment])
    >>>
    >>> print(f"CUPED p-value: {results[0].pvalue:.4f}")
    >>> print(f"Regular p-value: {regular_results[0].pvalue:.4f}")
    >>> print("CUPED typically has lower p-value (more sensitive)")

    Notes
    -----
    When to use CUPED:
    - You have pre-experiment data (e.g., user behavior before the test)
    - The pre-experiment metric correlates with the experiment metric (ρ > 0.5)
    - You want to increase sensitivity or reduce required sample size

    When NOT to use CUPED:
    - No pre-experiment data available
    - Low correlation between metric and covariate (ρ < 0.3)
    - Pre-experiment data may be biased or unreliable

    References
    ----------
    Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013).
    "Improving the Sensitivity of Online Controlled Experiments by Utilizing
    Pre-Experiment Data". WSDM '13.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        return_effect_distribution: bool = False,
        calculate_mde: bool = True,
        power: float = 0.8,
        min_correlation: float = 0.5,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)
        validate_power(power)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Incorrect test type. Use "relative" or "absolute"')

        if not 0 <= min_correlation <= 1:
            raise ValueError(f"min_correlation must be between 0 and 1, got {min_correlation}")

        # Initialize base class
        super().__init__(
            test_name="cuped-t-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type,
            calculate_mde=calculate_mde,
            power=power,
            return_effect_distribution=return_effect_distribution,
            min_correlation=min_correlation
        )

        # Test-specific parameters
        self.test_type = test_type
        self.return_effect_distribution = return_effect_distribution
        self.calculate_mde = calculate_mde
        self.power = power
        self.min_correlation = min_correlation

    @staticmethod
    def _calculate_effect_distribution(
        sample1: SampleData,
        sample2: SampleData,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> Tuple[sps.norm, float]:
        """
        Calculate effect distribution for CUPED t-test.

        CUPED (Controlled-experiment Using Pre-Experiment Data) reduces variance
        by using covariates (pre-experiment data) to adjust the metric.

        The adjustment formula:
            Y_adjusted = Y - θ * X_covariate

        Where θ is chosen to minimize variance:
            θ = [Cov(Y1,X1) + Cov(Y2,X2)] / [Var(X1) + Var(X2)]
        """
        # Validate that covariates are present
        if sample1.covariates is None or sample2.covariates is None:
            raise ValueError("CUPED requires covariates (pre-experiment data) for both samples")

        # Get data arrays
        y1 = sample1.data  # Control metric
        y2 = sample2.data  # Treatment metric

        # Handle both 1D and 2D covariates (use first covariate if multiple)
        x1 = sample1.covariates[:, 0] if sample1.covariates.ndim == 2 else sample1.covariates
        x2 = sample2.covariates[:, 0] if sample2.covariates.ndim == 2 else sample2.covariates

        # Calculate theta (pooled across both samples)
        # θ = [Cov(Y1, X1) + Cov(Y2, X2)] / [Var(X1) + Var(X2)]
        cov_y1_x1 = np.cov(y1, x1)[0, 1]
        cov_y2_x2 = np.cov(y2, x2)[0, 1]
        var_x1 = np.var(x1)
        var_x2 = np.var(x2)

        theta = (cov_y1_x1 + cov_y2_x2) / (var_x1 + var_x2)

        # Apply CUPED adjustment
        y1_cuped = y1 - theta * x1
        y2_cuped = y2 - theta * x2

        # Calculate statistics for adjusted data
        mean_1_cuped = np.mean(y1_cuped)
        mean_2_cuped = np.mean(y2_cuped)
        var_1_cuped = np.var(y1_cuped)
        var_2_cuped = np.var(y2_cuped)
        n1 = len(y1)
        n2 = len(y2)

        if test_type == "absolute":
            # Absolute effect: difference in adjusted means
            difference_mean = mean_2_cuped - mean_1_cuped
            difference_var = var_1_cuped / n1 + var_2_cuped / n2

            distribution = sps.norm(
                loc=difference_mean,
                scale=np.sqrt(difference_var)
            )
            effect = difference_mean

        elif test_type == "relative":
            # Relative effect: use original mean_1 as denominator
            # This is important: we adjust numerator but not denominator
            mean_den = sample1.mean  # Original control mean (not adjusted)
            mean_num = mean_2_cuped - mean_1_cuped  # Adjusted difference

            if mean_den == 0:
                raise ValueError("Cannot calculate relative effect when baseline mean is zero")

            # Variance calculations
            var_mean_den = sample1.variance / n1
            var_mean_num = var_1_cuped / n1 + var_2_cuped / n2

            # Covariance between adjusted difference and original control mean
            cov = -np.cov(y1_cuped, sample1.data)[0, 1] / n1

            # Delta method for relative effect variance
            relative_mu = mean_num / mean_den
            relative_var = (
                var_mean_num / (mean_den**2)
                + var_mean_den * ((mean_num**2) / (mean_den**4))
                - 2 * (mean_num / (mean_den**3)) * cov
            )

            if relative_var < 0:
                # Numerical stability
                relative_var = var_mean_num / (mean_den**2)

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
        correlation: float,
        alpha: float = 0.05,
        power: float = 0.8,
        ratio: float = 1.0,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> float:
        """
        Calculate Minimum Detectable Effect (MDE) for CUPED t-test.

        CUPED reduces variance through covariate adjustment, making it possible
        to detect smaller effects with the same sample size.

        The variance reduction factor is (1 - ρ²) where ρ is the correlation
        between the metric and the covariate.
        """
        if not -1 <= correlation <= 1:
            raise ValueError(f"Correlation must be between -1 and 1, got {correlation}")
        if n <= 0:
            raise ValueError("Sample size must be positive")
        if std < 0:
            raise ValueError("Standard deviation cannot be negative")

        # Calculate variance reduction factor
        variance_reduction = 1 - correlation**2

        # CUPED adjusted standard deviation
        std_cuped = std * np.sqrt(variance_reduction)

        # Z-scores for power and alpha
        z_alpha = sps.norm.ppf(1 - alpha / 2)  # Two-sided test
        z_beta = sps.norm.ppf(power)

        # Pooled standard error with CUPED adjustment
        se_cuped = std_cuped * np.sqrt(1/n + 1/(ratio * n))

        # MDE in absolute terms
        mde_absolute = (z_alpha + z_beta) * se_cuped

        if test_type == "relative":
            # Convert to relative MDE
            if mean == 0:
                return 0.0
            return mde_absolute / abs(mean)
        else:
            return mde_absolute

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise comparisons using CUPED.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare (must include covariates)

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results

        Raises
        ------
        ValueError
            If samples don't have covariates or fail validation
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples and covariates
        validate_samples_with_covariates(
            samples,
            min_samples=2,
            min_correlation=self.min_correlation
        )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using CUPED t-test.

        This method applies CUPED variance reduction using covariates,
        then calculates the effect size, p-value, confidence interval,
        and optionally the minimum detectable effect.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline) with covariates
        sample2 : SampleData
            Second sample (treatment/variant) with covariates

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval, etc.
            MDE values will be smaller than regular t-test due to variance reduction.

        Raises
        ------
        ValueError
            If samples are missing covariates or effect calculation fails
        """
        try:
            # Calculate effect distribution using CUPED
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

            # Calculate MDE with CUPED adjustment
            mde_1 = mde_2 = 0.0
            if self.calculate_mde:
                # Use correlation from first covariate
                corr_1 = abs(sample1.cov_corr_coef) if sample1.cov_corr_coef is not None else 0.0
                corr_2 = abs(sample2.cov_corr_coef) if sample2.cov_corr_coef is not None else 0.0

                mde_1 = self._calculate_mde(
                    mean=sample1.mean,
                    std=sample1.std_dev,
                    n=sample1.sample_size,
                    correlation=corr_1,
                    alpha=self.alpha,
                    power=self.power,
                    ratio=sample2.sample_size / sample1.sample_size,
                    test_type=self.test_type
                )
                mde_2 = self._calculate_mde(
                    mean=sample2.mean,
                    std=sample2.std_dev,
                    n=sample2.sample_size,
                    correlation=corr_2,
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
                cov_value_1=sample1.cov_mean,  # Pre-experiment mean
                name_2=sample2.name or "sample_2",
                value_2=sample2.mean,
                std_2=sample2.std_dev,
                size_2=sample2.sample_size,
                cov_value_2=sample2.cov_mean,  # Pre-experiment mean
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
            self.logger.error(f"Error in CupedTTest compare_samples: {str(e)}", exc_info=True)
            raise
