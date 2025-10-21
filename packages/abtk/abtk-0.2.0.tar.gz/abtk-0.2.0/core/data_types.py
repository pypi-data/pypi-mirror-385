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
                 cluster_ids: Union[list, np.ndarray] = None,
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

        # Cluster ids (for cluster-randomized experiments - future)
        self.cluster_ids = None
        self.n_clusters = 0

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

        if cluster_ids is not None:
            self._set_cluster_ids(cluster_ids)

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

    def _set_cluster_ids(self, cluster_ids):
        """
        Sets cluster IDs for cluster-randomized experiments.

        Cluster IDs identify which cluster each observation belongs to.
        Can be 1D (simple clusters) or 2D (hierarchical clusters).

        Examples:
        - 1D: [school_id, school_id, ...]
        - 2D: [[country_id, city_id, school_id], ...]

        Note: Cluster-randomized analysis is not yet implemented.
        This is reserved for future use.
        """
        cluster_ids = np.asarray(cluster_ids)

        # Validate dimensions
        if cluster_ids.ndim == 1:
            # Simple clusters
            if len(cluster_ids) != self.sample_size:
                raise ValueError('Data and cluster_ids lengths do not match')
            self.cluster_ids = cluster_ids
            self.n_clusters = len(np.unique(cluster_ids))
        elif cluster_ids.ndim == 2:
            # Hierarchical clusters
            if cluster_ids.shape[0] != self.sample_size:
                raise ValueError('Data and cluster_ids lengths do not match')
            self.cluster_ids = cluster_ids
            # Count unique combinations for hierarchical clusters
            unique_clusters = np.unique(cluster_ids, axis=0)
            self.n_clusters = len(unique_clusters)
        else:
            raise ValueError('cluster_ids must be 1D or 2D array')

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