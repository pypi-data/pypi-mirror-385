# Parametric Tests Guide

Parametric tests make assumptions about the data distribution (typically normality) but are more powerful when those assumptions are met.

## Overview

ABTK provides 5 parametric tests:

| Test | Use Case | Assumptions | Key Feature |
|------|----------|-------------|-------------|
| **TTest** | Standard A/B test | Normality | Fast, well-understood |
| **PairedTTest** | Matched pairs | Normality of differences | Removes between-subject variability |
| **CupedTTest** | A/B with 1 covariate | Normality | Variance reduction |
| **ZTest** | Proportions (CTR, CVR) | Large sample | Binary outcomes |
| **AncovaTest** | Multiple covariates | Linearity | Maximum variance reduction + diagnostics |

---

## TTest - Independent Samples T-Test

### When to Use

Use TTest when:
- ✅ Standard A/B test with independent randomization
- ✅ Continuous metric (revenue, time, engagement)
- ✅ Data is approximately normal (or n > 30 per group)
- ✅ No historical data available
- ✅ Want fast, well-understood results

### Basic Example

```python
from core.data_types import SampleData
from tests.parametric import TTest
import numpy as np

# Generate sample data
np.random.seed(42)

control = SampleData(
    data=np.random.normal(100, 15, 1000),  # mean=100, sd=15, n=1000
    name="Control"
)

treatment = SampleData(
    data=np.random.normal(105, 15, 1000),  # 5% lift
    name="Treatment"
)

# Run t-test
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")        # 5.00%
print(f"P-value: {result.pvalue:.4f}")       # ~0.001
print(f"Significant: {result.reject}")       # True
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

### Parameters

```python
TTest(
    alpha=0.05,              # Significance level
    test_type="relative",    # "relative" (default) or "absolute"
    return_effect_distribution=False,  # Return scipy.stats distribution?
    calculate_mde=False,     # Calculate Minimum Detectable Effect?
    power=0.8,              # Target power for MDE calculation
    logger=None             # Custom logger
)
```

### Relative vs Absolute Effects

```python
# Relative effect (percentage change)
test_rel = TTest(test_type="relative")
result_rel = test_rel.compare([control, treatment])[0]
print(f"Effect: {result_rel.effect:.2%}")  # e.g., 5.0% (0.05)

# Absolute effect (raw difference)
test_abs = TTest(test_type="absolute")
result_abs = test_abs.compare([control, treatment])[0]
print(f"Effect: {result_abs.effect:.2f}")  # e.g., 5.0 units
```

**Relationship:** `absolute_effect = relative_effect * control_mean`

### Assumptions

**Normality:**
- T-test assumes data is normally distributed
- Central Limit Theorem: With n > 30, sample means are approximately normal even if data isn't
- For highly skewed data or outliers, consider Bootstrap instead

**Independence:**
- Observations must be independent (not paired or matched)
- For paired data, use PairedTTest instead

**Equal or unequal variance:**
- T-test handles both (uses Welch's correction for unequal variance)
- ABTK automatically applies appropriate correction

### When NOT to Use

❌ **Use Bootstrap instead if:**
- Data is highly skewed (e.g., revenue with extreme outliers)
- Small sample size (n < 20) with non-normal data
- Want to analyze medians or other non-mean statistics

❌ **Use ZTest instead if:**
- Analyzing proportions (CTR, conversion rate)

❌ **Use CUPED/ANCOVA instead if:**
- Have historical data that could reduce variance

---

## PairedTTest - Paired Samples T-Test

### When to Use

Use PairedTTest when:
- ✅ Matched pairs design (users matched before randomization)
- ✅ Same subjects measured twice (before/after)
- ✅ Want to remove between-subject/pair variability
- ✅ Data is approximately normal (or differences are normal)

### Matched Pairs Design

**What is matched pairs?**
1. Match users by characteristics (demographics, usage, etc.)
2. **Then** randomly assign one to control, one to treatment
3. Analyze differences within pairs

**Example scenario:**
- Match users by historical spend
- Randomize matched users to control/treatment
- Compare within-pair differences

### Basic Example

```python
from tests.parametric import PairedTTest

