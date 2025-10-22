"""
Base class for cluster-randomized experiment tests.

This module provides the base class for all cluster-randomized statistical tests.
It handles cluster validation, ICC calculation, and design effect reporting.
"""

import warnings
from typing import Dict, Optional
import logging

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from utils.cluster_utils import validate_clusters, calculate_icc, calculate_design_effect


class BaseClusterTest(BaseTestProcessor):
    """
    Base class for cluster-randomized experiment tests.

    This class extends BaseTestProcessor with cluster-specific functionality:
    - Cluster validation (minimum clusters, balance, etc.)
    - ICC calculation and reporting
    - Design effect calculation
    - Cluster diagnostic warnings

    All cluster tests (ClusteredTTest, ClusteredAncovaTest, etc.) should
    inherit from this class.

    Parameters
    ----------
    test_name : str
        Name of the statistical test
    alpha : float, default=0.05
        Significance level for hypothesis testing
    min_clusters : int, default=5
        Minimum number of clusters per group
        - Error if < 3 clusters
        - Warning if < min_clusters
    warn_cv : float, default=0.5
        CV threshold for cluster size imbalance warning
        - Warns if coefficient of variation > warn_cv
    warn_icc_low : float, default=0.01
        ICC threshold below which clustering might not be needed
    warn_icc_high : float, default=0.15
        ICC threshold above which clustering strongly matters
    logger : logging.Logger, optional
        Logger instance for error reporting
    **test_params : dict
        Additional test-specific parameters

    Attributes
    ----------
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
    >>> # Concrete cluster test would inherit from this
    >>> control = SampleData(data=[10,20,30,40], clusters=[1,1,2,2])
    >>> treatment = SampleData(data=[15,25,35,45], clusters=[3,3,4,4])
    >>> test = ClusteredTTest(alpha=0.05, min_clusters=2)  # Concrete implementation
    >>> results = test.compare([control, treatment])

    Notes
    -----
    - This is an intermediate base class; concrete tests must still implement
      compare() and compare_samples()
    - Validation is performed automatically in _validate_clusters()
    - ICC and design effect are calculated for diagnostics
    """

    def __init__(
        self,
        test_name: str,
        alpha: float = 0.05,
        min_clusters: int = 5,
        warn_cv: float = 0.5,
        warn_icc_low: float = 0.01,
        warn_icc_high: float = 0.15,
        logger: logging.Logger = None,
        **test_params
    ):
        super().__init__(test_name, alpha, logger, **test_params)

        self.min_clusters = min_clusters
        self.warn_cv = warn_cv
        self.warn_icc_low = warn_icc_low
        self.warn_icc_high = warn_icc_high

        # Validate parameters
        if min_clusters < 3:
            raise ValueError(f"min_clusters must be >= 3 (got {min_clusters})")

        if warn_cv < 0:
            raise ValueError(f"warn_cv must be >= 0 (got {warn_cv})")

    def _validate_clusters(
        self,
        sample1: SampleData,
        sample2: SampleData
    ) -> Dict:
        """
        Validate cluster design for two samples.

        Performs comprehensive validation including:
        - Both samples have clusters
        - Minimum number of clusters per group
        - Cluster size balance
        - ICC calculation
        - Design effect calculation

        Parameters
        ----------
        sample1 : SampleData
            First sample (e.g., control)
        sample2 : SampleData
            Second sample (e.g., treatment)

        Returns
        -------
        dict
            Validation results with keys:
            - 'valid': bool, overall validity
            - 'n_clusters_1', 'n_clusters_2': int
            - 'cluster_size_cv_1', 'cluster_size_cv_2': float
            - 'icc_1', 'icc_2': float
            - 'design_effect_1', 'design_effect_2': float
            - 'warnings': list of warning messages
            - 'errors': list of error messages

        Raises
        ------
        ValueError
            If critical validation fails (< 3 clusters, no clusters set)

        Examples
        --------
        >>> control = SampleData(data=[...], clusters=[...])
        >>> treatment = SampleData(data=[...], clusters=[...])
        >>> test = ClusteredTTest()
        >>> validation = test._validate_clusters(control, treatment)
        >>> if not validation['valid']:
        >>>     print(validation['errors'])
        """
        # Use utility function for validation
        validation = validate_clusters(
            sample1,
            sample2,
            min_clusters=self.min_clusters,
            warn_cv=self.warn_cv
        )

        # Raise error if critical validation failed
        if not validation['valid']:
            error_msg = '; '.join(validation['errors'])
            raise ValueError(f"Cluster validation failed: {error_msg}")

        # Emit warnings
        for warning_msg in validation['warnings']:
            warnings.warn(warning_msg, UserWarning)

        # Additional ICC-specific warnings
        self._check_icc_warnings(validation['icc_1'], validation['icc_2'])

        return validation

    def _check_icc_warnings(self, icc_1: float, icc_2: float) -> None:
        """
        Check ICC values and emit appropriate warnings.

        Parameters
        ----------
        icc_1 : float
            ICC for sample 1
        icc_2 : float
            ICC for sample 2

        Notes
        -----
        Emits warnings for:
        - Very low ICC (< warn_icc_low): clustering might not be needed
        - High ICC (> warn_icc_high): strong clustering effect
        """
        # Very low ICC - clustering might not matter
        if icc_1 < self.warn_icc_low and icc_2 < self.warn_icc_low:
            warnings.warn(
                f"Very low ICC detected (sample1: {icc_1:.3f}, sample2: {icc_2:.3f}). "
                f"Clustering effect is minimal - consider using regular (non-cluster) test.",
                UserWarning
            )

        # High ICC - clustering strongly matters
        if icc_1 > self.warn_icc_high or icc_2 > self.warn_icc_high:
            warnings.warn(
                f"High ICC detected (sample1: {icc_1:.3f}, sample2: {icc_2:.3f}). "
                f"Strong clustering effect - ensure sufficient clusters for reliable inference.",
                UserWarning
            )

    def _create_cluster_diagnostics(self, validation: Dict) -> Dict:
        """
        Create cluster diagnostics dictionary for TestResult.method_params.

        This creates a standardized diagnostics dict that should be included
        in the method_params of TestResult for all cluster tests.

        Parameters
        ----------
        validation : dict
            Validation results from _validate_clusters()

        Returns
        -------
        dict
            Cluster diagnostics with keys:
            - 'n_clusters_control': int
            - 'n_clusters_treatment': int
            - 'cluster_size_cv_control': float
            - 'cluster_size_cv_treatment': float
            - 'icc_control': float
            - 'icc_treatment': float
            - 'design_effect_control': float
            - 'design_effect_treatment': float

        Examples
        --------
        >>> validation = test._validate_clusters(control, treatment)
        >>> diagnostics = test._create_cluster_diagnostics(validation)
        >>> method_params = {'test_statistic': ..., **diagnostics}
        """
        return {
            'n_clusters_control': validation['n_clusters_1'],
            'n_clusters_treatment': validation['n_clusters_2'],
            'cluster_size_cv_control': validation['cluster_size_cv_1'],
            'cluster_size_cv_treatment': validation['cluster_size_cv_2'],
            'icc_control': validation['icc_1'],
            'icc_treatment': validation['icc_2'],
            'design_effect_control': validation['design_effect_1'],
            'design_effect_treatment': validation['design_effect_2']
        }

    def _get_effective_sample_size(
        self,
        n_total: int,
        design_effect: float
    ) -> float:
        """
        Calculate effective sample size accounting for clustering.

        Effective sample size is reduced due to clustering:
        n_eff = n_total / design_effect

        Parameters
        ----------
        n_total : int
            Total number of observations
        design_effect : float
            Design effect from clustering

        Returns
        -------
        float
            Effective sample size

        Examples
        --------
        >>> # 100 observations, DE=2.0 → n_eff = 50
        >>> n_eff = test._get_effective_sample_size(100, 2.0)
        >>> print(n_eff)  # 50.0

        Notes
        -----
        - DE = 1.0: No clustering, n_eff = n_total
        - DE > 1.0: Clustering reduces effective sample size
        - Higher ICC or larger clusters → larger DE → smaller n_eff
        """
        if design_effect <= 0:
            raise ValueError(f"design_effect must be > 0 (got {design_effect})")

        return n_total / design_effect

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"test_name='{self.test_name}', "
            f"alpha={self.alpha}, "
            f"min_clusters={self.min_clusters})"
        )
