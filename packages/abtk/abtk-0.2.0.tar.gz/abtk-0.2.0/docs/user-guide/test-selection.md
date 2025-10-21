# Test Selection Guide

Choosing the right statistical test is crucial for valid A/B test analysis. This guide helps you select the appropriate test for your experiment.

## Decision Tree

```
START: What type of metric are you analyzing?

┌─ Proportions (CTR, CVR, conversion rate)
│  └─→ Use: ZTest
│
└─ Continuous metric (revenue, time, engagement)
   │
   ├─ Do you have paired data? (matched pairs design)
   │  │
   │  ├─ Yes: Observations are matched/paired
   │  │  │
   │  │  ├─ Assume normality?
   │  │  │  ├─ Yes → PairedTTest
   │  │  │  └─ No  → PairedBootstrapTest
   │  │  │
   │  └─ No: Independent samples
   │     │
   │     ├─ Do you have covariates (historical data)?
   │     │  │
   │     │  ├─ Yes: Have pre-experiment data
   │     │  │  │
   │     │  │  ├─ Multiple covariates → AncovaTest
   │     │  │  ├─ One covariate + normal → CupedTTest
   │     │  │  └─ One covariate + non-parametric → PostNormedBootstrapTest
   │     │  │
   │     │  └─ No: No covariates
   │     │     │
   │     │     ├─ Assume normality?
   │     │        ├─ Yes → TTest
   │     │        └─ No  → BootstrapTest
```

## Test Comparison Table

| Test | Data Type | Assumptions | Covariates | When to Use |
|------|-----------|-------------|------------|-------------|
| **TTest** | Continuous | Normality | No | Standard A/B test, normal data |
| **ZTest** | Proportions | Large sample | No | CTR, conversion rate |
| **PairedTTest** | Continuous | Normality, Pairing | Optional | Matched pairs design |
| **CupedTTest** | Continuous | Normality | Yes (1) | Variance reduction with 1 covariate |
| **AncovaTest** | Continuous | Linearity | Yes (many) | Multiple covariates, diagnostics |
| **BootstrapTest** | Continuous | None | No | Non-normal, outliers, small samples |
| **PairedBootstrapTest** | Continuous | None | No | Matched pairs, non-parametric |
| **PostNormedBootstrapTest** | Continuous | None | Yes (1) | Bootstrap + variance reduction |

## Detailed Test Descriptions

### 1. TTest - Independent Samples T-Test

**Use when:**
- Standard A/B test
- Continuous metric (revenue, time, engagement)
- Data is approximately normal
- Independent samples (no pairing)
- No historical data available

**Example:**
```python
from tests.parametric import TTest

test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])
```

**Pros:**
- Fast
- Well-understood
- Exact p-values

**Cons:**
- Assumes normality
- Less robust to outliers
- Doesn't use historical data

---

### 2. ZTest - Z-Test for Proportions

**Use when:**
- Binary metric (click/no-click, convert/no-convert)
- CTR, CVR, conversion rate
- Large sample size (n > 30)

**Example:**
```python
from core.data_types import ProportionData
from tests.parametric import ZTest

control = ProportionData(successes=450, trials=1000, name="Control")
treatment = ProportionData(successes=520, trials=1000, name="Treatment")

test = ZTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])
```

**Pros:**
- Designed for proportions
- Fast
- Handles large samples well

**Cons:**
- Only for binary outcomes
- Needs large sample

---

### 3. PairedTTest - Paired Samples T-Test

**Use when:**
- Matched pairs A/B test (users matched by historical data, then randomized)
- Same subjects measured twice (before/after)
- Want to remove between-subject variability
- Data is approximately normal

**Example:**
```python
from tests.parametric import PairedTTest

# paired_ids indicate which observations are matched
control = SampleData(
    data=[100, 105, 95, 110],
    paired_ids=[1, 2, 3, 4],
    name="Control"
)
treatment = SampleData(
    data=[105, 110, 100, 115],
    paired_ids=[1, 2, 3, 4],
    name="Treatment"
)

test = PairedTTest(alpha=0.05)
results = test.compare([control, treatment])
```

**Pros:**
- Removes between-subject noise
- More powerful than independent t-test
- Narrower confidence intervals

