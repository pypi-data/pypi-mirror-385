"""
Paired bootstrap test for matched pairs experiments.

Paired bootstrap resamples PAIRS instead of individual observations,
preserving the pairing structure. This is used when observations in two
samples are naturally paired (e.g., matched pairs in A/B test, before/after).
"""

from typing import List, Literal, Optional, Callable
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_paired_samples, validate_alpha
from utils.bootstrap import (
    generate_paired_bootstrap_samples,
    calculate_bootstrap_ci,
    calculate_bootstrap_pvalue,
    apply_statistic_to_bootstrap_samples,
    check_bootstrap_normality
)


class PairedBootstrapTest(BaseTestProcessor):
    """
    Paired bootstrap test for matched pairs.

    Paired bootstrap resamples PAIRS (not individual observations) to preserve
    the pairing structure. This is critical when observations are matched.

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    stat_func : callable, default=np.mean
        Statistic function to apply to bootstrap samples
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference (stat2 - stat1)
        - 'relative': relative difference ((stat2 - stat1) / stat1)
    n_samples : int, default=1000
        Number of bootstrap samples
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
    >>> # Matched pairs A/B test
    >>> # Users matched by historical data, then randomly assigned
    >>> control = SampleData(
    ...     data=[100, 105, 95, 110],
    ...     paired_ids=[1, 2, 3, 4],
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 110, 100, 115],
    ...     paired_ids=[1, 2, 3, 4],
    ...     name="Treatment"
    ... )
    >>>
    >>> # Paired bootstrap test
    >>> test = PairedBootstrapTest(n_samples=10000)
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")

    Notes
    -----
    Use paired bootstrap when:
    - Observations are matched/paired (matched pairs A/B test)
    - Same subjects measured twice (before/after)
    - You want to remove between-subject/pair variability
    - paired_ids indicate which observations are matched

    Paired bootstrap workflow:
    1. Align data by paired_ids
    2. Sample PAIR indices with replacement
    3. Use SAME pair indices for both samples (preserves pairing)
    4. Calculate differences on bootstrap samples
    5. Estimate CI and p-value from bootstrap distribution

    Comparison to paired t-test:
    - Paired t-test: Parametric (assumes normality of differences)
    - Paired bootstrap: Nonparametric (no normality assumption)
    - Both preserve pairing structure and remove between-pair variability

    The key difference from regular bootstrap:
    - Regular: Samples each group independently (breaks pairing)
    - Paired: Samples pairs synchronously (preserves pairing)
    """

    def __init__(
        self,
        alpha: float = 0.05,
        stat_func: Callable[[np.ndarray], float] = np.mean,
        test_type: Literal["relative", "absolute"] = "relative",
        n_samples: int = 1000,
        random_seed: Optional[int] = None,
        return_effect_distribution: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Invalid test_type. Use "relative" or "absolute"')

        if n_samples < 100:
            raise ValueError("n_samples should be at least 100 for reliable results")

        # Initialize base class
        super().__init__(
            test_name="paired-bootstrap-test",
            alpha=alpha,
            logger=logger,
            stat_func=stat_func.__name__ if hasattr(stat_func, '__name__') else str(stat_func),
            test_type=test_type,
            n_samples=n_samples
        )

        # Test-specific parameters
        self.stat_func = stat_func
        self.test_type = test_type
        self.n_samples = n_samples
        self.random_seed = random_seed
        self.return_effect_distribution = return_effect_distribution

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise paired bootstrap tests.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare (must have paired_ids)

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples (checks for paired_ids)
        validate_paired_samples(samples, min_samples=2)

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two paired samples using paired bootstrap test.

        Parameters
        ----------
        sample1 : SampleData
            First sample (must have paired_ids)
        sample2 : SampleData
            Second sample (must have paired_ids)

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval
        """
        try:
            # Validate paired_ids
            if sample1.paired_ids is None or sample2.paired_ids is None:
                raise ValueError(
                    "Paired bootstrap requires both samples to have paired_ids. "
                    "Please provide paired_ids when creating SampleData."
                )

            # Generate paired bootstrap samples
            # Key: This function ensures SAME pair indices are used for both samples
            boot_data1, boot_data2 = generate_paired_bootstrap_samples(
                sample1=sample1,
                sample2=sample2,
                n_samples=self.n_samples,
                random_seed=self.random_seed
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

            # Calculate confidence interval
            left_bound, right_bound, ci_length = calculate_bootstrap_ci(
                boot_effect, alpha=self.alpha
            )

            # Calculate p-value
            pvalue = calculate_bootstrap_pvalue(boot_effect, null_value=0.0)
            reject = pvalue < self.alpha

            # Calculate point estimate of effect on original data
            # Need to align data by paired_ids first
            common_ids = np.intersect1d(sample1.paired_ids, sample2.paired_ids)

            mask1 = np.isin(sample1.paired_ids, common_ids)
            mask2 = np.isin(sample2.paired_ids, common_ids)

            sort_idx1 = np.argsort(sample1.paired_ids[mask1])
            sort_idx2 = np.argsort(sample2.paired_ids[mask2])

            data1_aligned = sample1.data[mask1][sort_idx1]
            data2_aligned = sample2.data[mask2][sort_idx2]

            stat1 = self.stat_func(data1_aligned)
            stat2 = self.stat_func(data2_aligned)

            if self.test_type == "absolute":
                effect = stat2 - stat1
            else:  # relative
                effect = stat2 / stat1 - 1

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
                std_1=np.std(data1_aligned),
                size_1=len(data1_aligned),
                name_2=sample2.name or "sample_2",
                value_2=stat2,
                std_2=np.std(data2_aligned),
                size_2=len(data2_aligned),
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
            self.logger.error(f"Error in PairedBootstrapTest compare_samples: {str(e)}", exc_info=True)
            raise
