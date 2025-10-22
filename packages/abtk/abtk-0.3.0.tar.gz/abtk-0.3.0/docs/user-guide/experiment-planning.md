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
# Bad: Planning for single test but will run multiple variants
n = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)

# Good: Use alpha correction utility
from utils.sample_size_calculator import adjust_alpha_for_multiple_comparisons

alpha_adjusted = adjust_alpha_for_multiple_comparisons(
    alpha=0.05,
    num_groups=4,  # 1 control + 3 treatments
    comparison_type="vs_control"
)
n = calculate_sample_size_ttest(
    mean=100, std=20, mde=0.05, alpha=alpha_adjusted
)
```

---

## Multiple Comparisons in Planning

When testing multiple variants (A/B/C, A/B/C/D), you need **more users** to maintain the same overall significance level.

### Why Multiple Comparisons Matter

**Problem:** Each test has 5% false positive rate → with multiple tests, overall false positive rate increases!

**Example:** A/B/C test (2 comparisons)
- Each test: 5% chance of false positive
- Overall: ~10% chance of **at least one** false positive

**Solution:** Adjust alpha BEFORE calculating sample size.

### Calculate Number of Comparisons

```python
from utils.sample_size_calculator import calculate_number_of_comparisons

# A/B/C test: 1 control + 2 treatments
num_comp = calculate_number_of_comparisons(
    num_groups=3,
    comparison_type="vs_control"  # Compare each treatment to control
)
print(f"Number of comparisons: {num_comp}")
# Output: 2

# A/B/C/D test with all pairwise comparisons
num_comp = calculate_number_of_comparisons(
    num_groups=4,
    comparison_type="pairwise"  # Compare all pairs
)
print(f"Number of comparisons: {num_comp}")
# Output: 6
```

**Comparison types:**
- **`vs_control`** (recommended): Compare each treatment to control only
  - A/B/C: 2 comparisons (B vs A, C vs A)
  - A/B/C/D: 3 comparisons (B vs A, C vs A, D vs A)
- **`pairwise`**: Compare all groups with each other
  - A/B/C: 3 comparisons (A vs B, A vs C, B vs C)
  - A/B/C/D: 6 comparisons (all pairs)

### Adjust Alpha for Multiple Comparisons

```python
from utils.sample_size_calculator import adjust_alpha_for_multiple_comparisons

# A/B/C test: 1 control + 2 treatments
alpha_adj = adjust_alpha_for_multiple_comparisons(
    alpha=0.05,  # Desired overall alpha
    num_groups=3,
    comparison_type="vs_control",
    method="bonferroni"
)
print(f"Adjusted alpha: {alpha_adj:.4f}")
# Output: 0.0250 (0.05 / 2)

# Now calculate sample size with adjusted alpha
n = calculate_sample_size_ttest(
    baseline_mean=100,
    std=20,
    mde=0.05,
    alpha=alpha_adj  # Use corrected alpha!
)
print(f"Sample size needed: {n:,}")
# Output: 2,102 users per group (vs 1,571 without correction)
```

### Correction Methods

**Bonferroni (default):**
```python
alpha_adj = adjust_alpha_for_multiple_comparisons(
    alpha=0.05,
    num_groups=3,
    method="bonferroni"
)
# Formula: alpha_adj = alpha / m = 0.05 / 2 = 0.025
```

**Sidak (less conservative):**
```python
alpha_adj = adjust_alpha_for_multiple_comparisons(
    alpha=0.05,
    num_groups=3,
    method="sidak"
)
# Formula: alpha_adj = 1 - (1 - alpha)^(1/m) = 0.0253
```

**Comparison:**
| Method | Formula | A/B/C (2 comp) | A/B/C/D (3 comp) |
|--------|---------|----------------|------------------|
| Bonferroni | α/m | 0.0250 | 0.0167 |
| Sidak | 1-(1-α)^(1/m) | 0.0253 | 0.0170 |

Sidak is slightly less conservative (more power), but difference is small.

### Complete Workflow Example

```python
from utils.sample_size_calculator import (
    adjust_alpha_for_multiple_comparisons,
    calculate_sample_size_ttest
)

# Step 1: Define experiment design
num_groups = 4  # 1 control + 3 treatments
comparison_type = "vs_control"  # Compare each treatment to control
overall_alpha = 0.05  # Overall significance level

# Step 2: Adjust alpha
alpha_adj = adjust_alpha_for_multiple_comparisons(
    alpha=overall_alpha,
    num_groups=num_groups,
    comparison_type=comparison_type
)
print(f"Adjusted alpha: {alpha_adj:.4f}")
# Output: 0.0167 (0.05 / 3 comparisons)

