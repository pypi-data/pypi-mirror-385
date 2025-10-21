# Experiment Planning

Before running an A/B test, you need to plan:
1. **Minimum Detectable Effect (MDE)**: Smallest effect you can detect
2. **Sample Size**: How many users you need

ABTK provides utilities for experiment planning in `utils.sample_size_calculator`.

---

## Quick Start

```python
from utils.sample_size_calculator import (
    calculate_mde_ttest,
    calculate_sample_size_ttest
)

# Question 1: What effect can we detect with 1000 users?
mde = calculate_mde_ttest(mean=100, std=20, n=1000)
print(f"Can detect {mde:.2%} effect")  # 3.5%

# Question 2: How many users to detect 5% effect?
n = calculate_sample_size_ttest(baseline_mean=100, std=20, mde=0.05)
print(f"Need {n:,} users per group")  # 1,571 users
```

---

## Two Approaches

### Approach 1: Use Historical Data (Recommended)

If you have historical data, use `SampleData` or `ProportionData`:

```python
from core.data_types import SampleData
from utils.sample_size_calculator import calculate_mde_ttest, calculate_sample_size_ttest

# Load historical revenue data
historical = SampleData(data=last_month_revenue_array)

# Calculate MDE for planned sample size
mde = calculate_mde_ttest(sample=historical, n=1000)
print(f"With 1000 users, can detect {mde:.2%}")

# Calculate required sample size
n = calculate_sample_size_ttest(sample=historical, mde=0.05)
print(f"To detect 5%, need {n:,} users")
```

**Advantages:**
- Uses actual mean/std from your data
- More accurate than estimates
- Quick to update as data changes

### Approach 2: Use Parameters

If planning from scratch, provide parameters directly:

```python
# Based on estimates: mean=$100, std=$20
mde = calculate_mde_ttest(mean=100, std=20, n=1000)
n = calculate_sample_size_ttest(baseline_mean=100, std=20, mde=0.05)
```

**Use when:**
- No historical data available
- Launching new product/feature
- Doing quick "what-if" scenarios

---

## Continuous Metrics (Revenue, Time, etc.)

### Calculate MDE

**What effect can we detect?**

```python
from utils.sample_size_calculator import calculate_mde_ttest

# Given: 1000 users per group, mean=$100, std=$20
mde = calculate_mde_ttest(
    mean=100,
    std=20,
    n=1000,
    alpha=0.05,    # 5% significance level
    power=0.8,     # 80% power
    test_type="relative"  # or "absolute"
)

print(f"Minimum Detectable Effect: {mde:.2%}")
# Output: 3.5%
# Interpretation: Can detect revenue change from $100 to $103.50
```

**Parameters:**
- `mean`: Expected baseline mean
- `std`: Expected standard deviation
- `n`: Planned sample size per group
- `alpha`: Significance level (default 0.05)
- `power`: Statistical power (default 0.8 = 80%)
- `test_type`: `"relative"` (%) or `"absolute"` (units)

### Calculate Sample Size

**How many users do we need?**

```python
from utils.sample_size_calculator import calculate_sample_size_ttest

# Want to detect 5% revenue increase
n = calculate_sample_size_ttest(
    baseline_mean=100,
    std=20,
    mde=0.05,  # 5% effect
    alpha=0.05,
    power=0.8
)

print(f"Required sample size: {n:,} per group")
# Output: 1,571 users per group
# Total users needed: 3,142
```

---

## CUPED Planning (Variance Reduction)

**CUPED reduces variance → detect smaller effects OR need fewer users!**

### Key Concept: Correlation

CUPED effectiveness depends on **correlation** between covariate and metric:

| Correlation | Variance Reduction | Sample Size Reduction |
|-------------|--------------------|-----------------------|
| ρ = 0.3 | 9% | 9% |
| ρ = 0.5 | 25% | 25% |
| ρ = 0.7 | 51% | **51%** |
| ρ = 0.9 | 81% | **81%** |

**Rule of thumb:** correlation ≥ 0.5 for CUPED to be worthwhile.

### Calculate MDE with CUPED

```python
from utils.sample_size_calculator import calculate_mde_cuped

# Same scenario, but with baseline revenue covariate (ρ=0.7)
mde = calculate_mde_cuped(
    mean=100,
    std=20,
    n=1000,
    correlation=0.7  # Correlation with baseline revenue
)

print(f"MDE with CUPED: {mde:.2%}")
# Output: 2.5% (vs 3.5% without CUPED!)
```

### Calculate Sample Size with CUPED

```python
from utils.sample_size_calculator import calculate_sample_size_cuped

# Want to detect 5% effect with CUPED
n = calculate_sample_size_cuped(
    baseline_mean=100,
    std=20,
    mde=0.05,
    correlation=0.7
)

print(f"Required sample size with CUPED: {n:,}")
# Output: 770 users per group (vs 1,571 without CUPED!)
# You need 51% fewer users!
```

### Compare Regular vs CUPED

