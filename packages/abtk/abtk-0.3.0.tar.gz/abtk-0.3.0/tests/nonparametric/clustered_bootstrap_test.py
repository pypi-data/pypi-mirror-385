"""
Cluster bootstrap test for comparing samples in cluster-randomized experiments.

This module provides a nonparametric bootstrap test for cluster-randomized
experiments. It resamples clusters (not individuals) to preserve within-cluster
correlation structure.
"""

from typing import List, Literal, Optional, Callable
import logging
from itertools import combinations
import numpy as np
import warnings

from core.base_cluster_test import BaseClusterTest
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha
from utils.bootstrap import (
    generate_cluster_bootstrap_samples,
    calculate_bootstrap_ci,
    calculate_bootstrap_pvalue,
    check_bootstrap_normality
)


class ClusteredBootstrapTest(BaseClusterTest):
    """
    Bootstrap test for cluster-randomized experiments with cluster resampling.

    Uses cluster bootstrap (resamples clusters, not individuals) to account for
    within-cluster correlation. Appropriate for cluster-randomized experiments
    with non-normal data, outliers, or when distribution is unknown.

    The test works by:
    1. Resampling clusters WITH REPLACEMENT from each group
    2. Taking all observations from each sampled cluster
    3. Calculating test statistic (e.g., mean) for each bootstrap sample
    4. Estimating sampling distribution empirically

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
    n_samples : int, default=10000
        Number of bootstrap samples to generate
        Note: Cluster bootstrap typically needs more samples than individual bootstrap
    min_clusters : int, default=5
        Minimum number of clusters per group
    warn_cv : float, default=0.5
        CV threshold for cluster size imbalance warning
    warn_icc_low : float, default=0.01
        ICC threshold below which clustering might not be needed
    warn_icc_high : float, default=0.15
        ICC threshold above which clustering strongly matters
    random_seed : Optional[int], default=None
        Random seed for reproducibility
    logger : logging.Logger, optional
        Logger instance

    Attributes
    ----------
    stat_func : callable
        Statistic function
    test_type : str
        Type of effect
    n_samples : int
        Number of bootstrap samples
    random_seed : int or None
        Random seed

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Geo experiment: 10 cities with non-normal data
    >>> control_data = []
    >>> control_clusters = []
    >>> for city in range(1, 6):
    >>>     # Exponential distribution (non-normal)
    >>>     city_data = np.random.exponential(100, 200)
    >>>     control_data.extend(city_data)
    >>>     control_clusters.extend([city] * 200)
    >>>
    >>> treatment_data = []
    >>> treatment_clusters = []
    >>> for city in range(6, 11):
    >>>     city_data = np.random.exponential(105, 200)  # 5% higher
    >>>     treatment_data.extend(city_data)
    >>>     treatment_clusters.extend([city] * 200)
    >>>
    >>> control = SampleData(
    >>>     data=control_data,
    >>>     clusters=control_clusters,
    >>>     name="Control"
    >>> )
    >>> treatment = SampleData(
    >>>     data=treatment_data,
    >>>     clusters=treatment_clusters,
    >>>     name="Treatment"
    >>> )
    >>>
    >>> # Run cluster bootstrap test
    >>> test = ClusteredBootstrapTest(alpha=0.05, n_samples=10000)
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")
    >>> print(f"ICC: {result.method_params['icc_control']:.3f}")

    Notes
    -----
    **When to use ClusteredBootstrapTest:**
    - Cluster-randomized design (cities, stores randomized)
    - Non-normal data, outliers, or unknown distribution
    - Want distribution-free inference
    - Have at least 5 clusters per group

    **Cluster bootstrap vs individual bootstrap:**
    - Individual bootstrap: Resamples observations, ignores clustering
    - Cluster bootstrap: Resamples clusters, preserves ICC structure
    - Cluster bootstrap is more conservative (wider CIs) when ICC > 0

    **Cluster bootstrap algorithm:**
    1. Identify unique clusters in each group
    2. For each bootstrap iteration:
       a. Randomly sample clusters WITH REPLACEMENT
       b. Take ALL observations from each sampled cluster
       c. Calculate statistic on combined observations
    3. Estimate sampling distribution from bootstrap samples

    **Computational notes:**
    - Cluster bootstrap needs more iterations than individual bootstrap
    - Recommended: n_samples >= 10000 for stable results
    - Use random_seed for reproducibility

    **Comparison:**
    - vs BootstrapTest: Adds cluster resampling (preserves ICC)
    - vs ClusteredTTest: Nonparametric (no normality assumption)

    References
    ----------
    - Field, C. A., & Welsh, A. H. (2007). Bootstrapping Clustered Data.
      Journal of the Royal Statistical Society: Series B.
    - Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008).
      Bootstrap-Based Improvements for Inference with Clustered Errors.
      Review of Economics and Statistics.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        stat_func: Callable[[np.ndarray], float] = np.mean,
        test_type: Literal["relative", "absolute"] = "relative",
        n_samples: int = 10000,
        min_clusters: int = 5,
        warn_cv: float = 0.5,
        warn_icc_low: float = 0.01,
        warn_icc_high: float = 0.15,
        random_seed: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('test_type must be "relative" or "absolute"')

        if n_samples < 1000:
            warnings.warn(
                f"n_samples={n_samples} is quite low for cluster bootstrap. "
                f"Recommend n_samples >= 10000 for stable results.",
                UserWarning
            )

        # Initialize base class
        super().__init__(
            test_name="clustered-bootstrap",
            alpha=alpha,
            min_clusters=min_clusters,
            warn_cv=warn_cv,
            warn_icc_low=warn_icc_low,
            warn_icc_high=warn_icc_high,
            logger=logger,
            stat_func=stat_func.__name__ if hasattr(stat_func, '__name__') else str(stat_func),
            test_type=test_type,
            n_samples=n_samples,
            random_seed=random_seed
        )

        # Test-specific parameters
        self.stat_func = stat_func
        self.test_type = test_type
        self.n_samples = n_samples
        self.random_seed = random_seed

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples with pairwise cluster bootstrap tests.

        Parameters
        ----------
        samples : List[SampleData]
            Samples with clusters attribute set

        Returns
        -------
        List[TestResult]
            Pairwise comparison results

        Raises
        ------
        ValueError
            If samples missing clusters
        """
        if not samples or len(samples) < 2:
            return []

        validate_samples(samples, min_samples=2)

        # Check clusters
        for sample in samples:
            if sample.clusters is None:
                raise ValueError(
                    f"Sample '{sample.name or 'unnamed'}' missing clusters. "
                    "ClusteredBootstrapTest requires clusters."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using cluster bootstrap test.

        Resamples clusters from each group independently, calculates statistic
        for each bootstrap sample, and estimates sampling distribution empirically.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control), must have clusters
        sample2 : SampleData
            Second sample (treatment), must have clusters

        Returns
        -------
        TestResult
            Result with cluster diagnostics
        """
        # Validate clusters
        validation = self._validate_clusters(sample1, sample2)

        # Generate cluster bootstrap samples for both groups
        # IMPORTANT: Use different seeds for independent samples
        seed1 = self.random_seed if self.random_seed is None else self.random_seed
        seed2 = self.random_seed if self.random_seed is None else self.random_seed + 1

        boot_stats1 = generate_cluster_bootstrap_samples(
            sample=sample1,
            n_samples=self.n_samples,
            random_seed=seed1
        )

        boot_stats2 = generate_cluster_bootstrap_samples(
            sample=sample2,
            n_samples=self.n_samples,
            random_seed=seed2
        )

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

        # Create cluster diagnostics
        cluster_diagnostics = self._create_cluster_diagnostics(validation)

        # Build method_params
        method_params = {
            'stat_control': stat1,
            'stat_treatment': stat2,
            'bootstrap_mean': np.mean(boot_effect),
            'bootstrap_std': np.std(boot_effect),
            'bootstrap_normality_pvalue': ks_pvalue,
            'bootstrap_is_normal': is_normal,
            **cluster_diagnostics
        }

        return TestResult(
            statistic_value=effect,  # Use effect as statistic
            pvalue=pvalue,
            reject=reject,
            effect=effect,
            left_bound=left_bound,
            right_bound=right_bound,
            ci_length=ci_length,
            alpha=self.alpha,
            test_type=self.test_name,
            alternative_hypothesis="two-sided",
            method_params=method_params,
            name_1=sample1.name,
            name_2=sample2.name
        )

    def __repr__(self) -> str:
        return (
            f"ClusteredBootstrapTest("
            f"alpha={self.alpha}, "
            f"stat_func={self.stat_func.__name__ if hasattr(self.stat_func, '__name__') else self.stat_func}, "
            f"test_type='{self.test_type}', "
            f"n_samples={self.n_samples}, "
            f"min_clusters={self.min_clusters})"
        )
