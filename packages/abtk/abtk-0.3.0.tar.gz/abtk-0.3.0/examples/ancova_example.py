"""
Example of using ANCOVA test for A/B testing with covariates.

This example demonstrates:
1. Basic ANCOVA with single covariate
2. ANCOVA with multiple covariates
3. Checking for heterogeneous treatment effects
4. Comparing relative vs absolute effects
5. Multiple comparisons correction
"""

import numpy as np
from core.data_types import SampleData
from tests.parametric import AncovaTest
from utils.corrections import adjust_pvalues


def example_1_single_covariate():
    """
    Example 1: ANCOVA with single covariate.

    Scenario: We run an A/B test and have historical revenue data.
    We want to adjust for baseline differences using ANCOVA.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: ANCOVA with Single Covariate")
    print("="*70)

    np.random.seed(42)

    # Generate realistic A/B test data
    n_control = 100
    n_treatment = 100

    # Historical revenue (covariate)
    control_historical = np.random.gamma(shape=2, scale=50, size=n_control)
    treatment_historical = np.random.gamma(shape=2, scale=50, size=n_treatment)

    # Current revenue (outcome)
    # Treatment increases revenue by 10%
    control_revenue = control_historical * (1 + np.random.normal(0.05, 0.2, n_control))
    treatment_revenue = treatment_historical * (1.10 + np.random.normal(0.05, 0.2, n_treatment))

    control = SampleData(
        data=control_revenue,
        covariates=control_historical,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_revenue,
        covariates=treatment_historical,
        name="Treatment"
    )

    # Run ANCOVA (relative effect)
    test = AncovaTest(alpha=0.05, test_type="relative")
    results = test.compare([control, treatment])

    result = results[0]

    print(f"\n{'Control Mean:':<30} ${result.value_1:.2f}")
    print(f"{'Treatment Mean:':<30} ${result.value_2:.2f}")
    print(f"{'Historical Control Mean:':<30} ${np.mean(control_historical):.2f}")
    print(f"{'Historical Treatment Mean:':<30} ${np.mean(treatment_historical):.2f}")

    print(f"\n{'ANCOVA Results:':<30}")
    print(f"{'Treatment Effect:':<30} {result.effect:.2%}")
    print(f"{'95% CI:':<30} [{result.left_bound:.2%}, {result.right_bound:.2%}]")
    print(f"{'P-value:':<30} {result.pvalue:.4f}")
    print(f"{'Significant:':<30} {'Yes ✓' if result.reject else 'No ✗'}")
    print(f"{'R-squared:':<30} {result.method_params['r_squared']:.3f}")

    # Compare with naive approach (ignoring covariates)
    naive_effect = (result.value_2 - result.value_1) / result.value_1
    print(f"\n{'Naive Effect (no adjustment):':<30} {naive_effect:.2%}")
    print(f"{'ANCOVA Effect (adjusted):':<30} {result.effect:.2%}")
    print(f"{'Difference:':<30} {abs(naive_effect - result.effect):.2%}")


def example_2_multiple_covariates():
    """
    Example 2: ANCOVA with multiple covariates.

    Scenario: We have multiple pre-experiment variables:
    - Historical revenue
    - Historical sessions
    - User tenure (days since registration)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: ANCOVA with Multiple Covariates")
    print("="*70)

    np.random.seed(42)

    n_control = 150
    n_treatment = 150

    # Three covariates
    control_cov = np.column_stack([
        np.random.gamma(shape=2, scale=50, size=n_control),     # Historical revenue
        np.random.poisson(lam=10, size=n_control),              # Historical sessions
        np.random.exponential(scale=100, size=n_control)        # User tenure (days)
    ])

    treatment_cov = np.column_stack([
        np.random.gamma(shape=2, scale=50, size=n_treatment),
        np.random.poisson(lam=10, size=n_treatment),
        np.random.exponential(scale=100, size=n_treatment)
    ])

    # Outcome depends on all covariates + treatment effect
    control_revenue = (
        50 +
        0.5 * control_cov[:, 0] +      # Revenue matters
        2.0 * control_cov[:, 1] +      # Sessions matter
        0.1 * control_cov[:, 2] +      # Tenure matters
        np.random.normal(0, 10, n_control)
    )

    treatment_revenue = (
        50 +
        0.5 * treatment_cov[:, 0] +
        2.0 * treatment_cov[:, 1] +
        0.1 * treatment_cov[:, 2] +
        15 +  # Treatment effect: +$15
        np.random.normal(0, 10, n_treatment)
    )

    control = SampleData(
        data=control_revenue,
        covariates=control_cov,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_revenue,
        covariates=treatment_cov,
        name="Treatment"
    )

    # Run ANCOVA (absolute effect)
    test = AncovaTest(alpha=0.05, test_type="absolute")
    results = test.compare([control, treatment])

    result = results[0]

    print(f"\n{'Covariates Used:':<30} 3 (revenue, sessions, tenure)")
    print(f"{'Sample Size:':<30} n={n_control + n_treatment}")

    print(f"\n{'ANCOVA Results:':<30}")
    print(f"{'Treatment Effect:':<30} ${result.effect:.2f}")
    print(f"{'95% CI:':<30} [${result.left_bound:.2f}, ${result.right_bound:.2f}]")
    print(f"{'P-value:':<30} {result.pvalue:.4f}")
    print(f"{'Significant:':<30} {'Yes ✓' if result.reject else 'No ✗'}")
    print(f"{'R-squared:':<30} {result.method_params['r_squared']:.3f}")
    print(f"{'Adjusted R-squared:':<30} {result.method_params['adj_r_squared']:.3f}")

    # Show variance reduction
    print(f"\n{'Variance Reduction:':<30}")
    print(f"{'With covariates, CI width:':<30} ${result.ci_length:.2f}")
    print(f"{'Higher R² = narrower CI':<30} (more precise estimate)")


