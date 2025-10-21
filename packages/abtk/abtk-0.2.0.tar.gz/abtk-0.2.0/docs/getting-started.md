# Getting Started with ABTK

Welcome to ABTK (A/B Testing Toolkit)! This guide will help you get started with statistical analysis of your A/B tests.

## What is ABTK?

ABTK is a Python library for analyzing A/B test results. It provides:

- **8 statistical tests** (parametric and nonparametric)
- **Variance reduction techniques** (CUPED, ANCOVA)
- **Multiple comparisons correction** (Bonferroni, Benjamini-Hochberg, etc.)
- **Quantile treatment effect analysis**
- **Unified interface** - all tests return the same `TestResult` format

## Installation

### For Users

```bash
# Basic installation from PyPI
pip install abtk

# With visualization support (adds matplotlib)
pip install abtk[viz]
```

All dependencies (numpy, scipy, pandas, statsmodels) are automatically installed.

### For Developers

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/alexeiveselov92/abtk.git
cd abtk

# Install in editable mode with development dependencies (pytest, black, etc.)
pip install -e ".[dev]"

# Or with both dev and visualization dependencies
pip install -e ".[dev,viz]"
```

## Your First A/B Test

Let's analyze a simple A/B test comparing control vs treatment:

```python
from core.data_types import SampleData
from tests.parametric import TTest

# Your experiment data
control = SampleData(
    data=[100, 110, 95, 105, 98, 102, 107, 103],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 103, 108, 112, 109],
    name="Treatment"
)

# Run t-test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

# Get results
result = results[0]
print(f"Effect: {result.effect:.2%}")           # e.g., "Effect: 9.50%"
print(f"P-value: {result.pvalue:.4f}")          # e.g., "P-value: 0.0234"
print(f"Significant: {result.reject}")          # True or False
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

**Output:**
```
Effect: 5.50%
P-value: 0.0234
Significant: True
95% CI: [0.80%, 10.20%]
```

## Working with pandas DataFrames

If your data is in a pandas DataFrame (most common case), use the helper utilities for easy conversion:

### For Continuous Metrics

```python
import pandas as pd
from utils.dataframe_helpers import sample_data_from_dataframe
from tests.parametric import TTest

# Your experiment data as DataFrame
df = pd.DataFrame({
    'group': ['control', 'control', 'control', 'treatment', 'treatment', 'treatment'],
    'revenue': [100, 110, 95, 105, 115, 100],
    'baseline_revenue': [90, 100, 85, 92, 102, 87]  # Optional: for CUPED
})

# Convert to SampleData objects
samples = sample_data_from_dataframe(
    df,
    group_col='group',
    metric_col='revenue',
    covariate_cols='baseline_revenue'  # Optional
)

# Run test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare(samples)

# Get results
result = results[0]
print(f"Effect: {result.effect:.2%}, p-value: {result.pvalue:.4f}")
```

### For Proportions (CTR, CVR)

```python
from utils.dataframe_helpers import proportion_data_from_dataframe
from tests.parametric import ZTest

# Format 1: Aggregated data (clicks and impressions)
df_agg = pd.DataFrame({
    'variant': ['control', 'treatment'],
    'clicks': [450, 520],
    'impressions': [10000, 10000]
})

samples = proportion_data_from_dataframe(
    df_agg,
    group_col='variant',
    successes_col='clicks',
    trials_col='impressions'
)

# Format 2: Raw binary data (0/1 for each user)
df_raw = pd.DataFrame({
    'variant': ['control'] * 1000 + ['treatment'] * 1000,
    'clicked': [0, 1, 0, 0, 1, ...]  # 0 or 1 for each impression
})

samples = proportion_data_from_dataframe(
    df_raw,
    group_col='variant',
    binary_col='clicked'
)

# Run test (same for both formats)
test = ZTest(alpha=0.05)
results = test.compare(samples)
```

**Tip:** The DataFrame helpers automatically:
- Split data by group
- Handle missing values (with warnings)
- Convert to the right data types
- Create properly formatted SampleData/ProportionData objects

## Key Concepts

### 1. Relative vs Absolute Effects

**Relative effect** (default): Percentage change
```python
test = TTest(test_type="relative")  # Returns 0.05 = 5%
```

**Absolute effect**: Raw difference
```python
test = TTest(test_type="absolute")  # Returns 5.5 (units)
```

Most analysts prefer relative effects (easier to interpret).

### 2. Sample Data Structure

All tests use `SampleData`:

```python
sample = SampleData(
    data=[100, 110, 95],              # Required: metric values
    covariates=[90, 100, 85],         # Optional: for variance reduction
    strata=['Mobile', 'Mobile', 'Desktop'],  # Optional: for stratified bootstrap
    paired_ids=[1, 2, 3],             # Optional: for paired tests
    name="Control"                    # Optional: for labeling
)
```

