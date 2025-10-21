"""
Validation utilities for statistical testing.

This module provides validation functions for samples and test inputs
to ensure data quality and prevent common errors.
"""

from typing import List
import logging
import numpy as np

from core.data_types import SampleData


logger = logging.getLogger(__name__)


def validate_samples(samples: List[SampleData], min_samples: int = 2) -> None:
    """
    Validate a list of samples for statistical testing.

    Performs comprehensive validation checks on samples to ensure they meet
    the requirements for statistical testing.

    Parameters
    ----------
    samples : List[SampleData]
        List of samples to validate
    min_samples : int, default=2
        Minimum number of samples required

    Raises
    ------
    ValueError
        If validation fails for any reason

    Notes
    -----
    This function checks:
    - Minimum number of samples
    - Sample sizes are non-zero
    - Variances and standard deviations are non-negative
    - Warns about duplicate sample names
    """
    # Check minimum samples
    if not samples:
        raise ValueError("Sample list cannot be empty")

    if len(samples) < min_samples:
        raise ValueError(
            f"At least {min_samples} samples are required for comparison, "
            f"but only {len(samples)} provided"
        )

    # Validate each sample
    for i, sample in enumerate(samples):
        sample_name = sample.name or f"sample_{i}"

        # Check sample size
        if sample.sample_size == 0:
            raise ValueError(f"Sample size for '{sample_name}' cannot be zero")

        if sample.sample_size < 2:
            logger.warning(
                f"Sample '{sample_name}' has only {sample.sample_size} observation(s). "
                "Statistical tests may not be reliable with very small samples."
            )

        # Check variance and standard deviation
        if sample.variance < 0:
            raise ValueError(f"Variance for '{sample_name}' cannot be negative")

        if sample.std_dev < 0:
            raise ValueError(f"Standard deviation for '{sample_name}' cannot be negative")

        # Warn about zero variance
        if sample.variance == 0:
            logger.warning(
                f"Sample '{sample_name}' has zero variance. "
                "All values are identical. Statistical tests may not be meaningful."
            )

    # Check for duplicate names (warning only)
    names = [sample.name for sample in samples if sample.name is not None]
    if len(names) != len(set(names)):
        logger.warning(
            "Some samples have duplicate names. "
            "This might lead to confusion in results interpretation."
        )


def validate_sample_pair(sample1: SampleData, sample2: SampleData) -> None:
    """
    Validate a pair of samples for comparison.

    Convenience function for validating exactly two samples.

    Parameters
    ----------
    sample1 : SampleData
        First sample
    sample2 : SampleData
        Second sample

    Raises
    ------
    ValueError
        If validation fails
    """
    validate_samples([sample1, sample2], min_samples=2)


def validate_alpha(alpha: float) -> None:
    """
    Validate significance level (alpha).

    Parameters
    ----------
    alpha : float
        Significance level to validate

    Raises
    ------
    ValueError
        If alpha is not in valid range (0, 1)
    """
    if not 0 < alpha < 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")


def validate_power(power: float) -> None:
    """
    Validate statistical power.

    Parameters
    ----------
    power : float
        Statistical power to validate

    Raises
    ------
    ValueError
        If power is not in valid range (0, 1)
    """
    if not 0 < power < 1:
        raise ValueError(f"Power must be between 0 and 1, got {power}")


def validate_sample_sizes_equal(samples: List[SampleData]) -> bool:
    """
    Check if all samples have equal sizes.

    Parameters
    ----------
    samples : List[SampleData]
        Samples to check

    Returns
    -------
    bool
        True if all samples have the same size, False otherwise
    """
    if not samples:
        return True

    first_size = samples[0].sample_size
    return all(sample.sample_size == first_size for sample in samples)


