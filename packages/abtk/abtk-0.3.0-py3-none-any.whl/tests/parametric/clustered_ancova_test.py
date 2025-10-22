"""
Cluster-randomized ANCOVA test with covariate adjustment and cluster-robust inference.

This module provides ANCOVA (Analysis of Covariance) for cluster-randomized experiments
where randomization occurs at the cluster level and multiple covariates are available
for variance reduction.
"""

from typing import List, Literal, Optional
import logging
from itertools import combinations
import numpy as np
import pandas as pd
import warnings

try:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

from core.base_cluster_test import BaseClusterTest
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha


class ClusteredAncovaTest(BaseClusterTest):
    """
    ANCOVA for cluster-randomized experiments with cluster-robust inference.

    Combines:
    - Multiple covariate adjustment (like ANCOVA)
    - Cluster-robust standard errors (like ClusteredTTest)

    Uses OLS regression with covariates and cluster-robust SE:
        Y_ij = β₀ + β₁*Treatment_j + β₂*X₁ + β₃*X₂ + ... + ε_ij

    Where:
    - i indexes individuals, j indexes clusters
    - Treatment_j is cluster-level indicator
    - X₁, X₂, ... are covariates (can be individual or cluster-level)
    - Standard errors are clustered at randomization level

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'relative': Uses log(Y) transformation, effect as percentage
        - 'absolute': Uses Y directly, effect in absolute units
    min_clusters : int, default=5
        Minimum number of clusters per group
    warn_cv : float, default=0.5
        CV threshold for cluster size imbalance warning
    warn_icc_low : float, default=0.01
        ICC threshold below which clustering might not be needed
    warn_icc_high : float, default=0.15
        ICC threshold above which clustering strongly matters
    check_interaction : bool, default=False
        If True, checks for heterogeneous treatment effects
        (interaction between treatment and covariates)
    interaction_alpha : float, default=0.10
        Significance level for interaction terms
    validate_assumptions : bool, default=True
        If True, validates regression assumptions (VIF for multicollinearity)
    logger : logging.Logger, optional
        Logger instance

    Attributes
    ----------
    test_type : str
        Type of effect
    check_interaction : bool
        Whether to check interactions
    interaction_alpha : float
        Significance for interactions
    validate_assumptions : bool
        Whether to validate assumptions

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Geo experiment with baseline data
    >>> # Control: 5 cities, 100 users each
    >>> control_data = []
    >>> control_covariates = []
    >>> control_clusters = []
    >>> for city in range(1, 6):
    >>>     city_baseline = np.random.normal(90, 10, 100)
    >>>     city_current = city_baseline * 1.1 + np.random.normal(0, 5, 100)
    >>>     control_data.extend(city_current)
    >>>     control_covariates.extend(city_baseline)
    >>>     control_clusters.extend([city] * 100)
    >>>
    >>> # Treatment: 5 cities, 100 users each
    >>> treatment_data = []
    >>> treatment_covariates = []
    >>> treatment_clusters = []
    >>> for city in range(6, 11):
    >>>     city_baseline = np.random.normal(90, 10, 100)
    >>>     city_current = city_baseline * 1.15 + np.random.normal(0, 5, 100)  # +5% effect
    >>>     treatment_data.extend(city_current)
    >>>     treatment_covariates.extend(city_baseline)
    >>>     treatment_clusters.extend([city] * 100)
    >>>
    >>> control = SampleData(
    >>>     data=control_data,
    >>>     covariates=control_covariates,
    >>>     clusters=control_clusters,
    >>>     name="Control"
    >>> )
    >>> treatment = SampleData(
    >>>     data=treatment_data,
    >>>     covariates=treatment_covariates,
    >>>     clusters=treatment_clusters,
    >>>     name="Treatment"
    >>> )
    >>>
    >>> test = ClusteredAncovaTest(alpha=0.05, test_type="relative")
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"ICC: {result.method_params['icc_control']:.3f}")
    >>> print(f"R²: {result.method_params['r_squared']:.3f}")

    Notes
    -----
    **When to use ClusteredAncovaTest:**
    - Randomization at cluster level (cities, stores, schools)
    - Have pre-experiment covariates for variance reduction
    - Want maximum variance reduction (cluster adjustment + covariate adjustment)
    - ICC > 0.01
    - At least 5 clusters per group

    **Advantages over ClusteredTTest:**
    - Reduces variance using covariates (narrower CIs)
    - Can use multiple covariates simultaneously
    - Typically 20-50% narrower CIs than ClusteredTTest

    **Comparison:**
    - vs ClusteredTTest: Adds covariate adjustment for variance reduction
    - vs AncovaTest: Adds cluster-robust SE for cluster-randomized designs
    - vs CUPED: Can use multiple covariates + handles clusters

    **Requirements:**
    - Both samples must have covariates
    - Both samples must have clusters
    - Sample size: n > n_covariates + 10
    - For relative effect: all outcome values must be positive

    References
    ----------
    - Donner & Klar (2000). Design and Analysis of Cluster Randomization Trials
    - Deng et al. (2013). Improving sensitivity using pre-experiment data (CUPED)
    - Cameron & Miller (2015). A Practitioner's Guide to Cluster-Robust Inference
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        min_clusters: int = 5,
        warn_cv: float = 0.5,
        warn_icc_low: float = 0.01,
        warn_icc_high: float = 0.15,
        check_interaction: bool = False,
        interaction_alpha: float = 0.10,
        validate_assumptions: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        # Check statsmodels
        if not STATSMODELS_AVAILABLE:
            raise ImportError(
                "ClusteredAncovaTest requires statsmodels. Install: pip install statsmodels"
            )

        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('test_type must be "relative" or "absolute"')

        if not 0 < interaction_alpha < 1:
            raise ValueError("interaction_alpha must be between 0 and 1")

        # Initialize base class
        super().__init__(
            test_name="clustered-ancova-test",
            alpha=alpha,
            min_clusters=min_clusters,
            warn_cv=warn_cv,
            warn_icc_low=warn_icc_low,
            warn_icc_high=warn_icc_high,
            logger=logger,
            test_type=test_type,
            check_interaction=check_interaction,
            interaction_alpha=interaction_alpha,
            validate_assumptions=validate_assumptions
        )

        # Test-specific parameters
        self.test_type = test_type
        self.check_interaction = check_interaction
        self.interaction_alpha = interaction_alpha
        self.validate_assumptions = validate_assumptions

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples with pairwise cluster ANCOVA.

        Parameters
        ----------
        samples : List[SampleData]
            Samples to compare (must have both covariates and clusters)

        Returns
        -------
        List[TestResult]
            Pairwise comparison results

        Raises
        ------
        ValueError
            If samples missing covariates or clusters
        """
        if not samples or len(samples) < 2:
            return []

        validate_samples(samples, min_samples=2)

        # Check covariates
        for sample in samples:
            if sample.covariates is None:
                raise ValueError(
                    f"Sample '{sample.name or 'unnamed'}' missing covariates. "
                    "ClusteredAncovaTest requires covariates."
                )
            if sample.clusters is None:
                raise ValueError(
                    f"Sample '{sample.name or 'unnamed'}' missing clusters. "
                    "ClusteredAncovaTest requires clusters."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using cluster ANCOVA.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control), must have covariates and clusters
        sample2 : SampleData
            Second sample (treatment), must have covariates and clusters

        Returns
        -------
        TestResult
            Result with treatment effect, cluster diagnostics, ANCOVA diagnostics
        """
        # Validate clusters
        validation = self._validate_clusters(sample1, sample2)

        # Validate covariates
        if sample1.covariates is None or sample2.covariates is None:
            raise ValueError("Both samples must have covariates for ClusteredAncovaTest")

        # Prepare regression data
        df = self._prepare_regression_data(sample1, sample2)

        # Validate for relative effect
        if self.test_type == "relative":
            if (df['outcome'] <= 0).any():
                raise ValueError(
                    "For relative effect (log transformation), all outcome values must be positive. "
                    f"Found {(df['outcome'] <= 0).sum()} non-positive values."
                )
            df['outcome_transformed'] = np.log(df['outcome'])
        else:
            df['outcome_transformed'] = df['outcome']

        # Check sample size
        n_total = len(df)
        n_covariates = df.filter(regex='^covariate_').shape[1]

        if n_total < n_covariates + 10:
            raise ValueError(
                f"Insufficient sample size. Need at least {n_covariates + 10} observations, "
                f"got {n_total}. (Rule: n > k + 10, where k = {n_covariates} covariates)"
            )

        # Build design matrix: outcome_transformed ~ treatment + covariates
        covariate_cols = [col for col in df.columns if col.startswith('covariate_')]
        X = sm.add_constant(df[['treatment'] + covariate_cols])

        y = df['outcome_transformed']

        # Fit OLS with cluster-robust SE
        model = sm.OLS(y, X)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': df['cluster'].values})

        # Extract treatment effect
        treatment_coef = results.params['treatment']
        treatment_se = results.bse['treatment']
        treatment_pvalue = results.pvalues['treatment']

        # Confidence interval
        ci = results.conf_int(alpha=self.alpha)
        ci_lower = ci.loc['treatment', 0]
        ci_upper = ci.loc['treatment', 1]

        # Convert to relative if needed
        if self.test_type == "relative":
            effect = np.exp(treatment_coef) - 1
            left_bound = np.exp(ci_lower) - 1
            right_bound = np.exp(ci_upper) - 1
        else:
            effect = treatment_coef
            left_bound = ci_lower
            right_bound = ci_upper

        ci_length = right_bound - left_bound
        reject = treatment_pvalue < self.alpha

        # Validate assumptions
        validation_info = {}
        if self.validate_assumptions:
            validation_info = self._validate_vif(X, covariate_cols)

        # Check interactions
        interaction_info = {}
        if self.check_interaction:
            interaction_info = self._check_interactions(df, covariate_cols)

        # Create cluster diagnostics
        cluster_diagnostics = self._create_cluster_diagnostics(validation)

        # Build method_params
        n_clusters_total = validation['n_clusters_1'] + validation['n_clusters_2']

        method_params = {
            'beta_treatment': treatment_coef,
            'se_cluster_robust': treatment_se,
            't_statistic': results.tvalues['treatment'],
            'df': n_clusters_total - 2,
            'n_covariates': n_covariates,
            'r_squared': results.rsquared,
            'adj_r_squared': results.rsquared_adj,
            'n_obs': n_total,
            **cluster_diagnostics,
            **validation_info,
            **interaction_info
        }

        return TestResult(
            statistic_value=results.tvalues['treatment'],
            pvalue=treatment_pvalue,
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

    def _prepare_regression_data(self, sample1: SampleData, sample2: SampleData) -> pd.DataFrame:
        """
        Prepare data for regression.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: outcome, treatment, covariate_0, ..., cluster
        """
        # Combine outcomes
        outcome = np.concatenate([sample1.data, sample2.data])

        # Treatment indicator
        treatment = np.concatenate([
            np.zeros(sample1.sample_size),
            np.ones(sample2.sample_size)
        ])

        # Combine covariates
        cov1 = sample1.covariates
        cov2 = sample2.covariates

        # Ensure 2D
        if cov1.ndim == 1:
            cov1 = cov1.reshape(-1, 1)
        if cov2.ndim == 1:
            cov2 = cov2.reshape(-1, 1)

        covariates = np.vstack([cov1, cov2])

        # Combine clusters (ensure unique IDs)
        clusters_combined = np.concatenate([
            sample1.clusters,
            sample2.clusters + (np.max(sample1.clusters) + 1) if sample1.clusters.ndim == 1
            else sample2.clusters
        ])

        # Build DataFrame
        df_dict = {'outcome': outcome, 'treatment': treatment, 'cluster': clusters_combined}

        # Add covariates
        for i in range(covariates.shape[1]):
            df_dict[f'covariate_{i}'] = covariates[:, i]

        return pd.DataFrame(df_dict)

    def _validate_vif(self, X: pd.DataFrame, covariate_cols: List[str]) -> dict:
        """
        Calculate VIF (Variance Inflation Factor) for covariates.

        VIF > 10 indicates multicollinearity.

        Returns
        -------
        dict
            VIF information
        """
        vif_info = {}

        try:
            # Calculate VIF for each covariate
            vif_values = {}
            for i, col in enumerate(covariate_cols):
                if col in X.columns:
                    # Get column index (skip const)
                    col_idx = list(X.columns).index(col)
                    vif = variance_inflation_factor(X.values, col_idx)
                    vif_values[col] = vif

            max_vif = max(vif_values.values()) if vif_values else 0

            vif_info['vif_values'] = vif_values
            vif_info['max_vif'] = max_vif

            # Warn if multicollinearity detected
            if max_vif > 10:
                warnings.warn(
                    f"Multicollinearity detected (max VIF={max_vif:.1f}). "
                    f"Consider removing correlated covariates.",
                    UserWarning
                )

        except Exception as e:
            self.logger.warning(f"Could not calculate VIF: {e}")

        return vif_info

    def _check_interactions(self, df: pd.DataFrame, covariate_cols: List[str]) -> dict:
        """
        Check for heterogeneous treatment effects (interactions).

        Fits model with interaction terms: treatment * covariates

        Returns
        -------
        dict
            Interaction information
        """
        interaction_info = {}

        try:
            # Build design matrix with interactions
            X_main = df[['treatment'] + covariate_cols]

            # Add interaction terms
            for cov in covariate_cols:
                df[f'interaction_{cov}'] = df['treatment'] * df[cov]

            interaction_cols = [f'interaction_{cov}' for cov in covariate_cols]
            X_full = sm.add_constant(df[['treatment'] + covariate_cols + interaction_cols])

            y = df['outcome_transformed'] if 'outcome_transformed' in df.columns else df['outcome']

            # Fit with cluster SE
            model = sm.OLS(y, X_full)
            results = model.fit(cov_type='cluster', cov_kwds={'groups': df['cluster'].values})

            # Check significance of interaction terms
            significant_interactions = []
            for int_col in interaction_cols:
                if int_col in results.pvalues:
                    p = results.pvalues[int_col]
                    if p < self.interaction_alpha:
                        significant_interactions.append((int_col, p))

            interaction_info['has_significant_interactions'] = len(significant_interactions) > 0
            interaction_info['significant_interactions'] = significant_interactions

            if significant_interactions:
                warnings.warn(
                    f"Heterogeneous treatment effects detected. "
                    f"Treatment effect varies by: {[x[0] for x in significant_interactions]}",
                    UserWarning
                )

        except Exception as e:
            self.logger.warning(f"Could not check interactions: {e}")

        return interaction_info

    def __repr__(self) -> str:
        return (
            f"ClusteredAncovaTest("
            f"alpha={self.alpha}, "
            f"test_type='{self.test_type}', "
            f"min_clusters={self.min_clusters})"
        )


# Alias for practitioners who prefer "OLS" terminology
ClusteredOLSTest = ClusteredAncovaTest
