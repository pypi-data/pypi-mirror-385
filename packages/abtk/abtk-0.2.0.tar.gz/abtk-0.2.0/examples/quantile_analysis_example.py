"""
Example of quantile treatment effect analysis.

This example demonstrates:
1. Basic quantile analysis with bootstrap
2. Using paired bootstrap for quantile analysis
3. Post-normed bootstrap with quantile analysis
4. Visualizing quantile effects
5. Interpreting heterogeneous treatment effects
"""

import numpy as np
from core.data_types import SampleData
from tests.nonparametric import (
    BootstrapTest,
    PairedBootstrapTest,
    PostNormedBootstrapTest
)
from utils.quantile_analysis import QuantileAnalyzer


def example_1_basic_quantile_analysis():
    """
    Example 1: Basic quantile analysis with BootstrapTest.

    Scenario: Revenue data where treatment effect is stronger for high-spenders.
    We want to understand at which quantiles the effect is concentrated.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Quantile Analysis")
    print("="*70)

    np.random.seed(42)

    # Generate data with heterogeneous effects
    # Treatment effect increases with baseline: low-spenders +5%, high-spenders +15%
    n = 500

    # Control: Exponential distribution (many low-spenders, few high-spenders)
    control_data = np.random.exponential(scale=100, size=n)

    # Treatment: Effect increases with value
    # For low values (~$50): +5%
    # For high values (~$300): +15%
    treatment_base = np.random.exponential(scale=100, size=n)
    # Add heterogeneous effect: effect = 0.05 + 0.0003 * value
    treatment_data = treatment_base * (1 + 0.05 + 0.0003 * treatment_base)

    control = SampleData(
        data=control_data,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_data,
        name="Treatment"
    )

    print(f"\n{'Sample Statistics:':<30}")
    print(f"{'Control mean:':<30} ${np.mean(control_data):.2f}")
    print(f"{'Treatment mean:':<30} ${np.mean(treatment_data):.2f}")
    print(f"{'Naive effect:':<30} {(np.mean(treatment_data) / np.mean(control_data) - 1):.2%}")

    # Initialize bootstrap test
    bootstrap = BootstrapTest(
        alpha=0.05,
        test_type="relative",
        n_samples=5000,
        random_seed=42
    )

    # Wrap with quantile analyzer
    analyzer = QuantileAnalyzer(
        test=bootstrap,
        quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    )

    print("\n" + "Running quantile analysis (this may take a moment)...")
    results = analyzer.compare([control, treatment])

    result = results[0]

    # Display results
    print("\n" + result.summary())

    # Key insights
    sig_quantiles = result.significant_quantiles()
    if len(sig_quantiles) > 0:
        print(f"\n{'Key Insights:':<30}")
        print(f"  Effect is significant at quantiles: {', '.join([f'{q:.0%}' for q in sig_quantiles])}")

        if min(sig_quantiles) > 0.5:
            print("  → Effect is concentrated in upper half of distribution (high-spenders)")
        elif max(sig_quantiles) < 0.5:
            print("  → Effect is concentrated in lower half of distribution (low-spenders)")
        else:
            print("  → Effect is present throughout distribution")

        # Compare low vs high quantiles
        low_effect = result.get_effect(0.25)
        high_effect = result.get_effect(0.95)
        print(f"\n  25th percentile effect: {low_effect:.2%}")
        print(f"  95th percentile effect: {high_effect:.2%}")
        print(f"  → Effect is {abs(high_effect / low_effect):.1f}x stronger at 95th percentile")


def example_2_paired_quantile_analysis():
    """
    Example 2: Quantile analysis with PairedBootstrapTest.

    Scenario: Matched pairs A/B test where we matched users by historical revenue.
    We want to see if treatment effect varies across the revenue distribution.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Paired Bootstrap Quantile Analysis")
    print("="*70)

    np.random.seed(42)

    n = 300

    # Historical revenue (used for matching)
    historical = np.random.gamma(shape=2, scale=50, size=n)

    # Current revenue (outcome)
    # Control: correlated with historical + noise
    control_data = historical * (1 + np.random.normal(0.05, 0.2, n))

    # Treatment: +10% effect, stronger for high historical revenue
    treatment_data = historical * (
        1.10 +  # Base effect
        0.001 * historical +  # Heterogeneous effect
        np.random.normal(0.05, 0.2, n)
    )

    # Create paired data
    paired_ids = np.arange(n)

    control = SampleData(
        data=control_data,
        covariates=historical,
        paired_ids=paired_ids,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_data,
        covariates=historical,
        paired_ids=paired_ids,
        name="Treatment"
    )

    print(f"\n{'Matched Pairs A/B Test:':<30}")
    print(f"{'Number of pairs:':<30} {n}")
    print(f"{'Control mean:':<30} ${np.mean(control_data):.2f}")
    print(f"{'Treatment mean:':<30} ${np.mean(treatment_data):.2f}")

    # Paired bootstrap test
    paired_bootstrap = PairedBootstrapTest(
        alpha=0.05,
        test_type="relative",
        n_samples=5000,
        random_seed=42
    )

    # Quantile analysis
    analyzer = QuantileAnalyzer(
        test=paired_bootstrap,
        quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    )

    print("\nRunning paired quantile analysis...")
    results = analyzer.compare([control, treatment])

    result = results[0]
    print("\n" + result.summary())


