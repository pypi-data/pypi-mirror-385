# ABTK Documentation

Welcome to the A/B Testing Toolkit documentation!

## Getting Started

New to ABTK? Start here:
- [**Getting Started Guide**](getting-started.md) - Installation, first steps, basic concepts, and working with DataFrames

## User Guides

Comprehensive guides for all ABTK features:

**Planning:**
- [Experiment Planning](user-guide/experiment-planning.md) - Sample size & MDE calculations (⭐ START HERE BEFORE RUNNING TEST)

**Test Types:**
- [Test Selection Guide](user-guide/test-selection.md) - Decision tree for choosing the right test
- [Parametric Tests](user-guide/parametric-tests.md) - T-Test, Z-Test, Paired T-Test, CUPED
- [Nonparametric Tests](user-guide/nonparametric-tests.md) - Bootstrap, Paired Bootstrap, Post-Normed Bootstrap

**Advanced Features:**
- [Variance Reduction](user-guide/variance-reduction.md) - Overview of CUPED, ANCOVA, and Post-Normed Bootstrap
- [ANCOVA Guide](user-guide/ancova-guide.md) - Detailed ANCOVA guide with diagnostics and troubleshooting
- [Multiple Comparisons](user-guide/multiple-comparisons.md) - Bonferroni, Holm, Benjamini-Hochberg corrections
- [Quantile Analysis](user-guide/quantile-analysis.md) - Quantile Treatment Effects (QTE) analysis

## Examples

Runnable code examples:
- [Experiment Planning Examples](../examples/experiment_planning_example.py) - Sample size & MDE calculations
- [DataFrame Usage Examples](../examples/dataframe_usage_example.py) - Working with pandas DataFrames
- [ANCOVA Example](../examples/ancova_example.py) - Complete ANCOVA workflow
- [Quantile Analysis Example](../examples/quantile_analysis_example.py) - Quantile treatment effects

## FAQ

Common questions and answers:
- [**Frequently Asked Questions**](faq.md) - Test selection, data preparation, interpretation, troubleshooting

## Contributing

Want to contribute? See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

---

## Documentation Structure Summary

```
docs/
├── README.md                  # This file
├── getting-started.md         # Tutorial for beginners
├── faq.md                     # Common questions
└── user-guide/
    ├── experiment-planning.md # Sample size & MDE ⭐
    ├── test-selection.md      # Decision tree
    ├── parametric-tests.md    # T-Test, CUPED, Z-Test
    ├── nonparametric-tests.md # Bootstrap tests
    ├── variance-reduction.md  # CUPED/ANCOVA overview
    ├── ancova-guide.md        # Detailed ANCOVA guide
    ├── multiple-comparisons.md # P-value corrections
    └── quantile-analysis.md   # QTE analysis
```
