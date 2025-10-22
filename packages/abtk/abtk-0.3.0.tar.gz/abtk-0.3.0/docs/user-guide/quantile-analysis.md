# Quantile Treatment Effect Analysis

Quantile analysis reveals **where** in the distribution treatment effects occur. Instead of just comparing means, analyze effects at different quantiles (25th, 50th, 75th percentiles, etc.).

## Why Quantile Analysis?

### The Problem with Means

**Standard A/B tests compare means:**
```python
# Control: mean = $100
# Treatment: mean = $105
# Result: 5% average lift
```

**But this hides important information:**
- Does treatment affect everyone equally?
- Or only high-value users?
- Or only low-value users?

### Quantile Analysis Reveals More

```
Quantile  Control  Treatment  Effect
25th      $50      $51        2%    (low spenders)
50th      $100     $105       5%    (median users)
75th      $200     $215       7.5%  (high spenders)
90th      $500     $550       10%   (very high spenders)
```

**Insight:** Treatment effect is **stronger** for high-value users!

---

## Basic Example

```python
from tests.nonparametric import BootstrapTest
from utils.quantile_analysis import QuantileAnalyzer
from core.data_types import SampleData
import numpy as np

# Generate data where effect is stronger for high-value users
np.random.seed(42)

# Exponential distribution (skewed, like revenue)
control = SampleData(
    data=np.random.exponential(100, 1000),
    name="Control"
)

# 10% lift, but stronger for high values
treatment_data = np.random.exponential(100, 1000) * 1.10
treatment = SampleData(
    data=treatment_data,
    name="Treatment"
)

# 1. Initialize bootstrap test
bootstrap = BootstrapTest(
    alpha=0.05,
    test_type="relative",
    n_samples=10000  # More samples = more accurate
)

# 2. Wrap with quantile analyzer
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]  # Default
)

# 3. Run analysis
results = analyzer.compare([control, treatment])
result = results[0]

# 4. View results
print(result.summary())
print("\\n", result.to_dataframe())

# 5. Find where effects are significant
sig_quantiles = result.significant_quantiles()
print(f"\\nSignificant at: {sig_quantiles}")
```

**Output:**
```
Quantile Treatment Effect Analysis
Control vs Treatment
----------------------------------------
Quantile  Effect    CI_Lower  CI_Upper  P-value  Sig
0.25       2.1%     -0.5%      4.8%     0.12     ✗
0.50       5.5%      2.3%      8.9%     0.001    ✓
0.75       9.2%      5.8%     12.7%     0.000    ✓
0.90      14.3%      9.5%     19.4%     0.000    ✓
0.95      18.7%     12.2%     25.8%     0.000    ✓

Significant at: [0.5, 0.75, 0.9, 0.95]
```

**Interpretation:** Effect is concentrated in upper half of distribution (high-value users).

---

## Understanding Quantiles

### What are Quantiles?

- **0.25 (25th percentile / Q1):** 25% of users have lower values
- **0.50 (50th percentile / Median):** Half of users have lower values
- **0.75 (75th percentile / Q3):** 75% of users have lower values
- **0.90 (90th percentile):** 90% of users have lower values

### Default Quantiles

ABTK uses these by default:
```python
quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
```

**Why these?**
- **0.25, 0.5, 0.75:** Quartiles (standard statistical practice)
- **0.9, 0.95:** Upper tail (where effects often differ)

### Custom Quantiles

```python
# Fine-grained analysis
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
)

# Focus on extremes
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.05, 0.25, 0.75, 0.95]
)

# Just median
analyzer = QuantileAnalyzer(
    test=bootstrap,
    quantiles=[0.5]
)
```

---

## Which Bootstrap Test to Use?

QuantileAnalyzer works with **any** bootstrap test:

### 1. Standard Bootstrap (Independent Samples)

```python
from tests.nonparametric import BootstrapTest

bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=bootstrap)
```

### 2. Paired Bootstrap (Matched Pairs)

```python
from tests.nonparametric import PairedBootstrapTest

control = SampleData(
    data=[100, 105, 95, 110],
    paired_ids=[1, 2, 3, 4],  # Matched pairs
    name="Control"
)

paired_bootstrap = PairedBootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=paired_bootstrap)
results = analyzer.compare([control, treatment])
```

