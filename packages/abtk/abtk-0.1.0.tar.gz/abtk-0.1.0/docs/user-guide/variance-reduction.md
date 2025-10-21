# Variance Reduction

Variance reduction techniques increase the **sensitivity** of A/B tests by reducing noise in your data. This allows you to detect smaller effects or reach conclusions faster with smaller sample sizes.

## Overview

ABTK supports 3 variance reduction methods:

| Method | Covariates | Complexity | Diagnostics | Best For |
|--------|-----------|------------|-------------|----------|
| **CUPED** | 1 | Simple | No | Quick variance reduction |
| **ANCOVA** | Multiple | Complex | Yes | Maximum reduction, need diagnostics |
| **Post-Normed Bootstrap** | 1+ | Medium | No | Non-normal data + variance reduction |

**Key benefit:** Narrower confidence intervals → detect smaller effects!

---

## Why Variance Reduction?

### The Problem

Standard A/B tests have high **variance** (noise):
- Individual differences between users
- Random fluctuations in behavior
- Seasonal patterns

**Result:** Wide confidence intervals, low statistical power.

### The Solution

Use **pre-experiment data** (covariates) to reduce variance:
- User's historical behavior
- Baseline metrics
- Demographics

**Result:** Narrower CIs, more sensitive tests!

### Example Comparison

```python
from core.data_types import SampleData
from tests.parametric import TTest, CupedTTest

# Same users, with baseline data
control = SampleData(
    data=[100, 110, 95, 105],           # Current metric
    covariates=[90, 100, 85, 95],       # Baseline (pre-experiment)
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110],
    covariates=[92, 102, 87, 97],
    name="Treatment"
)

# Regular T-Test
test_regular = TTest(alpha=0.05, test_type="relative")
results_regular = test_regular.compare([control, treatment])

# CUPED T-Test
test_cuped = CupedTTest(alpha=0.05, test_type="relative")
results_cuped = test_cuped.compare([control, treatment])

print("Regular T-Test:")
print(f"  CI width: {results_regular[0].ci_length:.2%}")
print(f"  P-value: {results_regular[0].pvalue:.4f}")

print("\nCUPED T-Test:")
print(f"  CI width: {results_cuped[0].ci_length:.2%}")
print(f"  P-value: {results_cuped[0].pvalue:.4f}")
print(f"  CI reduction: {(1 - results_cuped[0].ci_length/results_regular[0].ci_length):.1%}")
```

**Typical result:** 30-50% narrower CI with CUPED!

---

## CUPED (Controlled-Experiment Using Pre-Experiment Data)

### What is CUPED?

**CUPED** adjusts your metric using pre-experiment data:

**Formula:**
```
Adjusted metric = Original metric - θ * (Covariate - Mean(Covariate))
```

Where θ is chosen to minimize variance.

**Intuition:**
- If user had high baseline → expect high current metric
- Subtract expected part → reduce variance

### When to Use CUPED

✅ **Use CUPED when:**
- Have pre-experiment data (baseline metrics)
- Correlation between baseline and current metric > 0.5
- Want quick variance reduction
- Data is approximately normal

❌ **Don't use CUPED when:**
- No historical data available
- Correlation < 0.3 (won't help much)
- Baseline data is biased/unreliable

### Basic Example

```python
from tests.parametric import CupedTTest

control = SampleData(
    data=[100, 110, 95, 105, 98, 102],           # Current revenue
    covariates=[90, 100, 85, 95, 88, 92],        # Baseline revenue
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 103, 108],
    covariates=[92, 102, 87, 97, 90, 94],
    name="Treatment"
)

test = CupedTTest(
    alpha=0.05,
    test_type="relative",
    min_correlation=0.5  # Require at least 0.5 correlation
)

results = test.compare([control, treatment])
result = results[0]

print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

### Checking Correlation

CUPED only helps if baseline correlates with current metric:

```python
import numpy as np

# Calculate correlation
control_corr = np.corrcoef(control.data, control.covariates)[0, 1]
treatment_corr = np.corrcoef(treatment.data, treatment.covariates)[0, 1]

print(f"Control correlation: {control_corr:.3f}")
print(f"Treatment correlation: {treatment_corr:.3f}")

# CUPED works best when correlation > 0.5
```

### CUPED Requirements

1. **Covariates must be pre-experiment**
   - Measured BEFORE randomization
   - Not affected by treatment

2. **Must be correlated with outcome**
   - Typically > 0.5 for good variance reduction
   - Check correlation before using CUPED

3. **Same for all groups**
   - All groups must have covariates
   - Same covariate for all samples

---

## ANCOVA (Analysis of Covariance)

**ANCOVA** uses regression to adjust for **multiple covariates**. See [ANCOVA Guide](ancova-guide.md) for comprehensive documentation including diagnostics, VIF checks, and troubleshooting.

**Quick overview:**

| Feature | CUPED | ANCOVA |
|---------|-------|--------|
| Covariates | 1 | Multiple |
| Diagnostics | No | Yes (VIF, normality, etc.) |
| Best for | Simple variance reduction | Maximum reduction |

**When to use:**
- ✅ Have multiple covariates (age, tenure, baseline metrics, etc.)
- ✅ Want maximum variance reduction
- ✅ Need diagnostic validation (VIF, assumption checks)
- ✅ Sample size: n > 10 * (num_covariates + 2)

**Quick example:**
```python
from tests.parametric import AncovaTest

# Multiple covariates: [baseline_revenue, age, tenure_days]
control = SampleData(
    data=[100, 110, 95, 105],
    covariates=[[90, 25, 100], [100, 30, 150], [85, 22, 80], [95, 28, 120]],
    name="Control"
)

test = AncovaTest(alpha=0.05, validate_assumptions=True)
results = test.compare([control, treatment])
```

**For details on diagnostics, VIF, interactions, and troubleshooting, see [ANCOVA Guide](ancova-guide.md).**

---

## Post-Normed Bootstrap

Combines **bootstrap** (nonparametric) with **variance reduction**.

### When to Use

✅ **Use Post-Normed Bootstrap when:**
- Data is non-normal or has outliers
- Have pre-experiment data
- Want variance reduction without normality assumption

### Example

```python
from tests.nonparametric import PostNormedBootstrapTest

control = SampleData(
    data=[100, 110, 95, 150, 98],      # Has outlier: 150
    covariates=[90, 100, 85, 140, 88],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 160, 103],
    covariates=[92, 102, 87, 145, 90],
    name="Treatment"
)

