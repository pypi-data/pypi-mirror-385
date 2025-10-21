# ANCOVA Guide

**ANCOVA (Analysis of Covariance)** is the most powerful variance reduction method in ABTK. It uses multiple covariates and provides comprehensive diagnostics to validate assumptions.

## Overview

**What is ANCOVA?**
- Statistical test that combines ANOVA with regression
- Adjusts for **multiple covariates** simultaneously
- Provides **diagnostic tests** for assumptions
- Maximizes variance reduction

**When to use:**
- ✅ Have multiple pre-experiment covariates
- ✅ Want maximum variance reduction
- ✅ Need diagnostic validation
- ✅ Large enough sample size (n > 10 * (covariates + 2))

---

## How ANCOVA Works

### The Model

ANCOVA fits a linear regression model:

```
Y = β₀ + β₁*Treatment + β₂*Covariate₁ + β₃*Covariate₂ + ... + ε
```

**Components:**
- `Y`: Outcome metric (e.g., revenue)
- `β₀`: Intercept
- `β₁`: Treatment effect (what we care about!)
- `β₂, β₃, ...`: Covariate coefficients
- `ε`: Residual error

**Process:**
1. Fit regression model
2. Test if `β₁` (treatment effect) is significant
3. Adjust for covariates → reduced variance → narrower CI

### Versus CUPED

| Feature | CUPED | ANCOVA |
|---------|-------|--------|
| Covariates | 1 | Multiple |
| Method | Analytical adjustment | Regression |
| Diagnostics | No | Yes (VIF, normality, etc.) |
| Complexity | Simple | Complex |
| Assumptions | Fewer | More |

**Rule of thumb:** Use CUPED for 1 covariate, ANCOVA for multiple.

---

## Basic Usage

```python
from core.data_types import SampleData
from tests.parametric import AncovaTest
import numpy as np

# Create data with multiple covariates
control = SampleData(
    data=[100, 110, 95, 105, 98, 102, 107, 103],
    covariates=[
        [90, 25, 100],   # [baseline_revenue, age, tenure_days]
        [100, 30, 150],
        [85, 22, 80],
        [95, 28, 120],
        [88, 26, 90],
        [92, 24, 110],
        [97, 27, 130],
        [93, 23, 95]
    ],
    name="Control"
)

treatment = SampleData(
    data=[105, 115, 100, 110, 103, 108, 112, 109],
    covariates=[
        [92, 26, 105],
        [102, 31, 155],
        [87, 23, 85],
        [97, 29, 125],
        [90, 27, 95],
        [94, 25, 115],
        [99, 28, 135],
        [95, 24, 100]
    ],
    name="Treatment"
)

# Run ANCOVA with diagnostics
test = AncovaTest(
    alpha=0.05,
    test_type="relative",
    validate_assumptions=True,  # Run diagnostic tests
    check_interactions=False    # Skip interaction tests (faster)
)

results = test.compare([control, treatment])
result = results[0]

print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
print(f"Significant: {result.reject}")
```

---

## Choosing Covariates

### What Makes a Good Covariate?

**Essential criteria:**
1. **Pre-experiment** - measured before randomization
2. **Correlated with outcome** - r > 0.3 (ideally > 0.5)
3. **Not affected by treatment** - independent of treatment assignment
4. **Low multicollinearity** - not too correlated with other covariates

### Example Covariate Sets

**E-commerce experiment:**
```python
covariates = np.column_stack([
    baseline_revenue,        # Revenue in past 30 days (r=0.7)
    num_past_purchases,      # Purchase count (r=0.6)
    days_since_signup,       # Account age (r=0.4)
    avg_order_value          # Typical order size (r=0.5)
])
```

**Content platform:**
```python
covariates = np.column_stack([
    baseline_pageviews,      # Pageviews last month (r=0.8)
    num_sessions,            # Session count (r=0.7)
    avg_session_duration,    # Time per session (r=0.5)
    account_age_days         # User tenure (r=0.3)
])
```