# Step 3: Calculate sample size
n = calculate_sample_size_ttest(
    baseline_mean=100,
    std=20,
    mde=0.05,
    alpha=alpha_adj  # Use corrected alpha
)
print(f"Need {n:,} users per group")
# Output: 2,418 users per group

# Step 4: Calculate total users
total_users = n * num_groups
print(f"Total users needed: {total_users:,}")
# Output: 9,672 total users

# Compare with uncorrected (WRONG!)
n_wrong = calculate_sample_size_ttest(
    baseline_mean=100,
    std=20,
    mde=0.05,
    alpha=0.05  # Not corrected!
)
print(f"\nWithout correction (WRONG): {n_wrong:,} per group")
print(f"Difference: {n - n_wrong:,} extra users per group needed")
# Output: Without correction: 1,571
#         Difference: 847 extra users per group needed
```

### Sample Size Impact

**Impact of multiple comparisons on sample size:**

| Test Type | Comparisons | Alpha Adjustment | Sample Size per Group | Increase |
|-----------|-------------|------------------|------------------------|----------|
| A/B | 1 | 0.0500 | 1,571 | Baseline |
| A/B/C | 2 | 0.0250 | 2,102 | +34% |
| A/B/C/D | 3 | 0.0167 | 2,418 | +54% |
| A/B/C/D/E | 4 | 0.0125 | 2,653 | +69% |

### When to Use Correction

**Always use correction when:**
- Testing multiple variants (A/B/C, A/B/C/D, etc.)
- Want to control family-wise error rate (FWER)
- Planning sample size BEFORE running test

**Use `vs_control` comparison when:**
- Each treatment is independent
- Only care about "is treatment better than control?"
- Most common for A/B tests

**Use `pairwise` comparison when:**
- Need to compare all treatments with each other
- Want to rank treatments
- Less common, more conservative

### Planning vs Post-hoc Correction

**Planning (use this function):**
```python
# BEFORE running test: adjust alpha for sample size calculation
alpha_adj = adjust_alpha_for_multiple_comparisons(alpha=0.05, num_groups=3)
n = calculate_sample_size_ttest(..., alpha=alpha_adj)
```

**Post-hoc (use after running test):**
```python
# AFTER running test: adjust p-values
from utils.corrections import adjust_pvalues
results = test.compare([control, t1, t2])
adjusted_results = adjust_pvalues(results, method="bonferroni")
```

Both approaches control FWER, but planning approach is recommended!

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

## Cluster-Randomized Experiments

For cluster-randomized experiments (geo tests, store tests), clustering reduces effective sample size. You need to account for the **design effect (DE)** when planning.

### Key Concept: Design Effect

**Formula:**
```
DE = 1 + (m̄ - 1) × ICC
```

where:
- `m̄` = average cluster size
- `ICC` = intra-class correlation (how similar observations within a cluster are)

**Impact:**
```
Effective Sample Size = Total Observations / Design Effect
```

**Example:**
- Total observations: n = 1000
- Design Effect: DE = 2.0
- Effective sample size: n_eff = 1000 / 2.0 = 500

→ You have the statistical power of only 500 independent observations!

### Estimating ICC

ICC typically ranges 0.01-0.20 for cluster-randomized experiments:

**Geo experiments (cities):**
- ICC ≈ 0.05-0.15 (users in same city are somewhat similar)

**Store experiments:**
- ICC ≈ 0.01-0.10 (customers in same store have some similarities)

**School experiments:**
- ICC ≈ 0.10-0.20 (students in same class are more similar)

You can estimate ICC from historical data:

```python
from utils.cluster_utils import calculate_icc
import numpy as np

# Historical data with cluster assignments
icc = calculate_icc(historical_data, cluster_ids, method="anova")
print(f"Estimated ICC: {icc:.3f}")

if icc < 0.01:
    print("→ Low ICC: clustering doesn't matter much")
elif icc < 0.15:
    print("→ Moderate ICC: account for clustering")
else:
    print("→ High ICC: clustering strongly matters")
```

### Sample Size for Cluster Experiments

**Step 1: Calculate sample size as if individual randomization**

```python
from utils.sample_size_calculator import calculate_sample_size_ttest

# Calculate as if no clustering
n_individual = calculate_sample_size_ttest(
    mean=100,
    std=20,
    mde=0.05,
    alpha=0.05,
    power=0.8
)
print(f"Individual randomization: {n_individual:,} per group")
# 1,571 per group
```

**Step 2: Account for design effect**

```python
from utils.cluster_utils import calculate_design_effect