### 3. Post-Normed Bootstrap (With Covariate)

```python
from tests.nonparametric import PostNormedBootstrapTest

control = SampleData(
    data=[100, 110, 95, 105],
    covariates=[90, 100, 85, 95],  # Historical data
    name="Control"
)

post_normed = PostNormedBootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=post_normed)
results = analyzer.compare([control, treatment])
```

---

## Interpreting Results

### Pattern 1: Uniform Effect

```
Quantile  Effect
0.25       5.0%
0.50       5.2%
0.75       4.8%
0.90       5.1%
```

**Interpretation:** Treatment affects everyone equally.

**Example scenarios:**
- UI change that improves usability for all users
- Bug fix that helps everyone
- Performance improvement

### Pattern 2: Increasing Effect

```
Quantile  Effect
0.25       2.0%
0.50       5.0%
0.75       8.0%
0.90      12.0%
```

**Interpretation:** Effect is stronger for high-value users.

**Example scenarios:**
- Premium feature that appeals to power users
- Personalization that works better for engaged users
- Pricing change that affects big spenders more

### Pattern 3: Decreasing Effect

```
Quantile  Effect
0.25      10.0%
0.50       6.0%
0.75       3.0%
0.90       1.0%
```

**Interpretation:** Effect is stronger for low-value users.

**Example scenarios:**
- Onboarding improvement helping new users
- Discount targeting occasional users
- Feature helping less engaged users catch up

### Pattern 4: Middle Effect Only

```
Quantile  Effect   Significant
0.25       1.0%    ✗
0.50       8.0%    ✓
0.75       2.0%    ✗
0.90       0.5%    ✗
```

**Interpretation:** Effect concentrated in median users.

**Example scenarios:**
- Feature targeting "average" users
- Change that doesn't affect extremes

### Pattern 5: Tail Effects

```
Quantile  Effect   Significant
0.25       0.5%    ✗
0.50       1.0%    ✗
0.75       2.0%    ✗
0.90       8.0%    ✓
0.95      12.0%    ✓
```

**Interpretation:** Only affects top users.

**Example scenarios:**
- High-value feature (VIP, premium)
- Change targeting whales/power users

---

## Working with Results

### QuantileTestResult Object

```python
result = results[0]

# Basic info
result.name_1           # "Control"
result.name_2           # "Treatment"
result.quantiles        # [0.25, 0.5, 0.75, 0.9, 0.95]
result.effects          # [0.021, 0.055, 0.092, 0.143, 0.187]

# Statistical tests
result.pvalues          # P-values for each quantile
result.reject           # Boolean array (significant?)
result.ci_lower         # Lower confidence bounds
result.ci_upper         # Upper confidence bounds

# Metadata
result.alpha            # 0.05
result.test_type        # "relative"
result.base_test_name   # "bootstrap-test"
```

### Get Specific Quantile

```python
# Get 75th percentile effect
effect_75 = result.get_effect(0.75)
print(f"75th percentile effect: {effect_75:.2%}")

# Get 90th percentile CI
ci_lower, ci_upper = result.get_ci(0.90)
print(f"90th percentile 95% CI: [{ci_lower:.2%}, {ci_upper:.2%}]")
```

### Find Significant Quantiles

```python
# Which quantiles have significant effects?
sig_quantiles = result.significant_quantiles()
print(f"Significant at: {sig_quantiles}")
# e.g., [0.5, 0.75, 0.9, 0.95]

# Are any quantiles significant?
if len(sig_quantiles) > 0:
    print("Effect detected!")
else:
    print("No significant effects")
```

### Convert to DataFrame

```python
import pandas as pd

df = result.to_dataframe()
print(df)
```

**Output:**
```
   quantile  effect  ci_lower  ci_upper   pvalue  reject
0      0.25  0.0210   -0.0048    0.0479  0.1180   False
1      0.50  0.0552    0.0227    0.0891  0.0010    True
2      0.75  0.0918    0.0581    0.1271  0.0000    True
3      0.90  0.1431    0.0953    0.1937  0.0000    True
4      0.95  0.1867    0.1223    0.2580  0.0000    True
```

### Summary Text

```python
summary = result.summary()
print(summary)
```

---

## Visualization

