# Multiple Comparisons Correction

When testing multiple hypotheses simultaneously, the probability of false positives increases. This guide explains how to control for multiple comparisons in ABTK.

## The Multiple Testing Problem

### Why Correct?

**Single test:**
- α = 0.05
- Probability of false positive = 5%

**Multiple tests (without correction):**
- Test 3 variants vs control (3 tests)
- Probability of at least one false positive ≈ 14%
- Test 10 variants: ≈ 40% chance of false positive!

**Formula:** `P(at least one false positive) = 1 - (1 - α)^n`

### Example

```python
from tests.parametric import TTest

# Test control vs 3 treatments (3 comparisons)
test = TTest(alpha=0.05)
results = test.compare([control, treatment_a, treatment_b, treatment_c])

# 3 tests × 5% = 15% family-wise error rate (FWER)
# One result might be significant by chance!
```

---

## When to Correct

### ✅ Correct When:

1. **Multiple variants in same experiment**
   ```python
   # A/B/C/D test (3 comparisons)
   results = test.compare([control, t1, t2, t3])
   ```

2. **Testing multiple metrics on same data**
   ```python
   # Testing revenue, CTR, and time-on-site
   results_revenue = test.compare([c_revenue, t_revenue])
   results_ctr = test.compare([c_ctr, t_ctr])
   results_time = test.compare([c_time, t_time])
   ```

3. **Sequential testing (peeking)**
   - Looking at results multiple times during experiment
   - Each peek is a test!

### ❌ Don't Correct When:

1. **Single pre-planned comparison**
   ```python
   # Simple A/B test (1 comparison)
   results = test.compare([control, treatment])
   ```

2. **Different experiments**
   - Each experiment is independent
   - No need to correct across experiments

3. **Exploratory analysis with clear disclaimer**
   - If you're exploring and will validate later
   - Document that results are uncorrected

---

## ABTK Correction Methods

### Available Methods

| Method | Type | Control | When to Use |
|--------|------|---------|-------------|
| **Bonferroni** | FWER | Strongest | Few tests (< 10), conservative |
| **Holm** | FWER | Strong | Better than Bonferroni, still conservative |
| **Šidák** | FWER | Strong | Assumes independence |
| **Benjamini-Hochberg** | FDR | Moderate | Many tests, exploratory |
| **Benjamini-Yekutieli** | FDR | Moderate | Tests are correlated |

**FWER (Family-Wise Error Rate):** Controls probability of ANY false positive
**FDR (False Discovery Rate):** Controls expected proportion of false positives

---

## Basic Usage

```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues

# Run multiple comparisons
test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment_a, treatment_b, treatment_c])

# Apply correction
adjusted = adjust_pvalues(results, method="bonferroni")

# Check results
for result in adjusted:
    print(f"{result.name_1} vs {result.name_2}:")
    print(f"  Original p-value: {result.pvalue_original:.4f}")
    print(f"  Adjusted p-value: {result.pvalue:.4f}")
    print(f"  Significant: {result.reject}")
    print()
```

---

## Bonferroni Correction

### Method

**Most conservative** approach:
- `adjusted_pvalue = min(pvalue * n_tests, 1.0)`
- Controls FWER (probability of ANY false positive)

### When to Use

- ✅ Few tests (< 10)
- ✅ Want strong control (minimize false positives)
- ✅ High cost of false positives

### Example

```python
from utils.corrections import adjust_pvalues

results = test.compare([control, t1, t2, t3])  # 3 tests

# Bonferroni correction
adjusted = adjust_pvalues(results, method="bonferroni")

# P-values are multiplied by 3
# Original: [0.01, 0.03, 0.06]
# Adjusted: [0.03, 0.09, 0.18]
```

### Pros & Cons

**Pros:**
- Simple to understand
- Strong FWER control
- No assumptions needed

**Cons:**
- Very conservative (many false negatives)
- Low power with many tests

