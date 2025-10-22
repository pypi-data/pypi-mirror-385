"""
Quantile Treatment Effect (QTE) analysis.

This module provides tools for analyzing treatment effects at different
quantiles of the distribution using bootstrap resampling.

Unlike standard tests that compare means, quantile analysis reveals:
- Where in the distribution the treatment effect occurs
- Whether effects are concentrated in tails or center
- Heterogeneous effects across the distribution
"""

from typing import List, Union
import numpy as np
import warnings
from copy import deepcopy
from itertools import combinations

from core.data_types import SampleData
from core.quantile_test_result import QuantileTestResult


class QuantileAnalyzer:
    """
    Quantile Treatment Effect (QTE) analyzer.

    Analyzes treatment effects at different quantiles of the distribution
    using any bootstrap test. Simply runs the bootstrap test multiple times
    with different quantile functions.

    This is useful for understanding:
    - Whether treatment affects all users equally
    - If effects are concentrated in high or low spenders
    - Heterogeneous treatment effects across distribution

    Parameters
    ----------
    test : BootstrapTest | PairedBootstrapTest | PostNormedBootstrapTest
        Initialized bootstrap test to use for quantile analysis.
        All test parameters (n_samples, stratify, etc.) will be used.
    quantiles : list of float, default=[0.25, 0.5, 0.75, 0.9, 0.95]
        Quantiles to analyze (each between 0 and 1).
        Default covers quartiles plus high quantiles where effects
        often differ.

    Attributes
    ----------
    test : Bootstrap test instance
        The underlying bootstrap test
    quantiles : list of float
        Quantiles being analyzed

    Examples
    --------
    >>> from tests.nonparametric import BootstrapTest
    >>> from utils.quantile_analysis import QuantileAnalyzer
    >>> import numpy as np
    >>>
    >>> # Data where effect is stronger for high-value users
    >>> control = SampleData(
    ...     data=np.random.exponential(100, 1000),
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=np.random.exponential(110, 1000),  # 10% higher
    ...     name="Treatment"
    ... )
    >>>
    >>> # Initialize bootstrap test
    >>> bootstrap = BootstrapTest(
    ...     alpha=0.05,
    ...     test_type="relative",
    ...     n_samples=10000
    ... )
    >>>
    >>> # Wrap in quantile analyzer
    >>> analyzer = QuantileAnalyzer(
    ...     test=bootstrap,
    ...     quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    ... )
    >>>
    >>> # Run analysis
    >>> results = analyzer.compare([control, treatment])
    >>> result = results[0]
    >>>
    >>> # View results
    >>> print(result.summary())
    >>> df = result.to_dataframe()
    >>> print(df)
    >>>
    >>> # Find where effects are significant
    >>> sig_quantiles = result.significant_quantiles()
    >>> print(f"Effects significant at: {sig_quantiles}")

    Notes
    -----
    Performance:
    - With n samples and q quantiles, runs n*(n-1)/2 * q bootstrap tests
    - Each test uses n_samples bootstrap resamples
    - For 4 samples and 5 quantiles: 6 pairs * 5 quantiles = 30 tests
    - Consider reducing n_samples or quantiles for large datasets

    Works with any bootstrap test:
    - BootstrapTest: Standard independent samples
    - PairedBootstrapTest: Matched pairs (preserves pairing)
    - PostNormedBootstrapTest: With covariate normalization

    All parameters from the bootstrap test are preserved:
    - stratify, weight_method (if applicable)
    - random_seed (for reproducibility)
    - test_type (relative/absolute)
    """

    def __init__(
        self,
        test: Union['BootstrapTest', 'PairedBootstrapTest', 'PostNormedBootstrapTest'],
        quantiles: List[float] = None
    ):
        # Import here to avoid circular imports
        from tests.nonparametric import (
            BootstrapTest,
            PairedBootstrapTest,
            PostNormedBootstrapTest
        )

        # Validate test type
        valid_tests = (BootstrapTest, PairedBootstrapTest, PostNormedBootstrapTest)
        if not isinstance(test, valid_tests):
            raise TypeError(
                f"test must be one of {[t.__name__ for t in valid_tests]}, "
                f"got {type(test).__name__}"
            )

        self.test = test

        # Default quantiles
        if quantiles is None:
            quantiles = [0.25, 0.5, 0.75, 0.9, 0.95]

        # Validate quantiles
        if not all(0 < q < 1 for q in quantiles):
            raise ValueError("All quantiles must be between 0 and 1")

        if len(quantiles) != len(set(quantiles)):
            raise ValueError("Duplicate quantiles found")

        self.quantiles = sorted(quantiles)

    def compare(self, samples: List[SampleData]) -> List[QuantileTestResult]:
        """
        Compare samples and compute quantile treatment effects.

        Performs pairwise quantile analysis for all sample pairs.
        For each pair and each quantile, runs the bootstrap test and
        collects results.

        Parameters
        ----------
        samples : List[SampleData]
            Samples to compare. All pairwise comparisons will be performed.

        Returns
        -------
        List[QuantileTestResult]
            One QuantileTestResult per pairwise comparison.
            For n samples, returns n*(n-1)/2 results.

        Warns
        -----
        UserWarning
            If total number of tests (pairs * quantiles) exceeds 50,
            warns about potential performance impact.

        Examples
        --------
        >>> # Compare 2 samples
        >>> results = analyzer.compare([control, treatment])
        >>> # Returns 1 result (1 pair)
        >>>
        >>> # Compare 4 samples
        >>> results = analyzer.compare([control, t1, t2, t3])
        >>> # Returns 6 results (6 pairs)
        >>> for result in results:
        ...     print(f"{result.name_1} vs {result.name_2}")
        ...     print(result.to_dataframe())
        """
        if not samples or len(samples) < 2:
            return []

        n_samples = len(samples)
        n_pairs = n_samples * (n_samples - 1) // 2
        n_tests = n_pairs * len(self.quantiles)

        # Warn if many tests
        if n_tests > 50:
            warnings.warn(
                f"Running {n_tests} bootstrap tests "
                f"({n_pairs} pairs × {len(self.quantiles)} quantiles). "
                f"This may take a while. Consider:\n"
                f"  - Reducing number of quantiles\n"
                f"  - Reducing n_samples in bootstrap test\n"
                f"  - Analyzing only specific pairs",
                UserWarning
            )

        results = []

        for sample1, sample2 in combinations(samples, 2):
            result = self._analyze_pair(sample1, sample2)
            results.append(result)

        return results

    def _analyze_pair(
        self,
        sample1: SampleData,
        sample2: SampleData
    ) -> QuantileTestResult:
        """
        Analyze quantile effects for a single pair of samples.

        Parameters
        ----------
        sample1 : SampleData
            First sample
        sample2 : SampleData
            Second sample

        Returns
        -------
        QuantileTestResult
            Quantile analysis results for this pair
        """
        quantile_results = []

        for q in self.quantiles:
            # Create a copy of the test for this quantile
            test_copy = deepcopy(self.test)

            # Replace stat_func with quantile function
            # Use closure to capture q properly
            test_copy.stat_func = lambda x, q=q: np.percentile(x, q * 100)

            # Run the bootstrap test
            test_results = test_copy.compare([sample1, sample2])
            quantile_results.append(test_results[0])

        # Collect results into QuantileTestResult
        result = QuantileTestResult(
            name_1=sample1.name or "sample_1",
            name_2=sample2.name or "sample_2",
            quantiles=np.array(self.quantiles),
            effects=np.array([r.effect for r in quantile_results]),
            ci_lower=np.array([r.left_bound for r in quantile_results]),
            ci_upper=np.array([r.right_bound for r in quantile_results]),
            pvalues=np.array([r.pvalue for r in quantile_results]),
            reject=np.array([r.reject for r in quantile_results]),
            alpha=self.test.alpha,
            test_type=self.test.test_type,
            n_samples=self.test.n_samples,
            base_test_name=self.test.test_name
        )

        return result