```python
from utils.visualization import plot_quantile_effects
import matplotlib.pyplot as plt

# Create plot
fig, ax = plot_quantile_effects(result)
plt.show()

# Save to file
plt.savefig('quantile_effects.png', dpi=300, bbox_inches='tight')
```

**Plot shows:**
- Effect estimate at each quantile (points)
- Confidence intervals (vertical lines)
- Color coding: green=significant, gray=not significant
- Horizontal reference line at zero

---

## Multiple Comparisons

### Comparing Multiple Treatments

```python
# A/B/C/D test with quantile analysis
results = analyzer.compare([control, treatment_a, treatment_b, treatment_c])

# Results for each pairwise comparison
for result in results:
    print(f"\\n{result.name_1} vs {result.name_2}")
    print(result.to_dataframe())
```

**Warning:** With many comparisons, consider correction:
```python
# Analyzer automatically warns if > 50 tests
# (n_pairs * n_quantiles)

# For 4 samples, 5 quantiles: 3 pairs * 5 quantiles = 15 tests
# This is manageable without correction

# For 10 samples, 10 quantiles: 45 pairs * 10 = 450 tests!
# Consider reducing quantiles or correcting p-values
```

### Visualize Multiple Comparisons

```python
from utils.visualization import plot_multiple_quantile_effects

# Create grid of plots
fig = plot_multiple_quantile_effects(results)
plt.show()
```

---

## Performance Considerations

### Bootstrap Samples

More bootstrap samples = more accurate but slower:

```python
# Quick check (development)
bootstrap = BootstrapTest(n_samples=1000)
analyzer = QuantileAnalyzer(test=bootstrap)
# Fast: ~1 second for 2 samples, 5 quantiles

# Production (recommended)
bootstrap = BootstrapTest(n_samples=10000)
analyzer = QuantileAnalyzer(test=bootstrap)
# Moderate: ~10 seconds

# Publication quality
bootstrap = BootstrapTest(n_samples=100000)
analyzer = QuantileAnalyzer(test=bootstrap)
# Slow: ~100 seconds
```

### Number of Quantiles

```python
# Fast: 5 quantiles (default)
analyzer = QuantileAnalyzer(quantiles=[0.25, 0.5, 0.75, 0.9, 0.95])

# Moderate: 9 quantiles (fine-grained)
analyzer = QuantileAnalyzer(quantiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

# Fast: 3 quantiles (coarse)
analyzer = QuantileAnalyzer(quantiles=[0.25, 0.5, 0.75])
```

### Multiple Samples

Analyzer runs `n_pairs * n_quantiles` bootstrap tests:

```python
# 2 samples, 5 quantiles: 1 pair * 5 = 5 tests
# Fast

# 5 samples, 5 quantiles: 10 pairs * 5 = 50 tests
# Moderate, warning issued

# 10 samples, 10 quantiles: 45 pairs * 10 = 450 tests!
# Slow, warning issued
```

**Tip:** For many samples, analyze key pairs only:
```python
# Instead of analyzing all pairs
results_all = analyzer.compare([control, t1, t2, t3, t4, t5])  # Slow!

# Analyze specific pairs
results_t1 = analyzer.compare([control, t1])
results_t2 = analyzer.compare([control, t2])
# Faster, more focused
```

---

## Real-World Examples

### Example 1: E-commerce Revenue

```python
# Revenue is typically right-skewed
np.random.seed(42)

control_revenue = np.random.exponential(50, 5000)  # Exponential: mean=$50
treatment_revenue = np.random.exponential(55, 5000)  # 10% higher mean

control = SampleData(data=control_revenue, name="Control")
treatment = SampleData(data=treatment_revenue, name="Treatment")

bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=bootstrap)
results = analyzer.compare([control, treatment])

result = results[0]
print(result.summary())

# Interpretation: Is lift uniform or concentrated in high spenders?
```

### Example 2: Session Duration (with Pairing)

```python
# Matched pairs design
n = 500

control_duration = np.random.lognormal(mean=3, sigma=0.5, size=n)
treatment_duration = control_duration * 1.05  # 5% lift, uniform

control = SampleData(
    data=control_duration,
    paired_ids=np.arange(n),
    name="Control"
)

treatment = SampleData(
    data=treatment_duration,
    paired_ids=np.arange(n),
    name="Treatment"
)

paired_bootstrap = PairedBootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=paired_bootstrap)
results = analyzer.compare([control, treatment])

result = results[0]
if len(result.significant_quantiles()) == len(result.quantiles):
    print("Uniform effect across all quantiles!")
```