### 3. Test Results

All tests return `TestResult` objects:

```python
result.effect          # Treatment effect (0.05 = 5%)
result.pvalue          # P-value
result.reject          # True/False (significant at alpha?)
result.left_bound      # CI lower bound
result.right_bound     # CI upper bound
result.ci_length       # CI width
result.value_1         # Control mean/proportion
result.value_2         # Treatment mean/proportion
result.size_1          # Control sample size
result.size_2          # Treatment sample size
```

## When to Use Each Test

### For Continuous Metrics (revenue, time, etc.)

**Normal data, no covariates:**
```python
from tests.parametric import TTest
test = TTest(alpha=0.05)
```

**Normal data, with historical data (covariates):**
```python
from tests.parametric import CupedTTest
test = CupedTTest(alpha=0.05)
```

**Non-normal data (outliers, skewed):**
```python
from tests.nonparametric import BootstrapTest
test = BootstrapTest(alpha=0.05, n_samples=10000)
```

**Matched pairs (users matched before randomization):**
```python
from tests.parametric import PairedTTest
test = PairedTTest(alpha=0.05)
```

### For Proportions (CTR, conversion rate)

```python
from core.data_types import ProportionData
from tests.parametric import ZTest

control = ProportionData(successes=450, trials=1000, name="Control")
treatment = ProportionData(successes=520, trials=1000, name="Treatment")

test = ZTest(alpha=0.05)
results = test.compare([control, treatment])
```

## Multiple Variants (A/B/C/D)

Testing multiple variants? Use correction:

```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues

# Test control vs 3 treatments
test = TTest(alpha=0.05)
results = test.compare([control, treatment_a, treatment_b, treatment_c])

# Apply Bonferroni correction
adjusted = adjust_pvalues(results, method="bonferroni")

for r in adjusted:
    print(f"{r.name_1} vs {r.name_2}:")
    print(f"  Adjusted p-value: {r.pvalue:.4f}")
    print(f"  Significant: {r.reject}")
```

## Variance Reduction with CUPED

Have pre-experiment data? Use CUPED to reduce variance:

```python
from tests.parametric import CupedTTest

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

# CUPED typically gives narrower CI and lower p-value
```

## Next Steps

Now that you understand the basics:

1. **Choose the right test**: See [Test Selection Guide](user-guide/test-selection.md)
2. **Learn variance reduction**: See [Variance Reduction Guide](user-guide/variance-reduction.md)
3. **Explore advanced features**: See [ANCOVA Guide](user-guide/ancova-guide.md)
4. **Check examples**: See [Examples](examples/)

## Common Workflows

### Workflow 1: Simple A/B Test
```python
from core.data_types import SampleData
from tests.parametric import TTest

# 1. Prepare data
control = SampleData(data=[...], name="Control")
treatment = SampleData(data=[...], name="Treatment")

# 2. Run test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

# 3. Interpret
result = results[0]
if result.reject:
    print(f"Significant! Effect: {result.effect:.2%}")
else:
    print("Not significant")
```

### Workflow 2: A/B Test with Variance Reduction
```python
from tests.parametric import CupedTTest

# Include historical data
control = SampleData(
    data=[...],           # Current metric
    covariates=[...],     # Pre-experiment data
    name="Control"
)
treatment = SampleData(
    data=[...],
    covariates=[...],
    name="Treatment"
)

test = CupedTTest(alpha=0.05)
results = test.compare([control, treatment])
```

### Workflow 3: Multi-Variant with Correction
```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues

# Test multiple variants
results = test.compare([control, t1, t2, t3])

# Correct for multiple comparisons
adjusted = adjust_pvalues(results, method="bonferroni")

# Check which are significant
for r in adjusted:
    if r.reject:
        print(f"{r.name_2} is significantly different!")
```

## Getting Help

- **Documentation**: Browse [User Guides](user-guide/) for detailed topics
- **Examples**: See [Examples](examples/) for real-world use cases
- **API Reference**: See [API Reference](api-reference/) for detailed API docs
- **FAQ**: See [FAQ](faq.md) for common questions
- **Issues**: Report bugs at [GitHub Issues](https://github.com/yourusername/abtk/issues)

## Tips for Success

1. **Always check assumptions** - Use appropriate test for your data distribution
2. **Use variance reduction when possible** - CUPED/ANCOVA can greatly increase sensitivity
3. **Correct for multiple comparisons** - When testing multiple variants
4. **Visualize results** - Use quantile analysis to understand where effects occur
5. **Validate with simulations** - Test your analysis pipeline with synthetic data

Ready to dive deeper? Continue to [Test Selection Guide](user-guide/test-selection.md).
