# ABTK Usage Guide

A/B Testing Toolkit - Python library for statistical analysis of A/B tests.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Import Tests

```python
# Parametric tests
from tests.parametric import (
    TTest,           # Independent t-test
    PairedTTest,     # Paired t-test for matched pairs
    CupedTTest,      # T-test with CUPED variance reduction
    ZTest,           # Z-test for proportions
    AncovaTest       # ANCOVA / Regression Adjustment
)

# Nonparametric tests
from tests.nonparametric import (
    BootstrapTest,             # Bootstrap resampling
    PairedBootstrapTest,       # Paired bootstrap
    PostNormedBootstrapTest    # Bootstrap with covariate normalization
)

# Multiple comparisons correction
from utils.corrections import adjust_pvalues
```

### 2. Prepare Data

```python
from core.data_types import SampleData, ProportionData
import numpy as np

# For continuous metrics (revenue, time, etc.)
control = SampleData(
    data=[100, 110, 95, 105],          # Metric values
    covariates=[90, 100, 85, 95],      # Optional: historical data
    strata=['A', 'A', 'B', 'B'],       # Optional: stratification
    paired_ids=[1, 2, 3, 4],           # Optional: for paired tests
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110],
    covariates=[92, 102, 87, 97],
    strata=['A', 'A', 'B', 'B'],
    paired_ids=[1, 2, 3, 4],
    name="Treatment"
)

# For proportions (CTR, conversion rate, etc.)
control_prop = ProportionData(
    successes=450,
    trials=1000,
    name="Control"
)

treatment_prop = ProportionData(
    successes=520,
    trials=1000,
    name="Treatment"
)
```

### 3. Run Tests

```python
# T-Test (most common)
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")           # e.g., "Effect: 9.50%"
print(f"P-value: {result.pvalue:.4f}")
print(f"Significant: {result.reject}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")

# Z-Test for proportions
ztest = ZTest(alpha=0.05, test_type="relative")
results = ztest.compare([control_prop, treatment_prop])

# Bootstrap (nonparametric, no assumptions)
bootstrap = BootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000,
    stratify=False
)
results = bootstrap.compare([control, treatment])

# ANCOVA (with covariates for variance reduction)
ancova = AncovaTest(
    alpha=0.05,
    test_type="relative",
    check_interaction=False,
    validate_assumptions=True
)
results = ancova.compare([control, treatment])
```

## Test Selection Guide

### When to Use Each Test:

| Test | Use When | Assumptions | Covariates | Multiple |
|------|----------|-------------|------------|----------|
| **TTest** | Standard A/B test, normal data | Normality | No | No |
| **PairedTTest** | Matched pairs A/B test | Normality, pairing | Yes | No |
| **CupedTTest** | Need variance reduction | Normality | Yes (1) | No |
| **AncovaTest** | Multiple covariates, diagnostics | Linearity | Yes (many) | Yes |
| **ZTest** | Proportions (CTR, CVR) | Large sample | No | No |
| **BootstrapTest** | Non-normal data, small samples | None | No | No |
| **PairedBootstrapTest** | Matched pairs, non-normal | None | No | No |
| **PostNormedBootstrapTest** | Bootstrap + variance reduction | None | Yes | No |

### Decision Tree:

```
Do you have proportions (CTR, CVR)?
├─ Yes → ZTest
└─ No (continuous metric)
    └─ Do you have paired data (matched pairs)?
        ├─ Yes
        │   ├─ Assume normality? → PairedTTest
        │   └─ No assumptions → PairedBootstrapTest
        └─ No (independent samples)
            └─ Do you have covariates (historical data)?
                ├─ Yes
                │   ├─ Multiple covariates? → AncovaTest
                │   ├─ One covariate, assume normality → CupedTTest
                │   └─ One covariate, no assumptions → PostNormedBootstrapTest
                └─ No covariates
                    ├─ Assume normality? → TTest
                    └─ No assumptions → BootstrapTest
```

## Key Parameters

### All Tests:
- **`alpha`**: Significance level (default: 0.05)
- **`test_type`**: `"relative"` (default, returns %) or `"absolute"` (raw difference)

