import numpy as np
from typing import Union, Optional, Dict

class ProportionData:
    def __init__(self, successes: int, nobs: int, name: str = None, metadata: Dict = None):
        self.successes = successes
        self.nobs = nobs
        self.name = name
        self.prop = successes / nobs
        self.std = np.sqrt(self.prop * (1 - self.prop) / nobs)
        self.metadata = metadata
        
class SampleData:
    def __init__(self,
                 data: Union[list, np.ndarray],
                 covariates: Union[list, np.ndarray] = None,
                 strata: Union[list, np.ndarray] = None,
                 paired_ids: Union[list, np.ndarray] = None,
                 clusters: Union[list, np.ndarray] = None,
                 name: str = None,
                 metadata: Dict = None):

        if not isinstance(data, (list, np.ndarray)):
            raise ValueError('data must be a list or numpy array')

        # Main data
        self.data = np.array(data)
        self.sample_size = len(self.data)
        self.mean = np.mean(self.data)
        self.std_dev = np.std(self.data)
        self.variance = np.var(self.data)
        self.name = name
        self.metadata = metadata

        # Paired ids (for paired tests)
        self.paired_ids = None

        # Strata (for stratified bootstrap)
        self.strata = None
        self.strata_proportions = None

        # Clusters (for cluster-randomized experiments)
        self.clusters = None
        self.n_clusters = 0
        self._cluster_sizes = {}

        # Covariate(s) - universal feature
        self.covariates = None  # always 2D array (n_samples, n_covariates)
        self.n_covs = 0
        self.cov_means = None
        self.cov_stds = None
        self.cov_variances = None
        self.cov_corr_matrix = None  # correlations between data and covariates

        if paired_ids is not None:
            self._set_paired_ids(paired_ids)

        if strata is not None:
            self._set_strata(strata)

        if clusters is not None:
            self._set_clusters(clusters)

        if covariates is not None:
            self._set_covariates(covariates)

    def _set_paired_ids(self, paired_ids):
        """
        Sets paired IDs for matched observations.

        Paired IDs identify which observations are matched across samples.
        For example, in a before/after study, the same subject would have
        the same paired_id in both samples.
        """
        if len(paired_ids) != self.sample_size:
            raise ValueError('Data and paired_ids lengths do not match')
        self.paired_ids = np.array(paired_ids)

    def _set_strata(self, strata):
        """
        Sets strata for stratified sampling/bootstrap.

        Strata are used in stratified bootstrap to preserve the proportion
        of different subgroups (e.g., mobile/desktop, US/EU) in resamples.
        """
        if len(strata) != self.sample_size:
            raise ValueError('Data and strata lengths do not match')
        self.strata = np.array(strata)

        unique_strata, strata_counts = np.unique(self.strata, return_counts=True)
        self.strata_proportions = dict(zip(unique_strata, strata_counts))

    def _set_clusters(self, clusters):
        """
        Sets cluster assignments for cluster-randomized experiments.

        Clusters identify which cluster each observation belongs to.
        Can be 1D (simple clusters) or 2D (hierarchical/nested clusters).

        Examples:
        - 1D: [1, 1, 2, 2, 3, 3] - simple clustering (e.g., school_id)
        - 2D: [[1,1], [1,2], [2,1], [2,2]] - nested (e.g., [city_id, store_id])

        Args:
            clusters: 1D or 2D array of cluster assignments

        Raises:
            ValueError: If validation fails
        """
        clusters = np.asarray(clusters)

        # Check for missing values
        if np.any(np.isnan(clusters.astype(float, errors='ignore'))):
            raise ValueError('clusters cannot contain NaN values')

        # Validate dimensions
        if clusters.ndim == 1:
            # Simple clusters (1D)
            if len(clusters) != self.sample_size:
                raise ValueError(f'Data length ({self.sample_size}) and clusters length ({len(clusters)}) do not match')

            self.clusters = clusters
            unique_clusters = np.unique(clusters)
            self.n_clusters = len(unique_clusters)

            # Calculate cluster sizes
            self._cluster_sizes = {
                cluster: np.sum(clusters == cluster)
                for cluster in unique_clusters
            }

        elif clusters.ndim == 2:
            # Hierarchical clusters (2D) - for v0.4.0+
            if clusters.shape[0] != self.sample_size:
                raise ValueError(f'Data length ({self.sample_size}) and clusters rows ({clusters.shape[0]}) do not match')

            self.clusters = clusters
            # Count unique combinations for hierarchical clusters
            unique_clusters = np.unique(clusters, axis=0)
            self.n_clusters = len(unique_clusters)

            # Calculate cluster sizes (for hierarchical, count by unique tuple)
            self._cluster_sizes = {}
            for cluster_tuple in unique_clusters:
                mask = np.all(clusters == cluster_tuple, axis=1)
                count = np.sum(mask)
                cluster_key = tuple(cluster_tuple)
                self._cluster_sizes[cluster_key] = count
        else:
            raise ValueError('clusters must be 1D or 2D array')

        # Validation warnings
        import warnings

        # Warn if too few clusters
        if self.n_clusters < 5:
            warnings.warn(
                f'Only {self.n_clusters} clusters detected. Cluster-randomized experiments '
                f'typically require at least 5-10 clusters per group for reliable inference.',
                UserWarning
            )

        # Warn if any cluster has size 1
        min_cluster_size = min(self._cluster_sizes.values())
        if min_cluster_size == 1:
            warnings.warn(
                f'Some clusters have only 1 observation. This may lead to unstable estimates.',
                UserWarning
            )

    def _set_covariates(self, covariates):
        """
        Sets covariates. Accepts either one (1D) or multiple (2D) covariates.
        """
        covariates = np.array(covariates)
        
        # Convert to 2D format if needed
        if covariates.ndim == 1:
            covariates = covariates.reshape(-1, 1)
        elif covariates.ndim != 2:
            raise ValueError('Covariate must be 1D or 2D array')
        
        if covariates.shape[0] != self.sample_size:
            raise ValueError('Data and covariates lengths do not match')
        
        self.covariates = covariates
        self.n_covs = covariates.shape[1]
        
        # Calculate statistics for each covariate
        self.cov_means = np.mean(covariates, axis=0)
        self.cov_stds = np.std(covariates, axis=0)
        self.cov_variances = np.var(covariates, axis=0)
        
        # Correlation between data and each covariate
        self.cov_corr_matrix = np.array([
            np.corrcoef(self.data, covariates[:, i])[0, 1] 
            for i in range(self.n_covs)
        ])
    
    # Convenient methods for backward compatibility
    @property
    def cov_mean(self):
        """For backward compatibility - returns the mean of the first covariate"""
        return self.cov_means[0] if self.n_covs > 0 else None
    
    @property
    def cov_std(self):
        """For backward compatibility - returns the std of the first covariate"""
        return self.cov_stds[0] if self.n_covs > 0 else None
    
    @property
    def cov_variance(self):
        """For backward compatibility - returns the variance of the first covariate"""
        return self.cov_variances[0] if self.n_covs > 0 else None
    
    @property
    def cov_corr_coef(self):
        """For backward compatibility - returns the correlation with the first covariate"""
        return self.cov_corr_matrix[0] if self.n_covs > 0 else None

    # Cluster helper methods
    def get_cluster_sizes(self):
        """
        Get sizes of all clusters.

        Returns:
            dict: Dictionary mapping cluster -> cluster_size
                  For 1D clusters: {cluster: size}
                  For 2D clusters: {(cluster_tuple): size}

        Raises:
            ValueError: If clusters not set

        Example:
            >>> sample = SampleData(data=[1,2,3,4,5,6], clusters=[1,1,2,2,3,3])
            >>> sample.get_cluster_sizes()
            {1: 2, 2: 2, 3: 2}
        """
        if self.clusters is None:
            raise ValueError('clusters not set for this sample')
        return self._cluster_sizes.copy()

    def get_cluster_size_stats(self):
        """
        Get statistics about cluster sizes.

        Returns:
            dict: Dictionary with keys:
                - 'mean': Mean cluster size
                - 'std': Standard deviation of cluster sizes
                - 'min': Minimum cluster size
                - 'max': Maximum cluster size
                - 'cv': Coefficient of variation (std/mean)

        Raises:
            ValueError: If clusters not set

        Example:
            >>> sample = SampleData(data=[1,2,3,4,5,6,7], clusters=[1,1,2,2,2,3,3])
            >>> stats = sample.get_cluster_size_stats()
            >>> stats['mean']  # (2 + 3 + 2) / 3 = 2.33
            2.33...
        """
        if self.clusters is None:
            raise ValueError('clusters not set for this sample')

        sizes = np.array(list(self._cluster_sizes.values()))

        return {
            'mean': np.mean(sizes),
            'std': np.std(sizes),
            'min': np.min(sizes),
            'max': np.max(sizes),
            'cv': np.std(sizes) / np.mean(sizes) if np.mean(sizes) > 0 else 0
        }

    def get_cluster_data(self, cluster):
        """
        Get all observations from a specific cluster.

        Args:
            cluster: Cluster identifier (scalar for 1D, tuple for 2D)

        Returns:
            np.ndarray: Array of observations from that cluster

        Raises:
            ValueError: If clusters not set or cluster not found

        Example:
            >>> sample = SampleData(data=[10,20,30,40], clusters=[1,1,2,2])
            >>> sample.get_cluster_data(1)
            array([10, 20])
            >>> sample.get_cluster_data(2)
            array([30, 40])
        """
        if self.clusters is None:
            raise ValueError('clusters not set for this sample')

        if self.clusters.ndim == 1:
            # Simple 1D clusters
            mask = self.clusters == cluster
        elif self.clusters.ndim == 2:
            # Hierarchical 2D clusters
            if not isinstance(cluster, (tuple, list, np.ndarray)):
                raise ValueError('For 2D clusters, cluster must be a tuple/list/array')
            cluster = np.asarray(cluster)
            mask = np.all(self.clusters == cluster, axis=1)
        else:
            raise ValueError('Invalid clusters dimensions')

        cluster_data = self.data[mask]

        if len(cluster_data) == 0:
            raise ValueError(f'Cluster {cluster} not found in data')

        return cluster_data

    @property
    def cluster_size_mean(self):
        """Mean cluster size (property for convenience)"""
        if self.clusters is None:
            return None
        return self.get_cluster_size_stats()['mean']

    @property
    def cluster_size_std(self):
        """Standard deviation of cluster sizes (property for convenience)"""
        if self.clusters is None:
            return None
        return self.get_cluster_size_stats()['std']

    @property
    def cluster_size_cv(self):
        """Coefficient of variation of cluster sizes (property for convenience)"""
        if self.clusters is None:
            return None
        return self.get_cluster_size_stats()['cv']