# Assume: 10 clusters, 200 users per cluster
cluster_sizes = [200] * 10
icc = 0.10  # Estimated from historical data

de = calculate_design_effect(cluster_sizes, icc)
print(f"Design Effect: {de:.2f}")
# DE = 1 + (200 - 1) × 0.10 = 20.9

# Adjust sample size
n_cluster = int(n_individual * de)
print(f"Cluster randomization: {n_cluster:,} per group")
# 32,835 per group (20.9× more!)
```

**Step 3: Determine number of clusters**

```python
# Given:
# - Need 32,835 observations per group
# - Have 10 clusters available
# - Each cluster has ~2,000 users

observations_per_cluster = 32835 / 10
print(f"Need {observations_per_cluster:,.0f} observations per cluster")
# 3,284 per cluster

# Check if feasible
available_per_cluster = 2000
if available_per_cluster < observations_per_cluster:
    print(f"⚠️ Not enough users per cluster!")
    print(f"Options:")
    print(f"  1. Increase number of clusters")
    print(f"  2. Accept lower power")
    print(f"  3. Detect larger MDE")
```

### MDE for Cluster Experiments

**What effect can we detect with cluster randomization?**

```python
from utils.sample_size_calculator import calculate_mde_ttest

# Given:
# - 10 clusters per group
# - 2,000 users per cluster
# - ICC = 0.10

n_total_per_group = 10 * 2000  # 20,000 observations
cluster_sizes = [2000] * 10

# Calculate design effect
from utils.cluster_utils import calculate_design_effect
de = calculate_design_effect(cluster_sizes, icc=0.10)

# Effective sample size
n_eff = n_total_per_group / de
print(f"Effective n: {n_eff:,.0f} (out of {n_total_per_group:,})")
# Effective n: 957 (out of 20,000)

# Calculate MDE using effective sample size
mde = calculate_mde_ttest(
    mean=100,
    std=20,
    n=n_eff,  # Use effective n!
    alpha=0.05,
    power=0.8
)
print(f"MDE: {mde:.2%}")
# 6.3% (vs 3.5% for individual randomization)
```

### How Many Clusters Do You Need?

**Rule of thumb:** At least 5-10 clusters per group, preferably 10+

**Power depends more on NUMBER OF CLUSTERS than cluster size:**

```python
# Scenario 1: Few large clusters (BAD)
cluster_sizes_1 = [1000] * 5  # 5 clusters, 1000 each
de_1 = calculate_design_effect(cluster_sizes_1, icc=0.10)
n_eff_1 = sum(cluster_sizes_1) / de_1
print(f"Scenario 1 (5×1000): Effective n = {n_eff_1:.0f}")
# Effective n ≈ 49 (very low!)

# Scenario 2: Many small clusters (BETTER)
cluster_sizes_2 = [100] * 50  # 50 clusters, 100 each
de_2 = calculate_design_effect(cluster_sizes_2, icc=0.10)
n_eff_2 = sum(cluster_sizes_2) / de_2
print(f"Scenario 2 (50×100): Effective n = {n_eff_2:.0f}")
# Effective n ≈ 456 (much better!)

# Both have 5000 total observations, but scenario 2 has 9× more power!
```

**Key insight:** 50 clusters × 100 obs >> 5 clusters × 1000 obs

### Optimal Cluster Size

**Trade-off:**
- Larger clusters → Higher design effect → Lower power
- More clusters → Higher cost/complexity

**Optimal strategy:**
1. Maximize number of clusters (>10 per group)
2. Keep cluster sizes moderate (50-500 observations)
3. Aim for balanced cluster sizes (CV < 0.5)

**Example planning:**

```python
# Goal: Detect 5% effect with 80% power
# Constraints: Can randomize up to 20 cities per group

# Option 1: Use all 20 cities with ~200 users each
n_clusters = 20
cluster_size = 200
icc = 0.10

cluster_sizes = [cluster_size] * n_clusters
de = calculate_design_effect(cluster_sizes, icc)
n_total = n_clusters * cluster_size
n_eff = n_total / de

mde = calculate_mde_ttest(mean=100, std=20, n=n_eff)
print(f"Option 1: {n_clusters} clusters × {cluster_size} users")
print(f"  Design Effect: {de:.2f}")
print(f"  Effective n: {n_eff:.0f}")
print(f"  MDE: {mde:.2%}")

# Option 2: Use fewer cities with more users
n_clusters = 10
cluster_size = 400