# Matched pairs: users matched by historical behavior
control = SampleData(
    data=[100, 105, 95, 110, 98, 102, 107, 103],
    paired_ids=[1, 2, 3, 4, 5, 6, 7, 8],  # Pair identifiers
    name="Control"
)

treatment = SampleData(
    data=[105, 110, 100, 115, 103, 108, 112, 109],
    paired_ids=[1, 2, 3, 4, 5, 6, 7, 8],  # Same pairs
    name="Treatment"
)

test = PairedTTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
```

### Key Difference from Regular T-Test

**Regular T-Test:**
- Compares group means
- Variance includes between-subject differences
- Lower power

**Paired T-Test:**
- Compares within-pair differences
- Removes between-pair variability
- Higher power (narrower CI, lower p-values)

**Example:**
```python
# Same data, different analyses
control = SampleData(data=[100, 105, 95, 110], name="Control")
treatment = SampleData(data=[105, 110, 100, 115], name="Treatment")

# Regular t-test (ignores pairing)
ttest = TTest()
result_unpaired = ttest.compare([control, treatment])[0]

# Paired t-test (uses pairing)
control_paired = SampleData(data=[100, 105, 95, 110], paired_ids=[1,2,3,4], name="Control")
treatment_paired = SampleData(data=[105, 110, 100, 115], paired_ids=[1,2,3,4], name="Treatment")

paired_ttest = PairedTTest()
result_paired = paired_ttest.compare([control_paired, treatment_paired])[0]

print(f"Unpaired CI width: {result_unpaired.ci_length:.4f}")
print(f"Paired CI width: {result_paired.ci_length:.4f}")  # Narrower!
```

### Setting up Paired Data

```python
# Option 1: Use paired_ids
control = SampleData(
    data=[100, 110, 95],
    paired_ids=[1, 2, 3],  # Match to treatment pairs
    name="Control"
)

# Option 2: Ensure same order (implicit pairing)
# First observation in control matches first in treatment, etc.
```

**Important:** paired_ids must match between control and treatment!

### Assumptions

- **Normality of differences**: The differences (treatment - control) should be approximately normal
- **Pairing is meaningful**: Users/observations are truly matched
- **No missing pairs**: Every control has matching treatment

---

## CupedTTest - CUPED T-Test

**CUPED** (Controlled-experiment Using Pre-Experiment Data) reduces variance by adjusting for pre-experiment baseline metrics. See [Variance Reduction Guide](variance-reduction.md#cuped-controlled-experiment-using-pre-experiment-data) for detailed explanation.

**Quick summary:**
- Uses historical data to reduce noise → narrower confidence intervals
- Variance reduction: `1 - ρ²` where ρ = correlation with baseline
- Example: ρ=0.7 → 51% variance reduction!

### When to Use

Use CupedTTest when:
- ✅ Have pre-experiment data (baseline metric)
- ✅ Correlation between baseline and outcome > 0.5
- ✅ Want to increase test sensitivity
- ✅ Want to detect smaller effects
- ✅ Have only 1 covariate (for multiple, use ANCOVA)

### Basic Example

```python
from tests.parametric import CupedTTest
import numpy as np

np.random.seed(42)

# Generate correlated baseline (ρ ≈ 0.7)
n = 500
baseline_control = np.random.normal(100, 15, n)
baseline_treatment = np.random.normal(100, 15, n)

# Experiment metric correlated with baseline
control = SampleData(
    data=0.7 * baseline_control + 0.3 * np.random.normal(100, 15, n),
    covariates=baseline_control,  # Historical data
    name="Control"
)

treatment = SampleData(
    data=0.7 * baseline_treatment + 0.3 * np.random.normal(105, 15, n) + 5,  # 5% lift
    covariates=baseline_treatment,
    name="Treatment"
)

# CUPED test
cuped_test = CupedTTest(alpha=0.05, min_correlation=0.5)
cuped_results = cuped_test.compare([control, treatment])

