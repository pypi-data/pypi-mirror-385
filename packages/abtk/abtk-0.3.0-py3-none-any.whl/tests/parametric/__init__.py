"""
Parametric statistical tests.

This module contains parametric hypothesis tests that assume specific
distributional properties (typically normality). These tests are generally
more powerful than nonparametric tests when their assumptions are met.

Available tests:
- TTest: Independent samples t-test for means
- PairedTTest: Paired samples t-test for matched pairs
- CupedTTest: T-test with CUPED variance reduction
- ZTest: Z-test for proportions
- AncovaTest: ANCOVA / Regression Adjustment with multiple covariates
- OLSTest: Alias for AncovaTest (OLS regression with covariates)
- ClusteredTTest: T-test for cluster-randomized experiments (cluster-robust SE)
- ClusteredAncovaTest: ANCOVA for cluster-randomized experiments (covariates + cluster-robust SE)
- ClusteredOLSTest: Alias for ClusteredAncovaTest
- ClusteredZTest: Z-test for proportions in cluster-randomized experiments
"""

from .ttest import TTest
from .paired_ttest import PairedTTest
from .cuped_ttest import CupedTTest
from .ztest import ZTest
from .ancova_test import AncovaTest
from .clustered_ttest import ClusteredTTest
from .clustered_ancova_test import ClusteredAncovaTest, ClusteredOLSTest
from .clustered_ztest import ClusteredZTest

# Alias for practitioners who prefer "OLS" terminology
OLSTest = AncovaTest

__all__ = [
    'TTest',
    'PairedTTest',
    'CupedTTest',
    'ZTest',
    'AncovaTest',
    'OLSTest',  # Alias
    'ClusteredTTest',
    'ClusteredAncovaTest',
    'ClusteredOLSTest',  # Alias
    'ClusteredZTest',
]