**Cons:**
- Requires paired design
- Assumes normality of differences
- More complex experiment setup

---

### 4. CupedTTest - CUPED T-Test

**Use when:**
- Have pre-experiment data (1 covariate)
- Want variance reduction
- Data is approximately normal
- Pre-experiment metric correlates with experiment metric (ρ > 0.5)

**Example:**
```python
from tests.parametric import CupedTTest

control = SampleData(
    data=[100, 110, 95, 105],      # Current metric
    covariates=[90, 100, 85, 95],  # Historical baseline
    name="Control"
)

test = CupedTTest(alpha=0.05)
results = test.compare([control, treatment])
```

**Pros:**
- Reduces variance → narrower CI
- More sensitive (lower p-values)
- Can detect smaller effects
- Variance reduction = (1 - ρ²)

**Cons:**
- Requires historical data
- Only 1 covariate
- Assumes normality

**When NOT to use:**
- Correlation < 0.3 (doesn't help)
- Historical data unreliable

---

### 5. AncovaTest - ANCOVA / Regression Adjustment

**Use when:**
- Have multiple covariates (pre-experiment variables)
- Want maximum variance reduction
- Need to check for heterogeneous effects (interactions)
- Want diagnostic tests for assumptions

**Example:**
```python
from tests.parametric import AncovaTest
import numpy as np

control = SampleData(
    data=[100, 110, 95, 105],
    covariates=np.array([
        [90, 5, 1],   # [historical_revenue, sessions, platform]
        [100, 8, 1],
        [85, 3, 0],
        [95, 6, 0]
    ]),
    name="Control"
)

test = AncovaTest(
    alpha=0.05,
    check_interaction=True,      # Check if effect varies by covariate
    validate_assumptions=True    # Run diagnostic tests
)
results = test.compare([control, treatment])
```

**Pros:**
- Uses multiple covariates
- Maximum variance reduction
- Checks for heterogeneous effects
- Provides diagnostics (VIF, normality, etc.)

**Cons:**
- Requires more data (n > 10 * p)
- More complex
- Assumes linearity

**Diagnostics included:**
- VIF (multicollinearity check)
- Normality tests
- Homoscedasticity tests
- Interaction tests

---

### 6. BootstrapTest - Bootstrap Resampling

**Use when:**
- Data is non-normal (skewed, heavy-tailed)
- Outliers present
- Small sample size (n < 30)
- Don't want to assume normality
- Need robust inference

**Example:**
```python
from tests.nonparametric import BootstrapTest

test = BootstrapTest(
    alpha=0.05,
    n_samples=10000,    # More samples = more accurate
    stratify=False       # Set True if strata are imbalanced
)
results = test.compare([control, treatment])
```

**Pros:**
- No normality assumption
- Robust to outliers
- Works with any statistic (mean, median, quantiles)
- Provides empirical distribution

**Cons:**
- Computationally intensive
- Requires more bootstrap samples (10k+)
- Slightly conservative for very small samples

**Stratified bootstrap:**
```python
# Use when strata are imbalanced
test = BootstrapTest(
    alpha=0.05,
    n_samples=10000,
    stratify=True,          # Balance strata
    weight_method='min'     # Conservative
)
```

---

### 7. PairedBootstrapTest - Paired Bootstrap

**Use when:**
- Matched pairs design
- Non-normal data
- Want robustness of bootstrap + power of pairing

**Example:**
```python
from tests.nonparametric import PairedBootstrapTest

control = SampleData(
    data=[100, 105, 95, 110],
    paired_ids=[1, 2, 3, 4],
    name="Control"
)

test = PairedBootstrapTest(alpha=0.05, n_samples=10000)
results = test.compare([control, treatment])
```

**Pros:**
- Combines pairing + nonparametric
- Robust to outliers
- Removes between-pair variability

**Cons:**
- Requires paired design
- Computationally intensive

---

### 8. PostNormedBootstrapTest - Post-Normalized Bootstrap

**Use when:**
- Want variance reduction (like CUPED)
- Don't want to assume normality
- Have 1 covariate
- Data has outliers or is skewed

**Example:**
```python
from tests.nonparametric import PostNormedBootstrapTest

control = SampleData(
    data=[100, 110, 95, 105],
    covariates=[90, 100, 85, 95],
    name="Control"
)

test = PostNormedBootstrapTest(alpha=0.05, n_samples=10000)
results = test.compare([control, treatment])
```

**Pros:**
- Variance reduction without normality assumption
- Robust to outliers
- Alternative to CUPED for non-normal data

**Cons:**
- Computationally intensive
- Only 1 covariate

---

## Quick Selection Guide

### Scenario 1: Simple A/B Test (Revenue)
- **Metric**: Revenue per user
- **Design**: Independent randomization
- **Data**: ~1000 users per group
- **Distribution**: Slightly right-skewed (typical revenue)

**Recommendation**: **BootstrapTest** (robust to skew)

```python
test = BootstrapTest(alpha=0.05, n_samples=10000)
```

---

### Scenario 2: CTR Test
- **Metric**: Click-through rate
- **Design**: Standard A/B
- **Data**: 10,000 users per group

**Recommendation**: **ZTest** (designed for proportions)

```python
test = ZTest(alpha=0.05, test_type="relative")
```

---

### Scenario 3: Revenue with Historical Data
- **Metric**: Revenue per user
- **Design**: Independent randomization
- **Data**: Have 30-day pre-experiment revenue for each user
- **Correlation**: 0.7 (strong correlation)

**Recommendation**: **CupedTTest** (variance reduction)

```python
test = CupedTTest(alpha=0.05, min_correlation=0.5)
```

---

### Scenario 4: Matched Pairs Design
- **Metric**: Session duration
- **Design**: Users matched by demographics + usage, then randomized
- **Data**: 500 matched pairs
- **Distribution**: Approximately normal

**Recommendation**: **PairedTTest**

```python
test = PairedTTest(alpha=0.05)
```

---

### Scenario 5: Multiple Historical Variables
- **Metric**: Purchase amount
- **Design**: Independent randomization
- **Data**: Have user age, tenure, past purchases, session count
- **Goal**: Maximum variance reduction + check if effect varies by segment

**Recommendation**: **AncovaTest**

```python
test = AncovaTest(
    alpha=0.05,
    check_interaction=True,
    validate_assumptions=True
)
```

---

## Common Mistakes

### ❌ Mistake 1: Using T-Test on Highly Skewed Data
**Problem**: Revenue is often heavily right-skewed with outliers

**Solution**: Use BootstrapTest instead
```python
# Bad
test = TTest()  # Assumes normality

# Good
test = BootstrapTest(n_samples=10000)  # No assumptions
```

---

### ❌ Mistake 2: Ignoring Historical Data
**Problem**: Not using CUPED when you have pre-experiment data

**Solution**: Use CupedTTest or AncovaTest
```python
# Bad: Throwing away variance reduction
test = TTest()

# Good: Using historical data
test = CupedTTest()
```

---

### ❌ Mistake 3: Using ZTest on Continuous Metrics
**Problem**: Z-test is for proportions, not continuous metrics

**Solution**: Use TTest or BootstrapTest
```python
# Bad
test = ZTest()  # For proportions only!

# Good
test = TTest()  # For continuous metrics
```

---

### ❌ Mistake 4: Not Correcting for Multiple Comparisons
**Problem**: Testing A vs B, A vs C, A vs D without correction

**Solution**: Use adjust_pvalues()
```python
from utils.corrections import adjust_pvalues

results = test.compare([control, t1, t2, t3])
adjusted = adjust_pvalues(results, method="bonferroni")
```

---

## Summary Flowchart

```
1. Is it a proportion (CTR, CVR)?
   Yes → ZTest
   No → Continue

2. Is data paired/matched?
   Yes → Normal? → PairedTTest : PairedBootstrapTest
   No → Continue

3. Do you have covariates?
   Yes → Multiple? → AncovaTest : (Normal? → CupedTTest : PostNormedBootstrapTest)
   No → Continue

4. Is data normal?
   Yes → TTest
   No → BootstrapTest
```

## Next Steps

- [Parametric Tests Guide](parametric-tests.md) - Deep dive into parametric tests
- [Nonparametric Tests Guide](nonparametric-tests.md) - Deep dive into nonparametric tests
- [Variance Reduction Guide](variance-reduction.md) - Learn about CUPED and ANCOVA
- [Examples](../examples/) - See real-world applications
