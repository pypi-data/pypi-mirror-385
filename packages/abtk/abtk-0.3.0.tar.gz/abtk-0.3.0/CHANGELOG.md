# Changelog

All notable changes to ABTK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-21

### Added

#### Cluster-Randomized Experiments Support
Major new feature enabling analysis of experiments where randomization occurs at the group level (cities, stores, schools, etc.) rather than individual level.

**New Statistical Tests:**
- `ClusteredTTest` - Parametric t-test with cluster-robust standard errors for continuous metrics
- `ClusteredAncovaTest` (alias: `ClusteredOLSTest`) - OLS regression with multiple covariates and cluster-robust SE
- `ClusteredZTest` - Z-test for proportions (CTR, CVR) with cluster-robust SE
- `ClusteredBootstrapTest` - Nonparametric bootstrap that resamples clusters instead of individuals

**Core Infrastructure:**
- Added `clusters` parameter to `SampleData` for specifying cluster membership
- New `utils/cluster_utils.py` module with utilities:
  - `calculate_icc()` - Intra-Class Correlation calculation (ANOVA and regression methods)
  - `calculate_design_effect()` - Variance inflation due to clustering
  - `validate_clusters()` - Cluster validation with diagnostics (size distribution, CV, warnings)
- New `core/base_cluster_test.py` - Abstract base class for all cluster tests
- Cluster bootstrap sampling in `utils/bootstrap/generator.py`

**Comprehensive Diagnostics:**
All cluster tests now return rich diagnostics in `TestResult.method_params`:
- `icc_control`, `icc_treatment` - Intra-Class Correlation coefficients
- `design_effect_control`, `design_effect_treatment` - Variance inflation factors
- `n_clusters_control`, `n_clusters_treatment` - Number of clusters per group
- `cluster_size_cv_control`, `cluster_size_cv_treatment` - Cluster size coefficient of variation
- `effective_n_control`, `effective_n_treatment` - Effective sample sizes accounting for clustering

**Documentation:**
- New comprehensive user guide: `docs/user-guide/cluster-experiments.md` (800+ lines)
  - What are cluster-randomized experiments
  - When to use cluster tests vs regular tests
  - Detailed guide for each test type
  - ICC interpretation and design effect implications
  - Best practices and common pitfalls
- Updated `docs/user-guide/test-selection.md` with cluster test decision tree
- New section in `docs/user-guide/experiment-planning.md` for cluster experiment planning
- New examples: `examples/cluster_experiments_example.py` with 6 complete workflows:
  - Basic geo experiment with ClusteredTTest
  - CTR experiment with ClusteredZTest
  - Store experiment with covariates using ClusteredAncovaTest
  - Nonparametric analysis with ClusteredBootstrapTest
  - Comparing cluster vs regular test results
  - Multiple comparison correction for cluster tests

**Testing:**
- 105+ new tests across 5 test files (1860+ lines):
  - `test_cluster_utils.py` - Core utilities (30+ tests)
  - `test_clustered_ttest.py` - Parametric t-test (25+ tests)
  - `test_clustered_ztest.py` - Proportions z-test (20+ tests)
  - `test_clustered_bootstrap_test.py` - Nonparametric bootstrap (20+ tests)
  - `test_cluster_integration.py` - End-to-end workflows (10 scenarios)

### Changed
- `SampleData` now accepts optional `clusters` parameter (numpy array of cluster IDs)
- All cluster tests inherit from `BaseClusterTest` ensuring consistent API
- Enhanced validation and error messages for cluster-related issues

### Technical Details
- Uses `statsmodels` OLS with `cov_type='cluster'` for cluster-robust standard errors
- Implements Liang-Zeger/Huber-White sandwich estimator
- No new dependencies required (uses existing statsmodels, numpy, scipy)
- ~7960 total lines added (code + docs + tests)

---

## [0.2.0] - 2025-10-20

### Added
- `AncovaTest` (alias: `OLSTest`) - OLS regression with multiple covariates
  - Support for multiple covariates (1D or 2D arrays)
  - Comprehensive diagnostics: VIF, residual normality, linearity checks
  - Handles both relative and absolute effects
- Sample size and MDE calculators in `utils/sample_size_calculator.py`:
  - `calculate_mde_ttest()`, `calculate_sample_size_ttest()` - For t-tests
  - `calculate_mde_cuped()`, `calculate_sample_size_cuped()` - For CUPED (accounts for correlation)
  - `calculate_mde_proportions()`, `calculate_sample_size_proportions()` - For proportions
  - Hybrid approach: accepts both SampleData/ProportionData objects AND raw parameters
- Comprehensive documentation (5000+ lines):
  - `docs/getting-started.md` - Beginner tutorial
  - `docs/faq.md` - Common questions
  - 7 user guides: test selection, parametric tests, nonparametric tests, variance reduction, ANCOVA, multiple comparisons, quantile analysis
- Added `OLSTest` as alias for `AncovaTest` for clarity

### Changed
- Improved ANCOVA validation and diagnostics
- Enhanced error messages and warnings across all tests

### Fixed
- Various edge cases in CUPED and ANCOVA tests
- Improved handling of zero variances and degenerate cases

---

## [0.1.0] - 2025-10-15

### Added
Initial release of ABTK with core functionality:

**Data Types:**
- `SampleData` - For continuous metrics (with optional covariates, strata, paired_ids)
- `ProportionData` - For binary metrics (successes/trials)
- `TestResult` - Unified result format across all tests

**Parametric Tests:**
- `TTest` - Standard two-sample t-test
- `PairedTTest` - For matched pairs
- `CupedTTest` - Variance reduction with single covariate
- `ZTest` - For proportions (binary metrics)

**Nonparametric Tests:**
- `BootstrapTest` - No distributional assumptions, custom statistics
- `PairedBootstrapTest` - Bootstrap for paired data
- `PostNormedBootstrapTest` - Bootstrap with variance reduction

**Utilities:**
- `corrections.py` - Multiple comparison corrections (Bonferroni, Holm, BH, Sidak, Hommel)
- `quantile_analysis.py` - Quantile Treatment Effects (QTE) analysis
- `dataframe_helpers.py` - Convert pandas DataFrames to SampleData/ProportionData
- `visualization.py` - Plotting utilities

**Key Features:**
- Unified API: all tests use `.compare(samples)` method
- Pairwise comparisons for multiple groups
- Support for relative and absolute effects
- Comprehensive test result with effect, p-value, CI, diagnostics
- Minimal pandas usage, numpy-based calculations
- Python 3.8+ support

[0.3.0]: https://github.com/alexeiveselov92/abtk/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/alexeiveselov92/abtk/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/alexeiveselov92/abtk/releases/tag/v0.1.0