test = PostNormedBootstrapTest(
    alpha=0.05,
    n_samples=10000
)

results = test.compare([control, treatment])
```

**Comparison:**
- **CUPED**: Assumes normality, faster
- **Post-Normed Bootstrap**: No assumptions, slower

---

## Choosing Covariates

### What Makes a Good Covariate?

**Requirements:**
1. **Pre-experiment** - measured before randomization
2. **Correlated with outcome** - r > 0.3 (ideally > 0.5)
3. **Not affected by treatment** - independent of treatment assignment
4. **Available for all users** - no missing values

### Example Covariates by Domain

**E-commerce:**
```python
covariates = [
    baseline_revenue,      # Revenue in past 30 days
    num_purchases,         # Number of past purchases
    avg_order_value,       # Average order size
    days_since_signup      # Account age
]
```

**Content/Media:**
```python
covariates = [
    baseline_pageviews,    # Pageviews last month
    avg_session_duration,  # Typical session length
    num_visits,            # Visit frequency
    user_tenure            # Days as user
]
```

**SaaS:**
```python
covariates = [
    baseline_usage,        # Product usage last month
    num_logins,            # Login frequency
    feature_adoption,      # Features used
    plan_type              # Subscription tier (encoded)
]
```

### Checking Covariate Quality

```python
import numpy as np

# Calculate correlation between covariate and outcome
correlation = np.corrcoef(data, covariate)[0, 1]

print(f"Correlation: {correlation:.3f}")

if correlation > 0.7:
    print("Excellent covariate! High variance reduction expected.")
elif correlation > 0.5:
    print("Good covariate. Moderate variance reduction.")
elif correlation > 0.3:
    print("Weak covariate. Small variance reduction.")
else:
    print("Poor covariate. Consider not using it.")
```

---

## Practical Comparison

### Experiment Setup

Same data, different methods:

```python
import numpy as np
from core.data_types import SampleData
from tests.parametric import TTest, CupedTTest, AncovaTest

np.random.seed(42)
n = 500

# Simulate correlated baseline and current metrics
baseline = np.random.normal(100, 15, n*2)
current = baseline * 0.7 + np.random.normal(0, 10, n*2)
current[n:] += 5  # Treatment effect: +5

# Create samples
control = SampleData(
    data=current[:n],
    covariates=baseline[:n],
    name="Control"
)

treatment = SampleData(
    data=current[n:],
    covariates=baseline[n:],
    name="Treatment"
)

# Compare methods
print("=" * 60)
print("Method Comparison")
print("=" * 60)

# 1. Regular T-Test
test_regular = TTest(alpha=0.05, test_type="absolute")
result_regular = test_regular.compare([control, treatment])[0]
print(f"\n1. Regular T-Test (no variance reduction)")
print(f"   Effect: {result_regular.effect:.2f}")
print(f"   P-value: {result_regular.pvalue:.4f}")
print(f"   CI width: {result_regular.ci_length:.2f}")

# 2. CUPED
test_cuped = CupedTTest(alpha=0.05, test_type="absolute")
result_cuped = test_cuped.compare([control, treatment])[0]
print(f"\n2. CUPED (1 covariate)")
print(f"   Effect: {result_cuped.effect:.2f}")
print(f"   P-value: {result_cuped.pvalue:.4f}")
print(f"   CI width: {result_cuped.ci_length:.2f}")
print(f"   CI reduction: {(1 - result_cuped.ci_length/result_regular.ci_length):.1%}")
```

**Typical results:**
- Regular: CI width = 2.5
- CUPED: CI width = 1.5 (40% reduction!)

---

## Variance Reduction Metrics

### How Much Reduction?

**Variance reduction factor:**
```python
vrf = 1 - (var_cuped / var_original)
```

**CI width reduction:**
```python
ci_reduction = 1 - (ci_cuped / ci_original)
```

**Example:**
```python
ci_original = results_regular[0].ci_length
ci_cuped = results_cuped[0].ci_length

