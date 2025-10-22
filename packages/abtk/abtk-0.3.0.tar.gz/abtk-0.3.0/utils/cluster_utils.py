"""
Utilities for cluster-randomized experiments.

This module provides functions for:
- Calculating Intra-Class Correlation (ICC)
- Calculating design effect
- Validating cluster designs
- Cluster-robust standard errors
"""

import numpy as np
import warnings
from typing import Dict, Tuple, Optional, Union
from core.data_types import SampleData


def calculate_icc(
    data: np.ndarray,
    clusters: np.ndarray,
    method: str = "anova"
) -> float:
    """
    Calculate Intra-Class Correlation (ICC) for clustered data.

    ICC measures the proportion of total variance that is between clusters.
    Higher ICC means observations within clusters are more similar.

    ICC = 0: No clustering effect (observations independent)
    ICC > 0: Positive clustering (observations within cluster more similar)
    ICC < 0: Negative clustering (rare, observations within cluster more different)

    Args:
        data: 1D array of observations
        clusters: 1D array of cluster assignments (same length as data)
        method: Method for ICC calculation:
            - "anova": One-way ANOVA method (default, most common)
            - "variance": Variance components method

    Returns:
        float: ICC value (typically between 0 and 1)

    Raises:
        ValueError: If inputs are invalid

    Example:
        >>> data = np.array([10, 12, 30, 32, 50, 52])
        >>> clusters = np.array([1, 1, 2, 2, 3, 3])
        >>> icc = calculate_icc(data, clusters)
        >>> print(f"ICC: {icc:.3f}")
        ICC: 0.971

    References:
        - Donner & Klar (2000). Design and Analysis of Cluster Randomization Trials.
        - Eldridge et al. (2009). Internal and external validity of cluster randomised trials.
    """
    data = np.asarray(data)
    clusters = np.asarray(clusters)

    if len(data) != len(clusters):
        raise ValueError(f"data and clusters must have same length (got {len(data)} and {len(clusters)})")

    if len(data) == 0:
        raise ValueError("data cannot be empty")

    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    if n_clusters < 2:
        raise ValueError(f"Need at least 2 clusters for ICC calculation (got {n_clusters})")

    if method == "anova":
        # One-way ANOVA method (most common)

        # Grand mean
        grand_mean = np.mean(data)

        # Between-cluster sum of squares
        ss_between = 0
        ss_within = 0
        total_n = 0

        cluster_means = []
        cluster_sizes = []

        for cluster in unique_clusters:
            cluster_data = data[clusters == cluster]
            cluster_size = len(cluster_data)
            cluster_mean = np.mean(cluster_data)

            cluster_means.append(cluster_mean)
            cluster_sizes.append(cluster_size)

            # Between-cluster SS
            ss_between += cluster_size * (cluster_mean - grand_mean) ** 2

            # Within-cluster SS
            ss_within += np.sum((cluster_data - cluster_mean) ** 2)

            total_n += cluster_size

        # Degrees of freedom
        df_between = n_clusters - 1
        df_within = total_n - n_clusters

        # Mean squares
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 0

        # Average cluster size (accounting for unbalanced clusters)
        cluster_sizes = np.array(cluster_sizes)
        n0 = (total_n - np.sum(cluster_sizes**2) / total_n) / (n_clusters - 1)

        # ICC formula from ANOVA
        if ms_within == 0:
            # Perfect clustering (all variance between clusters)
            icc = 1.0
        else:
            icc = (ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within)

        # ICC can be negative (indicates less similarity within clusters than between)
        # but usually we expect ICC >= 0

        return float(icc)

    elif method == "variance":
        # Variance components method

        total_var = np.var(data, ddof=1)

        # Within-cluster variance
        within_var = 0
        total_n = 0

        for cluster in unique_clusters:
            cluster_data = data[clusters == cluster]
            if len(cluster_data) > 1:
                within_var += np.var(cluster_data, ddof=1) * len(cluster_data)
                total_n += len(cluster_data)

        within_var = within_var / total_n if total_n > 0 else 0

        # Between-cluster variance
        between_var = total_var - within_var

        # ICC
        if total_var == 0:
            icc = 0.0
        else:
            icc = between_var / total_var

        return float(icc)

    else:
        raise ValueError(f"Unknown method: {method}. Use 'anova' or 'variance'")


