# ABTK - A/B Testing Toolkit

[![PyPI version](https://badge.fury.io/py/abtk.svg)](https://pypi.org/project/abtk/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ABTK** is a comprehensive Python library for statistical analysis of A/B tests. It provides a unified interface for parametric and nonparametric hypothesis tests, variance reduction techniques, and multiple comparisons correction.

## Key Features

- **12 Statistical Tests** - Parametric (T-Test, Z-Test, CUPED, ANCOVA) and Nonparametric (Bootstrap)
- **Cluster-Randomized Experiments** - Geo experiments, store tests, market-level randomization (NEW in v0.3.0)
- **Variance Reduction** - CUPED, ANCOVA with multiple covariates
- **Multiple Comparisons** - Bonferroni, Holm, Benjamini-Hochberg, and more
- **Quantile Analysis** - Analyze treatment effects across the distribution
- **Unified Interface** - All tests return standardized `TestResult` objects
- **Automatic Diagnostics** - ICC, design effect, VIF, and more
- **Flexible** - Support for relative and absolute effects

## Quick Start

### Installation

```bash
pip install abtk
```

For visualization support:
```bash
pip install abtk[viz]
```

### Basic Example

```python
from core.data_types import SampleData
from tests.parametric import TTest

# Prepare your data
control = SampleData(
    data=[100, 110, 95, 105, 98, 102],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 103, 108],
    name="Treatment"
)

# Run test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

# Get results
result = results[0]
print(f"Effect: {result.effect:.2%}")           # e.g., "Effect: 5.5%"
print(f"P-value: {result.pvalue:.4f}")
print(f"Significant: {result.reject}")          # True/False
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

### Using pandas DataFrames

For most analysts, data starts in a pandas DataFrame. Use the helper utilities for easy conversion:

```python
import pandas as pd
from utils.dataframe_helpers import sample_data_from_dataframe
from tests.parametric import TTest

# Your experiment data as DataFrame
df = pd.DataFrame({
    'variant': ['control', 'control', 'treatment', 'treatment'],
    'revenue': [100, 110, 105, 115],
    'baseline_revenue': [90, 100, 92, 102]  # Optional: for CUPED
})

# Convert to SampleData objects automatically
samples = sample_data_from_dataframe(
    df,
    group_col='variant',
    metric_col='revenue',
    covariate_cols='baseline_revenue'  # Optional
)

# Run test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare(samples)
```

See the [DataFrame Usage Examples](examples/dataframe_usage_example.py) for more.

## Available Tests

### Parametric Tests

| Test | Use Case | Special Features |
|------|----------|------------------|
| **TTest** | Standard A/B test | Fast, well-understood |
| **PairedTTest** | Matched pairs A/B test | Removes between-subject variability |
| **CupedTTest** | A/B test with 1 covariate | Variance reduction |
| **ZTest** | Proportions (CTR, CVR) | Designed for binary outcomes |
| **AncovaTest** (or **OLSTest**) | A/B test with multiple covariates | Maximum variance reduction, diagnostics |

### Nonparametric Tests

| Test | Use Case | Special Features |
|------|----------|------------------|
| **BootstrapTest** | Non-normal data, outliers | No assumptions, robust |
| **PairedBootstrapTest** | Matched pairs, non-normal | Combines pairing + nonparametric |
| **PostNormedBootstrapTest** | Non-normal with covariate | Bootstrap + variance reduction |

### Cluster-Randomized Tests (NEW in v0.3.0)

For experiments where randomization occurs at group level (cities, stores, schools, etc.) rather than individual level.

| Test | Use Case | Special Features |
|------|----------|------------------|
| **ClusteredTTest** | Geo experiments, store tests | Cluster-robust SE, ICC diagnostics |
| **ClusteredAncovaTest** | Cluster experiments with covariates | Multiple covariates + cluster SE |
| **ClusteredZTest** | Proportions in geo experiments | CTR/CVR by city with cluster SE |
| **ClusteredBootstrapTest** | Non-normal cluster data | Resamples clusters, not individuals |

**Key Features:**
- Accounts for within-cluster correlation (ICC)
- Provides design effect and effective sample size
- Validates cluster structure (minimum clusters, balance)
- All tests return comprehensive cluster diagnostics

See [Cluster Experiments Guide](docs/user-guide/cluster-experiments.md) for details.

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation, first steps, basic concepts
- **[Test Selection Guide](docs/user-guide/test-selection.md)** - How to choose the right test
- **[User Guides](docs/user-guide/)** - Detailed guides for each test type
- **[API Reference](docs/api-reference/)** - Complete API documentation
- **[Examples](docs/examples/)** - Real-world use cases
- **[FAQ](docs/faq.md)** - Frequently asked questions

## Example: Variance Reduction with CUPED

```python
from tests.parametric import CupedTTest

# Include historical data for variance reduction
control = SampleData(
    data=[100, 110, 95, 105],           # Current metric
    covariates=[90, 100, 85, 95],       # Historical baseline
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110],
    covariates=[92, 102, 87, 97],
    name="Treatment"
)

test = CupedTTest(alpha=0.05)
results = test.compare([control, treatment])

# CUPED typically gives narrower CI and lower p-value!
```

## Example: Cluster-Randomized Experiment (NEW in v0.3.0)

For geo experiments where cities/regions are randomized:

```python
from tests.parametric import ClusteredTTest

# Geo experiment: cities randomized to control/treatment
control = SampleData(
    data=[100, 110, 95, 105, 98, 102, 108, 92],  # User metrics
    clusters=[1, 1, 2, 2, 3, 3, 4, 4],            # City IDs (2 users per city)
    name="Control Cities"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 103, 108, 113, 97],
    clusters=[5, 5, 6, 6, 7, 7, 8, 8],
    name="Treatment Cities"
)