---

## Holm Correction

### Method

**Step-down Bonferroni:**
1. Sort p-values: p₁ ≤ p₂ ≤ ... ≤ pₙ
2. For rank i: `adjusted_pᵢ = pᵢ * (n - i + 1)`
3. Enforce monotonicity

More powerful than Bonferroni while controlling FWER.

### When to Use

- ✅ Better than Bonferroni (always)
- ✅ Want FWER control
- ✅ Moderate number of tests (< 20)

### Example

```python
adjusted = adjust_pvalues(results, method="holm")

# More powerful than Bonferroni
# Some tests significant with Holm, not with Bonferroni
```

### Comparison: Bonferroni vs Holm

```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues
import numpy as np

# Simulate 4 tests
np.random.seed(42)
results = []
for i in range(4):
    c = SampleData(data=np.random.normal(100, 10, 100), name="Control")
    t = SampleData(data=np.random.normal(102, 10, 100), name=f"Treatment{i+1}")
    results.extend(test.compare([c, t]))

# Compare methods
bonf = adjust_pvalues(results, method="bonferroni")
holm = adjust_pvalues(results, method="holm")

print("Method      | Test 1 | Test 2 | Test 3 | Test 4")
print("------------|--------|--------|--------|--------")
print(f"Original    | {results[0].pvalue:.4f} | {results[1].pvalue:.4f} | {results[2].pvalue:.4f} | {results[3].pvalue:.4f}")
print(f"Bonferroni  | {bonf[0].pvalue:.4f} | {bonf[1].pvalue:.4f} | {bonf[2].pvalue:.4f} | {bonf[3].pvalue:.4f}")
print(f"Holm        | {holm[0].pvalue:.4f} | {holm[1].pvalue:.4f} | {holm[2].pvalue:.4f} | {holm[3].pvalue:.4f}")
```

**Holm is generally preferred over Bonferroni** (more powerful, same FWER control).

---

## Benjamini-Hochberg Correction

### Method

**FDR control** (less conservative than FWER):
1. Sort p-values: p₁ ≤ p₂ ≤ ... ≤ pₙ
2. Work backwards: find largest i where `pᵢ ≤ (i/n) * α`
3. Reject all hypotheses up to i

Controls expected proportion of false discoveries.

### When to Use

- ✅ Many tests (> 10)
- ✅ Exploratory analysis
- ✅ Can tolerate some false positives
- ✅ Want to maximize discoveries

### Example

```python
adjusted = adjust_pvalues(results, method="benjamini-hochberg")

# Less conservative than Bonferroni/Holm
# More tests will be significant
```

### FWER vs FDR

**FWER (Bonferroni, Holm):**
- Controls P(any false positive) ≤ α
- Very conservative
- Few false positives, many false negatives

**FDR (Benjamini-Hochberg):**
- Controls E(false positives / all positives) ≤ α
- Less conservative
- Allows some false positives, fewer false negatives

**Example:**
- 100 tests, 20 truly significant
- FWER: Might find 10 significant (very conservative)
- FDR: Might find 18 significant, 1 false positive (less conservative)

---

## Benjamini-Yekutieli Correction

### Method

**FDR control for correlated tests:**
- Like Benjamini-Hochberg but adds correction factor
- Works when tests are dependent/correlated

### When to Use

- ✅ Tests are correlated (e.g., testing related metrics)
- ✅ Many tests
- ✅ Exploratory analysis

### Example

```python
# Testing correlated metrics (revenue, LTV, AOV)
adjusted = adjust_pvalues(results, method="benjamini-yekutieli")
```

---

## Šidák Correction

### Method

Assumes independence:
- `adjusted_pvalue = 1 - (1 - pvalue)^n`

Less conservative than Bonferroni if tests are independent.

### When to Use

- ✅ Tests are truly independent
- ✅ Want slightly more power than Bonferroni

### Example