def calculate_design_effect(
    cluster_sizes: Union[np.ndarray, list, Dict],
    icc: float
) -> float:
    """
    Calculate design effect for cluster-randomized design.

    Design effect (DE) quantifies the inflation of variance due to clustering.

    DE = 1: No clustering effect (same as individual randomization)
    DE > 1: Clustering increases variance (need larger sample size)
    DE < 1: Rare, clustering decreases variance (can happen with negative ICC)

    Formula: DE = 1 + (m̄ - 1) * ICC
    where m̄ is the average cluster size

    Args:
        cluster_sizes: Cluster sizes as:
            - np.ndarray or list of sizes [5, 6, 4, 5, ...]
            - dict mapping cluster_id -> size {1: 5, 2: 6, ...}
        icc: Intra-Class Correlation

    Returns:
        float: Design effect

    Example:
        >>> cluster_sizes = [10, 10, 10, 10]  # 4 clusters, 10 obs each
        >>> icc = 0.05
        >>> de = calculate_design_effect(cluster_sizes, icc)
        >>> print(f"Design Effect: {de:.2f}")
        Design Effect: 1.45

    Notes:
        - To get effective sample size: n_eff = n_total / DE
        - To get required sample size: n_required = n_individual * DE
        - Higher ICC or larger clusters → larger DE → need more total observations

    References:
        - Donner & Klar (2000), Chapter 3
        - Kerry & Bland (1998). Statistics notes: The intracluster correlation coefficient
    """
    # Convert to array of sizes
    if isinstance(cluster_sizes, dict):
        sizes = np.array(list(cluster_sizes.values()))
    else:
        sizes = np.asarray(cluster_sizes)

    if len(sizes) == 0:
        raise ValueError("cluster_sizes cannot be empty")

    # Average cluster size
    m_bar = np.mean(sizes)

    # Design effect formula
    de = 1 + (m_bar - 1) * icc

    return float(de)


def validate_clusters(
    sample1: SampleData,
    sample2: SampleData,
    min_clusters: int = 5,
    warn_cv: float = 0.5
) -> Dict:
    """
    Validate cluster design for two samples.

    Checks:
    1. Both samples have clusters set
    2. Minimum number of clusters per group
    3. Cluster size balance (via coefficient of variation)
    4. ICC calculation for each group
    5. Design effect calculation

    Args:
        sample1: First sample (e.g., control)
        sample2: Second sample (e.g., treatment)
        min_clusters: Minimum clusters per group (default: 5)
            - Raises error if < 3
            - Warns if < min_clusters
        warn_cv: CV threshold for cluster size imbalance warning (default: 0.5)

    Returns:
        dict: Validation results with keys:
            - 'valid': bool, overall validity
            - 'n_clusters_1': int, clusters in sample 1
            - 'n_clusters_2': int, clusters in sample 2
            - 'cluster_size_cv_1': float, CV for sample 1
            - 'cluster_size_cv_2': float, CV for sample 2
            - 'icc_1': float, ICC for sample 1
            - 'icc_2': float, ICC for sample 2
            - 'design_effect_1': float, DE for sample 1
            - 'design_effect_2': float, DE for sample 2
            - 'warnings': list of warning messages
            - 'errors': list of error messages

    Raises:
        ValueError: If critical validation fails (< 3 clusters per group)

    Example:
        >>> from core.data_types import SampleData
        >>> control = SampleData(data=[...], clusters=[...])
        >>> treatment = SampleData(data=[...], clusters=[...])
        >>> validation = validate_clusters(control, treatment, min_clusters=5)
        >>> if validation['valid']:
        >>>     print("Cluster design is valid!")
        >>> else:
        >>>     print("Issues:", validation['warnings'] + validation['errors'])
    """
    warnings_list = []
    errors_list = []
    valid = True

    # Check if clusters are set
    if sample1.clusters is None:
        errors_list.append("sample1 does not have clusters set")
        valid = False

    if sample2.clusters is None:
        errors_list.append("sample2 does not have clusters set")
        valid = False

    if not valid:
        return {
            'valid': False,
            'warnings': warnings_list,
            'errors': errors_list
        }

    # Get cluster counts
    n_clusters_1 = sample1.n_clusters
    n_clusters_2 = sample2.n_clusters

    # Critical: Must have at least 3 clusters per group
    if n_clusters_1 < 3:
        errors_list.append(
            f"sample1 has only {n_clusters_1} cluster(s). "
            f"Cluster-randomized experiments require at least 3 clusters per group."
        )
        valid = False

    if n_clusters_2 < 3:
        errors_list.append(
            f"sample2 has only {n_clusters_2} cluster(s). "
            f"Cluster-randomized experiments require at least 3 clusters per group."
        )
        valid = False

    # Warning: Recommend at least min_clusters (default 5)
    if n_clusters_1 < min_clusters:
        warnings_list.append(
            f"sample1 has only {n_clusters_1} cluster(s). "
            f"Recommended: at least {min_clusters} clusters per group for reliable inference."
        )

    if n_clusters_2 < min_clusters:
        warnings_list.append(
            f"sample2 has only {n_clusters_2} cluster(s). "
            f"Recommended: at least {min_clusters} clusters per group for reliable inference."
        )

    # Check cluster size balance (CV)
    cv_1 = sample1.cluster_size_cv
    cv_2 = sample2.cluster_size_cv

    if cv_1 > warn_cv:
        warnings_list.append(
            f"sample1 has unbalanced cluster sizes (CV={cv_1:.2f}). "
            f"Consider balancing cluster sizes for better precision."
        )

    if cv_2 > warn_cv:
        warnings_list.append(
            f"sample2 has unbalanced cluster sizes (CV={cv_2:.2f}). "
            f"Consider balancing cluster sizes for better precision."
        )

    # Calculate ICC for each group
    icc_1 = calculate_icc(sample1.data, sample1.clusters)
    icc_2 = calculate_icc(sample2.data, sample2.clusters)

    # Calculate design effect
    de_1 = calculate_design_effect(sample1.get_cluster_sizes(), icc_1)
    de_2 = calculate_design_effect(sample2.get_cluster_sizes(), icc_2)

    # Warning if high ICC (clustering strongly matters)
    if icc_1 > 0.15 or icc_2 > 0.15:
        warnings_list.append(
            f"High ICC detected (sample1: {icc_1:.3f}, sample2: {icc_2:.3f}). "
            f"Strong clustering effect - ensure sufficient clusters."
        )

    # Warning if very low ICC (clustering might not matter)
    if icc_1 < 0.01 and icc_2 < 0.01:
        warnings_list.append(
            f"Very low ICC detected (sample1: {icc_1:.3f}, sample2: {icc_2:.3f}). "
            f"Clustering effect is minimal - consider using regular (non-cluster) test."
        )

    return {
        'valid': valid,
        'n_clusters_1': n_clusters_1,
        'n_clusters_2': n_clusters_2,
        'cluster_size_cv_1': cv_1,
        'cluster_size_cv_2': cv_2,
        'icc_1': icc_1,
        'icc_2': icc_2,
        'design_effect_1': de_1,
        'design_effect_2': de_2,
        'warnings': warnings_list,
        'errors': errors_list
    }