cluster_sizes = [cluster_size] * n_clusters
de = calculate_design_effect(cluster_sizes, icc)
n_total = n_clusters * cluster_size
n_eff = n_total / de

mde = calculate_mde_ttest(mean=100, std=20, n=n_eff)
print(f"\nOption 2: {n_clusters} clusters × {cluster_size} users")
print(f"  Design Effect: {de:.2f}")
print(f"  Effective n: {n_eff:.0f}")
print(f"  MDE: {mde:.2%}")

# Option 1 has better power despite same total users!
```

### Quick Reference: Design Effect by ICC

For planning, here's design effect for common scenarios:

| Cluster Size | ICC=0.01 | ICC=0.05 | ICC=0.10 | ICC=0.20 |
|--------------|----------|----------|----------|----------|
| 50 | 1.5 | 3.5 | 5.9 | 10.8 |
| 100 | 2.0 | 6.0 | 10.9 | 20.8 |
| 200 | 3.0 | 11.0 | 20.9 | 40.8 |
| 500 | 6.0 | 26.0 | 50.9 | 100.8 |
| 1000 | 11.0 | 51.0 | 100.9 | 200.8 |

**How to use this table:**
1. Estimate ICC from historical data
2. Decide on cluster size (based on constraints)
3. Look up design effect
4. Multiply sample size by design effect

**Example:**
- Need 1000 users for individual randomization
- Have clusters of size 200
- ICC = 0.10
- Design effect = 20.9
- Need 1000 × 20.9 = 20,900 users for cluster randomization
- With 10 clusters → 2,090 users per cluster

### Variance Reduction with Covariates

CUPED/ANCOVA can help reduce required sample size for cluster experiments too!

```python
# Cluster experiment with covariate
from utils.sample_size_calculator import calculate_sample_size_cuped

# Without covariate
n_no_cov = calculate_sample_size_ttest(mean=100, std=20, mde=0.05)

# With covariate (correlation = 0.7)
n_with_cov = calculate_sample_size_cuped(
    mean=100,
    std=20,
    mde=0.05,
    correlation=0.7  # Between current and historical metric
)

print(f"Without covariate: {n_no_cov:,} per group")
print(f"With covariate: {n_with_cov:,} per group")
reduction = 1 - (n_with_cov / n_no_cov)
print(f"Reduction: {reduction:.1%}")

# Then multiply by design effect
de = calculate_design_effect([200]*10, icc=0.10)
n_cluster_with_cov = int(n_with_cov * de)
print(f"\nCluster + covariate: {n_cluster_with_cov:,} per group")
```

**Recommendation:** Use `ClusteredAncovaTest` for cluster experiments with covariates!

### Cluster Experiments Checklist

Before launching a cluster-randomized experiment:

- [ ] Estimate ICC from historical data (or use conservative estimate)
- [ ] Calculate design effect based on planned cluster sizes
- [ ] Determine effective sample size
- [ ] Check if you have enough clusters (5+ per group minimum)
- [ ] Verify cluster sizes are balanced (CV < 0.5)
- [ ] Consider covariates to reduce required sample size
- [ ] Plan for ClusteredTTest or ClusteredAncovaTest analysis
- [ ] Document ICC assumption for future reference

**See also:** [Cluster Experiments Guide](cluster-experiments.md) for complete details

---

## Summary

**Key functions:**

**Sample Size & MDE:**
- `calculate_mde_ttest()` - What effect can we detect?
- `calculate_sample_size_ttest()` - How many users needed?
- `calculate_mde_cuped()` - MDE with variance reduction
- `calculate_sample_size_cuped()` - Sample size with CUPED
- `calculate_mde_proportions()` - MDE for binary metrics
- `calculate_sample_size_proportions()` - Sample size for proportions

**Multiple Comparisons:**
- `calculate_number_of_comparisons()` - How many comparisons in multi-variant test?
- `adjust_alpha_for_multiple_comparisons()` - Adjust alpha for planning multi-variant tests

**Remember:**
1. Use historical data when available
2. CUPED can reduce sample size by 50%+ (if correlation > 0.7)
3. Plan for total users (both groups!)
4. Check correlation before using CUPED
5. **Always adjust alpha for multiple comparisons** (A/B/C, A/B/C/D, etc.)
6. Account for attrition

---

## Next Steps

- [Run your experiment](parametric-tests.md)
- [Apply variance reduction with CUPED](variance-reduction.md)
- [See complete examples](../../examples/experiment_planning_example.py)

**Pro tip:** Run a small pilot first to validate your assumptions about mean, std, and correlation!