### Bootstrap Tests:
- **`n_samples`**: Number of bootstrap samples (default: 1000, use 10000 for production)
- **`stratify`**: Balance categorical variables (default: False)
- **`random_seed`**: For reproducibility

### ANCOVA Specific:
- **`check_interaction`**: Check for heterogeneous effects (default: False)
- **`validate_assumptions`**: Run diagnostic tests (default: True, set False for simulations)
- **`use_robust_se`**: Use robust standard errors (default: True)

## Multiple Comparisons

When testing multiple variants, correct for multiple comparisons:

```python
# Test 1 control vs 3 treatments
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment1, treatment2, treatment3])

# Apply correction
adjusted = adjust_pvalues(results, method="bonferroni")

# Available methods:
# - "bonferroni": Most conservative (FWER control)
# - "sidak": Less conservative than Bonferroni
# - "holm": Step-down procedure (more powerful)
# - "benjamini-hochberg": FDR control (exploratory analysis)
# - "benjamini-yekutieli": FDR with dependent tests

for result in adjusted:
    print(f"{result.name_1} vs {result.name_2}:")
    print(f"  Original p-value: {result.pvalue_original:.4f}")
    print(f"  Adjusted p-value: {result.pvalue:.4f}")
    print(f"  Significant: {result.reject}")
```

## Advanced Examples

### Example 1: ANCOVA with Multiple Covariates

```python
# Multiple pre-experiment variables
control = SampleData(
    data=[100, 110, 95, 105],
    covariates=np.array([
        [90, 5, 1],    # [prev_revenue, prev_sessions, platform]
        [100, 8, 1],
        [85, 3, 0],
        [95, 6, 0]
    ]),
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110],
    covariates=np.array([
        [92, 5, 1],
        [102, 9, 1],
        [87, 4, 0],
        [97, 7, 0]
    ]),
    name="Treatment"
)

test = AncovaTest(
    alpha=0.05,
    test_type="relative",
    check_interaction=True  # Check if effect varies by segment
)

results = test.compare([control, treatment])
result = results[0]

print(f"Effect: {result.effect:.2%}")
print(f"R-squared: {result.method_params['r_squared']:.3f}")

# Check for heterogeneous effects
if result.method_params.get('has_heterogeneous_effect'):
    print("⚠ Effect varies by covariate level!")
    print(f"Significant interactions: {result.method_params['significant_interactions']}")
```

### Example 2: Stratified Bootstrap

```python
# When strata are imbalanced between groups
control = SampleData(
    data=[100, 110, 90, 95, 105],
    strata=['Mobile', 'Mobile', 'Desktop', 'Desktop', 'Desktop'],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 92, 98],
    strata=['Mobile', 'Desktop', 'Desktop', 'Desktop'],
    name="Treatment"
)

# Stratified bootstrap balances strata
test = BootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000,
    stratify=True,           # Enable stratification
    weight_method='min'      # Conservative balancing
)

results = test.compare([control, treatment])
```

### Example 3: Paired Test (Matched Pairs A/B)

```python
# Users matched by historical data, then randomly assigned
control = SampleData(
    data=[100, 105, 95, 110],
    covariates=[90, 100, 85, 105],  # Historical data used for matching
    paired_ids=[1, 2, 3, 4],         # Which observations are matched
    name="Control"
)

treatment = SampleData(
    data=[105, 110, 100, 115],
    covariates=[92, 102, 87, 107],
    paired_ids=[1, 2, 3, 4],
    name="Treatment"
)

# Paired t-test
test = PairedTTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

# Or paired bootstrap (no assumptions)
test = PairedBootstrapTest(alpha=0.05, test_type="relative", n_samples=10000)
results = test.compare([control, treatment])
```

## TestResult Object

All tests return `TestResult` objects with:

```python
result = results[0]

# Sample info
result.name_1           # "Control"
result.name_2           # "Treatment"
result.value_1          # Mean/proportion for group 1
result.value_2          # Mean/proportion for group 2
result.size_1           # Sample size group 1
result.size_2           # Sample size group 2

# Test results
result.effect           # Treatment effect (decimal: 0.1 = 10%)
result.pvalue           # P-value
result.reject           # True/False (significant at alpha)
result.left_bound       # CI lower bound
result.right_bound      # CI upper bound
result.ci_length        # CI width

# Metadata
result.method_name      # "ttest", "ancova-test", etc.
result.method_params    # Dict with test-specific info
result.alpha            # Significance level used

# Multiple comparisons (if corrected)
result.pvalue_original  # Original p-value before correction
result.correction_method # "bonferroni", "benjamini-hochberg", etc.
```

## Best Practices

1. **Default to relative effects**: `test_type="relative"` gives % change (easier to interpret)
2. **Use covariates when available**: ANCOVA/CUPED reduce variance → narrower CI
3. **Check assumptions**: ANCOVA validates automatically (set `validate_assumptions=True`)
4. **Correct for multiple comparisons**: Use `adjust_pvalues()` when testing multiple variants
5. **Bootstrap for robustness**: When data is non-normal or has outliers
6. **Use sufficient bootstrap samples**: 10,000+ for production (1,000 for quick checks)
7. **Consider heterogeneous effects**: Set `check_interaction=True` in ANCOVA to detect segment differences

## Performance Tips

- For simulations, set `validate_assumptions=False` (faster)
- Use `stratify=False` in bootstrap if strata are balanced
- For quick checks, use `n_samples=1000` in bootstrap
- For production/reports, use `n_samples=10000` in bootstrap

## Quantile Treatment Effect Analysis

Analyze treatment effects at different quantiles of the distribution to understand:
- Where in the distribution the treatment effect occurs
- Whether effects are concentrated in high/low spenders
- Heterogeneous treatment effects

### Basic Usage

```python
from tests.nonparametric import BootstrapTest
from utils.quantile_analysis import QuantileAnalyzer

# Initialize any bootstrap test
bootstrap = BootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000
)

# Wrap with quantile analyzer
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]  # Default
)

# Run analysis
results = analyzer.compare([control, treatment])
result = results[0]

# View results as table
print(result.to_dataframe())

# Or formatted summary
print(result.summary())

# Find where effects are significant
sig_quantiles = result.significant_quantiles()
print(f"Effects significant at: {sig_quantiles}")
```

### Visualization (requires matplotlib)

```python
# Install matplotlib first: pip install matplotlib
from utils.visualization import plot_quantile_effects
import matplotlib.pyplot as plt

# Create plot
fig, ax = plot_quantile_effects(result)
plt.show()

# Or save to file
plt.savefig('quantile_effects.png', dpi=300, bbox_inches='tight')
```

### Works with Any Bootstrap Test

```python
# With PairedBootstrapTest
paired_bootstrap = PairedBootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=paired_bootstrap)
results = analyzer.compare([control, treatment])

# With PostNormedBootstrapTest (variance reduction)
post_normed = PostNormedBootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=post_normed)
results = analyzer.compare([control, treatment])
```

### Interpreting Results

The quantile analysis reveals:
- **Uniform effect**: Similar effects across all quantiles → treatment affects everyone equally
- **Increasing effect**: Effects grow from 25th to 95th percentile → stronger for high-value users
- **Decreasing effect**: Effects decrease → stronger for low-value users
- **Middle effect**: Significant only at 50th percentile → affects average users

**Example output:**
```
Quantile  Effect    CI_Lower  CI_Upper  P-value  Sig
0.25       2.0%     -1.0%      5.0%     0.18     ✗
0.50       5.5%      2.1%      9.0%     0.01     ✓
0.75       9.2%      5.3%     13.5%     0.001    ✓
0.90      14.8%      9.7%     20.2%     0.000    ✓
0.95      19.5%     12.8%     26.7%     0.000    ✓

Effect is significant at quantiles: 0.5, 0.75, 0.9, 0.95
→ Effect concentrated in upper half of distribution (high-value users)
```

## See Also

- `examples/ancova_example.py` - Comprehensive ANCOVA examples
- `examples/quantile_analysis_example.py` - Quantile analysis examples
- `core/data_types.py` - Data structure definitions
- `core/test_result.py` - Result object structure
- `core/quantile_test_result.py` - Quantile result object