test = ClusteredTTest(alpha=0.05, min_clusters=4)
results = test.compare([control, treatment])

result = results[0]
# Access cluster diagnostics
print(f"ICC: {result.method_params['icc_control']:.3f}")
print(f"Design Effect: {result.method_params['design_effect_control']:.2f}")
print(f"Effective N: {result.method_params['effective_n_control']:.0f}")
```

See [Cluster Experiments Guide](docs/user-guide/cluster-experiments.md) for complete workflows.

## Example: Multiple Comparisons Correction

```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues

# Test multiple variants
test = TTest(alpha=0.05)
results = test.compare([control, treatment_a, treatment_b, treatment_c])

# Apply Bonferroni correction
adjusted = adjust_pvalues(results, method="bonferroni")

for r in adjusted:
    print(f"{r.name_1} vs {r.name_2}: p={r.pvalue:.4f}, significant={r.reject}")
```

## Example: Quantile Analysis

```python
from tests.nonparametric import BootstrapTest
from utils.quantile_analysis import QuantileAnalyzer

# Analyze treatment effects at different quantiles
bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
)

results = analyzer.compare([control, treatment])
result = results[0]

# View results as table
print(result.to_dataframe())

# Find where effects are significant
sig_quantiles = result.significant_quantiles()
print(f"Effects significant at: {sig_quantiles}")
```

## Test Selection Decision Tree

```
Is randomization at GROUP level (cities, stores)?
├─ Yes (Cluster-Randomized)
│   ├─ Proportions (CTR, CVR)? → ClusteredZTest
│   └─ Continuous metric
│       ├─ Have covariates? → ClusteredAncovaTest
│       ├─ Assume normality? → ClusteredTTest
│       └─ No assumptions → ClusteredBootstrapTest
└─ No (Individual-Level Randomization)
    ├─ Do you have proportions (CTR, CVR)?
    │   └─ Yes → ZTest
    └─ No (continuous metric)
        └─ Do you have paired data?
            ├─ Yes
            │   ├─ Assume normality? → PairedTTest
            │   └─ No assumptions → PairedBootstrapTest
            └─ No (independent samples)
                └─ Do you have covariates?
                    ├─ Yes
                    │   ├─ Multiple covariates? → AncovaTest (or OLSTest)
                    │   ├─ One covariate, normal → CupedTTest
                    │   └─ One covariate, non-parametric → PostNormedBootstrapTest
                    └─ No covariates
                        ├─ Assume normality? → TTest
                        └─ No assumptions → BootstrapTest
```

See [Test Selection Guide](docs/user-guide/test-selection.md) for detailed recommendations.

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- scipy >= 1.7.0
- pandas >= 1.3.0
- statsmodels >= 0.13.0

Optional:
- matplotlib >= 3.5.0 (for visualization)

## Installation Options

### For Users

```bash
# Basic installation from PyPI
pip install abtk

# With visualization support
pip install abtk[viz]
```

### For Developers

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/alexeiveselov92/abtk.git
cd abtk

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Or with visualization support
pip install -e ".[dev,viz]"
```

## Running Tests

```bash
# Run all tests
pytest unit_tests/

# Run with coverage
pytest --cov=. unit_tests/

# Run specific test file
pytest unit_tests/test_ancova.py
```

## Project Structure

```
abtk/
├── core/                    # Core data structures
│   ├── data_types.py        # SampleData, ProportionData
│   ├── test_result.py       # TestResult
│   └── quantile_test_result.py
├── tests/
│   ├── parametric/          # Parametric tests
│   └── nonparametric/       # Nonparametric tests
├── utils/                   # Utilities
│   ├── corrections.py       # Multiple comparisons
│   ├── quantile_analysis.py # Quantile treatment effects
│   └── visualization.py     # Plotting (optional)
├── unit_tests/              # Unit tests
├── examples/                # Runnable examples
└── docs/                    # Documentation
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use ABTK in your research, please cite:

```bibtex
@software{abtk2025,
  title={ABTK: A/B Testing Toolkit},
  author={Alexei Veselov},
  year={2025},
  url={https://github.com/alexeiveselov92/abtk}
}
```

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/abtk/issues)
- **FAQ**: [docs/faq.md](docs/faq.md)

## Acknowledgments

ABTK implements methods from:
- Deng et al. (2013) - CUPED methodology
- Benjamini & Hochberg (1995) - FDR control
- And many other contributions to A/B testing literature

---

**Ready to get started?** → Check out the [Getting Started Guide](docs/getting-started.md)