### Example 3: Targeting High-Value Users

```python
# Simulate feature that only affects high-value users
n = 2000

# Control: exponential distribution
control_data = np.random.exponential(100, n)

# Treatment: same for low values, 20% lift for high values
treatment_data = control_data.copy()
high_value_mask = treatment_data > np.percentile(treatment_data, 75)
treatment_data[high_value_mask] *= 1.20  # 20% lift for top 25%

control = SampleData(data=control_data, name="Control")
treatment = SampleData(data=treatment_data, name="Treatment")

bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
analyzer = QuantileAnalyzer(test=bootstrap)
results = analyzer.compare([control, treatment])

result = results[0]
print(result.to_dataframe())

# Expected: Low quantiles not significant, high quantiles significant
```

---

## Best Practices

### 1. Use Sufficient Bootstrap Samples

```python
# Minimum: 1000 (quick checks)
# Recommended: 10000 (production)
# Maximum: 100000 (publication)

bootstrap = BootstrapTest(n_samples=10000)
```

### 2. Choose Meaningful Quantiles

```python
# Good: Focus on relevant quantiles
analyzer = QuantileAnalyzer(quantiles=[0.25, 0.5, 0.75, 0.9, 0.95])

# Avoid: Too many quantiles (slow, multiple testing issues)
analyzer = QuantileAnalyzer(quantiles=np.arange(0.1, 1.0, 0.05))  # 18 quantiles!
```

### 3. Interpret in Context

Don't just report numbers - explain what they mean:

```python
result = results[0]
sig_q = result.significant_quantiles()

if len(sig_q) > 0:
    if min(sig_q) >= 0.75:
        print("Effect concentrated in top 25% of users (high-value)")
    elif max(sig_q) <= 0.25:
        print("Effect concentrated in bottom 25% of users (low-value)")
    else:
        print(f"Effect significant at quantiles: {sig_q}")
```

### 4. Visualize Results

Always create plots for presentations/reports:

```python
from utils.visualization import plot_quantile_effects

fig, ax = plot_quantile_effects(result)
plt.title(f"{result.name_1} vs {result.name_2}")
plt.savefig('quantile_effects.png', dpi=300)
```

---

## Common Questions

### Q: Why not just test median instead of mean?

A: You can! But quantile analysis goes further:

```python
# Option 1: Test median only
bootstrap_median = BootstrapTest(stat_func=np.median)
results = bootstrap_median.compare([control, treatment])

# Option 2: Test multiple quantiles (more information!)
analyzer = QuantileAnalyzer(quantiles=[0.25, 0.5, 0.75, 0.9])
results = analyzer.compare([control, treatment])
```

Quantile analysis reveals the **full picture**, not just one point.

### Q: Should I correct for multiple comparisons?

It depends:

```python
# Few quantiles (5): Usually no correction needed
# Many quantiles (10+): Consider correction

# But remember: quantiles are correlated!
# Standard corrections might be too conservative

# Recommendation: Report uncorrected, note exploratory nature
```

### Q: Can I use with parametric tests?

No - QuantileAnalyzer only works with bootstrap tests:
- BootstrapTest
- PairedBootstrapTest
- PostNormedBootstrapTest

Parametric tests (TTest, CUPED, ANCOVA) compare means, not quantiles.

---

## Summary

**Quantile analysis reveals:**
- ✅ Where in distribution effects occur
- ✅ Whether effects are uniform or concentrated
- ✅ Heterogeneous treatment effects
- ✅ Who benefits most from treatment

**Use when:**
- Data is skewed (revenue, time, engagement)
- Want to understand effect heterogeneity
- Need to target specific user segments
- Standard mean comparison insufficient

**Key insight:** Don't just compare means - understand the full distribution!

---

## Next Steps

- [Nonparametric Tests Guide](nonparametric-tests.md) - Learn about bootstrap tests
- [Examples](../examples/) - See real-world quantile analysis
- [FAQ](../faq.md) - Common questions about quantile analysis