def example_3_post_normed_quantile_analysis():
    """
    Example 3: Quantile analysis with PostNormedBootstrapTest.

    Scenario: We have historical data and want variance reduction
    while analyzing quantile effects.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Post-Normed Bootstrap Quantile Analysis")
    print("="*70)

    np.random.seed(42)

    n = 400

    # Historical revenue (covariate)
    control_historical = np.random.gamma(shape=2, scale=50, size=n)
    treatment_historical = np.random.gamma(shape=2, scale=50, size=n)

    # Current revenue (correlated with historical)
    control_data = control_historical * (1 + np.random.normal(0.05, 0.2, n))
    treatment_data = treatment_historical * (
        1.08 +  # Base effect
        0.0005 * treatment_historical +  # Heterogeneous
        np.random.normal(0.05, 0.2, n)
    )

    control = SampleData(
        data=control_data,
        covariates=control_historical,
        name="Control"
    )
    treatment = SampleData(
        data=treatment_data,
        covariates=treatment_historical,
        name="Treatment"
    )

    print(f"\n{'Using covariates for variance reduction:':<30}")
    print(f"{'Control mean:':<30} ${np.mean(control_data):.2f}")
    print(f"{'Treatment mean:':<30} ${np.mean(treatment_data):.2f}")
    print(f"{'Historical control mean:':<30} ${np.mean(control_historical):.2f}")
    print(f"{'Historical treatment mean:':<30} ${np.mean(treatment_historical):.2f}")

    # Post-normed bootstrap
    post_normed = PostNormedBootstrapTest(
        alpha=0.05,
        test_type="relative",
        n_samples=5000,
        stratify=False,
        random_seed=42
    )

    # Quantile analysis
    analyzer = QuantileAnalyzer(
        test=post_normed,
        quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    )

    print("\nRunning post-normed quantile analysis...")
    results = analyzer.compare([control, treatment])

    result = results[0]
    print("\n" + result.summary())


def example_4_visualization():
    """
    Example 4: Visualizing quantile effects.

    Demonstrates how to create plots of quantile treatment effects.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Visualizing Quantile Effects")
    print("="*70)

    try:
        from utils.visualization import plot_quantile_effects
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n⚠ Matplotlib not installed. Skipping visualization example.")
        print("Install with: pip install matplotlib")
        return

    np.random.seed(42)

    n = 600
    control_data = np.random.exponential(scale=100, size=n)
    treatment_base = np.random.exponential(scale=100, size=n)
    treatment_data = treatment_base * (1 + 0.05 + 0.0004 * treatment_base)

    control = SampleData(data=control_data, name="Control")
    treatment = SampleData(data=treatment_data, name="Treatment")

    bootstrap = BootstrapTest(
        alpha=0.05,
        test_type="relative",
        n_samples=5000,
        random_seed=42
    )

    analyzer = QuantileAnalyzer(
        test=bootstrap,
        quantiles=np.arange(0.1, 1.0, 0.1)  # 10th to 90th percentile
    )

    print("\nRunning quantile analysis with 9 quantiles...")
    results = analyzer.compare([control, treatment])
    result = results[0]

    # Create plot
    print("\nCreating visualization...")
    fig, ax = plot_quantile_effects(
        result,
        figsize=(14, 7),
        show_ci=True,
        highlight_significant=True
    )

    # Save to file (optional)
    try:
        plt.savefig('quantile_effects.png', dpi=150, bbox_inches='tight')
        print("✓ Plot saved to 'quantile_effects.png'")
    except Exception as e:
        print(f"Could not save plot: {e}")

    print("✓ Displaying plot (close window to continue)...")
    plt.show()