**SaaS product:**
```python
covariates = np.column_stack([
    baseline_feature_usage,  # Product usage (r=0.75)
    num_logins_last_month,   # Login frequency (r=0.6)
    plan_tier_encoded,       # Subscription level (r=0.4)
    days_since_activation    # Tenure (r=0.3)
])
```

### How Many Covariates?

**Sample size requirement:**
```
n > 10 * (number_of_covariates + 2)
```

**Examples:**
- 3 covariates → need n > 50 per group
- 5 covariates → need n > 70 per group
- 10 covariates → need n > 120 per group

**Rule of thumb:** Start with 3-5 most correlated covariates.

---

## Diagnostics

ANCOVA assumes:
1. **Linearity** - covariates linearly related to outcome
2. **Normality** - residuals are normally distributed
3. **Homoscedasticity** - constant variance of residuals
4. **No multicollinearity** - covariates not too correlated
5. **Independence** - observations are independent

**ABTK automatically checks these when `validate_assumptions=True`!**

### Variance Inflation Factor (VIF)

**VIF** measures multicollinearity (correlation between covariates).

**Interpretation:**
- VIF < 5: Good (low multicollinearity)
- VIF 5-10: Moderate (acceptable)
- VIF > 10: High (problematic, remove covariates)

**Example:**
```python
test = AncovaTest(validate_assumptions=True)
results = test.compare([control, treatment])

# Check VIF
if hasattr(results[0], 'diagnostics'):
    vif = results[0].diagnostics.get('vif')
    print(f"VIF values: {vif}")

    for i, v in enumerate(vif):
        if v > 10:
            print(f"Warning: Covariate {i} has high VIF ({v:.2f})")
```

**If VIF > 10:** Remove one of the correlated covariates.

### Normality Tests

ANCOVA tests if **residuals** are normal (not original data!).

**Tests performed:**
- Shapiro-Wilk test (if n < 5000)
- Kolmogorov-Smirnov test (if n ≥ 5000)

**Interpretation:**
- p > 0.05: Residuals are normal ✅
- p < 0.05: Residuals may be non-normal ⚠️

**Example:**
```python
if hasattr(results[0], 'diagnostics'):
    normality = results[0].diagnostics.get('normality_test')
    print(f"Normality test p-value: {normality['pvalue']:.4f}")

    if normality['pvalue'] < 0.05:
        print("Warning: Residuals may not be normal")
        print("Consider using Post-Normed Bootstrap instead")
```

**If residuals non-normal:** Use `PostNormedBootstrapTest` instead.

### Homoscedasticity (Levene's Test)

Tests if variance is constant across groups.

**Interpretation:**
- p > 0.05: Homoscedasticity assumption holds ✅
- p < 0.05: Heteroscedasticity detected ⚠️

**Example:**
```python
if hasattr(results[0], 'diagnostics'):
    levene = results[0].diagnostics.get('levene_test')
    print(f"Levene's test p-value: {levene:.4f}")

    if levene < 0.05:
        print("Warning: Unequal variances detected")
```

**If heteroscedastic:** Results may still be valid, but be cautious.

---

## Interactions

### What Are Interactions?

**Interaction** means the effect of treatment depends on covariate value.

**Example:**
- Treatment works better for high-tenure users
- Effect is different for mobile vs desktop

**ANCOVA can test for interactions** with `check_interactions=True`.

### Checking Interactions

```python
test = AncovaTest(
    alpha=0.05,
    validate_assumptions=True,
    check_interactions=True  # Enable interaction tests
)

results = test.compare([control, treatment])

# Check for significant interactions
if hasattr(results[0], 'diagnostics'):
    interactions = results[0].diagnostics.get('interactions')
    if interactions:
        print(f"Interaction p-values: {interactions}")

        if any(p < 0.05 for p in interactions.values()):
            print("Warning: Significant interactions detected!")
            print("Treatment effect may vary by covariate")
```