```python
from utils.sample_size_calculator import compare_mde_with_without_cuped

mde_regular, mde_cuped, improvement = compare_mde_with_without_cuped(
    mean=100,
    std=20,
    n=1000,
    correlation=0.7
)

print(f"Regular MDE: {mde_regular:.2%}")
print(f"CUPED MDE: {mde_cuped:.2%}")
print(f"Improvement: {improvement:.1%}")
# Regular MDE: 3.5%
# CUPED MDE: 2.5%
# Improvement: 30%
```

---

## Proportions (CTR, CVR, Churn)

For binary metrics (click/no-click, convert/no-convert):

### Calculate MDE for Proportions

```python
from utils.sample_size_calculator import calculate_mde_proportions

# CTR test: baseline CTR = 5%, 10,000 users per group
mde = calculate_mde_proportions(
    p=0.05,  # 5% baseline CTR
    n=10000,
    test_type="relative"
)

print(f"Can detect {mde:.2%} relative change")
# Output: 12.5% relative change
# Interpretation: Can detect CTR change from 5.0% to 5.6%
```

### Calculate Sample Size for Proportions

```python
from utils.sample_size_calculator import calculate_sample_size_proportions

# Want to detect 10% relative increase in CTR (5% → 5.5%)
n = calculate_sample_size_proportions(
    baseline_proportion=0.05,
    mde=0.10,  # 10% relative increase
    test_type="relative"
)

print(f"Need {n:,} users per group")
# Output: 15,732 users per group
```

### With Historical ProportionData

```python
from core.data_types import ProportionData
from utils.sample_size_calculator import calculate_mde_proportions

# Historical CTR: 500 clicks / 10,000 impressions
historical_ctr = ProportionData(successes=500, trials=10000)

# Calculate MDE using historical data
mde = calculate_mde_proportions(sample=historical_ctr, n=10000)
print(f"MDE: {mde:.2%}")
```

---

## Common Scenarios

### Scenario 1: Planning New Revenue Test

```python
# Historical data
historical = SampleData(data=last_month_revenue)

# Question: What can we detect with 2000 users?
mde = calculate_mde_ttest(sample=historical, n=2000)
print(f"With 2000 users: MDE = {mde:.2%}")

# Question: How many users for 3% effect?
n = calculate_sample_size_ttest(sample=historical, mde=0.03)
print(f"For 3% effect: need {n:,} users")
```

### Scenario 2: CUPED with Known Correlation

```python
# You ran a pilot and found correlation=0.65 between baseline and current revenue
# How many users to detect 5% with CUPED?

n_regular = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)
n_cuped = calculate_sample_size_cuped(mean=100, std=20, mde=0.05, correlation=0.65)

print(f"Regular: {n_regular:,} users")
print(f"CUPED: {n_cuped:,} users")
print(f"Savings: {n_regular - n_cuped:,} users")
```

### Scenario 3: CTR Test Planning

```python
# Historical: 5% CTR, want to detect 15% relative increase

# Option 1: With historical data
historical_ctr = ProportionData(successes=500, trials=10000)
n = calculate_sample_size_proportions(sample=historical_ctr, mde=0.15)

# Option 2: With parameters
n = calculate_sample_size_proportions(baseline_proportion=0.05, mde=0.15)

print(f"Need {n:,} impressions per group")
```

### Scenario 4: Budget-Constrained Planning

```python
# Budget: Can only run 500 users per group
# What's the smallest effect we can detect?

mde = calculate_mde_ttest(mean=100, std=20, n=500)
print(f"With 500 users, can detect {mde:.2%}")

# With CUPED?
mde_cuped = calculate_mde_cuped(mean=100, std=20, n=500, correlation=0.7)
print(f"With CUPED, can detect {mde_cuped:.2%}")
```

---

## Parameter Guide

### Alpha (Significance Level)

- **Default: 0.05** (5%)
- Probability of false positive (Type I error)
- Lower alpha → harder to detect effects → need more users

**Common values:**
- 0.05: Standard (95% confidence)
- 0.01: Conservative (99% confidence)
- 0.10: Liberal (90% confidence)

### Power

- **Default: 0.80** (80%)
- Probability of detecting real effect (1 - Type II error)
- Higher power → need more users

**Common values:**
- 0.80: Standard
- 0.90: High power (medical, critical tests)
- 0.70: Quick experiments

### Ratio

- **Default: 1.0** (equal sizes)
- Ratio of treatment to control sample size
- ratio=1.0: Equal groups (recommended)
- ratio=2.0: Treatment 2x larger than control

**Example:**
```python
# 1000 control, 2000 treatment
n = calculate_sample_size_ttest(
    baseline_mean=100,
    std=20,
    mde=0.05,
    ratio=2.0  # Treatment is 2x control
)
# Returns control group size: 1248
# Treatment group size: 1248 * 2 = 2496
```

---

## Best Practices

### 1. Always Use Historical Data When Available

```python
# Good: Use actual data
historical = SampleData(data=last_month_revenue)
mde = calculate_mde_ttest(sample=historical, n=1000)

# Less good: Guess parameters
mde = calculate_mde_ttest(mean=100, std=20, n=1000)
```