def example_3_heterogeneous_effects():
    """
    Example 3: Checking for heterogeneous treatment effects.

    Scenario: Does the treatment effect vary by user segment?
    E.g., is the effect stronger for high-value users?
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Heterogeneous Treatment Effects")
    print("="*70)

    np.random.seed(42)

    n_control = 200
    n_treatment = 200

    # Historical revenue (will interact with treatment)
    control_historical = np.random.gamma(shape=2, scale=50, size=n_control)
    treatment_historical = np.random.gamma(shape=2, scale=50, size=n_treatment)

    # Treatment effect DEPENDS on historical revenue
    # High-value users benefit more!
    control_revenue = control_historical * (1 + np.random.normal(0.05, 0.2, n_control))

    treatment_revenue = treatment_historical * (
        1.05 +  # Base effect: 5%
        0.001 * treatment_historical +  # Additional effect for high-value users
        np.random.normal(0, 0.2, n_treatment)
    )

    control = SampleData(
        data=control_revenue,
        covariates=control_historical,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_revenue,
        covariates=treatment_historical,
        name="Treatment"
    )

    # Run ANCOVA with interaction check
    test = AncovaTest(
        alpha=0.05,
        test_type="relative",
        check_interaction=True,
        interaction_alpha=0.10
    )
    results = test.compare([control, treatment])

    result = results[0]

    print(f"\n{'Overall Treatment Effect:':<30} {result.effect:.2%}")
    print(f"{'P-value:':<30} {result.pvalue:.4f}")

    print(f"\n{'Heterogeneity Check:':<30}")
    has_het = result.method_params.get('has_heterogeneous_effect', False)
    print(f"{'Heterogeneous Effect Detected:':<30} {'Yes ✓' if has_het else 'No ✗'}")

    if has_het:
        sig_interactions = result.method_params.get('significant_interactions', [])
        interaction_pvalues = result.method_params.get('interaction_pvalues', {})

        print(f"{'Significant Interactions:':<30} {sig_interactions}")
        for cov, pval in interaction_pvalues.items():
            print(f"  {cov}:<30} p={pval:.4f}")

        print("\n⚠ Interpretation:")
        print("  Treatment effect varies by covariate level.")
        print("  Consider segmented analysis or targeting strategy.")
    else:
        print("\n✓ Interpretation:")
        print("  Treatment effect is homogeneous across covariate levels.")


def example_4_multiple_treatments_with_correction():
    """
    Example 4: Testing multiple treatments with correction for multiple comparisons.

    Scenario: We have 1 control and 3 treatment variants.
    We need to correct for multiple comparisons.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Multiple Treatments + Multiple Comparisons Correction")
    print("="*70)

    np.random.seed(42)

    n = 100

    # Control
    control_cov = np.random.gamma(shape=2, scale=50, size=n)
    control_data = control_cov * (1 + np.random.normal(0.05, 0.2, n))

    control = SampleData(
        data=control_data,
        covariates=control_cov,
        name="Control"
    )

    # Treatment 1: Small effect (3%)
    treatment1_cov = np.random.gamma(shape=2, scale=50, size=n)
    treatment1_data = treatment1_cov * (1.03 + np.random.normal(0.05, 0.2, n))

    treatment1 = SampleData(
        data=treatment1_data,
        covariates=treatment1_cov,
        name="Treatment_A"
    )

    # Treatment 2: Medium effect (8%)
    treatment2_cov = np.random.gamma(shape=2, scale=50, size=n)
    treatment2_data = treatment2_cov * (1.08 + np.random.normal(0.05, 0.2, n))

    treatment2 = SampleData(
        data=treatment2_data,
        covariates=treatment2_cov,
        name="Treatment_B"
    )

    # Treatment 3: Large effect (15%)
    treatment3_cov = np.random.gamma(shape=2, scale=50, size=n)
    treatment3_data = treatment3_cov * (1.15 + np.random.normal(0.05, 0.2, n))

    treatment3 = SampleData(
        data=treatment3_data,
        covariates=treatment3_cov,
        name="Treatment_C"
    )

    # Run ANCOVA for all pairwise comparisons
    test = AncovaTest(alpha=0.05, test_type="relative", validate_assumptions=False)
    results = test.compare([control, treatment1, treatment2, treatment3])

    print(f"\n{'Uncorrected Results:':<30}")
    print(f"{'Comparison':<20} {'Effect':<15} {'P-value':<10} {'Significant':<12}")
    print("-" * 57)

    for result in results:
        comparison = f"{result.name_1} vs {result.name_2}"
        sig = "Yes ✓" if result.reject else "No ✗"
        print(f"{comparison:<20} {result.effect:>7.2%}      {result.pvalue:>7.4f}   {sig:<12}")

    # Apply Bonferroni correction
    adjusted_bonf = adjust_pvalues(results, method="bonferroni")

    print(f"\n{'Bonferroni Corrected Results:':<30}")
    print(f"{'Comparison':<20} {'Effect':<15} {'P-adj':<10} {'Significant':<12}")
    print("-" * 57)

    for result in adjusted_bonf:
        comparison = f"{result.name_1} vs {result.name_2}"
        sig = "Yes ✓" if result.reject else "No ✗"
        print(f"{comparison:<20} {result.effect:>7.2%}      {result.pvalue:>7.4f}   {sig:<12}")

    # Apply Benjamini-Hochberg (less conservative)
    adjusted_bh = adjust_pvalues(results, method="benjamini-hochberg")

    print(f"\n{'Benjamini-Hochberg Corrected Results:':<30}")
    print(f"{'Comparison':<20} {'Effect':<15} {'P-adj':<10} {'Significant':<12}")
    print("-" * 57)

    for result in adjusted_bh:
        comparison = f"{result.name_1} vs {result.name_2}"
        sig = "Yes ✓" if result.reject else "No ✗"
        print(f"{comparison:<20} {result.effect:>7.2%}      {result.pvalue:>7.4f}   {sig:<12}")

    print("\n" + "="*70)
    print("Notice: Bonferroni is conservative, BH is less conservative.")
    print("Strong effects (Treatment_C) survive correction.")
    print("Weak effects (Treatment_A) may not survive strict correction.")
    print("="*70)


if __name__ == "__main__":
    example_1_single_covariate()
    example_2_multiple_covariates()
    example_3_heterogeneous_effects()
    example_4_multiple_treatments_with_correction()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
