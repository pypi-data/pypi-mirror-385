"""
Bootstrap utilities.

This module provides general-purpose bootstrap tools for:
- Generating bootstrap samples (with stratification support)
- Calculating confidence intervals
- Calculating p-values
- Statistical utilities

These utilities are used across:
- Bootstrap tests (nonparametric hypothesis testing)
- Simulations (power analysis, sample size calculations)
- Variance estimation
"""

from utils.bootstrap.generator import (
    generate_bootstrap_samples,
    generate_paired_bootstrap_samples,
    calculate_balanced_stratum_weights,
    generate_cluster_bootstrap_samples
)
from utils.bootstrap.statistics import (
    calculate_bootstrap_ci,
    calculate_bootstrap_pvalue,
    apply_statistic_to_bootstrap_samples,
    check_bootstrap_normality,
    calculate_bootstrap_variance_reduction
)

__all__ = [
    # Generator
    'generate_bootstrap_samples',
    'generate_paired_bootstrap_samples',
    'calculate_balanced_stratum_weights',
    'generate_cluster_bootstrap_samples',

    # Statistics
    'calculate_bootstrap_ci',
    'calculate_bootstrap_pvalue',
    'apply_statistic_to_bootstrap_samples',
    'check_bootstrap_normality',
    'calculate_bootstrap_variance_reduction',
]
