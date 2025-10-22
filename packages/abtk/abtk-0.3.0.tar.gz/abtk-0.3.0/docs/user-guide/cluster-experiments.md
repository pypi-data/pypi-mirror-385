# Cluster-Randomized Experiments

This guide covers cluster-randomized experiments in ABTK, including when to use cluster tests, how to check for clustering effects, and how to choose the right test.

## Table of Contents

1. [What are Cluster-Randomized Experiments?](#what-are-cluster-randomized-experiments)
2. [When to Use Cluster Tests](#when-to-use-cluster-tests)
3. [Key Concepts](#key-concepts)
4. [Available Cluster Tests](#available-cluster-tests)
5. [Getting Started](#getting-started)
6. [Checking for Clustering Effects](#checking-for-clustering-effects)
7. [Choosing the Right Test](#choosing-the-right-test)
8. [Examples](#examples)
9. [Common Pitfalls](#common-pitfalls)
10. [References](#references)

---

## What are Cluster-Randomized Experiments?

In cluster-randomized experiments, randomization occurs at the **group level** rather than the individual level.

### Examples of Cluster-Randomized Experiments

**Geo experiments:**
- **Units:** Cities or regions
- **Randomization:** Entire cities assigned to control/treatment
- **Observations:** Users within each city
- **Example:** Testing a new feature in 10 cities (5 control, 5 treatment)

**Store experiments:**
- **Units:** Retail locations
- **Randomization:** Stores assigned to different promotions
- **Observations:** Customer purchases within each store
- **Example:** Testing pricing strategy across 20 stores

**School experiments:**
- **Units:** Schools or classrooms
- **Randomization:** Schools assigned to different curricula
- **Observations:** Student test scores within each school
- **Example:** Educational intervention in 15 schools

**Server experiments:**
- **Units:** Backend servers
- **Randomization:** Servers assigned to different algorithms
- **Observations:** Request latencies on each server
- **Example:** Testing new caching strategy on 8 servers

### Key Difference from Regular A/B Tests

| Aspect | Regular A/B Test | Cluster-Randomized |
|--------|------------------|-------------------|
| **Randomization** | Individual users | Groups (cities, stores) |
| **Independence** | Users are independent | Users within cluster are correlated |
| **ICC** | ICC ≈ 0 | ICC > 0 |
| **Test to use** | TTest, ZTest, BootstrapTest | ClusteredTTest, ClusteredZTest, etc. |

---

## When to Use Cluster Tests

Use cluster tests when:

✅ **Randomization is at cluster level**
- Cities, stores, schools, servers are randomized
- Cannot randomize individuals within clusters
- Example: Can't A/B test users within same city (network effects)

✅ **Within-cluster correlation exists (ICC > 0.01)**
- Users in same cluster behave similarly
- Cluster membership affects outcome
- Example: Users in same city have similar demographics

✅ **Have enough clusters (5+ per group)**
- Minimum: 3 clusters per group (test will fail with < 3)
- Recommended: 5-10+ clusters per group
- More clusters = more power

**DO NOT use cluster tests when:**

❌ Individual-level randomization (use regular tests instead)
❌ ICC ≈ 0 (no clustering effect)
❌ < 3 clusters per group (test will fail)

---

## Key Concepts

### Intra-Class Correlation (ICC)

ICC measures how similar observations within a cluster are.

**Formula:**
```
ICC = Var(between clusters) / (Var(between clusters) + Var(within clusters))
```

**Interpretation:**
- ICC = 0: No clustering (observations are independent)
- ICC = 0.01-0.05: Small cluster effect
- ICC = 0.05-0.15: Moderate cluster effect
- ICC > 0.15: Large cluster effect

**Example:**
```python
from utils.cluster_utils import calculate_icc
import numpy as np

# Sample data: 3 clusters
data = np.array([100, 105, 110, 95, 98, 102, 108, 112])
clusters = np.array([1, 1, 1, 2, 2, 3, 3, 3])

icc = calculate_icc(data, clusters, method="anova")
print(f"ICC: {icc:.3f}")  # e.g., 0.120

if icc < 0.01:
    print("Low ICC - clustering not important, use regular tests")
elif icc < 0.15:
    print("Moderate ICC - use cluster tests")
else:
    print("High ICC - definitely use cluster tests")
```

### Design Effect (DE)

Design effect quantifies how much clustering inflates variance.

**Formula:**
```
DE = 1 + (m̄ - 1) × ICC
```

where m̄ = average cluster size

**Interpretation:**
- DE = 1.0: No clustering effect
- DE = 1.5: Variance is 50% higher due to clustering
- DE = 2.0: Variance is 2× higher (CI is √2 ≈ 1.41× wider)

**Example:**
```python
from utils.cluster_utils import calculate_design_effect

# 5 clusters with sizes [100, 120, 95, 110, 105]
cluster_sizes = [100, 120, 95, 110, 105]
icc = 0.10

de = calculate_design_effect(cluster_sizes, icc)
print(f"Design Effect: {de:.2f}")  # e.g., 11.8

# Interpretation
print(f"Variance is {de:.1f}× higher due to clustering")
print(f"CI is {np.sqrt(de):.1f}× wider")
print(f"Effective sample size: {sum(cluster_sizes) / de:.0f}")
# Total n=530, but effective n ≈ 45 due to clustering!
```

### Effective Sample Size

Clustering reduces effective sample size:

```
n_effective = n_total / DE
```

**Example:**
- Total observations: n = 1000
- Design effect: DE = 2.0
- Effective sample size: n_eff = 1000 / 2.0 = 500

**Impact:** Even with 1000 observations, you only have the power of 500 independent observations!

---

## Available Cluster Tests

ABTK provides 4 cluster tests:

### 1. ClusteredTTest

**Use for:** Continuous metrics in cluster-randomized experiments

**Method:** OLS regression with cluster-robust standard errors

**Model:**
```
Y_ij = β₀ + β₁×Treatment_j + ε_ij
```

**When to use:**
- Continuous metric (revenue, engagement time, etc.)
- Approximately normal data
- No covariates available

**Example:**
```python
from core.data_types import SampleData
from tests.parametric import ClusteredTTest

# Geo experiment: 10 cities
control = SampleData(
    data=control_revenue,      # 500 observations
    clusters=control_cities,   # 5 clusters (cities 1-5)
    name="Control"
)
treatment = SampleData(
    data=treatment_revenue,    # 500 observations
    clusters=treatment_cities, # 5 clusters (cities 6-10)
    name="Treatment"
)

test = ClusteredTTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"ICC: {result.method_params['icc_control']:.3f}")
print(f"Design Effect: {result.method_params['design_effect_control']:.2f}")
```

---

### 2. ClusteredAncovaTest

**Use for:** Continuous metrics with covariates (variance reduction)

**Method:** OLS with multiple covariates + cluster-robust SE

**Model:**
```
Y_ij = β₀ + β₁×Treatment_j + β₂×X1_ij + β₃×X2_ij + ... + ε_ij
```

**When to use:**
- Continuous metric
- Have covariates (pre-experiment data, demographics, etc.)
- Want variance reduction (narrower CI)

**Variance reduction:** Typically 30-50% narrower CI vs ClusteredTTest

**Example:**
```python
from tests.parametric import ClusteredAncovaTest

# Same as ClusteredTTest but with pre-experiment revenue as covariate
control = SampleData(
    data=control_revenue,
    covariates=control_pre_revenue,  # Covariate for variance reduction
    clusters=control_cities,
    name="Control"
)
treatment = SampleData(
    data=treatment_revenue,
    covariates=treatment_pre_revenue,
    clusters=treatment_cities,
    name="Treatment"
)

test = ClusteredAncovaTest(
    alpha=0.05,
    test_type="relative",
    validate_assumptions=True  # Check VIF, normality
)
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"CI width: {result.ci_length:.4f}")  # Narrower than ClusteredTTest!
print(f"VIF: {result.method_params['vif_values']}")  # Check multicollinearity
```

**Alias:** `ClusteredOLSTest` (same as `ClusteredAncovaTest`)

---

### 3. ClusteredZTest

**Use for:** Proportions (CTR, CVR) in cluster-randomized experiments

**Method:** Linear probability model with cluster-robust SE

**Model:**
```
Pr(Y_ij = 1) = β₀ + β₁×Treatment_j + ε_ij
```

**When to use:**
- Binary outcome (click/no-click, convert/no-convert)
- Cluster-randomized design
- Proportions between 0.05 and 0.95 (works best)

**Data format:** Use `SampleData` with binary (0/1) data, NOT `ProportionData`

**Example:**
```python
from tests.parametric import ClusteredZTest

# CTR experiment: 10 cities
# Need individual-level binary data (0/1) to preserve clustering
control = SampleData(
    data=[1, 0, 1, 1, 0, 0, ...],  # Binary: 1=click, 0=no-click
    clusters=[1, 1, 1, 2, 2, 2, ...],  # City assignments
    name="Control"
)
treatment = SampleData(
    data=[1, 1, 1, 0, 1, 1, ...],
    clusters=[6, 6, 6, 7, 7, 7, ...],
    name="Treatment"
)

test = ClusteredZTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Relative effect: {result.effect:.2%}")
print(f"Control CTR: {result.method_params['proportion_control']:.2%}")
print(f"Treatment CTR: {result.method_params['proportion_treatment']:.2%}")
print(f"Absolute difference: {result.method_params['absolute_difference']:.4f}")
```

**Warning:** Test warns if proportions < 0.05 or > 0.95 (linear probability model less accurate)

---

### 4. ClusteredBootstrapTest

**Use for:** Non-normal data, outliers, or unknown distribution

**Method:** Cluster bootstrap (resamples clusters, not individuals)

**When to use:**
- Cluster-randomized design
- Non-normal data (skewed, heavy-tailed)
- Outliers present
- Unknown distribution
- Want distribution-free inference

**Advantage:** No assumptions about data distribution

**Disadvantage:** Computationally intensive (recommend n_samples >= 10000)

**Example:**
```python
from tests.nonparametric import ClusteredBootstrapTest
import numpy as np

# Geo experiment with non-normal data (exponential)
control = SampleData(
    data=control_data,  # Exponential distribution
    clusters=control_cities,
    name="Control"
)
treatment = SampleData(
    data=treatment_data,
    clusters=treatment_cities,
    name="Treatment"
)

# Custom statistic: median instead of mean (robust to outliers)
test = ClusteredBootstrapTest(
    alpha=0.05,
    stat_func=np.median,  # Or np.mean, lambda x: np.percentile(x, 90), etc.
    n_samples=10000,      # Higher for cluster bootstrap
    test_type="relative"
)
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"Bootstrap is normal: {result.method_params['bootstrap_is_normal']}")
```

---

## Getting Started

### Step 1: Prepare Your Data

Ensure your data includes cluster assignments:

```python
from core.data_types import SampleData
import numpy as np

# Option 1: Manual construction
control = SampleData(
    data=[100, 105, 110, 95, 98, ...],  # Your metric
    clusters=[1, 1, 1, 2, 2, ...],      # Cluster IDs
    name="Control"
)

# Option 2: From pandas DataFrame
import pandas as pd
from utils.dataframe_helpers import sample_data_from_dataframe

df = pd.DataFrame({
    'variant': ['control', 'control', 'treatment', 'treatment', ...],
    'city': [1, 1, 2, 2, ...],  # Cluster IDs
    'revenue': [100, 105, 95, 110, ...]
})

samples = sample_data_from_dataframe(
    df,
    group_col='variant',
    metric_col='revenue',
    cluster_col='city'  # Specify cluster column
)
```

### Step 2: Calculate ICC

Check if clustering matters:

```python
from utils.cluster_utils import calculate_icc

# Calculate ICC for control group
icc_control = calculate_icc(
    data=control.data,
    clusters=control.clusters,
    method="anova"
)

print(f"ICC: {icc_control:.3f}")

if icc_control < 0.01:
    print("→ Use regular tests (TTest, ZTest, BootstrapTest)")
else:
    print("→ Use cluster tests (ClusteredTTest, etc.)")
```

### Step 3: Choose and Run Test

```python
from tests.parametric import ClusteredTTest

test = ClusteredTTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
print(f"P-value: {result.pvalue:.4f}")
print(f"Significant: {result.reject}")
```

### Step 4: Interpret Cluster Diagnostics

```python
# All cluster tests return diagnostics
print("\n--- Cluster Diagnostics ---")
print(f"N clusters (control): {result.method_params['n_clusters_control']}")
print(f"N clusters (treatment): {result.method_params['n_clusters_treatment']}")
print(f"ICC (control): {result.method_params['icc_control']:.3f}")
print(f"Design Effect (control): {result.method_params['design_effect_control']:.2f}")
print(f"Cluster size CV (control): {result.method_params['cluster_size_cv_control']:.2f}")

# Check warnings
if result.method_params['icc_control'] > 0.15:
    print("⚠️ High ICC - clustering strongly matters")

if result.method_params['cluster_size_cv_control'] > 0.5:
    print("⚠️ High cluster size imbalance")
```

---

## Checking for Clustering Effects

### Method 1: Calculate ICC Directly

```python
from utils.cluster_utils import calculate_icc

icc = calculate_icc(data, clusters, method="anova")

if icc < 0.01:
    print("No meaningful clustering - use regular tests")
elif icc < 0.05:
    print("Small clustering effect - consider cluster tests")
elif icc < 0.15:
    print("Moderate clustering - use cluster tests")
else:
    print("Strong clustering - definitely use cluster tests")
```

### Method 2: Compare Regular vs Cluster Test

```python
from tests.parametric import TTest, ClusteredTTest

# Regular test (ignores clustering)
regular_test = TTest(alpha=0.05, test_type="relative")
regular_result = regular_test.compare([control, treatment])[0]

# Cluster test (accounts for clustering)
cluster_test = ClusteredTTest(alpha=0.05, test_type="relative")
cluster_result = cluster_test.compare([control, treatment])[0]

print(f"Regular CI: [{regular_result.left_bound:.3f}, {regular_result.right_bound:.3f}]")
print(f"Cluster CI: [{cluster_result.left_bound:.3f}, {cluster_result.right_bound:.3f}]")
print(f"CI width ratio: {cluster_result.ci_length / regular_result.ci_length:.2f}x")

# If cluster CI is much wider (ratio > 1.2), clustering matters
if cluster_result.ci_length / regular_result.ci_length > 1.2:
    print("→ Clustering matters! Use cluster tests.")
else:
    print("→ Little clustering. Regular tests OK.")
```

### Method 3: Use Validation Utilities

```python
from utils.cluster_utils import validate_clusters

# Comprehensive validation
validation = validate_clusters(
    sample1=control,
    sample2=treatment,
    min_clusters=5,
    warn_cv=0.5
)

print(f"Valid: {validation['valid']}")
print(f"ICC (control): {validation['icc_1']:.3f}")
print(f"Design Effect (control): {validation['design_effect_1']:.2f}")
print(f"Warnings: {validation['warnings']}")
print(f"Errors: {validation['errors']}")
```

---

## Choosing the Right Test

Use this decision tree:

```
Do you have cluster-randomized design?
├─ Yes (cities, stores randomized)
│   │
│   ├─ Data type?
│   │   ├─ Proportions (CTR, CVR) → ClusteredZTest
│   │   └─ Continuous (revenue, time, etc.)
│   │       │
│   │       ├─ Have covariates? (for variance reduction)
│   │       │   ├─ Yes → ClusteredAncovaTest
│   │       │   └─ No
│   │       │       ├─ Data distribution?
│   │       │       │   ├─ Normal → ClusteredTTest
│   │       │       │   └─ Non-normal/outliers → ClusteredBootstrapTest
│   │       │
│   └─ Alternative: ClusteredBootstrapTest (always works, but slower)
│
└─ No (individual randomization)
    └─ Use regular tests (TTest, ZTest, BootstrapTest, etc.)
```

### Quick Reference Table

| Scenario | Test | Assumptions |
|----------|------|-------------|
| Cluster + continuous + normal | ClusteredTTest | Normality |
| Cluster + continuous + covariates | ClusteredAncovaTest | Normality, linear relationship |
| Cluster + proportions | ClusteredZTest | 0.05 < p < 0.95 |
| Cluster + non-normal | ClusteredBootstrapTest | None |
| Cluster + outliers | ClusteredBootstrapTest | None |
| Cluster + unknown distribution | ClusteredBootstrapTest | None |

---

## Examples

### Example 1: Geo Experiment (Cities)

```python
from core.data_types import SampleData
from tests.parametric import ClusteredTTest
import numpy as np

# Generate synthetic geo experiment data
np.random.seed(42)

# Control: 5 cities, 100 users per city
control_data = []
control_clusters = []
for city_id in range(1, 6):
    # City baseline effect + individual variation
    city_effect = np.random.normal(100, 10)
    city_data = city_effect + np.random.normal(0, 15, 100)
    control_data.extend(city_data)
    control_clusters.extend([city_id] * 100)

# Treatment: 5 cities, 100 users per city, +5% effect
treatment_data = []
treatment_clusters = []
for city_id in range(6, 11):
    city_effect = np.random.normal(105, 10)  # +5% treatment effect
    city_data = city_effect + np.random.normal(0, 15, 100)
    treatment_data.extend(city_data)
    treatment_clusters.extend([city_id] * 100)

# Create SampleData
control = SampleData(
    data=control_data,
    clusters=control_clusters,
    name="Control Cities"
)
treatment = SampleData(
    data=treatment_data,
    clusters=treatment_clusters,
    name="Treatment Cities"
)

# Run cluster test
test = ClusteredTTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Treatment Effect: {result.effect:.2%}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
print(f"P-value: {result.pvalue:.4f}")
print(f"Significant: {'Yes' if result.reject else 'No'}")
print(f"\nCluster Diagnostics:")
print(f"  ICC: {result.method_params['icc_control']:.3f}")
print(f"  Design Effect: {result.method_params['design_effect_control']:.2f}")
print(f"  N Clusters: {result.method_params['n_clusters_control']}")
```

### Example 2: Store Experiment with Covariates

```python
from tests.parametric import ClusteredAncovaTest

# Stores with historical sales as covariate
control = SampleData(
    data=control_sales,           # Current period sales
    covariates=control_pre_sales,  # Pre-experiment sales (covariate)
    clusters=control_store_ids,
    name="Control Stores"
)
treatment = SampleData(
    data=treatment_sales,
    covariates=treatment_pre_sales,
    clusters=treatment_store_ids,
    name="Treatment Stores"
)

test = ClusteredAncovaTest(
    alpha=0.05,
    test_type="relative",
    validate_assumptions=True  # Check VIF, normality
)
results = test.compare([control, treatment])

result = results[0]
print(f"Effect (with variance reduction): {result.effect:.2%}")
print(f"CI width: {result.ci_length:.4f}")
print(f"Covariate coefficients: {result.method_params['covariate_coefficients']}")

# Variance reduction
# Compare with ClusteredTTest (without covariates)
from tests.parametric import ClusteredTTest
test_no_cov = ClusteredTTest(alpha=0.05, test_type="relative")
result_no_cov = test_no_cov.compare([control, treatment])[0]

reduction = 1 - (result.ci_length / result_no_cov.ci_length)
print(f"Variance reduction: {reduction:.1%}")  # e.g., 40% narrower CI
```

### Example 3: CTR Experiment (Proportions)

```python
from tests.parametric import ClusteredZTest

# CTR by city: need individual-level binary data
control = SampleData(
    data=[1, 0, 1, 1, 0, 0, ...],  # 1=click, 0=no-click
    clusters=[1, 1, 1, 2, 2, 2, ...],  # City IDs
    name="Control"
)
treatment = SampleData(
    data=[1, 1, 1, 0, 1, 1, ...],
    clusters=[6, 6, 6, 7, 7, 7, ...],
    name="Treatment"
)

test = ClusteredZTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Relative CTR lift: {result.effect:.2%}")
print(f"Control CTR: {result.method_params['proportion_control']:.2%}")
print(f"Treatment CTR: {result.method_params['proportion_treatment']:.2%}")
```

### Example 4: Non-Normal Data (Bootstrap)

```python
from tests.nonparametric import ClusteredBootstrapTest

# Exponential data (heavily skewed)
control = SampleData(
    data=np.random.exponential(100, 500),
    clusters=np.repeat(range(1, 6), 100),
    name="Control"
)
treatment = SampleData(
    data=np.random.exponential(105, 500),
    clusters=np.repeat(range(6, 11), 100),
    name="Treatment"
)

# Use median (robust to outliers)
test = ClusteredBootstrapTest(
    alpha=0.05,
    stat_func=np.median,
    n_samples=10000,
    test_type="relative"
)
results = test.compare([control, treatment])

result = results[0]
print(f"Median effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"Bootstrap distribution normal: {result.method_params['bootstrap_is_normal']}")
```

---

## Common Pitfalls

### Pitfall 1: Using Regular Tests with Cluster Data

**Problem:** Ignoring clustering leads to inflated Type I error (false positives)

**Example:**
```python
# ❌ WRONG: Regular test with cluster data
from tests.parametric import TTest

test = TTest(alpha=0.05)
result = test.compare([control, treatment])[0]
# CI is too narrow, p-value is too optimistic!

# ✅ CORRECT: Cluster test
from tests.parametric import ClusteredTTest

test = ClusteredTTest(alpha=0.05)
result = test.compare([control, treatment])[0]
# CI accounts for clustering, p-value is correct
```

**Impact:** Regular tests can claim significance when there isn't any!

### Pitfall 2: Too Few Clusters

**Problem:** Need at least 5 clusters per group for reliable results

```python
# ❌ WRONG: Only 3 clusters per group
control = SampleData(
    data=[...],
    clusters=[1, 1, 1, 2, 2, 3, 3],  # Only 3 clusters
    name="Control"
)

# Test will WARN (min_clusters=5 by default) or ERROR (if < 3)
test = ClusteredTTest(alpha=0.05, min_clusters=5)
```

**Solution:**
- Increase number of clusters (recommended: 10+ per group)
- Or reduce min_clusters threshold (not recommended)

### Pitfall 3: Imbalanced Cluster Sizes

**Problem:** Large variation in cluster sizes reduces power

```python
# Check cluster size imbalance
print(f"Cluster size CV: {control.cluster_size_cv:.2f}")

if control.cluster_size_cv > 0.5:
    print("⚠️ Warning: Cluster sizes are imbalanced")
    print("Consider:")
    print("  1. Rebalancing clusters (if possible)")
    print("  2. Dropping very small/large clusters")
    print("  3. Using weighted regression (future feature)")
```

### Pitfall 4: Using ProportionData for ClusteredZTest

**Problem:** ClusteredZTest needs individual-level data to preserve clustering

```python
# ❌ WRONG: ProportionData loses cluster structure
from core.data_types import ProportionData

control = ProportionData(successes=50, trials=100, name="Control")
# Can't do cluster test - no cluster information!

# ✅ CORRECT: SampleData with binary data
control = SampleData(
    data=[1, 0, 1, ...],  # Individual-level binary outcomes
    clusters=[1, 1, 2, ...],  # Cluster assignments
    name="Control"
)
```

### Pitfall 5: Not Checking ICC

**Problem:** Using cluster tests when ICC ≈ 0 (no clustering)

```python
from utils.cluster_utils import calculate_icc

icc = calculate_icc(control.data, control.clusters)

if icc < 0.01:
    print("ICC is very low - clustering doesn't matter")
    print("Use regular tests for better power")
```

**Impact:** Cluster tests are more conservative (lower power) when ICC ≈ 0

---

## References

### Statistical Methods

1. **Donner, A., & Klar, N. (2000).** *Design and Analysis of Cluster Randomization Trials in Health Research.* Arnold Publishers.
   - Comprehensive textbook on cluster-randomized trials
   - Covers sample size calculation, analysis methods

2. **Hayes, R. J., & Moulton, L. H. (2017).** *Cluster Randomised Trials.* Chapman and Hall/CRC.
   - Modern treatment of cluster trials
   - Includes practical examples and R code

3. **Cameron, A. C., & Miller, D. L. (2015).** *A Practitioner's Guide to Cluster-Robust Inference.* Journal of Human Resources, 50(2), 317-372.
   - Practical guide to cluster-robust standard errors
   - Addresses common questions and pitfalls

### Cluster Bootstrap

4. **Field, C. A., & Welsh, A. H. (2007).** *Bootstrapping Clustered Data.* Journal of the Royal Statistical Society: Series B, 69(3), 369-390.
   - Theory and applications of cluster bootstrap
   - Compares wild bootstrap, pairs bootstrap, residual bootstrap

5. **Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008).** *Bootstrap-Based Improvements for Inference with Clustered Errors.* Review of Economics and Statistics, 90(3), 414-427.
   - Shows cluster bootstrap often outperforms asymptotic methods
   - Especially important for small number of clusters

### Software Implementations

- **R:** `lme4::lmer()`, `multcomp` package, `clubSandwich` package
- **Stata:** `regress, cluster()`, `bootstrap, cluster()`, `mixed`
- **Python:** `statsmodels` (cluster SE), `linearmodels` package

### Industry Use Cases

- **Uber:** Geo experiments (cities as clusters)
- **Airbnb:** Market-level experiments
- **Microsoft:** Server-based experiments
- **Meta:** Regional experiments

---

## Next Steps

- **Learn more:** See [Test Selection Guide](test-selection.md) for choosing tests
- **Try examples:** Run [cluster_experiments_example.py](../../examples/cluster_experiments_example.py)
- **Plan experiments:** See [Experiment Planning Guide](experiment-planning.md) for sample size
- **Advanced:** See [Variance Reduction Guide](variance-reduction.md) for CUPED/ANCOVA

---

**Questions or feedback?** Open an issue at https://github.com/alexeiveselov92/abtk/issues