```python
adjusted = adjust_pvalues(results, method="sidak")
```

**Note:** Only use if tests are truly independent. If unsure, use Bonferroni or Holm.

---

## Choosing a Method

### Decision Tree

```
How many tests?
├─ Few (< 5)
│  └─ Want strong control?
│     ├─ Yes → Bonferroni or Holm
│     └─ No → No correction needed
│
├─ Moderate (5-20)
│  └─ Exploratory or confirmatory?
│     ├─ Confirmatory → Holm
│     └─ Exploratory → Benjamini-Hochberg
│
└─ Many (> 20)
   └─ Tests correlated?
      ├─ Yes → Benjamini-Yekutieli
      └─ No → Benjamini-Hochberg
```

### General Recommendations

**For most use cases:** Start with **Holm**
- More powerful than Bonferroni
- Strong FWER control
- Works for any number of tests

**For exploratory analysis:** Use **Benjamini-Hochberg**
- Allows more discoveries
- Controls FDR instead of FWER
- Good for many tests

**For very few tests (< 5):** Maybe **no correction**
- If tests are pre-planned and few
- Document decision clearly

---

## Practical Examples

### Example 1: A/B/C/D Test

```python
from tests.parametric import TTest
from utils.corrections import adjust_pvalues

# Test control vs 3 variants
control = SampleData(data=..., name="Control")
variant_a = SampleData(data=..., name="Variant A")
variant_b = SampleData(data=..., name="Variant B")
variant_c = SampleData(data=..., name="Variant C")

test = TTest(alpha=0.05, test_type="relative")
results = test.compare([control, variant_a, variant_b, variant_c])

# Apply Holm correction (3 tests)
adjusted = adjust_pvalues(results, method="holm")

print("Results:")
for result in adjusted:
    if result.reject:
        print(f"✓ {result.name_2}: {result.effect:.2%} lift (p={result.pvalue:.4f})")
    else:
        print(f"✗ {result.name_2}: {result.effect:.2%} lift (p={result.pvalue:.4f})")
```

### Example 2: Multiple Metrics

```python
# Testing 3 metrics: revenue, CTR, time-on-site
metrics = ['revenue', 'ctr', 'time']
all_results = []

for metric in metrics:
    control_data = SampleData(data=control_metrics[metric], name="Control")
    treatment_data = SampleData(data=treatment_metrics[metric], name="Treatment")

    test = TTest(alpha=0.05)
    results = test.compare([control_data, treatment_data])
    all_results.extend(results)

# Correct for 3 tests
adjusted = adjust_pvalues(all_results, method="holm")

print("Metric Results (corrected):")
for i, metric in enumerate(metrics):
    result = adjusted[i]
    print(f"{metric}: p={result.pvalue:.4f}, significant={result.reject}")
```

### Example 3: Sequential Testing

```python
# Looking at results 3 times during experiment
peeks = [
    (1000, 1000),  # Day 1: 1000 per group
    (2000, 2000),  # Day 3: 2000 per group
    (5000, 5000),  # Day 7: 5000 per group (final)
]

peek_results = []
for n_control, n_treatment in peeks:
    c = SampleData(data=control_data[:n_control], name="Control")
    t = SampleData(data=treatment_data[:n_treatment], name="Treatment")

    results = test.compare([c, t])
    peek_results.extend(results)

# Correct for 3 peeks
adjusted = adjust_pvalues(peek_results, method="bonferroni", alpha=0.05)

# Check final peek
final_result = adjusted[-1]
if final_result.reject:
    print("Significant after correction for peeking!")
```

---

## Interpreting Corrected Results

### Understanding Adjusted P-values

```python
result = adjusted[0]

print(f"Original p-value: {result.pvalue_original:.4f}")
print(f"Adjusted p-value: {result.pvalue:.4f}")
print(f"Correction method: {result.correction_method}")
print(f"Significant at α=0.05: {result.reject}")
```