**If interactions exist:**
- Consider stratified analysis (analyze subgroups separately)
- Or use more complex models

**Default:** `check_interactions=False` (faster, assumes no interactions)

---

## Sample Size Considerations

### Minimum Sample Size

**Formula:**
```
n_min = 10 * (num_covariates + 2)
```

**Examples:**
- 1 covariate: n > 30 per group
- 3 covariates: n > 50 per group
- 5 covariates: n > 70 per group
- 10 covariates: n > 120 per group

**Why?** Need enough data points to reliably estimate all regression coefficients.

### Power Analysis

ANCOVA increases **statistical power** through variance reduction:

**Example:**
```python
# Without covariates: need n=1000 to detect 2% effect
# With ANCOVA (r²=0.5): need n=500 to detect same effect

# Power gain ≈ 1 / (1 - R²)
# where R² is variance explained by covariates
```

**Typical R² by correlation:**
- r = 0.5 → R² = 0.25 → 33% sample size reduction
- r = 0.7 → R² = 0.49 → 50% sample size reduction
- r = 0.9 → R² = 0.81 → 81% sample size reduction

---

## Practical Examples

### Example 1: E-commerce Revenue

```python
import numpy as np
from core.data_types import SampleData
from tests.parametric import AncovaTest, TTest

np.random.seed(42)
n = 500

# Simulate data
baseline_rev = np.random.normal(100, 20, n*2)
age = np.random.randint(18, 65, n*2)
tenure = np.random.randint(1, 1000, n*2)

# Current revenue correlated with baseline and age
current_rev = (
    0.6 * baseline_rev +
    0.3 * age +
    0.1 * tenure +
    np.random.normal(0, 10, n*2)
)
current_rev[n:] += 5  # Treatment effect: +$5

# Create samples with multiple covariates
control = SampleData(
    data=current_rev[:n],
    covariates=np.column_stack([baseline_rev[:n], age[:n], tenure[:n]]),
    name="Control"
)

treatment = SampleData(
    data=current_rev[n:],
    covariates=np.column_stack([baseline_rev[n:], age[n:], tenure[n:]]),
    name="Treatment"
)

# Compare: Regular T-Test vs ANCOVA
print("Regular T-Test:")
test_regular = TTest(alpha=0.05, test_type="absolute")
result_regular = test_regular.compare([control, treatment])[0]
print(f"  Effect: ${result_regular.effect:.2f}")
print(f"  P-value: {result_regular.pvalue:.4f}")
print(f"  CI width: ${result_regular.ci_length:.2f}")

print("\nANCOVA (3 covariates):")
test_ancova = AncovaTest(alpha=0.05, test_type="absolute", validate_assumptions=True)
result_ancova = test_ancova.compare([control, treatment])[0]
print(f"  Effect: ${result_ancova.effect:.2f}")
print(f"  P-value: {result_ancova.pvalue:.4f}")
print(f"  CI width: ${result_ancova.ci_length:.2f}")
print(f"  CI reduction: {(1 - result_ancova.ci_length/result_regular.ci_length):.1%}")

# Check diagnostics
if hasattr(result_ancova, 'diagnostics'):
    print(f"\nDiagnostics:")
    diag = result_ancova.diagnostics
    print(f"  VIF: {diag.get('vif', 'N/A')}")
    print(f"  Normality p-value: {diag.get('normality_test', {}).get('pvalue', 'N/A')}")
```

### Example 2: Detecting Multicollinearity