### 2. Check Correlation Before Using CUPED

```python
import numpy as np

# Check correlation between baseline and current metric
correlation = np.corrcoef(baseline_revenue, current_revenue)[0, 1]
print(f"Correlation: {correlation:.3f}")

if correlation > 0.5:
    print("CUPED will help significantly!")
    n = calculate_sample_size_cuped(..., correlation=correlation)
else:
    print("CUPED won't help much, use regular t-test")
    n = calculate_sample_size_ttest(...)
```

### 3. Plan for Multiple Scenarios

```python
# Conservative: detect 3% effect
n_conservative = calculate_sample_size_ttest(mean=100, std=20, mde=0.03)

# Standard: detect 5% effect
n_standard = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)

# Optimistic: detect 7% effect
n_optimistic = calculate_sample_size_ttest(mean=100, std=20, mde=0.07)

print(f"3% effect: {n_conservative:,} users")
print(f"5% effect: {n_standard:,} users")
print(f"7% effect: {n_optimistic:,} users")
```

### 4. Account for Attrition

```python
# Need 1000 users, expect 10% dropout
n_needed = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)
n_with_attrition = int(n_needed / 0.9)  # Add 10% buffer

print(f"Ideal sample: {n_needed:,}")
print(f"With 10% attrition: {n_with_attrition:,}")
```

---

## Common Mistakes

### ❌ Mistake 1: Using Wrong Standard Deviation

```python
# Bad: Using population std (ddof=0)
std_wrong = np.std(data)  # Biased

# Good: Using sample std (ddof=1)
std_correct = np.std(data, ddof=1)  # Unbiased
```

### ❌ Mistake 2: Forgetting About Total Sample Size

```python
n = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)
print(f"Need {n} per group")  # 1,571

# Common mistake: "I need 1,571 users"
# Correct: "I need 1,571 * 2 = 3,142 total users"
```

### ❌ Mistake 3: Overestimating Correlation for CUPED

```python
# Bad: Assuming correlation without checking
n = calculate_sample_size_cuped(..., correlation=0.9)  # Too optimistic!

# Good: Check actual correlation first
actual_corr = np.corrcoef(baseline, current)[0, 1]
n = calculate_sample_size_cuped(..., correlation=actual_corr)
```

### ❌ Mistake 4: Not Accounting for Multiple Comparisons

```python
# Bad: Planning for single test but will run 4 variants
n = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)

# Good: Adjust alpha for multiple tests (Bonferroni)
alpha_adjusted = 0.05 / 4  # 4 variants = 6 pairwise comparisons
n = calculate_sample_size_ttest(
    mean=100, std=20, mde=0.05, alpha=alpha_adjusted
)
```

---

## FAQ

### How do I estimate correlation for CUPED?

Run a quick analysis on historical data:

```python
import numpy as np

# Calculate correlation between baseline and current
corr = np.corrcoef(baseline_revenue, current_revenue)[0, 1]
print(f"Correlation: {corr:.3f}")

# Typical values:
# 0.5-0.7: Good covariate
# 0.7-0.9: Excellent covariate
# < 0.5: Not worth using CUPED
```

### Should I use relative or absolute MDE?

**Relative (default):** Easier to interpret
```python
mde = 0.05  # "5% increase"
```

**Absolute:** When baseline varies
```python
mde = 5  # "$5 increase"
```

**Rule:** Use relative unless baseline is near zero.

### What if I don't have historical data?

Use industry benchmarks or educated guesses:

**E-commerce revenue:**
- Mean: $50-200
- Std: 1-2x mean
- CV (coefficient of variation) ≈ 1-2

**CTR:**
- Search ads: 2-5%
- Display ads: 0.1-0.5%
- Email: 3-10%

### How long will my experiment run?

```python
n_per_group = 1571  # From calculate_sample_size_ttest
daily_users = 500   # Your traffic

days = (n_per_group * 2) / daily_users
print(f"Experiment will run {days:.1f} days")
# 6.3 days
```

---

## Summary

**Key functions:**
- `calculate_mde_ttest()` - What effect can we detect?
- `calculate_sample_size_ttest()` - How many users needed?
- `calculate_mde_cuped()` - MDE with variance reduction
- `calculate_sample_size_cuped()` - Sample size with CUPED
- `calculate_mde_proportions()` - MDE for binary metrics
- `calculate_sample_size_proportions()` - Sample size for proportions

**Remember:**
1. Use historical data when available
2. CUPED can reduce sample size by 50%+ (if correlation > 0.7)
3. Plan for total users (both groups!)
4. Check correlation before using CUPED
5. Account for attrition and multiple comparisons

---

## Next Steps

- [Run your experiment](parametric-tests.md)
- [Apply variance reduction with CUPED](variance-reduction.md)
- [See complete examples](../../examples/experiment_planning_example.py)

**Pro tip:** Run a small pilot first to validate your assumptions about mean, std, and correlation!
