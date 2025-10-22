"""
Post-normed bootstrap test with covariate normalization.

Post-normalization is a variance reduction technique that uses covariates
(pre-experiment data) to normalize the treatment effect, similar to CUPED
but using bootstrap methodology.

The normalization adjusts for baseline differences by dividing the treatment
ratio by the baseline ratio: (Treatment/Control) / (Treatment_baseline/Control_baseline)
"""

from typing import List, Literal, Optional, Callable
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha
from utils.bootstrap import (
    generate_bootstrap_samples,
    calculate_balanced_stratum_weights,
    calculate_bootstrap_ci,
    calculate_bootstrap_pvalue,
    apply_statistic_to_bootstrap_samples,
    check_bootstrap_normality
)


class PostNormedBootstrapTest(BaseTestProcessor):
    """
    Post-normed bootstrap test with covariate normalization.

    This test combines bootstrap resampling with post-normalization using covariates.
    It reduces variance by normalizing the treatment effect with baseline (covariate) ratio.

    Formula:
    -------
    For relative effect:
        Normalized_effect = (S_treatment / S_control) / (S_treatment_baseline / S_control_baseline) - 1

    For absolute effect:
        Normalized_effect = S_treatment - (S_treatment_baseline / S_control_baseline) * S_control

    Where S is the statistic (mean, median, etc.) and baseline is from covariates.

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    stat_func : callable, default=np.mean
        Statistic function to apply to bootstrap samples
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate
    n_samples : int, default=1000
        Number of bootstrap samples
    stratify : bool, default=False
        Whether to use stratified bootstrap
    weight_method : {'min', 'mean'}, default='min'
        Method for balancing category weights (with stratify=True)
    random_seed : Optional[int], default=None
        Random seed for reproducibility
    return_effect_distribution : bool, default=False
        If True, returns fitted normal distribution
    logger : logging.Logger, optional
        Logger instance

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Samples with historical data (covariates)
    >>> control = SampleData(
    ...     data=[100, 110, 95, 105],          # Current metric
    ...     covariates=[90, 100, 85, 95],      # Historical baseline
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 115, 100, 110],
    ...     covariates=[92, 102, 87, 97],
    ...     name="Treatment"
    ... )
    >>>
    >>> # Post-normed bootstrap test
    >>> test = PostNormedBootstrapTest(n_samples=10000)
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Normalized effect: {result.effect:.2%}")

    Notes
    -----
    Use post-normed bootstrap when:
    - You have pre-experiment data (covariates)
    - You want variance reduction (like CUPED)
    - You don't want to assume normality (unlike CUPED t-test)
    - Baseline metrics correlate with outcome metrics

    Comparison to CUPED:
    - CUPED: Parametric (assumes normality), uses linear adjustment
    - Post-normed: Nonparametric (no normality assumption), uses ratio adjustment
    - Both reduce variance using historical data

    The normalization removes bias from baseline imbalances:
    - If treatment group had higher baseline, effect is adjusted downward
    - If control group had higher baseline, effect is adjusted upward
    """

    def __init__(
        self,
        alpha: float = 0.05,
        stat_func: Callable[[np.ndarray], float] = np.mean,
        test_type: Literal["relative", "absolute"] = "relative",
        n_samples: int = 1000,
        stratify: bool = False,
        weight_method: Literal["min", "mean"] = "min",
        random_seed: Optional[int] = None,
        return_effect_distribution: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Invalid test_type. Use "relative" or "absolute"')

        if weight_method not in ["min", "mean"]:
            raise ValueError('Invalid weight_method. Use "min" or "mean"')

        if n_samples < 100:
            raise ValueError("n_samples should be at least 100 for reliable results")

        # Initialize base class
        super().__init__(
            test_name="post-normed-bootstrap-test",
            alpha=alpha,
            logger=logger,
            stat_func=stat_func.__name__ if hasattr(stat_func, '__name__') else str(stat_func),
            test_type=test_type,
            n_samples=n_samples,
            stratify=stratify,
            weight_method=weight_method
        )

        # Test-specific parameters
        self.stat_func = stat_func
        self.test_type = test_type
        self.n_samples = n_samples
        self.stratify = stratify
        self.weight_method = weight_method
        self.random_seed = random_seed
        self.return_effect_distribution = return_effect_distribution

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise post-normed bootstrap tests.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare (must have covariates)

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples
        validate_samples(samples, min_samples=2)

        # Check that all samples have covariates
        for sample in samples:
            if sample.covariates is None:
                raise ValueError(
                    f"Sample '{sample.name}' is missing covariates. "
                    "Post-normed bootstrap requires covariates for normalization."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using post-normed bootstrap test.

        Parameters
        ----------
        sample1 : SampleData
            First sample (must have covariates)
        sample2 : SampleData
            Second sample (must have covariates)

        Returns
        -------
        TestResult
            Test result with normalized effect
        """
        try:
            # Validate covariates
            if sample1.covariates is None or sample2.covariates is None:
                raise ValueError("Both samples must have covariates for post-normed bootstrap")

            # Calculate stratum weights if stratified
            stratum_weights1 = None
            stratum_weights2 = None

            if self.stratify:
                stratum_weights1, stratum_weights2 = calculate_balanced_stratum_weights(
                    sample1, sample2, weight_method=self.weight_method
                )

            # Generate bootstrap samples (both data and covariates)
            # IMPORTANT: Use different seeds for independent samples to avoid artificial correlation
            seed1 = self.random_seed if self.random_seed is None else self.random_seed
            seed2 = self.random_seed if self.random_seed is None else self.random_seed + 1

            boot_data1, boot_cov1 = generate_bootstrap_samples(
                sample=sample1,
                n_samples=self.n_samples,
                stratify=self.stratify,
                bootstrap_covariates=True,  # Important: bootstrap covariates too!
                stratum_weights=stratum_weights1,
                random_seed=seed1
            )

            boot_data2, boot_cov2 = generate_bootstrap_samples(
                sample=sample2,
                n_samples=self.n_samples,
                stratify=self.stratify,
                bootstrap_covariates=True,
                stratum_weights=stratum_weights2,
                random_seed=seed2
            )

            # Apply statistic function to bootstrap samples
            boot_stats1 = apply_statistic_to_bootstrap_samples(boot_data1, self.stat_func)
            boot_stats2 = apply_statistic_to_bootstrap_samples(boot_data2, self.stat_func)

            # Apply statistic function to bootstrap covariates
            boot_cov_stats1 = apply_statistic_to_bootstrap_samples(boot_cov1, self.stat_func)
            boot_cov_stats2 = apply_statistic_to_bootstrap_samples(boot_cov2, self.stat_func)

            # Calculate normalized bootstrap distribution
            if self.test_type == "absolute":
                # S2 - (S2_cov / S1_cov) * S1
                boot_effect = boot_stats2 - (boot_cov_stats2 / boot_cov_stats1) * boot_stats1
            elif self.test_type == "relative":
                # (S2 / S1) / (S2_cov / S1_cov) - 1
                boot_effect = (boot_stats2 / boot_stats1) / (boot_cov_stats2 / boot_cov_stats1) - 1
            else:
                raise ValueError(f"Invalid test_type: {self.test_type}")

            # Calculate confidence interval
            left_bound, right_bound, ci_length = calculate_bootstrap_ci(
                boot_effect, alpha=self.alpha
            )

            # Calculate p-value
            pvalue = calculate_bootstrap_pvalue(boot_effect, null_value=0.0)
            reject = pvalue < self.alpha

            # Calculate point estimate
            stat1 = self.stat_func(sample1.data)
            stat2 = self.stat_func(sample2.data)
            cov_stat1 = self.stat_func(sample1.covariates if sample1.covariates.ndim == 1 else sample1.covariates[:, 0])
            cov_stat2 = self.stat_func(sample2.covariates if sample2.covariates.ndim == 1 else sample2.covariates[:, 0])

            if self.test_type == "absolute":
                effect = stat2 - (cov_stat2 / cov_stat1) * stat1
            else:  # relative
                effect = (stat2 / stat1) / (cov_stat2 / cov_stat1) - 1

            # Check normality
            ks_pvalue, is_normal = check_bootstrap_normality(
                boot_effect, alpha=0.05, logger=self.logger
            )

            # Create effect distribution if requested
            effect_distribution = None
            if self.return_effect_distribution:
                mean_boot = np.mean(boot_effect)
                std_boot = np.std(boot_effect)
                effect_distribution = sps.norm(loc=mean_boot, scale=std_boot)

            # Create result object
            result = TestResult(
                name_1=sample1.name or "sample_1",
                value_1=stat1,
                std_1=np.std(sample1.data),
                cov_value_1=cov_stat1,
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=stat2,
                std_2=np.std(sample2.data),
                cov_value_2=cov_stat2,
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
                effect_distribution=effect_distribution
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in PostNormedBootstrapTest compare_samples: {str(e)}", exc_info=True)
            raise