```python
# Bad example: highly correlated covariates
baseline_rev = np.random.normal(100, 20, 100)
total_spent = baseline_rev * 1.1 + np.random.normal(0, 1, 100)  # r ≈ 0.99!
num_purchases = baseline_rev / 10 + np.random.normal(0, 0.5, 100)  # r ≈ 0.95!

# All three are basically the same information
covariates = np.column_stack([baseline_rev, total_spent, num_purchases])

control = SampleData(
    data=np.random.normal(100, 10, 100),
    covariates=covariates,
    name="Control"
)

test = AncovaTest(validate_assumptions=True)
results = test.compare([control, treatment])

# VIF will be very high!
if hasattr(results[0], 'diagnostics'):
    vif = results[0].diagnostics.get('vif')
    print(f"VIF: {vif}")  # Will show VIF > 10
    print("High multicollinearity detected! Remove redundant covariates.")
```

**Solution:** Keep only one (e.g., baseline_rev), remove others.

---

## Advanced Features

### Stratified Analysis

If interactions exist, analyze subgroups separately:

```python
# Detected interaction: treatment works differently for high/low tenure users

# Split by tenure
high_tenure_control = SampleData(data=..., covariates=..., name="Control (High Tenure)")
high_tenure_treatment = SampleData(data=..., covariates=..., name="Treatment (High Tenure)")

low_tenure_control = SampleData(data=..., covariates=..., name="Control (Low Tenure)")
low_tenure_treatment = SampleData(data=..., covariates=..., name="Treatment (Low Tenure)")

# Separate tests
test = AncovaTest(alpha=0.05)
results_high = test.compare([high_tenure_control, high_tenure_treatment])
results_low = test.compare([low_tenure_control, low_tenure_treatment])

print(f"High tenure effect: {results_high[0].effect:.2%}")
print(f"Low tenure effect: {results_low[0].effect:.2%}")
```

### Multiple Testing Correction

When testing multiple outcomes with ANCOVA:

```python
from utils.corrections import adjust_pvalues

# Test multiple metrics with ANCOVA
metrics = ['revenue', 'orders', 'aov']
all_results = []

for metric in metrics:
    control_data = SampleData(data=control_metrics[metric], covariates=covariates)
    treatment_data = SampleData(data=treatment_metrics[metric], covariates=covariates)

    test = AncovaTest(alpha=0.05)
    results = test.compare([control_data, treatment_data])
    all_results.extend(results)

# Apply correction
adjusted = adjust_pvalues(all_results, method="holm")

for result in adjusted:
    print(f"{result.name_1} vs {result.name_2}:")
    print(f"  Adjusted p-value: {result.pvalue:.4f}")
    print(f"  Significant: {result.reject}")
```

---

## Troubleshooting

### Problem 1: High VIF

**Symptom:** VIF > 10 for some covariates

**Cause:** Covariates too correlated (multicollinearity)

**Solution:**
1. Check correlation matrix
2. Remove one of the correlated covariates
3. Rerun ANCOVA

```python
import numpy as np

# Check correlation between covariates
corr_matrix = np.corrcoef(covariates.T)
print(corr_matrix)

# If two covariates have r > 0.9, remove one
```

### Problem 2: Non-Normal Residuals

**Symptom:** Normality test p < 0.05

**Cause:** Data is skewed or has outliers

**Solution:** Use Post-Normed Bootstrap instead
```python
from tests.nonparametric import PostNormedBootstrapTest

test = PostNormedBootstrapTest(alpha=0.05, n_samples=10000)
results = test.compare([control, treatment])
```

### Problem 3: Sample Size Too Small

**Symptom:** Unstable estimates, warnings

**Cause:** n < 10 * (covariates + 2)

**Solution:**
1. Reduce number of covariates
2. Collect more data
3. Use CUPED (1 covariate) instead

### Problem 4: Significant Interactions

**Symptom:** Interaction tests show p < 0.05

**Cause:** Treatment effect varies by covariate

**Solution:**
1. Stratified analysis (analyze subgroups)
2. More complex model (beyond ABTK scope)
3. Report interaction and interpret carefully

---

## Best Practices

### 1. Always Run Diagnostics

```python
# Always validate assumptions
test = AncovaTest(validate_assumptions=True)
```

### 2. Check VIF First

