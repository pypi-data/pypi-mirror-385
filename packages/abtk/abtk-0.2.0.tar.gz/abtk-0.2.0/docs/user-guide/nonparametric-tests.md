# Nonparametric Tests

Nonparametric tests make no assumptions about the underlying data distribution. They're ideal for skewed data, outliers, or when you can't assume normality.

## Overview

ABTK provides 3 nonparametric tests based on bootstrapping:

| Test | Use Case | Key Feature |
|------|----------|-------------|
| **BootstrapTest** | Non-normal data, outliers | No assumptions, custom statistics |
| **PairedBootstrapTest** | Paired data, non-normal | Combines pairing + bootstrap |
| **PostNormedBootstrapTest** | Non-normal + covariates | Bootstrap + variance reduction |

**When to use nonparametric tests:**
- ✅ Data is skewed (revenue, time-on-site)
- ✅ Outliers are present
- ✅ Small sample sizes (n < 30)
- ✅ Can't assume normality
- ✅ Want custom statistics (median, 90th percentile)

---

## Bootstrap Test

### What is Bootstrapping?

**Bootstrapping** is a resampling method:
1. Take random samples WITH replacement from your data
2. Calculate statistic (mean, median, etc.) on each resample
3. Build empirical distribution of the statistic
4. Use this distribution to compute p-values and confidence intervals

**Advantage:** No assumptions about data distribution!

### Basic Usage

```python
from core.data_types import SampleData
from tests.nonparametric import BootstrapTest

# Non-normal data (e.g., revenue with outliers)
control = SampleData(
    data=[10, 12, 11, 13, 150, 9, 10, 11],  # Has outlier: 150
    name="Control"
)

treatment = SampleData(
    data=[12, 14, 13, 15, 180, 11, 12, 13],  # Has outlier: 180
    name="Treatment"
)

# Bootstrap test
test = BootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000,  # Number of bootstrap resamples
    random_state=42
)

results = test.compare([control, treatment])
result = results[0]

print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

### Parameters

```python
BootstrapTest(
    alpha=0.05,           # Significance level
    test_type="relative", # "relative" or "absolute"
    n_samples=10000,      # Bootstrap resamples (more = more accurate)
    stat_func=np.mean,    # Statistic to compute (mean, median, etc.)
    ci_method="percentile", # CI method: "percentile" or "bca"
    stratify=False,       # Stratified bootstrap (if strata provided)
    random_state=None     # For reproducibility
)
```

**Key parameters:**
- **`n_samples`**: Number of bootstrap resamples
  - 1000: Quick checks
  - 10000: Production (recommended)
  - 100000: Publication quality
- **`stat_func`**: Function to compute on each resample
  - `np.mean` (default)
  - `np.median`
  - `lambda x: np.percentile(x, 90)`
- **`ci_method`**:
  - `"percentile"`: Simple percentile method (default)
  - `"bca"`: Bias-corrected and accelerated (more accurate, slower)

---

## Custom Statistics

The power of bootstrap: test ANY statistic!

### Median Instead of Mean

```python
import numpy as np

# Test median difference
test = BootstrapTest(
    alpha=0.05,
    stat_func=np.median,  # Use median
    n_samples=10000
)

results = test.compare([control, treatment])
```

**Use median when:**
- Data is highly skewed
- Outliers are common
- Want robust estimates

### 90th Percentile

```python
# Test if treatment increases 90th percentile
test = BootstrapTest(
    stat_func=lambda x: np.percentile(x, 90),
    n_samples=10000
)

results = test.compare([control, treatment])
# Interpretation: "Treatment increases 90th percentile by X%"
```

**Use quantiles when:**
- Care about tail behavior (high spenders, long sessions)
- Want to understand distribution shifts
- Need quantile treatment effects

### Standard Deviation

```python
# Test if treatment reduces variance
test = BootstrapTest(
    stat_func=np.std,
    n_samples=10000
)

results = test.compare([control, treatment])
```

---

## Paired Bootstrap Test

Use when you have **matched pairs** and **non-normal data**.

### When to Use

✅ **Use Paired Bootstrap when:**
- Data is paired (same users, matched pairs)
- Data is non-normal or has outliers
- Want to remove between-subject variability

❌ **Don't use when:**
- Data is independent (not paired)
- Data is normal → use PairedTTest instead

### Example: Before/After Test

```python
from tests.nonparametric import PairedBootstrapTest

# Each user measured before and after
control = SampleData(
    data=[100, 110, 95, 105, 150],      # Before
    paired_ids=[1, 2, 3, 4, 5],
    name="Before"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 160],     # After (same users)
    paired_ids=[1, 2, 3, 4, 5],
    name="After"
)

test = PairedBootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000
)

results = test.compare([control, treatment])
```

### How It Works

1. **Calculate paired differences** for each user
2. **Bootstrap resample the differences** (not original data!)
3. Compute test statistic on each resample
4. Build confidence interval

**Why pairing helps:**
- Removes between-subject variability
- More sensitive to treatment effects
- Narrower confidence intervals

### Example: Matched Pairs

```python
# Users matched before randomization
control = SampleData(
    data=[100, 110, 95, 105],
    paired_ids=[1, 2, 3, 4],  # Match IDs
    name="Control"
)