**Interpretation:**
- `pvalue_original`: P-value from individual test
- `pvalue`: Adjusted p-value accounting for multiple testing
- Compare `pvalue` to α (e.g., 0.05) for decision

### Effect Sizes Don't Change

**Important:** Correction only affects p-values and significance decisions.

Effect sizes and confidence intervals remain the same:
```python
# Effect estimates are unchanged
original_effect = results[0].effect
adjusted_effect = adjusted[0].effect
assert original_effect == adjusted_effect  # True!

# Only p-value and reject change
assert results[0].pvalue != adjusted[0].pvalue
assert results[0].reject != adjusted[0].reject  # May differ
```

---

## Common Mistakes

### ❌ Mistake 1: Not Correcting When Needed

```python
# Bad: Multiple tests without correction
results = test.compare([control, t1, t2, t3, t4, t5])
for r in results:
    if r.pvalue < 0.05:
        print(f"{r.name_2} is significant!")  # Might be false positive!
```

**Solution:** Always correct for multiple tests
```python
# Good: Apply correction
adjusted = adjust_pvalues(results, method="holm")
for r in adjusted:
    if r.reject:
        print(f"{r.name_2} is significant (corrected)!")
```

### ❌ Mistake 2: Correcting Unnecessarily

```python
# Bad: Correcting single test
results = test.compare([control, treatment])
adjusted = adjust_pvalues(results, method="bonferroni")  # Unnecessary!
```

**Solution:** No correction needed for single test

### ❌ Mistake 3: Wrong Correction Method

```python
# Bad: Using Bonferroni for 50 tests
results = test.compare([control, *treatments])  # 50 treatments
adjusted = adjust_pvalues(results, method="bonferroni")  # Too conservative!
```

**Solution:** Use FDR control for many tests
```python
# Good: Use Benjamini-Hochberg for many tests
adjusted = adjust_pvalues(results, method="benjamini-hochberg")
```

---

## Best Practices

### 1. Plan Ahead

**Pre-register your analysis plan:**
- How many tests?
- Which correction method?
- Primary vs secondary metrics?

### 2. Document Decisions

```python
# Document in code
# Testing 3 variants vs control (3 tests)
# Using Holm correction for strong FWER control
adjusted = adjust_pvalues(results, method="holm")
```

### 3. Report Both Original and Adjusted

```python
for original, adjusted_result in zip(results, adjusted):
    print(f"{adjusted_result.name_2}:")
    print(f"  Effect: {adjusted_result.effect:.2%}")
    print(f"  Original p-value: {original.pvalue:.4f}")
    print(f"  Adjusted p-value: {adjusted_result.pvalue:.4f}")
    print(f"  Significant (corrected): {adjusted_result.reject}")
```

### 4. Choose Appropriate Method

- **Confirmatory tests:** Holm or Bonferroni
- **Exploratory analysis:** Benjamini-Hochberg
- **Many tests:** FDR control
- **Few tests:** FWER control

---

## Advanced: Custom Alpha

You can specify custom significance level:

```python
# More stringent
adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.01)

# Less stringent
adjusted = adjust_pvalues(results, method="benjamini-hochberg", alpha=0.10)
```

---

## Summary

| Number of Tests | Recommended Method | Type |
|----------------|-------------------|------|
| 1 | No correction | - |
| 2-5 | Holm | FWER |
| 5-20 | Holm | FWER |
| 20+ | Benjamini-Hochberg | FDR |
| Many correlated | Benjamini-Yekutieli | FDR |

**Key takeaway:** Always correct for multiple comparisons to avoid inflated false positive rates!

---

## Next Steps

- [Test Selection Guide](test-selection.md) - Choose the right test
- [Parametric Tests](parametric-tests.md) - T-Test, CUPED, ANCOVA
- [Nonparametric Tests](nonparametric-tests.md) - Bootstrap tests
- [FAQ](../faq.md) - Common questions about multiple comparisons