def cluster_robust_se(
    residuals: np.ndarray,
    X: np.ndarray,
    clusters: np.ndarray
) -> np.ndarray:
    """
    Calculate cluster-robust standard errors (Liang-Zeger/Huber-White).

    This function computes sandwich estimator for cluster-robust variance.
    Used when statsmodels cluster SE is not available or for custom implementations.

    Note: For most use cases, prefer statsmodels OLS with cov_type='cluster'
    which handles this automatically.

    Args:
        residuals: Regression residuals (n x 1)
        X: Design matrix (n x k) including intercept
        clusters: Cluster assignments (n x 1)

    Returns:
        np.ndarray: Cluster-robust standard errors (k x 1)

    Example:
        >>> import statsmodels.api as sm
        >>> # Fit OLS
        >>> model = sm.OLS(y, X)
        >>> results = model.fit()
        >>>
        >>> # Get cluster-robust SE manually
        >>> residuals = results.resid
        >>> cluster_se = cluster_robust_se(residuals, X, clusters)
        >>>
        >>> # Compare with statsmodels (should match):
        >>> results_cluster = model.fit(cov_type='cluster', cov_kwds={'groups': clusters})
        >>> statsmodels_se = results_cluster.bse

    References:
        - Liang & Zeger (1986). Longitudinal data analysis using GEE
        - Cameron & Miller (2015). A Practitioner's Guide to Cluster-Robust Inference
    """
    residuals = np.asarray(residuals).flatten()
    X = np.asarray(X)
    clusters = np.asarray(clusters).flatten()

    n, k = X.shape

    if len(residuals) != n:
        raise ValueError(f"residuals length ({len(residuals)}) must match X rows ({n})")

    if len(clusters) != n:
        raise ValueError(f"clusters length ({len(clusters)}) must match X rows ({n})")

    # Bread: (X'X)^(-1)
    XtX_inv = np.linalg.inv(X.T @ X)

    # Meat: cluster-robust middle matrix
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    meat = np.zeros((k, k))

    for cluster in unique_clusters:
        # Get observations for this cluster
        cluster_mask = clusters == cluster
        X_cluster = X[cluster_mask]
        resid_cluster = residuals[cluster_mask]

        # Cluster contribution: X_c' * e_c * e_c' * X_c
        score = X_cluster.T @ resid_cluster  # (k x 1)
        meat += np.outer(score, score)

    # Small-sample adjustment (degrees of freedom correction)
    # Multiply by n_clusters / (n_clusters - 1) * (n - 1) / (n - k)
    dof_adjustment = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))

    # Sandwich: (X'X)^(-1) * meat * (X'X)^(-1)
    variance_matrix = dof_adjustment * XtX_inv @ meat @ XtX_inv

    # Standard errors are sqrt of diagonal
    cluster_se = np.sqrt(np.diag(variance_matrix))

    return cluster_se