reduction = (1 - ci_cuped / ci_original) * 100
print(f"CI reduced by {reduction:.1f}%")
```

### Expected Reduction by Correlation

| Correlation | Expected CI Reduction |
|-------------|----------------------|
| 0.3 | ~10% |
| 0.5 | ~25% |
| 0.7 | ~50% |
| 0.9 | ~70% |

**Formula:**
```
CI reduction ≈ 1 - √(1 - ρ²)
```

Where ρ is correlation between covariate and outcome.

---

## Best Practices

### 1. Always Check Correlation First

```python
import numpy as np

# Before using CUPED/ANCOVA
corr = np.corrcoef(control.data, control.covariates)[0, 1]
print(f"Correlation: {corr:.3f}")

if corr < 0.3:
    print("Warning: Low correlation. Variance reduction may be minimal.")
```

### 2. Use Same Covariates for All Groups

```python
# Good: Same baseline metric for all
control = SampleData(data=[...], covariates=[...])
treatment = SampleData(data=[...], covariates=[...])

# Bad: Different covariates
control = SampleData(data=[...], covariates=baseline_revenue)
treatment = SampleData(data=[...], covariates=num_purchases)  # Wrong!
```

### 3. Covariates Must Be Pre-Experiment

```python
# Good: Baseline measured before experiment
baseline_revenue = revenue_30_days_before_experiment

# Bad: Measured during experiment
baseline_revenue = revenue_during_experiment  # Affected by treatment!
```

### 4. Handle Missing Covariates

```python
import pandas as pd

# Drop users with missing baseline
df_clean = df.dropna(subset=['baseline_revenue'])

# Or impute (use carefully!)
df['baseline_revenue'].fillna(df['baseline_revenue'].mean(), inplace=True)
```

---

## Common Mistakes

### ❌ Mistake 1: Using Post-Treatment Covariates

```python
# Bad: Using data from AFTER randomization
baseline = user_behavior_after_randomization  # Wrong!
```

**Solution:** Only use pre-experiment data

### ❌ Mistake 2: Low Correlation

```python
# Bad: Using covariate with correlation < 0.3
test = CupedTTest(min_correlation=0.1)  # Too low!
```

**Solution:** Check correlation, set min_correlation=0.5

### ❌ Mistake 3: Too Many Covariates (ANCOVA)

```python
# Bad: More covariates than sample size allows
n = 50
num_covariates = 10  # Need n > 10 * num_covariates
```

**Solution:** Use fewer covariates or collect more data

### ❌ Mistake 4: Multicollinearity (ANCOVA)

```python
# Bad: Highly correlated covariates
# baseline_revenue and total_spend are 0.99 correlated
covariates = [baseline_revenue, total_spend, ...]  # Redundant!
```

**Solution:** Remove one, check VIF in ANCOVA diagnostics

---

## Decision Guide

### Which Variance Reduction Method?

```
Do you have covariates?
├─ No → Use regular test (TTest, Bootstrap)
└─ Yes
    └─ How many covariates?
        ├─ 1 covariate
        │   └─ Data normal?
        │       ├─ Yes → CUPED
        │       └─ No → Post-Normed Bootstrap
        └─ Multiple covariates
            └─ Need diagnostics?
                ├─ Yes → ANCOVA
                └─ No → Try CUPED with most correlated covariate
```

### Quick Comparison

| Situation | Recommended Method |
|-----------|-------------------|
| 1 covariate, normal data | **CUPED** |
| 1 covariate, non-normal | **Post-Normed Bootstrap** |
| Multiple covariates, need max reduction | **ANCOVA** |
| Unsure about assumptions | **Bootstrap** (no variance reduction) |

---

## Summary

**Key Takeaways:**
1. Variance reduction → narrower CIs → detect smaller effects
2. Requires pre-experiment data (covariates)
3. Works best when correlation > 0.5
4. CUPED for 1 covariate, ANCOVA for multiple
5. Always validate correlation before using

**Expected benefits:**
- 30-50% narrower confidence intervals (typical)
- Reach conclusions with smaller sample sizes
- Detect smaller treatment effects

**Requirements:**
- Pre-experiment data for all users
- Correlation > 0.3 (ideally > 0.5)
- Covariates not affected by treatment

---

## Next Steps

- [CUPED Details](parametric-tests.md#cuped-t-test) - Deep dive into CUPED
- [ANCOVA Guide](ancova-guide.md) - Complete ANCOVA guide with diagnostics
- [Nonparametric Tests](nonparametric-tests.md) - Post-Normed Bootstrap
- [Test Selection](test-selection.md) - Choose the right test

**Pro tip:** Start with correlation analysis to see if variance reduction will help!