# Compare with regular t-test
regular_test = TTest(alpha=0.05)
regular_results = regular_test.compare([
    SampleData(data=control.data, name="Control"),
    SampleData(data=treatment.data, name="Treatment")
])

print("CUPED:")
print(f"  P-value: {cuped_results[0].pvalue:.4f}")
print(f"  CI width: {cuped_results[0].ci_length:.4f}")

print("\\nRegular T-Test:")
print(f"  P-value: {regular_results[0].pvalue:.4f}")
print(f"  CI width: {regular_results[0].ci_length:.4f}")

# CUPED has lower p-value and narrower CI!
```

### Parameters

```python
CupedTTest(
    alpha=0.05,
    test_type="relative",
    return_effect_distribution=False,
    calculate_mde=True,              # Calculate MDE with CUPED adjustment
    power=0.8,
    min_correlation=0.5,             # Warn if correlation < 0.5
    logger=None
)
```

### Checking Correlation

```python
# Check correlation before using CUPED
import numpy as np

corr = np.corrcoef(control.data, control.covariates)[0, 1]
print(f"Correlation: {corr:.2f}")

# Guidelines:
# ρ > 0.7: Excellent (50%+ variance reduction)
# ρ > 0.5: Good (25%+ variance reduction)
# ρ < 0.3: Don't use CUPED (minimal benefit)
```

### When NOT to Use

❌ Don't use CUPED if:
- Correlation < 0.3 (won't help much)
- No historical data available
- Historical data is unreliable/biased
- Multiple covariates (use ANCOVA instead)

---

## ZTest - Z-Test for Proportions

### When to Use

Use ZTest when:
- ✅ Binary metric (clicked/not clicked, converted/not converted)
- ✅ Proportions or rates (CTR, CVR, bounce rate)
- ✅ Large sample size (n > 30 per group)

### Basic Example

```python
from core.data_types import ProportionData
from tests.parametric import ZTest

# Click-through rate test
control = ProportionData(
    successes=450,   # Number of clicks
    trials=10000,    # Number of impressions
    name="Control"
)

treatment = ProportionData(
    successes=520,   # 520/10000 = 5.2%
    trials=10000,    # 450/10000 = 4.5%
    name="Treatment"
)

test = ZTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

result = results[0]
print(f"Control CTR: {result.value_1:.2%}")      # 4.50%
print(f"Treatment CTR: {result.value_2:.2%}")    # 5.20%
print(f"Relative lift: {result.effect:.2%}")     # 15.56%
print(f"P-value: {result.pvalue:.4f}")
```

### ProportionData vs SampleData

**Use ProportionData for:**
- Binary outcomes (0/1, True/False)
- Aggregated data (successes + trials)

**Use SampleData for:**
- Continuous metrics
- Individual observations

```python
# Binary data from individual observations
clicks = [0, 1, 0, 0, 1, 1, 0]  # Individual clicks

# Convert to ProportionData
control_prop = ProportionData(
    successes=sum(clicks),
    trials=len(clicks),
    name="Control"
)
```

### Relative vs Absolute for Proportions

```python
# Control: 4.5%, Treatment: 5.2%

# Relative (default) - percentage point change relative to baseline
test_rel = ZTest(test_type="relative")
# Effect: 15.56% = (5.2% - 4.5%) / 4.5%