def validate_covariates(samples: List[SampleData], min_correlation: float = 0.0) -> None:
    """
    Validate that samples have covariates for variance reduction methods (e.g., CUPED).

    Parameters
    ----------
    samples : List[SampleData]
        Samples to validate
    min_correlation : float, default=0.0
        Minimum acceptable correlation coefficient between metric and covariate.
        If correlation is below this threshold, a warning is issued.
        Set to 0.5 for CUPED to be effective.

    Raises
    ------
    ValueError
        If any sample is missing covariates

    Warnings
    --------
    Issues warning if correlation is below min_correlation threshold
    """
    for i, sample in enumerate(samples):
        sample_name = sample.name or f"sample_{i}"

        # Check if covariates are present
        if sample.covariates is None:
            raise ValueError(
                f"Sample '{sample_name}' is missing covariates. "
                "Variance reduction methods like CUPED require pre-experiment data (covariates)."
            )

        # Check covariate correlation if threshold is set
        if min_correlation > 0 and sample.cov_corr_matrix is not None:
            # Get first covariate correlation (or average if multiple)
            if sample.n_covs == 1:
                corr = abs(sample.cov_corr_coef)
            else:
                # Average absolute correlation across all covariates
                corr = np.mean(np.abs(sample.cov_corr_matrix))

            if corr < min_correlation:
                logger.warning(
                    f"Sample '{sample_name}' has low correlation (ρ={corr:.3f}) "
                    f"between metric and covariate (below threshold {min_correlation:.3f}). "
                    "Variance reduction methods may not be effective. "
                    "Consider using regular t-test instead."
                )


def validate_samples_with_covariates(
    samples: List[SampleData],
    min_samples: int = 2,
    min_correlation: float = 0.5
) -> None:
    """
    Validate samples for CUPED-style tests (samples + covariates).

    Combines standard sample validation with covariate validation.

    Parameters
    ----------
    samples : List[SampleData]
        Samples to validate
    min_samples : int, default=2
        Minimum number of samples required
    min_correlation : float, default=0.5
        Minimum acceptable correlation for effective variance reduction

    Raises
    ------
    ValueError
        If validation fails
    """
    # Standard validation
    validate_samples(samples, min_samples=min_samples)

    # Covariate-specific validation
    validate_covariates(samples, min_correlation=min_correlation)


def validate_paired_samples(samples: List[SampleData], min_samples: int = 2) -> None:
    """
    Validate samples for paired t-test in matched pairs A/B experiments.

    Paired t-test requires paired_ids to match observations between samples.
    This is used in matched pairs experiments where:
    - Users are matched based on historical data (covariates)
    - Each matched pair is randomly split between Control and Treatment
    - paired_ids indicate which observations are matched

    Parameters
    ----------
    samples : List[SampleData]
        Samples to validate (must have paired_ids)
    min_samples : int, default=2
        Minimum number of samples required

    Raises
    ------
    ValueError
        If validation fails (e.g., missing paired_ids, no common pairs)

    Warnings
    --------
    Issues warnings about number of common pairs found and data loss

    Notes
    -----
    Covariates may be present in samples for context but are NOT required
    for paired t-test (unlike CUPED). Only paired_ids are required.
    """
    # Standard validation first
    validate_samples(samples, min_samples=min_samples)

    # Check that all samples have paired_ids
    for i, sample in enumerate(samples):
        sample_name = sample.name or f"sample_{i}"
        if sample.paired_ids is None:
            raise ValueError(
                f"Sample '{sample_name}' is missing paired_ids. "
                "Paired t-test requires paired_ids to match observations. "
                "Provide paired_ids when creating SampleData: "
                "SampleData(data=..., paired_ids=[...])"
            )

    # For pairwise comparisons, check overlap of paired_ids
    if len(samples) == 2:
        sample1, sample2 = samples
        common_ids = np.intersect1d(sample1.paired_ids, sample2.paired_ids)

        if len(common_ids) == 0:
            raise ValueError(
                f"No common paired_ids found between '{sample1.name}' and '{sample2.name}'. "
                "Ensure that matched observations have the same paired_id in both samples."
            )

        # Warn if there's significant data loss
        loss_pct_1 = (1 - len(common_ids) / sample1.sample_size) * 100
        loss_pct_2 = (1 - len(common_ids) / sample2.sample_size) * 100

        if loss_pct_1 > 10 or loss_pct_2 > 10:
            logger.warning(
                f"Paired t-test: Only {len(common_ids)} common pairs found. "
                f"Data loss: {loss_pct_1:.1f}% from '{sample1.name}', "
                f"{loss_pct_2:.1f}% from '{sample2.name}'. "
                "Consider reviewing paired_ids for missing matches."
            )
        else:
            logger.info(
                f"Paired t-test: Found {len(common_ids)} matched pairs between samples."
            )