treatment = SampleData(
    data=[98, 108, 93, 103],  # Matched users
    paired_ids=[1, 2, 3, 4],
    name="Treatment"
)

test = PairedBootstrapTest(alpha=0.05, n_samples=10000)
results = test.compare([control, treatment])
```

---

## Post-Normed Bootstrap Test

Combines **bootstrap** (nonparametric) with **variance reduction** (covariates).

### When to Use

✅ **Use Post-Normed Bootstrap when:**
- Data is non-normal or has outliers
- You have pre-experiment data (covariates)
- Want variance reduction without normality assumption

### Example

```python
from tests.nonparametric import PostNormedBootstrapTest

# Non-normal data with baseline covariate
control = SampleData(
    data=[100, 110, 95, 150, 98],           # Has outlier
    covariates=[90, 100, 85, 140, 88],      # Baseline
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 160, 103],
    covariates=[92, 102, 87, 145, 90],
    name="Treatment"
)

test = PostNormedBootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000
)

results = test.compare([control, treatment])
```

### How It Works

**Post-normed Bootstrap:**
1. Adjust data using covariate (like CUPED)
2. Bootstrap the **adjusted data**
3. Compute confidence intervals

**Benefits:**
- Variance reduction (narrower CIs)
- No normality assumption
- Robust to outliers

**Comparison to CUPED:**
- CUPED: Assumes normality
- Post-Normed Bootstrap: No assumptions

---

## Stratified Bootstrap

Use when your data has natural **strata** (e.g., platforms, countries).

### When to Use

✅ **Use stratified bootstrap when:**
- Data has subgroups (mobile/desktop, US/EU)
- Want to preserve group proportions
- Strata have different characteristics

### Example

```python
control = SampleData(
    data=[100, 110, 95, 105],
    strata=['mobile', 'mobile', 'desktop', 'desktop'],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110],
    strata=['mobile', 'mobile', 'desktop', 'desktop'],
    name="Treatment"
)

# Enable stratified bootstrap
test = BootstrapTest(
    alpha=0.05,
    stratify=True,  # Resample within each category
    n_samples=10000
)

results = test.compare([control, treatment])
```

**How it works:**
- Resample within each stratum (mobile, desktop)
- Preserves proportion of mobile/desktop in each resample
- More accurate when strata have different means

---

## Choosing Bootstrap Parameters

### n_samples: How Many Resamples?

| n_samples | Use Case | Accuracy | Speed |
|-----------|----------|----------|-------|
| 1000 | Quick checks, debugging | Low | Fast |
| 5000 | Exploratory analysis | Medium | Medium |
| 10000 | Production (recommended) | High | Slow |
| 100000 | Publication, critical decisions | Very high | Very slow |

**Rule of thumb:** Start with 10,000 for most cases.

### CI Method: Percentile vs BCA

**Percentile (default):**
- Simple: takes 2.5th and 97.5th percentiles
- Fast
- Good for most cases

**BCA (Bias-Corrected and Accelerated):**
- Corrects for bias and skewness
- More accurate (especially for small n)
- Slower (computes jackknife)

```python
# Use BCA for small samples or skewed data
test = BootstrapTest(ci_method="bca", n_samples=10000)
```

---

## Bootstrap vs Parametric Tests

### When to Use Bootstrap

✅ **Use Bootstrap when:**
- Data is non-normal (skewed, outliers)
- Small sample size (n < 30)
- Want to test custom statistics (median, quantiles)
- Don't want to make assumptions

### When to Use Parametric (T-Test)

✅ **Use T-Test when:**
- Data is approximately normal
- Large sample size (n > 30, CLT applies)
- Need exact p-values
- Want faster computation

### Example Comparison

```python
from tests.parametric import TTest
from tests.nonparametric import BootstrapTest

# Same data, different tests
test_ttest = TTest(alpha=0.05)
test_boot = BootstrapTest(alpha=0.05, n_samples=10000)

results_ttest = test_ttest.compare([control, treatment])
results_boot = test_boot.compare([control, treatment])

print("T-Test:")
print(f"  P-value: {results_ttest[0].pvalue:.4f}")
print(f"  CI: [{results_ttest[0].left_bound:.2%}, {results_ttest[0].right_bound:.2%}]")

print("\nBootstrap:")
print(f"  P-value: {results_boot[0].pvalue:.4f}")
print(f"  CI: [{results_boot[0].left_bound:.2%}, {results_boot[0].right_bound:.2%}]")
```

**Usually similar results if data is normal!**

---

## Practical Examples

### Example 1: Revenue with Outliers

```python
import numpy as np

# Simulate skewed revenue data
np.random.seed(42)
control_data = np.random.lognormal(mean=3, sigma=1, size=1000)
treatment_data = np.random.lognormal(mean=3.05, sigma=1, size=1000)

