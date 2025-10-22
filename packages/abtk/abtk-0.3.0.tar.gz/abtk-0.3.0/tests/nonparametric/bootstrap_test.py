"""
Bootstrap test for comparing samples using resampling.

Bootstrap is a nonparametric method that doesn't assume normality.
It works by resampling with replacement and calculating the distribution
of test statistics empirically.

Use bootstrap when:
- Sample size is small
- Distribution is unknown or non-normal
- Outliers are present
- You want distribution-free inference
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


class BootstrapTest(BaseTestProcessor):
    """
    Bootstrap test for comparing two samples.

    Bootstrap is a resampling method that estimates the sampling distribution
    by repeatedly sampling with replacement from the observed data.

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    stat_func : callable, default=np.mean
        Statistic function to apply to each bootstrap sample.
        Should accept 1D array and return a scalar.
        Common choices: np.mean, np.median, lambda x: np.percentile(x, 90)
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference (stat2 - stat1)
        - 'relative': relative difference ((stat2 - stat1) / stat1)
    n_samples : int, default=1000
        Number of bootstrap samples to generate
    stratify : bool, default=False
        If True, performs stratified bootstrap to maintain category proportions.
        Useful when there's categorical imbalance between groups.
    weight_method : {'min', 'mean'}, default='min'
        Method for balancing category weights between groups (used with stratify=True):
        - 'min': Conservative approach (use minimum category count)
        - 'mean': Balanced approach (use average category count)
    random_seed : Optional[int], default=None
        Random seed for reproducibility
    return_effect_distribution : bool, default=False
        If True, returns fitted normal distribution to bootstrap distribution
    logger : logging.Logger, optional
        Logger instance for error reporting

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Non-normal data (e.g., exponential)
    >>> control = SampleData(
    ...     data=np.random.exponential(10, 100),
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=np.random.exponential(12, 100),
    ...     name="Treatment"
    ... )
    >>>
    >>> # Bootstrap test (no normality assumption)
    >>> boot_test = BootstrapTest(alpha=0.05, n_samples=10000)
    >>> results = boot_test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")

    >>> # Stratified bootstrap with strata
    >>> control = SampleData(
    ...     data=[100, 110, 90, 95, 105],
    ...     strata=['Mobile', 'Mobile', 'Desktop', 'Desktop', 'Desktop'],
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 115, 92, 98],
    ...     strata=['Mobile', 'Desktop', 'Desktop', 'Desktop'],
    ...     name="Treatment"
    ... )
    >>>
    >>> boot_test = BootstrapTest(stratify=True, weight_method='min')
    >>> results = boot_test.compare([control, treatment])

    Notes
    -----
    Bootstrap advantages:
    - No normality assumption required
    - Works with any statistic (mean, median, percentiles, etc.)
    - Handles small samples better than parametric tests
    - Provides empirical distribution

    Bootstrap limitations:
    - Computationally intensive (requires many resamples)
    - Assumes observations are independent
    - May be conservative for very small samples (n < 20)

    Stratified bootstrap:
    - Maintains stratum proportions in bootstrap samples
    - Reduces bias from categorical imbalance
    - Example: If control is 60% mobile and treatment is 45% mobile,
      stratified bootstrap ensures both groups use the same proportion
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
            test_name="bootstrap-test",
            alpha=alpha,
            logger=logger,
            stat_func=stat_func.__name__ if hasattr(stat_func, '__name__') else str(stat_func),
            test_type=test_type,
            n_samples=n_samples,
            stratify=stratify,
            weight_method=weight_method,
            random_seed=random_seed
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
        Compare multiple samples and perform pairwise bootstrap tests.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples
        validate_samples(samples, min_samples=2)

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using bootstrap test.

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
        """
        try:
            # Calculate stratum weights if stratified
            stratum_weights1 = None
            stratum_weights2 = None

            if self.stratify:
                stratum_weights1, stratum_weights2 = calculate_balanced_stratum_weights(
                    sample1, sample2, weight_method=self.weight_method
                )

            # Generate bootstrap samples for both groups
            # IMPORTANT: Use different seeds for independent samples to avoid artificial correlation
            seed1 = self.random_seed if self.random_seed is None else self.random_seed
            seed2 = self.random_seed if self.random_seed is None else self.random_seed + 1

            boot_data1, _ = generate_bootstrap_samples(
                sample=sample1,
                n_samples=self.n_samples,
                stratify=self.stratify,
                stratum_weights=stratum_weights1,
                random_seed=seed1
            )

            boot_data2, _ = generate_bootstrap_samples(
                sample=sample2,
                n_samples=self.n_samples,
                stratify=self.stratify,
                stratum_weights=stratum_weights2,
                random_seed=seed2
            )

            # Apply statistic function to bootstrap samples
            boot_stats1 = apply_statistic_to_bootstrap_samples(boot_data1, self.stat_func)
            boot_stats2 = apply_statistic_to_bootstrap_samples(boot_data2, self.stat_func)

            # Calculate bootstrap distribution of effect
            if self.test_type == "absolute":
                boot_effect = boot_stats2 - boot_stats1
            elif self.test_type == "relative":
                boot_effect = boot_stats2 / boot_stats1 - 1
            else:
                raise ValueError(f"Invalid test_type: {self.test_type}")

            # Calculate confidence interval from bootstrap distribution
            left_bound, right_bound, ci_length = calculate_bootstrap_ci(
                boot_effect, alpha=self.alpha
            )

            # Calculate p-value from bootstrap distribution
            pvalue = calculate_bootstrap_pvalue(boot_effect, null_value=0.0)
            reject = pvalue < self.alpha

            # Calculate point estimate of effect
            stat1 = self.stat_func(sample1.data)
            stat2 = self.stat_func(sample2.data)

            if self.test_type == "absolute":
                effect = stat2 - stat1
            else:  # relative
                effect = stat2 / stat1 - 1

            # Check normality of bootstrap distribution
            ks_pvalue, is_normal = check_bootstrap_normality(
                boot_effect, alpha=0.05, logger=self.logger
            )

            # Create effect distribution (fitted normal) if requested
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
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=stat2,
                std_2=np.std(sample2.data),
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
            self.logger.error(f"Error in BootstrapTest compare_samples: {str(e)}", exc_info=True)
            raise