def example_5_multiple_treatments():
    """
    Example 5: Comparing multiple treatments with quantile analysis.

    Scenario: 1 control vs 3 treatment variants.
    We want to see which variants work best at different quantiles.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Multiple Treatments - Quantile Analysis")
    print("="*70)

    np.random.seed(42)

    n = 300

    # Control
    control_data = np.random.exponential(scale=100, size=n)
    control = SampleData(data=control_data, name="Control")

    # Treatment A: Small uniform effect (+5% everywhere)
    treatment_a_data = np.random.exponential(scale=105, size=n)
    treatment_a = SampleData(data=treatment_a_data, name="Treatment_A")

    # Treatment B: Effect concentrated in middle (50th-75th percentile)
    treatment_b_base = np.random.exponential(scale=100, size=n)
    # Add effect only for middle quantiles (values between 70 and 150)
    mask = (treatment_b_base > 70) & (treatment_b_base < 150)
    treatment_b_data = treatment_b_base.copy()
    treatment_b_data[mask] *= 1.12  # +12% for middle range
    treatment_b = SampleData(data=treatment_b_data, name="Treatment_B")

    # Treatment C: Strong effect in top 25% only
    treatment_c_base = np.random.exponential(scale=100, size=n)
    treatment_c_data = treatment_c_base * (1 + 0.003 * treatment_c_base)
    treatment_c = SampleData(data=treatment_c_data, name="Treatment_C")

    print(f"\n{'Comparing 3 treatment variants:':<30}")
    print(f"{'Control mean:':<30} ${np.mean(control_data):.2f}")
    print(f"{'Treatment A mean:':<30} ${np.mean(treatment_a_data):.2f}")
    print(f"{'Treatment B mean:':<30} ${np.mean(treatment_b_data):.2f}")
    print(f"{'Treatment C mean:':<30} ${np.mean(treatment_c_data):.2f}")

    bootstrap = BootstrapTest(
        alpha=0.05,
        test_type="relative",
        n_samples=3000,  # Fewer for speed with multiple comparisons
        random_seed=42
    )

    analyzer = QuantileAnalyzer(
        test=bootstrap,
        quantiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    )

    print("\nRunning quantile analysis for all pairwise comparisons...")
    print("(This will run 15 bootstrap tests: 3 pairs × 5 quantiles)")

    # This compares: Control-A, Control-B, Control-C
    results = analyzer.compare([control, treatment_a, treatment_b, treatment_c])

    print(f"\nGenerated {len(results)} pairwise comparisons")

    # Display each comparison
    for result in results:
        print("\n" + "="*70)
        print(f"{result.name_1} vs {result.name_2}")
        print("="*70)
        df = result.to_dataframe()
        print(df.to_string(index=False))

        sig_quantiles = result.significant_quantiles()
        if len(sig_quantiles) > 0:
            print(f"\nSignificant at: {', '.join([f'{q:.0%}' for q in sig_quantiles])}")


if __name__ == "__main__":
    example_1_basic_quantile_analysis()
    example_2_paired_quantile_analysis()
    example_3_post_normed_quantile_analysis()
    example_4_visualization()
    example_5_multiple_treatments()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
