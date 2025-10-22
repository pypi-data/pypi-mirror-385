"""
Cluster-randomized test for proportions with cluster-robust inference.

This module provides a test for proportions (e.g., CTR, CVR) in cluster-randomized
experiments. Uses linear probability model with cluster-robust standard errors.
"""

from typing import List, Literal, Optional
import logging
from itertools import combinations
import numpy as np
import warnings

try:
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

from core.base_cluster_test import BaseClusterTest
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha


class ClusteredZTest(BaseClusterTest):
    """
    Test for proportions in cluster-randomized experiments with cluster-robust inference.

    For binary outcomes (e.g., click/no-click, convert/no-convert) in cluster-randomized
    experiments. Uses linear probability model with cluster-robust standard errors.

    Model:
        Pr(Y_ij = 1) = β₀ + β₁*Treatment_j + ε_ij

    Where:
    - Y_ij is binary outcome (0 or 1) for individual i in cluster j
    - Treatment_j is cluster-level indicator
    - β₁ is the difference in proportions (p_treatment - p_control)
    - Standard errors are clustered at randomization level

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='absolute'
        Type of effect to calculate:
        - 'absolute': difference in proportions (p2 - p1)
        - 'relative': relative difference ((p2 - p1) / p1)
    min_clusters : int, default=5
        Minimum number of clusters per group
    warn_cv : float, default=0.5
        CV threshold for cluster size imbalance warning
    warn_icc_low : float, default=0.01
        ICC threshold below which clustering might not be needed
    warn_icc_high : float, default=0.15
        ICC threshold above which clustering strongly matters
    warn_extreme_proportions : bool, default=True
        If True, warns when proportions are < 0.05 or > 0.95
        (linear probability model works best for 0.05 < p < 0.95)
    logger : logging.Logger, optional
        Logger instance

    Attributes
    ----------
    test_type : str
        Type of effect
    warn_extreme_proportions : bool
        Whether to warn for extreme proportions

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # CTR experiment: 10 cities randomized
    >>> # Control: cities 1-5
    >>> control_data = []
    >>> control_clusters = []
    >>> for city in range(1, 6):
    >>>     # 1000 impressions per city, 5% CTR
    >>>     clicks = np.random.binomial(1, 0.05, 1000)
    >>>     control_data.extend(clicks)
    >>>     control_clusters.extend([city] * 1000)
    >>>
    >>> # Treatment: cities 6-10, 6% CTR (+20% relative)
    >>> treatment_data = []
    >>> treatment_clusters = []
    >>> for city in range(6, 11):
    >>>     clicks = np.random.binomial(1, 0.06, 1000)
    >>>     treatment_data.extend(clicks)
    >>>     treatment_clusters.extend([city] * 1000)
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
    >>> # Run cluster test for proportions
    >>> test = ClusteredZTest(alpha=0.05, test_type="relative")
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")  # Relative change in CTR
    >>> print(f"P-value: {result.pvalue:.4f}")
    >>> print(f"Control CTR: {result.method_params['proportion_control']:.2%}")
    >>> print(f"Treatment CTR: {result.method_params['proportion_treatment']:.2%}")

    Notes
    -----
    **When to use ClusteredZTest:**
    - Binary outcomes (clicks, conversions, etc.)
    - Cluster-randomized design (cities, stores randomized)
    - Proportions between 0.05 and 0.95 (linear probability model works best)
    - At least 5 clusters per group

    **Data format:**
    - Use SampleData with binary data (0/1), NOT ProportionData
    - data should be array of 0s and 1s (e.g., [1, 0, 1, 1, 0, 0, ...])
    - clusters should identify which cluster each observation belongs to

    **Method:**
    - Uses linear probability model (OLS) instead of logistic regression
    - Easier to interpret: β₁ = difference in proportions
    - Works well for most proportions (0.05 < p < 0.95)
    - For extreme proportions (p < 0.05 or p > 0.95), consider logistic regression

    **Comparison:**
    - vs ZTest: Adds cluster-robust SE for cluster-randomized designs
    - vs ClusteredTTest: Specialized for binary outcomes (proportions)

    References
    ----------
    - Donner & Klar (2000). Design and Analysis of Cluster Randomization Trials
    - Wooldridge (2010). Econometric Analysis of Cross Section and Panel Data
    - Cameron & Miller (2015). A Practitioner's Guide to Cluster-Robust Inference
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "absolute",
        min_clusters: int = 5,
        warn_cv: float = 0.5,
        warn_icc_low: float = 0.01,
        warn_icc_high: float = 0.15,
        warn_extreme_proportions: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        # Check statsmodels
        if not STATSMODELS_AVAILABLE:
            raise ImportError(
                "ClusteredZTest requires statsmodels. Install: pip install statsmodels"
            )

        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('test_type must be "relative" or "absolute"')

        # Initialize base class
        super().__init__(
            test_name="clustered-ztest",
            alpha=alpha,
            min_clusters=min_clusters,
            warn_cv=warn_cv,
            warn_icc_low=warn_icc_low,
            warn_icc_high=warn_icc_high,
            logger=logger,
            test_type=test_type,
            warn_extreme_proportions=warn_extreme_proportions
        )

        # Test-specific parameters
        self.test_type = test_type
        self.warn_extreme_proportions = warn_extreme_proportions

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples with pairwise cluster proportion tests.

        Parameters
        ----------
        samples : List[SampleData]
            Samples with binary data (0/1) and clusters

        Returns
        -------
        List[TestResult]
            Pairwise comparison results

        Raises
        ------
        ValueError
            If samples missing clusters or data not binary
        """
        if not samples or len(samples) < 2:
            return []

        validate_samples(samples, min_samples=2)

        # Check clusters and binary data
        for sample in samples:
            if sample.clusters is None:
                raise ValueError(
                    f"Sample '{sample.name or 'unnamed'}' missing clusters. "
                    "ClusteredZTest requires clusters."
                )

            # Check if data is binary (0/1)
            unique_values = np.unique(sample.data)
            if not np.all(np.isin(unique_values, [0, 1])):
                raise ValueError(
                    f"Sample '{sample.name or 'unnamed'}' data must be binary (0 or 1). "
                    f"Found values: {unique_values}. "
                    f"For binary outcomes like clicks/conversions, use 1 for success and 0 for failure."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using cluster proportion test.

        Uses linear probability model:
            Pr(Y_ij = 1) = β₀ + β₁*Treatment_j + ε_ij

        Parameters
        ----------
        sample1 : SampleData
            First sample (control), must have binary data and clusters
        sample2 : SampleData
            Second sample (treatment), must have binary data and clusters

        Returns
        -------
        TestResult
            Result with difference in proportions, cluster diagnostics
        """
        # Validate clusters
        validation = self._validate_clusters(sample1, sample2)

        # Calculate proportions
        p_control = np.mean(sample1.data)
        p_treatment = np.mean(sample2.data)

        # Warn if extreme proportions (linear probability model less accurate)
        if self.warn_extreme_proportions:
            if p_control < 0.05 or p_control > 0.95 or p_treatment < 0.05 or p_treatment > 0.95:
                warnings.warn(
                    f"Extreme proportions detected (control: {p_control:.3f}, treatment: {p_treatment:.3f}). "
                    f"Linear probability model works best for 0.05 < p < 0.95. "
                    f"Consider using logistic regression for extreme proportions.",
                    UserWarning
                )

        # Combine data
        y = np.concatenate([sample1.data, sample2.data])  # Binary outcome
        n1 = sample1.sample_size
        n2 = sample2.sample_size

        # Treatment indicator
        treatment = np.concatenate([
            np.zeros(n1),
            np.ones(n2)
        ])

        # Combine cluster IDs (ensure unique)
        clusters_combined = np.concatenate([
            sample1.clusters,
            sample2.clusters + (np.max(sample1.clusters) + 1) if sample1.clusters.ndim == 1
            else sample2.clusters
        ])

        # Linear probability model: Pr(Y=1) = β₀ + β₁*Treatment
        X = sm.add_constant(treatment)

        model = sm.OLS(y, X)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': clusters_combined})

        # Extract treatment effect (difference in proportions)
        beta_treatment = results.params[1]  # p_treatment - p_control
        se_treatment = results.bse[1]
        t_stat = results.tvalues[1]
        pvalue = results.pvalues[1]

        # Calculate effect based on test_type
        if self.test_type == "absolute":
            # Absolute difference in proportions
            effect = beta_treatment

            # CI
            n_clusters_total = validation['n_clusters_1'] + validation['n_clusters_2']
            df = n_clusters_total - 2

            from scipy.stats import t as t_dist
            t_critical = t_dist.ppf(1 - self.alpha / 2, df)

            left_bound = effect - t_critical * se_treatment
            right_bound = effect + t_critical * se_treatment

        elif self.test_type == "relative":
            # Relative difference: (p_treatment - p_control) / p_control
            if p_control == 0:
                raise ValueError("Cannot calculate relative effect when control proportion is zero")

            effect = beta_treatment / p_control

            # SE for relative effect using delta method
            se_relative = se_treatment / p_control

            n_clusters_total = validation['n_clusters_1'] + validation['n_clusters_2']
            df = n_clusters_total - 2

            from scipy.stats import t as t_dist
            t_critical = t_dist.ppf(1 - self.alpha / 2, df)

            left_bound = effect - t_critical * se_relative
            right_bound = effect + t_critical * se_relative

        else:
            raise ValueError(f"Invalid test_type: {self.test_type}")

        reject = pvalue < self.alpha
        ci_length = right_bound - left_bound

        # Create cluster diagnostics
        cluster_diagnostics = self._create_cluster_diagnostics(validation)

        # Build method_params
        method_params = {
            'beta_treatment': beta_treatment,
            'se_cluster_robust': se_treatment,
            't_statistic': t_stat,
            'df': validation['n_clusters_1'] + validation['n_clusters_2'] - 2,
            'proportion_control': p_control,
            'proportion_treatment': p_treatment,
            'absolute_difference': beta_treatment,  # Always include absolute difference
            **cluster_diagnostics
        }

        return TestResult(
            statistic_value=t_stat,
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
            f"ClusteredZTest("
            f"alpha={self.alpha}, "
            f"test_type='{self.test_type}', "
            f"min_clusters={self.min_clusters})"
        )