```python
# Before running full test, check multicollinearity
import numpy as np

corr_matrix = np.corrcoef(covariates.T)
if np.any(np.abs(corr_matrix - np.eye(len(corr_matrix))) > 0.9):
    print("Warning: High correlation between covariates")
```

### 3. Start with Fewer Covariates

```python
# Start with 3-5 most correlated covariates
# Don't add everything just because you can!
```

### 4. Document Covariate Selection

```python
# Document why you chose these covariates
covariates = np.column_stack([
    baseline_revenue,     # r=0.75 with outcome
    user_tenure,          # r=0.45 with outcome
    num_past_purchases    # r=0.60 with outcome
])
# Total variance explained (R²) ≈ 0.65
```

### 5. Compare with and without Covariates

```python
# Always compare to regular test to see benefit
results_regular = TTest(...).compare([control, treatment])
results_ancova = AncovaTest(...).compare([control, treatment])

ci_reduction = 1 - results_ancova[0].ci_length / results_regular[0].ci_length
print(f"CI reduction from ANCOVA: {ci_reduction:.1%}")
```

---

## Common Mistakes

### ❌ Mistake 1: Too Many Covariates

```python
# Bad: 10 covariates with n=50
covariates = np.column_stack([cov1, cov2, ..., cov10])
# Need n > 120!
```

**Solution:** Use fewer covariates or more data

### ❌ Mistake 2: Post-Treatment Covariates

```python
# Bad: Using data from AFTER randomization
baseline = user_behavior_during_experiment  # Wrong!
```

**Solution:** Only use pre-experiment data

### ❌ Mistake 3: Ignoring Diagnostics

```python
# Bad: Not checking assumptions
test = AncovaTest(validate_assumptions=False)
```

**Solution:** Always validate assumptions

### ❌ Mistake 4: Redundant Covariates

```python
# Bad: Including revenue, total_spent, avg_order_value
# All highly correlated (measuring same thing)
```

**Solution:** Check VIF, remove redundant covariates

---

## Decision Guide

### Should I Use ANCOVA?

```
Do you have covariates?
├─ No → Use TTest or Bootstrap
└─ Yes
    └─ How many covariates?
        ├─ 1 → Use CUPED (simpler)
        └─ Multiple
            └─ Sample size large enough?
                ├─ No (n < 10*(k+2)) → Use fewer covariates or CUPED
                └─ Yes
                    └─ Data normal?
                        ├─ Yes → Use ANCOVA ✓
                        └─ No → Use Post-Normed Bootstrap
```

### CUPED vs ANCOVA

| Use CUPED when: | Use ANCOVA when: |
|----------------|------------------|
| 1 covariate | Multiple covariates |
| Want simplicity | Want max variance reduction |
| Don't need diagnostics | Need validation |
| Small-medium sample | Large sample |

---

## Summary

**ANCOVA Strengths:**
- ✅ Maximum variance reduction (up to 80%)
- ✅ Handles multiple covariates
- ✅ Comprehensive diagnostics
- ✅ Detects interactions

**ANCOVA Limitations:**
- ❌ Requires larger sample size
- ❌ More complex than CUPED
- ❌ Assumes normality (use bootstrap if violated)
- ❌ Sensitive to multicollinearity

**Key Takeaways:**
1. Use for multiple covariates
2. Always validate assumptions
3. Check VIF < 10
4. Need n > 10 * (covariates + 2)
5. Compare to regular test to see benefit

**Expected benefits:**
- 50-80% CI reduction (with good covariates)
- Detect 2-3x smaller effects
- 50-70% sample size reduction

---

## Next Steps

- [Variance Reduction Guide](variance-reduction.md) - Overview of all methods
- [Parametric Tests](parametric-tests.md) - CUPED details
- [Nonparametric Tests](nonparametric-tests.md) - Post-Normed Bootstrap
- [Test Selection](test-selection.md) - Choose the right test

**Pro tip:** Start with correlation analysis and VIF checks before committing to ANCOVA!
