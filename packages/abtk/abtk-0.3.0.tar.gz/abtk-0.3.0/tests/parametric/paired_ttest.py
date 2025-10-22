"""
Paired t-test for comparing matched pairs in A/B experiments.

Paired t-test is used when observations in two samples are matched/paired.
In A/B testing, this typically means:
- Users are matched based on historical data (covariates)
- Each matched pair is randomly split between Control and Treatment
- paired_ids indicate which observations are matched pairs

The key advantage of paired t-test over independent t-test is that it removes
between-subject variability by comparing matched pairs, making it more powerful
when strong pairing exists.
"""

from typing import List, Literal, Optional, Tuple
import logging
from itertools import combinations
import numpy as np
import scipy.stats as sps

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_paired_samples, validate_alpha
from utils.effect_size import (
    calculate_confidence_interval,
    calculate_pvalue_twosided
)


class PairedTTest(BaseTestProcessor):
    """
    Paired t-test for comparing matched pairs in A/B experiments.

    Use paired t-test when:
    - Observations are matched based on historical data (covariates)
    - Each matched pair is randomly assigned to Control vs Treatment
    - You want to remove between-subject variability through pairing
    - You have paired_ids to identify matched observations

    The test uses paired_ids to match observations between samples automatically.
    This is more reliable than assuming data is pre-sorted.

    The test works on the differences between paired observations, which typically
    have lower variance than independent observations due to removing between-pair variability.

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'absolute': difference in means (mean2 - mean1)
        - 'relative': relative difference ((mean2 - mean1) / mean1)
    return_effect_distribution : bool, default=False
        If True, includes the effect distribution in results
    logger : logging.Logger, optional
        Logger instance for error reporting

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # A/B Test with matched pairs
    >>> # Users are matched by historical data, then randomly assigned to groups
    >>> # paired_ids indicate which users are matched (e.g., [1,1] = pair 1, [2,2] = pair 2)
    >>>
    >>> control = SampleData(
    ...     data=[100, 105, 95, 110],              # Metric during experiment
    ...     covariates=[90, 100, 85, 105],         # Historical data (for matching)
    ...     paired_ids=[1, 2, 3, 4],               # Pair IDs (user 1 matched with user from pair 1 in treatment)
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 110, 100, 115],             # Metric during experiment
    ...     covariates=[92, 102, 87, 107],         # Historical data (for matching)
    ...     paired_ids=[1, 2, 3, 4],               # Same pair IDs indicate matched pairs
    ...     name="Treatment"
    ... )
    >>>
    >>> # Run paired t-test
    >>> paired_test = PairedTTest(alpha=0.05, test_type="relative")
    >>> results = paired_test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")
    >>> print(f"P-value: {result.pvalue:.4f}")

    Notes
    -----
    IMPORTANT: This test uses paired_ids to match observations automatically.
    - Each observation in a sample has a paired_id
    - The same paired_id across samples indicates matched observations
    - paired_ids track which observations form matched pairs

    The test will:
    1. Find common paired_ids between samples
    2. Align observations by paired_ids automatically
    3. Calculate differences on matched pairs only
    4. Warn if significant data loss occurs (>10% unmatched)

    Typical workflow for matched pairs A/B test:
    1. Collect historical data (covariates) for all users
    2. Sort users by historical metric
    3. Create matched pairs (consecutive users or similar values)
    4. Randomly assign one from each pair to Control, other to Treatment
    5. Run experiment and collect metrics
    6. Use paired t-test with paired_ids indicating matches

    When to use paired vs independent t-test vs CUPED:
    - **Paired t-test**: Matched pairs experiments (users matched, then split)
    - **Independent t-test**: Random assignment, no pairing or matching
    - **CUPED**: Random assignment + historical data for variance reduction

    Paired t-test is MORE powerful when:
    1. Strong correlation within pairs (similar historical behavior)
    2. Within-pair variance << between-pair variance
    3. Pairing captures important sources of variation

    Paired t-test is LESS powerful when:
    - Pairing is weak (low correlation within pairs)
    - It reduces degrees of freedom without reducing variance
    - Consider CUPED or independent t-test instead

    Key difference from CUPED:
    - CUPED: Uses covariates to adjust variance (independent samples)
    - Paired t-test: Uses pairing dependency (matched samples)
    - Both can use historical data, but in different ways
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        return_effect_distribution: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Incorrect test type. Use "relative" or "absolute"')

        # Initialize base class
        super().__init__(
            test_name="paired-t-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type,
            return_effect_distribution=return_effect_distribution
        )

        # Test-specific parameters
        self.test_type = test_type
        self.return_effect_distribution = return_effect_distribution

    @staticmethod
    def _calculate_effect_distribution(
        sample1: SampleData,
        sample2: SampleData,
        test_type: Literal["relative", "absolute"] = "relative"
    ) -> Tuple[sps.norm, float]:
        """
        Calculate effect distribution for paired t-test.

        Paired t-test works on the differences between paired observations,
        which typically have lower variance due to removing between-pair variability.
        """
        # Check if paired_ids are provided
        if sample1.paired_ids is None or sample2.paired_ids is None:
            raise ValueError(
                "Paired t-test requires paired_ids to match observations. "
                "Please provide paired_ids when creating SampleData objects."
            )

        # Match observations by paired_ids
        ids1 = sample1.paired_ids
        ids2 = sample2.paired_ids

        # Find common paired_ids (intersection)
        common_ids = np.intersect1d(ids1, ids2)

        if len(common_ids) == 0:
            raise ValueError(
                "No common paired_ids found between samples. "
                "Ensure that matched observations have the same paired_id in both samples."
            )

        # Sort data by paired_ids to ensure matching
        # Get indices where paired_ids match common_ids
        mask1 = np.isin(ids1, common_ids)
        mask2 = np.isin(ids2, common_ids)

        # Sort both samples by paired_id to align them
        sort_idx1 = np.argsort(ids1[mask1])
        sort_idx2 = np.argsort(ids2[mask2])

        x1_sorted = sample1.data[mask1][sort_idx1]
        x2_sorted = sample2.data[mask2][sort_idx2]

        # Verify alignment
        ids1_sorted = ids1[mask1][sort_idx1]
        ids2_sorted = ids2[mask2][sort_idx2]

        if not np.array_equal(ids1_sorted, ids2_sorted):
            raise ValueError(
                "Failed to align samples by paired_ids. This is an internal error."
            )

        n = len(common_ids)

        # Calculate paired differences on aligned data
        differences = x2_sorted - x1_sorted
        mean_diff = np.mean(differences)
        var_diff = np.var(differences)

        # Means for delta method (use aligned data)
        mean_1 = np.mean(x1_sorted)
        var_mean_1 = np.var(x1_sorted) / n

        if test_type == "absolute":
            # Absolute effect: mean of differences
            difference_mean = mean_diff
            difference_var = var_diff / n

            distribution = sps.norm(
                loc=difference_mean,
                scale=np.sqrt(difference_var)
            )
            effect = difference_mean

        elif test_type == "relative":
            # Relative effect using delta method
            if mean_1 == 0:
                raise ValueError("Cannot calculate relative effect when baseline mean is zero")

            # Covariance between differences and baseline (using aligned data)
            # Cov(X2 - X1, X1) = Cov(X2, X1) - Var(X1)
            cov = -np.cov(differences, x1_sorted)[0, 1] / n

            relative_mu = mean_diff / mean_1
            relative_var = (
                (var_diff / n) / (mean_1**2)
                + var_mean_1 * ((mean_diff**2) / (mean_1**4))
                - 2 * (mean_diff / (mean_1**3)) * cov
            )

            if relative_var < 0:
                # Numerical stability
                relative_var = (var_diff / n) / (mean_1**2)

            distribution = sps.norm(
                loc=relative_mu,
                scale=np.sqrt(relative_var)
            )
            effect = relative_mu

        else:
            raise ValueError(f"Invalid test_type: {test_type}. Use 'relative' or 'absolute'")

        return distribution, effect

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise comparisons using paired t-test.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare (must have paired_ids)

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results

        Raises
        ------
        ValueError
            If samples are missing paired_ids or have no common pairs
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples for pairing (checks paired_ids presence and overlap)
        validate_paired_samples(samples, min_samples=2)

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two matched samples using paired t-test.

        This method uses paired_ids to match observations automatically,
        calculates differences between paired observations,
        then computes the effect size, p-value, and confidence interval.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline) with paired_ids
            May include covariates (historical data) for context
        sample2 : SampleData
            Second sample (treatment/variant) with paired_ids
            May include covariates (historical data) for context

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval, etc.
            Based only on common paired_ids.

        Raises
        ------
        ValueError
            If samples are missing paired_ids or have no common pairs

        Notes
        -----
        Covariates are NOT used in calculation (unlike CUPED).
        They may be present in samples for context/documentation,
        but the test only uses data and paired_ids.
        """
        try:
            # Calculate effect distribution for paired test
            distribution, effect = self._calculate_effect_distribution(
                sample1, sample2, test_type=self.test_type
            )

            # Calculate confidence interval
            left_bound, right_bound, ci_length = calculate_confidence_interval(
                distribution, alpha=self.alpha
            )

            # Calculate two-sided p-value
            pvalue = calculate_pvalue_twosided(distribution, null_value=0.0)
            reject = pvalue < self.alpha

            # Note: MDE calculation is not included for paired t-test
            # because it requires knowing the correlation between pairs a priori,
            # which is typically unknown before data collection

            # Create result object
            result = TestResult(
                name_1=sample1.name or "sample_1",
                value_1=sample1.mean,
                std_1=sample1.std_dev,
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=sample2.mean,
                std_2=sample2.std_dev,
                size_2=sample2.sample_size,
                method_name=self.test_name,
                method_params=self.test_params,
                alpha=self.alpha,
                pvalue=pvalue,
                effect=effect,
                ci_length=ci_length,
                left_bound=left_bound,
                right_bound=right_bound,
                reject=reject,
                effect_distribution=distribution if self.return_effect_distribution else None,
                mde_1=0.0,  # MDE not calculated for paired t-test
                mde_2=0.0,  # MDE not calculated for paired t-test
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in PairedTTest compare_samples: {str(e)}", exc_info=True)
            raise