control = SampleData(data=control_data, name="Control")
treatment = SampleData(data=treatment_data, name="Treatment")

# Bootstrap handles outliers well
test = BootstrapTest(alpha=0.05, n_samples=10000)
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}, p-value: {result.pvalue:.4f}")
```

### Example 2: Testing Median Session Duration

```python
# Session duration is often skewed
control = SampleData(
    data=[30, 45, 60, 90, 120, 180, 300],  # Seconds
    name="Control"
)

treatment = SampleData(
    data=[35, 50, 70, 100, 150, 200, 350],
    name="Treatment"
)

# Test median (more robust than mean for time data)
test = BootstrapTest(
    stat_func=np.median,
    n_samples=10000
)

results = test.compare([control, treatment])
print(f"Median session duration change: {results[0].effect:.2%}")
```

### Example 3: High Spenders (90th Percentile)

```python
# Test if treatment increases revenue for high spenders
test = BootstrapTest(
    stat_func=lambda x: np.percentile(x, 90),
    n_samples=10000,
    test_type="relative"
)

results = test.compare([control, treatment])
result = results[0]

print(f"90th percentile revenue change: {result.effect:.2%}")
if result.reject:
    print("Treatment significantly affects high spenders!")
```

---

## Diagnostics and Validation

### Check Bootstrap Distribution

```python
# Run bootstrap manually to inspect distribution
test = BootstrapTest(n_samples=10000, random_state=42)

# Access bootstrap samples (if test saves them)
# Note: Current implementation doesn't expose this,
# but you can modify the test to save bootstrap samples
```

### Reproducibility

```python
# Always set random_state for reproducible results
test = BootstrapTest(
    n_samples=10000,
    random_state=42  # Same seed = same results
)

results1 = test.compare([control, treatment])
results2 = test.compare([control, treatment])

# results1 and results2 will be identical
assert results1[0].pvalue == results2[0].pvalue
```

---

## Common Mistakes

### ❌ Mistake 1: Too Few Resamples

```python
# Bad: Not enough resamples
test = BootstrapTest(n_samples=100)  # Unstable results
```

**Solution:** Use at least 5000, preferably 10000

### ❌ Mistake 2: Using Mean for Skewed Data

```python
# Bad: Using mean for highly skewed data
test = BootstrapTest(stat_func=np.mean)  # Mean affected by outliers
```

**Solution:** Use median for skewed distributions
```python
test = BootstrapTest(stat_func=np.median)
```

### ❌ Mistake 3: Ignoring Strata

```python
# Bad: Not stratifying when data has clear subgroups
# E.g., 90% mobile, 10% desktop - bootstrap might create unbalanced samples
```

**Solution:** Use stratified bootstrap
```python
test = BootstrapTest(stratify=True)
```

---

## Best Practices

### 1. Choose Appropriate n_samples

```python
# Development
test = BootstrapTest(n_samples=1000)  # Quick

# Production
test = BootstrapTest(n_samples=10000)  # Recommended

# Critical decisions
test = BootstrapTest(n_samples=100000)  # High accuracy
```

### 2. Use Median for Skewed Metrics

```python
# Revenue, time, session length → use median
test = BootstrapTest(stat_func=np.median)
```

### 3. Set random_state for Reproducibility

```python
test = BootstrapTest(n_samples=10000, random_state=42)
```

### 4. Consider Stratification

```python
# If data has natural groups
test = BootstrapTest(stratify=True, n_samples=10000)
```

---

## Performance Considerations

### Speed Comparison

| Test | Speed | Accuracy |
|------|-------|----------|
| TTest | ⚡⚡⚡⚡⚡ Fastest | High (if normal) |
| Bootstrap (n=1000) | ⚡⚡⚡ Fast | Medium |
| Bootstrap (n=10000) | ⚡⚡ Moderate | High |
| Bootstrap (n=100000) | ⚡ Slow | Very high |

### Optimization Tips

1. **Start small:** Use n=1000 for development
2. **Increase for production:** n=10000 for final results
3. **Cache results:** Bootstrap is deterministic with random_state
4. **Parallelize:** Could parallelize bootstrap (not currently implemented)

---

## Summary

| Test | Best For | Key Advantage |
|------|----------|---------------|
| **BootstrapTest** | Non-normal data, custom statistics | No assumptions |
| **PairedBootstrapTest** | Paired data, non-normal | Pairing + robustness |
| **PostNormedBootstrapTest** | Non-normal + covariates | Variance reduction + robustness |

**When in doubt:** Bootstrap is safe! It works for any distribution.

---

## Next Steps

- [Parametric Tests](parametric-tests.md) - When to use T-Test instead
- [Variance Reduction](variance-reduction.md) - CUPED and ANCOVA
- [Quantile Analysis](quantile-analysis.md) - Analyze effects across distribution
- [Test Selection Guide](test-selection.md) - Choose the right test

**Pro tip:** Combine Bootstrap with Quantile Analysis for maximum insight into distribution shifts!
