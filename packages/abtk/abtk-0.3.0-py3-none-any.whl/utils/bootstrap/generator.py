"""
Bootstrap sample generator.

This module provides utilities for generating bootstrap samples with support for:
- Stratified bootstrap (for categorical balance)
- Stratum weights (for balancing across groups)
- Covariate bootstrap (for post-normalization methods)

Bootstrap is a resampling technique used in:
- Hypothesis testing (bootstrap tests)
- Confidence interval estimation
- Power analysis and simulations
- Variance estimation
"""

from typing import Optional, Dict, Any, Tuple
import numpy as np

from core.data_types import SampleData


def generate_bootstrap_samples(
    sample: SampleData,
    n_samples: int = 1000,
    sample_size: Optional[int] = None,
    stratify: bool = False,
    bootstrap_covariates: bool = False,
    stratum_weights: Optional[Dict[Any, int]] = None,
    random_seed: Optional[int] = None
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Generate bootstrap samples from a SampleData object.

    Bootstrap resampling creates multiple samples by sampling with replacement
    from the original data. This is used for estimating sampling distributions,
    confidence intervals, and hypothesis testing.

    Parameters
    ----------
    sample : SampleData
        The sample data to bootstrap from
    n_samples : int, default=1000
        Number of bootstrap samples to generate
    sample_size : Optional[int], default=None
        Size of each bootstrap sample. If None, uses original sample size
    stratify : bool, default=False
        If True, performs stratified bootstrap to maintain stratum proportions.
        This is useful when there's categorical imbalance between groups.
        Requires sample.strata to be present.
    bootstrap_covariates : bool, default=False
        If True, also bootstrap covariate values (needed for post-normed bootstrap).
        Requires sample.covariates to be present.
    stratum_weights : Optional[Dict[Any, int]], default=None
        Manual stratum weights for stratified bootstrap.
        Keys are stratum values, values are sample sizes for each stratum.
        If None and stratify=True, uses proportional weights from original data.
    random_seed : Optional[int], default=None
        Random seed for reproducibility

    Returns
    -------
    tuple of (np.ndarray, Optional[np.ndarray])
        - Bootstrap samples array of shape (n_samples, sample_size)
        - Bootstrap covariate samples (if bootstrap_covariates=True), else None

    Raises
    ------
    ValueError
        If stratify=True but sample.strata is None
        If bootstrap_covariates=True but sample.covariates is None
        If stratum_weights don't match sample strata

    Examples
    --------
    >>> # Basic bootstrap
    >>> sample = SampleData(data=[1, 2, 3, 4, 5], name="Control")
    >>> boot_samples, _ = generate_bootstrap_samples(sample, n_samples=1000)
    >>> boot_samples.shape
    (1000, 5)

    >>> # Stratified bootstrap with strata
    >>> sample = SampleData(
    ...     data=[10, 20, 30, 40],
    ...     strata=['Mobile', 'Mobile', 'Desktop', 'Desktop'],
    ...     name="Control"
    ... )
    >>> boot_samples, _ = generate_bootstrap_samples(
    ...     sample, n_samples=1000, stratify=True
    ... )

    >>> # Bootstrap with covariates (for post-normed methods)
    >>> sample = SampleData(
    ...     data=[100, 110, 120],
    ...     covariates=[90, 95, 105],
    ...     name="Treatment"
    ... )
    >>> boot_data, boot_cov = generate_bootstrap_samples(
    ...     sample, n_samples=1000, bootstrap_covariates=True
    ... )

    Notes
    -----
    Stratified bootstrap is important when:
    - There's categorical imbalance between groups (e.g., 60% mobile in control, 45% in treatment)
    - Different strata have different baseline behavior
    - You want to maintain stratum proportions in bootstrap samples

    The stratified bootstrap works by:
    1. Splitting data by strata
    2. Sampling each stratum independently
    3. Combining samples to maintain overall stratum proportions
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Determine sample size
    if sample_size is None:
        sample_size = sample.sample_size

    # Validate parameters
    if stratify and sample.strata is None:
        raise ValueError(
            "Stratified bootstrap requires strata. "
            "Please provide strata when creating SampleData."
        )

    if bootstrap_covariates and sample.covariates is None:
        raise ValueError(
            "Bootstrap covariates requires covariates to be present in SampleData. "
            "Set bootstrap_covariates=False or provide covariates."
        )

    # Calculate stratum weights if stratified
    if stratify:
        if stratum_weights is None:
            stratum_weights = _calculate_stratum_weights(sample, sample_size)
        else:
            # Validate provided weights
            _validate_stratum_weights(sample, stratum_weights)

    # Generate bootstrap samples
    if stratify:
        boot_data, boot_cov = _generate_stratified_bootstrap(
            sample=sample,
            n_samples=n_samples,
            stratum_weights=stratum_weights,
            bootstrap_covariates=bootstrap_covariates
        )
    else:
        boot_data, boot_cov = _generate_simple_bootstrap(
            sample=sample,
            n_samples=n_samples,
            sample_size=sample_size,
            bootstrap_covariates=bootstrap_covariates
        )

    return boot_data, boot_cov


def _calculate_stratum_weights(sample: SampleData, target_size: int) -> Dict[Any, int]:
    """
    Calculate proportional stratum weights based on original data.

    Parameters
    ----------
    sample : SampleData
        Sample with strata
    target_size : int
        Target total sample size

    Returns
    -------
    Dict[Any, int]
        Dictionary mapping stratum -> sample size for that stratum
    """
    unique_strata, counts = np.unique(sample.strata, return_counts=True)
    proportions = counts / sample.sample_size

    stratum_weights = {}
    for stratum, proportion in zip(unique_strata, proportions):
        stratum_weights[stratum] = int(target_size * proportion)

    return stratum_weights


def _validate_stratum_weights(sample: SampleData, stratum_weights: Dict[Any, int]) -> None:
    """
    Validate that stratum_weights match sample strata.

    Parameters
    ----------
    sample : SampleData
        Sample with strata
    stratum_weights : Dict[Any, int]
        Provided stratum weights

    Raises
    ------
    ValueError
        If strata in weights don't match sample strata
    """
    sample_strata = set(sample.strata)
    weight_strata = set(stratum_weights.keys())

    if sample_strata != weight_strata:
        raise ValueError(
            f"Stratum weights keys {weight_strata} don't match "
            f"sample strata {sample_strata}"
        )


def _generate_simple_bootstrap(
    sample: SampleData,
    n_samples: int,
    sample_size: int,
    bootstrap_covariates: bool
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Generate simple (non-stratified) bootstrap samples.

    Parameters
    ----------
    sample : SampleData
        Sample to bootstrap from
    n_samples : int
        Number of bootstrap samples
    sample_size : int
        Size of each bootstrap sample
    bootstrap_covariates : bool
        Whether to bootstrap covariates

    Returns
    -------
    tuple of (np.ndarray, Optional[np.ndarray])
        Bootstrap data and optional bootstrap covariates
    """
    # Generate random indices with replacement
    indices = np.random.randint(0, sample.sample_size, size=(n_samples, sample_size))

    # Bootstrap data
    boot_data = sample.data[indices]

    # Bootstrap covariates if requested
    boot_cov = None
    if bootstrap_covariates:
        if sample.covariates.ndim == 1:
            boot_cov = sample.covariates[indices]
        else:
            # For 2D covariates, bootstrap along first axis
            boot_cov = sample.covariates[indices, :]

    return boot_data, boot_cov


def _generate_stratified_bootstrap(
    sample: SampleData,
    n_samples: int,
    stratum_weights: Dict[Any, int],
    bootstrap_covariates: bool
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Generate stratified bootstrap samples.

    Stratified bootstrap maintains stratum proportions by sampling
    each stratum independently according to specified weights.

    Parameters
    ----------
    sample : SampleData
        Sample to bootstrap from
    n_samples : int
        Number of bootstrap samples
    stratum_weights : Dict[Any, int]
        Stratum -> sample size mapping
    bootstrap_covariates : bool
        Whether to bootstrap covariates

    Returns
    -------
    tuple of (np.ndarray, Optional[np.ndarray])
        Bootstrap data and optional bootstrap covariates
    """
    total_size = sum(stratum_weights.values())

    # Initialize arrays
    boot_data = np.empty((n_samples, total_size), dtype=sample.data.dtype)

    boot_cov = None
    if bootstrap_covariates:
        if sample.covariates.ndim == 1:
            boot_cov = np.empty((n_samples, total_size), dtype=sample.covariates.dtype)
        else:
            # For 2D covariates
            boot_cov = np.empty((n_samples, total_size, sample.covariates.shape[1]), dtype=sample.covariates.dtype)

    # Sample each stratum independently
    start_idx = 0
    for stratum, stratum_size in stratum_weights.items():
        # Get data for this stratum
        stratum_mask = sample.strata == stratum
        stratum_data = sample.data[stratum_mask]

        if len(stratum_data) == 0:
            raise ValueError(f"No data found for stratum '{stratum}'")

        # Generate bootstrap indices for this stratum
        indices = np.random.randint(0, len(stratum_data), size=(n_samples, stratum_size))

        # Fill bootstrap arrays
        end_idx = start_idx + stratum_size
        boot_data[:, start_idx:end_idx] = stratum_data[indices]

        if bootstrap_covariates:
            stratum_cov = sample.covariates[stratum_mask]
            if sample.covariates.ndim == 1:
                boot_cov[:, start_idx:end_idx] = stratum_cov[indices]
            else:
                boot_cov[:, start_idx:end_idx, :] = stratum_cov[indices, :]

        start_idx = end_idx

    return boot_data, boot_cov


def generate_paired_bootstrap_samples(
    sample1: SampleData,
    sample2: SampleData,
    n_samples: int = 1000,
    sample_size: Optional[int] = None,
    random_seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate paired bootstrap samples with synchronized resampling.

    For paired bootstrap, we need to resample PAIRS, not individual observations.
    This function ensures that the same paired_ids are selected in both samples.

    Parameters
    ----------
    sample1 : SampleData
        First sample (must have paired_ids)
    sample2 : SampleData
        Second sample (must have paired_ids)
    n_samples : int, default=1000
        Number of bootstrap samples to generate
    sample_size : Optional[int], default=None
        Number of pairs to sample. If None, uses number of common pairs.
    random_seed : Optional[int], default=None
        Random seed for reproducibility

    Returns
    -------
    tuple of (np.ndarray, np.ndarray)
        - Bootstrap samples for sample1 of shape (n_samples, sample_size)
        - Bootstrap samples for sample2 of shape (n_samples, sample_size)

    Raises
    ------
    ValueError
        If samples don't have paired_ids or no common pairs found

    Examples
    --------
    >>> # Paired samples (e.g., matched pairs A/B test)
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
    >>> boot_control, boot_treatment = generate_paired_bootstrap_samples(
    ...     control, treatment, n_samples=1000
    ... )
    >>> # Both have same shape and correspond to same paired_ids

    Notes
    -----
    Paired bootstrap workflow:
    1. Find common paired_ids between samples
    2. For each bootstrap iteration, sample pairs WITH REPLACEMENT
    3. Use the SAME sampled pair indices for both samples
    4. This preserves the pairing structure

    This is critical for:
    - Matched pairs experiments (users matched by historical data)
    - Before/after measurements on same subjects
    - Any design where observations are naturally paired

    Example: If we sample pairs [1, 3, 3, 1], we get:
    - sample1: observations with paired_id in [1, 3, 3, 1]
    - sample2: observations with paired_id in [1, 3, 3, 1]
    - Pairing is preserved!
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Validate paired_ids
    if sample1.paired_ids is None or sample2.paired_ids is None:
        raise ValueError(
            "Paired bootstrap requires both samples to have paired_ids. "
            "Please provide paired_ids when creating SampleData."
        )

    # Find common paired_ids
    common_ids = np.intersect1d(sample1.paired_ids, sample2.paired_ids)

    if len(common_ids) == 0:
        raise ValueError(
            "No common paired_ids found between samples. "
            "Cannot perform paired bootstrap."
        )

    # Determine sample size
    if sample_size is None:
        sample_size = len(common_ids)

    # Get data aligned by paired_ids for both samples
    # (similar to what we do in paired t-test)
    mask1 = np.isin(sample1.paired_ids, common_ids)
    mask2 = np.isin(sample2.paired_ids, common_ids)

    sort_idx1 = np.argsort(sample1.paired_ids[mask1])
    sort_idx2 = np.argsort(sample2.paired_ids[mask2])

    data1_aligned = sample1.data[mask1][sort_idx1]
    data2_aligned = sample2.data[mask2][sort_idx2]

    ids1_sorted = sample1.paired_ids[mask1][sort_idx1]
    ids2_sorted = sample2.paired_ids[mask2][sort_idx2]

    # Verify alignment
    if not np.array_equal(ids1_sorted, ids2_sorted):
        raise ValueError("Failed to align samples by paired_ids")

    # Now we have aligned data where index i corresponds to the same pair in both samples
    n_pairs = len(common_ids)

    # Generate bootstrap samples by sampling PAIR INDICES with replacement
    # Key: We use the SAME indices for both samples to preserve pairing
    pair_indices = np.random.randint(0, n_pairs, size=(n_samples, sample_size))

    # Apply the same indices to both samples
    boot_data1 = data1_aligned[pair_indices]
    boot_data2 = data2_aligned[pair_indices]

    return boot_data1, boot_data2


def calculate_balanced_stratum_weights(
    sample1: SampleData,
    sample2: SampleData,
    weight_method: str = "min"
) -> Tuple[Dict[Any, int], Dict[Any, int]]:
    """
    Calculate balanced stratum weights for two samples.

    This is used in bootstrap tests to ensure both groups are bootstrapped
    with the same stratum proportions, reducing bias from categorical imbalance.

    Parameters
    ----------
    sample1 : SampleData
        First sample (must have strata)
    sample2 : SampleData
        Second sample (must have strata)
    weight_method : {'min', 'mean'}, default='min'
        Method for combining stratum counts:
        - 'min': Use minimum count across samples (conservative)
        - 'mean': Use average count across samples (balanced)

    Returns
    -------
    tuple of (Dict[Any, int], Dict[Any, int])
        Stratum weights for sample1 and sample2

    Raises
    ------
    ValueError
        If samples don't have strata or weight_method is invalid

    Examples
    --------
    >>> sample1 = SampleData(
    ...     data=[1, 2, 3, 4, 5, 6],
    ...     strata=['A', 'A', 'A', 'B', 'B', 'B'],
    ...     name="Control"
    ... )
    >>> sample2 = SampleData(
    ...     data=[7, 8, 9, 10],
    ...     strata=['A', 'B', 'B', 'B'],
    ...     name="Treatment"
    ... )
    >>> weights1, weights2 = calculate_balanced_stratum_weights(
    ...     sample1, sample2, weight_method="min"
    ... )
    >>> # With min: A has min(3,1)=1, B has min(3,3)=3
    >>> # Normalized and applied to each sample size
    """
    if sample1.strata is None or sample2.strata is None:
        raise ValueError("Both samples must have strata for balanced weighting")

    if weight_method not in ["min", "mean"]:
        raise ValueError(f"Invalid weight_method '{weight_method}'. Use 'min' or 'mean'")

    # Get stratum counts
    unique1, counts1 = np.unique(sample1.strata, return_counts=True)
    unique2, counts2 = np.unique(sample2.strata, return_counts=True)

    weights1_dict = dict(zip(unique1, counts1))
    weights2_dict = dict(zip(unique2, counts2))

    # Get all strata
    all_strata = set(unique1) | set(unique2)

    # Calculate combined weights
    if weight_method == "min":
        combined_weights = {
            stratum: min(weights1_dict.get(stratum, 0), weights2_dict.get(stratum, 0))
            for stratum in all_strata
        }
    else:  # mean
        combined_weights = {
            stratum: (weights1_dict.get(stratum, 0) + weights2_dict.get(stratum, 0)) / 2
            for stratum in all_strata
        }

    # Normalize weights to sum to 1
    total_weight = sum(combined_weights.values())
    if total_weight == 0:
        raise ValueError("No overlapping strata between samples")

    normalized_weights = {stratum: w / total_weight for stratum, w in combined_weights.items()}

    # Apply to each sample size
    stratum_weights1 = {
        stratum: int(sample1.sample_size * normalized_weights.get(stratum, 0))
        for stratum in unique1
    }
    stratum_weights2 = {
        stratum: int(sample2.sample_size * normalized_weights.get(stratum, 0))
        for stratum in unique2
    }

    return stratum_weights1, stratum_weights2


def generate_cluster_bootstrap_samples(
    sample: SampleData,
    n_samples: int = 1000,
    random_seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate cluster bootstrap samples by resampling clusters (not individuals).

    In cluster bootstrap, we resample CLUSTERS with replacement, not individual
    observations. This preserves within-cluster correlation structure and is
    appropriate for cluster-randomized experiments.

    Parameters
    ----------
    sample : SampleData
        The sample data to bootstrap from (must have clusters attribute)
    n_samples : int, default=1000
        Number of bootstrap samples to generate
    random_seed : Optional[int], default=None
        Random seed for reproducibility

    Returns
    -------
    np.ndarray
        Bootstrap statistics array of shape (n_samples,) containing the statistic
        (mean) for each bootstrap sample

    Raises
    ------
    ValueError
        If sample.clusters is None

    Examples
    --------
    >>> # Cluster-randomized experiment: 5 cities
    >>> sample = SampleData(
    ...     data=[100, 105, 110, 95, 98, 102, 108, 112],
    ...     clusters=[1, 1, 1, 2, 2, 3, 3, 3],  # 3 clusters
    ...     name="Treatment"
    ... )
    >>> boot_stats = generate_cluster_bootstrap_samples(sample, n_samples=1000)
    >>> boot_stats.shape
    (1000,)

    Notes
    -----
    Cluster bootstrap algorithm:
    1. Identify unique clusters in the sample
    2. For each bootstrap iteration:
       a. Randomly sample clusters WITH REPLACEMENT
       b. For each sampled cluster, take ALL observations from that cluster
       c. Calculate statistic (mean) on combined observations
    3. Return array of bootstrap statistics

    **Why cluster bootstrap?**
    - Preserves within-cluster correlation (ICC)
    - Appropriate for cluster-randomized designs
    - More conservative than individual-level bootstrap when ICC > 0

    **Example:**
    Original data: Cluster 1 [100, 105], Cluster 2 [95, 98], Cluster 3 [102, 108]
    Bootstrap sample might be: [Cluster 1, Cluster 1, Cluster 3]
    → observations: [100, 105, 100, 105, 102, 108]

    **Comparison with individual bootstrap:**
    - Individual bootstrap: Resamples observations, breaks cluster structure
    - Cluster bootstrap: Resamples clusters, preserves cluster structure
    - Cluster bootstrap typically has wider CI (accounts for clustering)
    """
    if sample.clusters is None:
        raise ValueError(
            "Cluster bootstrap requires clusters attribute. "
            "Please provide clusters when creating SampleData."
        )

    if random_seed is not None:
        np.random.seed(random_seed)

    # Get unique clusters
    unique_clusters = np.unique(sample.clusters)
    n_clusters = len(unique_clusters)

    # Initialize array for bootstrap statistics
    boot_stats = np.empty(n_samples)

    # For each bootstrap iteration
    for i in range(n_samples):
        # Resample clusters WITH REPLACEMENT
        sampled_clusters = np.random.choice(
            unique_clusters,
            size=n_clusters,
            replace=True
        )

        # Collect all observations from sampled clusters
        boot_data = []
        for cluster_id in sampled_clusters:
            # Get all observations from this cluster
            cluster_mask = sample.clusters == cluster_id
            cluster_data = sample.data[cluster_mask]
            boot_data.extend(cluster_data)

        # Calculate statistic (mean) for this bootstrap sample
        boot_stats[i] = np.mean(boot_data)

    return boot_stats
