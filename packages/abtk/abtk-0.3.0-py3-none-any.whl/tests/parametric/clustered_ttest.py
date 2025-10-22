"""
Cluster-randomized t-test for comparing means with cluster-robust inference.

This module provides a t-test implementation for cluster-randomized experiments
where randomization occurs at the cluster level (e.g., cities, stores, schools).
Uses OLS regression with cluster-robust standard errors.
"""

from typing import List, Literal, Optional
import logging
from itertools import combinations
import numpy as np
import statsmodels.api as sm

from core.base_cluster_test import BaseClusterTest
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha, validate_power
from utils.effect_size import calculate_pvalue_twosided


class ClusteredTTest(BaseClusterTest):
    """
    T-test for cluster-randomized experiments with cluster-robust inference.

    Uses OLS regression with cluster-robust standard errors (Liang-Zeger/Huber-White)
    to account for intra-cluster correlation. Appropriate when randomization occurs
    at the cluster level rather than individual level.

    The test estimates the treatment effect using regression:
        Y_ij = β₀ + β₁*Treatment_j + ε_ij

    Where:
    - i indexes individuals, j indexes clusters
    - Treatment_j is a cluster-level indicator
    - Standard errors are clustered at the randomization level

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference in means (mean_treatment - mean_control)
        - 'relative': relative difference ((mean_treatment - mean_control) / mean_control)
    min_clusters : int, default=5
        Minimum number of clusters per group
        - Raises error if < 3
        - Warns if < min_clusters
    warn_cv : float, default=0.5
        CV threshold for cluster size imbalance warning
    warn_icc_low : float, default=0.01
        ICC threshold below which clustering might not be needed
    warn_icc_high : float, default=0.15
        ICC threshold above which clustering strongly matters
    logger : logging.Logger, optional
        Logger instance for error reporting

    Attributes
    ----------
    test_type : str
        Type of effect being calculated
    min_clusters : int
        Minimum clusters per group
    warn_cv : float
        CV warning threshold
    warn_icc_low : float
        Low ICC warning threshold
    warn_icc_high : float
        High ICC warning threshold

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Geo experiment: 10 cities randomized
    >>> # Control: cities 1-5
    >>> control_data = []
    >>> control_clusters = []
    >>> for city in range(1, 6):
    >>>     # 100 users per city
    >>>     city_data = np.random.normal(100, 15, 100)
    >>>     control_data.extend(city_data)
    >>>     control_clusters.extend([city] * 100)
    >>>
    >>> # Treatment: cities 6-10
    >>> treatment_data = []
    >>> treatment_clusters = []
    >>> for city in range(6, 11):
    >>>     city_data = np.random.normal(105, 15, 100)  # +5% effect
    >>>     treatment_data.extend(city_data)
    >>>     treatment_clusters.extend([city] * 100)
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
    >>> # Run cluster test
    >>> test = ClusteredTTest(alpha=0.05, test_type="relative")
    >>> results = test.compare([control, treatment])
    >>>
    >>> # Access results
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")
    >>> print(f"ICC (control): {result.method_params['icc_control']:.3f}")
    >>> print(f"Design effect: {result.method_params['design_effect_control']:.2f}")

    Notes
    -----
    **When to use ClusteredTTest:**
    - Randomization at cluster level (cities, stores, schools, etc.)
    - ICC > 0.01 (some clustering effect)
    - At least 5 clusters per group (minimum 3, but 5+ recommended)

    **When NOT to use:**
    - Individual-level randomization → use TTest
    - ICC ≈ 0 (no clustering) → use TTest
    - < 3 clusters per group → test will fail

    **Key assumptions:**
    - Clusters are independent
    - Observations within clusters may be correlated
    - Randomization was at cluster level
    - Sufficient number of clusters (5-10+ per group)

    References
    ----------
    - Donner, A., & Klar, N. (2000). Design and Analysis of Cluster Randomization Trials
    - Cameron, A. C., & Miller, D. L. (2015). A Practitioner's Guide to Cluster-Robust Inference
    - Hayes, R. J., & Moulton, L. H. (2017). Cluster Randomised Trials
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        min_clusters: int = 5,
        warn_cv: float = 0.5,
        warn_icc_low: float = 0.01,
        warn_icc_high: float = 0.15,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('test_type must be "relative" or "absolute"')

        # Initialize base class
        super().__init__(
            test_name="clustered-ttest",
            alpha=alpha,
            min_clusters=min_clusters,
            warn_cv=warn_cv,
            warn_icc_low=warn_icc_low,
            warn_icc_high=warn_icc_high,
            logger=logger,
            test_type=test_type
        )

        # Test-specific parameters
        self.test_type = test_type

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise comparisons.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare. Each sample must have clusters attribute set.

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results

        Raises
        ------
        ValueError
            If samples don't pass validation or don't have clusters
        """
        if not samples or len(samples) < 2:
            return []

        # Use centralized validation
        validate_samples(samples, min_samples=2)

        # Check that all samples have clusters
        for i, sample in enumerate(samples):
            if sample.clusters is None:
                raise ValueError(
                    f"Sample {i} ({sample.name or 'unnamed'}) does not have clusters set. "
                    f"ClusteredTTest requires clusters attribute."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using cluster-randomized t-test.

        Uses OLS regression with cluster-robust standard errors:
            Y_ij = β₀ + β₁*Treatment_j + ε_ij

        Where β₁ is the treatment effect (difference in means).

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline), must have clusters
        sample2 : SampleData
            Second sample (treatment/variant), must have clusters

        Returns
        -------
        TestResult
            Test result with:
            - effect: treatment effect (relative or absolute)
            - pvalue: p-value from cluster-robust test
            - left_bound, right_bound: confidence interval
            - method_params: includes cluster diagnostics (ICC, design effect, etc.)

        Raises
        ------
        ValueError
            If clusters not set or validation fails
        """
        # Validate clusters
        validation = self._validate_clusters(sample1, sample2)

        # Combine data
        y = np.concatenate([sample1.data, sample2.data])
        n1 = sample1.sample_size
        n2 = sample2.sample_size

        # Treatment indicator (0 for sample1, 1 for sample2)
        treatment = np.concatenate([
            np.zeros(n1),
            np.ones(n2)
        ])

        # Combine cluster IDs (ensure they're unique across samples)
        # Add offset to sample2 clusters to avoid collision
        clusters_combined = np.concatenate([
            sample1.clusters,
            sample2.clusters + (np.max(sample1.clusters) + 1) if sample1.clusters.ndim == 1
            else sample2.clusters  # For 2D clusters, assume they're already unique
        ])

        # Design matrix: [intercept, treatment]
        X = sm.add_constant(treatment)

        # Fit OLS with cluster-robust SE
        model = sm.OLS(y, X)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': clusters_combined})

        # Extract treatment effect (β₁)
        beta_treatment = results.params[1]  # Coefficient on treatment
        se_treatment = results.bse[1]       # Cluster-robust SE
        t_stat = results.tvalues[1]
        pvalue = results.pvalues[1]

        # Calculate means
        mean_control = sample1.mean
        mean_treatment = sample2.mean

        # Calculate effect and CI based on test_type
        if self.test_type == "absolute":
            # Absolute effect = β₁
            effect = beta_treatment

            # CI for absolute effect
            # Use t-distribution with df = number of clusters - 2
            n_clusters_total = validation['n_clusters_1'] + validation['n_clusters_2']
            df = n_clusters_total - 2

            from scipy.stats import t as t_dist
            t_critical = t_dist.ppf(1 - self.alpha / 2, df)

            left_bound = effect - t_critical * se_treatment
            right_bound = effect + t_critical * se_treatment

        elif self.test_type == "relative":
            # Relative effect = β₁ / mean_control
            if mean_control == 0:
                raise ValueError("Cannot calculate relative effect when control mean is zero")

            effect = beta_treatment / mean_control

            # CI for relative effect using delta method
            # Var(β₁/μ) ≈ Var(β₁)/μ² (assuming μ is fixed)
            se_relative = se_treatment / abs(mean_control)

            n_clusters_total = validation['n_clusters_1'] + validation['n_clusters_2']
            df = n_clusters_total - 2

            from scipy.stats import t as t_dist
            t_critical = t_dist.ppf(1 - self.alpha / 2, df)

            left_bound = effect - t_critical * se_relative
            right_bound = effect + t_critical * se_relative

        else:
            raise ValueError(f"Invalid test_type: {self.test_type}")

        # Reject null hypothesis?
        reject = pvalue < self.alpha

        # CI length
        ci_length = right_bound - left_bound

        # Create cluster diagnostics
        cluster_diagnostics = self._create_cluster_diagnostics(validation)

        # Add test-specific params
        method_params = {
            'beta_treatment': beta_treatment,
            'se_cluster_robust': se_treatment,
            't_statistic': t_stat,
            'df': n_clusters_total - 2,
            'mean_control': mean_control,
            'mean_treatment': mean_treatment,
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
            f"ClusteredTTest("
            f"alpha={self.alpha}, "
            f"test_type='{self.test_type}', "
            f"min_clusters={self.min_clusters})"
        )