# Absolute - percentage point difference
test_abs = ZTest(test_type="absolute")
# Effect: 0.7% = 5.2% - 4.5%
```

**For proportions, relative is usually preferred** (easier to interpret lift).

### Sample Size Requirements

Z-test works best with:
- **Minimum:** n > 30 per group
- **Preferred:** n > 100 per group
- **For small samples:** Consider Fisher's exact test (not in ABTK)

### Common Use Cases

**Click-Through Rate (CTR):**
```python
control_ctr = ProportionData(successes=450, trials=10000, name="Control")
treatment_ctr = ProportionData(successes=520, trials=10000, name="Treatment")
```

**Conversion Rate:**
```python
control_cvr = ProportionData(successes=150, trials=5000, name="Control")
treatment_cvr = ProportionData(successes=180, trials=5000, name="Treatment")
```

**Bounce Rate:**
```python
control_bounce = ProportionData(successes=3200, trials=10000, name="Control")
treatment_bounce = ProportionData(successes=2900, trials=10000, name="Treatment")
```

---

## AncovaTest - ANCOVA / Regression Adjustment

See [ANCOVA Guide](ancova-guide.md) for comprehensive documentation.

**Quick overview:**

### When to Use

- Multiple covariates (age, tenure, past behavior, etc.)
- Want maximum variance reduction
- Need to check for heterogeneous effects (does effect vary by segment?)
- Want diagnostic tests (VIF, normality, homoscedasticity)

### Basic Example

```python
from tests.parametric import AncovaTest
import numpy as np

n = 200
control = SampleData(
    data=np.random.normal(100, 15, n),
    covariates=np.random.normal(100, 10, (n, 3)),  # 3 covariates
    name="Control"
)

treatment = SampleData(
    data=np.random.normal(105, 15, n),
    covariates=np.random.normal(100, 10, (n, 3)),
    name="Treatment"
)

test = AncovaTest(
    alpha=0.05,
    check_interaction=True,      # Check if effect varies by covariate
    validate_assumptions=True    # Run diagnostics
)
results = test.compare([control, treatment])

result = results[0]
print(f"Effect: {result.effect:.2%}")
print(f"R-squared: {result.method_params['r_squared']:.3f}")
```

For full details, see [ANCOVA Guide](ancova-guide.md).

---

## Comparison: Which Test to Choose?

| Scenario | Recommended Test | Why |
|----------|------------------|-----|
| Standard A/B, normal data | **TTest** | Simple, fast, well-understood |
| CTR or conversion rate | **ZTest** | Designed for proportions |
| Matched pairs design | **PairedTTest** | Removes between-pair variability |
| Have 1 covariate, ρ > 0.5 | **CupedTTest** | Variance reduction |
| Have multiple covariates | **AncovaTest** | Maximum variance reduction |
| Non-normal data | **BootstrapTest** | See [Nonparametric Tests](nonparametric-tests.md) |

---

## Best Practices

### 1. Check Normality

For small samples (n < 30), check if data is approximately normal:

```python
import scipy.stats as stats

# Visual check (histogram)
import matplotlib.pyplot as plt
plt.hist(control.data, bins=30)
plt.show()

# Statistical test
statistic, pvalue = stats.shapiro(control.data)
if pvalue < 0.05:
    print("Data is not normal - consider Bootstrap")
```

### 2. Use Variance Reduction When Possible

If you have historical data:
```python
# Without variance reduction
test_basic = TTest()

# With variance reduction (if ρ > 0.5)
test_cuped = CupedTTest()  # 1 covariate
# or
test_ancova = AncovaTest()  # Multiple covariates
```

### 3. Report Effect Sizes

Always report:
- Effect estimate
- Confidence interval
- P-value
- Sample sizes

```python
result = results[0]
print(f"Treatment effect: {result.effect:.2%} "
      f"(95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}])")
print(f"P-value: {result.pvalue:.4f}")
print(f"Sample sizes: n_control={result.size_1}, n_treatment={result.size_2}")
```

### 4. Consider Practical Significance

Statistical significance ≠ practical significance

```python
result = results[0]

if result.reject:
    if result.effect > 0.05:  # 5% lift
        print("Statistically AND practically significant!")
    else:
        print("Statistically significant but effect is small")
```

---

## Next Steps

- [Nonparametric Tests Guide](nonparametric-tests.md) - Bootstrap tests for non-normal data
- [Variance Reduction Guide](variance-reduction.md) - Deep dive into CUPED and ANCOVA
- [ANCOVA Guide](ancova-guide.md) - Comprehensive ANCOVA tutorial
- [Test Selection Guide](test-selection.md) - Decision tree for choosing tests
