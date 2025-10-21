"""
Experiment Planning Examples

Demonstrates how to use ABTK for experiment planning:
- Calculate Minimum Detectable Effect (MDE)
- Calculate required sample size
- Compare regular vs CUPED approaches
- Plan for different test types
"""

import numpy as np
from core.data_types import SampleData, ProportionData
from utils.sample_size_calculator import (
    calculate_mde_ttest,
    calculate_sample_size_ttest,
    calculate_mde_cuped,
    calculate_sample_size_cuped,
    calculate_mde_proportions,
    calculate_sample_size_proportions,
    compare_mde_with_without_cuped
)


def example_1_basic_mde_calculation():
    """
    Example 1: Calculate MDE for a revenue test.

    Given: 1000 users per group
    Question: What's the smallest effect we can detect?
    """
    print("=" * 70)
    print("Example 1: Calculate Minimum Detectable Effect (MDE)")
    print("=" * 70)

    # Scenario: Revenue test
    # Based on historical data: mean=100, std=20
    print("\nScenario: Revenue A/B test")
    print("  Historical mean: $100")
    print("  Historical std: $20")
    print("  Planned sample size: 1,000 users per group")

    # Calculate MDE
    mde = calculate_mde_ttest(
        mean=100,
        std=20,
        n=1000,
        alpha=0.05,
        power=0.8,
        test_type="relative"
    )

    print(f"\nResult:")
    print(f"  Minimum Detectable Effect: {mde:.2%}")
    print(f"  → Can detect effects ≥ {mde:.2%} with 80% power")
    print(f"  → E.g., revenue increase from $100 to ${100 * (1 + mde):.2f}")
    print()


def example_2_sample_size_calculation():
    """
    Example 2: Calculate required sample size.

    Given: Want to detect 5% effect
    Question: How many users do we need?
    """
    print("=" * 70)
    print("Example 2: Calculate Required Sample Size")
    print("=" * 70)

    # Target: Detect 5% revenue increase
    print("\nScenario: Want to detect 5% revenue increase")
    print("  Baseline mean: $100")
    print("  Baseline std: $20")
    print("  Target MDE: 5%")
    print("  Alpha: 0.05, Power: 0.80")

    n = calculate_sample_size_ttest(
        baseline_mean=100,
        std=20,
        mde=0.05,  # 5% effect
        alpha=0.05,
        power=0.8
    )

    print(f"\nResult:")
    print(f"  Required sample size: {n:,} users per group")
    print(f"  Total users needed: {n*2:,} (both groups)")
    print()


def example_3_using_historical_data():
    """
    Example 3: Use historical data instead of parameters.

    Demonstrates the hybrid approach with SampleData.
    """
    print("=" * 70)
    print("Example 3: Planning with Historical Data")
    print("=" * 70)

    # Simulate historical revenue data
    np.random.seed(42)
    historical_revenue = np.random.normal(100, 20, 5000)

    # Create SampleData from historical data
    historical = SampleData(
        data=historical_revenue,
        name="Last Month Revenue"
    )

    print(f"\nHistorical data:")
    print(f"  N: {len(historical.data):,}")
    print(f"  Mean: ${historical.data.mean():.2f}")
    print(f"  Std: ${historical.data.std():.2f}")

    # Calculate MDE using historical data
    mde = calculate_mde_ttest(
        sample=historical,  # Use SampleData directly!
        n=1000  # Target sample size
    )

    print(f"\nPlanning for new experiment:")
    print(f"  Target sample size: 1,000 per group")
    print(f"  MDE: {mde:.2%}")

    # Calculate required sample size
    n = calculate_sample_size_ttest(
        sample=historical,  # Use SampleData directly!
        mde=0.05  # Want to detect 5%
    )

    print(f"\nTo detect 5% effect:")
    print(f"  Need: {n:,} users per group")
    print()


def example_4_cuped_advantage():
    """
    Example 4: CUPED advantage - smaller MDE and smaller sample size!

    Shows how variance reduction helps detect smaller effects.
    """
    print("=" * 70)
    print("Example 4: CUPED Advantage (Variance Reduction)")
    print("=" * 70)

    # Scenario
    print("\nScenario: Revenue test with baseline revenue available")
    print("  Current mean: $100")
    print("  Current std: $20")
    print("  Correlation with baseline: 0.7")

    # Regular T-Test
    print("\n--- Regular T-Test (no variance reduction) ---")
    mde_regular = calculate_mde_ttest(mean=100, std=20, n=1000)
    n_regular = calculate_sample_size_ttest(baseline_mean=100, std=20, mde=0.05)

    print(f"  MDE (n=1000): {mde_regular:.2%}")
    print(f"  Sample size (MDE=5%): {n_regular:,}")

    # CUPED T-Test
    print("\n--- CUPED T-Test (with variance reduction) ---")
    mde_cuped = calculate_mde_cuped(mean=100, std=20, n=1000, correlation=0.7)
    n_cuped = calculate_sample_size_cuped(baseline_mean=100, std=20, mde=0.05, correlation=0.7)

    print(f"  MDE (n=1000): {mde_cuped:.2%}")
    print(f"  Sample size (MDE=5%): {n_cuped:,}")

    # Comparison
    print("\n--- Improvement with CUPED ---")
    mde_improvement = (mde_regular - mde_cuped) / mde_regular
    sample_reduction = (n_regular - n_cuped) / n_regular

    print(f"  MDE improved by: {mde_improvement:.1%}")
    print(f"  Sample size reduced by: {sample_reduction:.1%}")
    print(f"  → Need {n_regular - n_cuped:,} fewer users!")
    print()


def example_5_proportions_test():
    """
    Example 5: Planning for proportions (CTR, CVR).

    For binary metrics like click-through rate.
    """
    print("=" * 70)
    print("Example 5: Proportions Test (CTR/CVR)")
    print("=" * 70)

    # Scenario: CTR test
    print("\nScenario: Click-Through Rate (CTR) test")
    print("  Baseline CTR: 5%")
    print("  Want to detect: 10% relative increase (5% → 5.5%)")

    # Calculate required sample size
    n = calculate_sample_size_proportions(
        baseline_proportion=0.05,
        mde=0.10,  # 10% relative increase
        alpha=0.05,
        power=0.8,
        test_type="relative"
    )

    print(f"\nResult:")
    print(f"  Required sample size: {n:,} users per group")
    print(f"  Total impressions needed: {n*2:,}")

    # What MDE can we detect with smaller sample?
    print(f"\nIf we only have 5,000 users per group:")
    mde = calculate_mde_proportions(
        p=0.05,
        n=5000,
        test_type="relative"
    )

    print(f"  MDE: {mde:.2%} relative")
    print(f"  → Can detect CTR increase from 5.0% to {0.05 * (1 + mde):.2%}")
    print()


def example_6_using_proportion_data():
    """
    Example 6: Use ProportionData for planning.

    Demonstrates hybrid approach with ProportionData.
    """
    print("=" * 70)
    print("Example 6: Planning with Historical ProportionData")
    print("=" * 70)

    # Historical CTR data
    historical_ctr = ProportionData(
        successes=500,  # 500 clicks
        trials=10000,   # 10,000 impressions
        name="Last Month CTR"
    )

    print(f"\nHistorical data:")
    print(f"  Clicks: {historical_ctr.successes:,}")
    print(f"  Impressions: {historical_ctr.trials:,}")
    print(f"  CTR: {historical_ctr.successes/historical_ctr.trials:.2%}")

    # Calculate MDE using historical data
    mde = calculate_mde_proportions(
        sample=historical_ctr,  # Use ProportionData directly!
        n=10000
    )

    print(f"\nPlanning for new experiment:")
    print(f"  Target sample size: 10,000 per group")
    print(f"  MDE: {mde:.2%} relative")

    # Calculate required sample size
    n = calculate_sample_size_proportions(
        sample=historical_ctr,  # Use ProportionData directly!
        mde=0.10  # Want to detect 10% relative increase
    )

    print(f"\nTo detect 10% relative increase:")
    print(f"  Need: {n:,} impressions per group")
    print()


def example_7_correlation_impact():
    """
    Example 7: Impact of correlation on CUPED effectiveness.

    Shows how correlation affects variance reduction.
    """
    print("=" * 70)
    print("Example 7: Correlation Impact on CUPED")
    print("=" * 70)

    print("\nScenario: How does correlation affect sample size?")
    print("  Baseline: mean=$100, std=$20")
    print("  Target MDE: 5%")

    # Regular t-test
    n_regular = calculate_sample_size_ttest(baseline_mean=100, std=20, mde=0.05)
    print(f"\nRegular T-Test: {n_regular:,} users")

    # CUPED with different correlations
    correlations = [0.3, 0.5, 0.7, 0.9]
    print("\nCUPED with different correlations:")

    for corr in correlations:
        n_cuped = calculate_sample_size_cuped(
            baseline_mean=100,
            std=20,
            mde=0.05,
            correlation=corr
        )
        reduction = (n_regular - n_cuped) / n_regular
        print(f"  ρ={corr:.1f}: {n_cuped:,} users (reduction: {reduction:.1%})")

    print("\n→ Higher correlation = more variance reduction = fewer users needed!")
    print()


def example_8_comparison_utility():
    """
    Example 8: Use comparison utility to see CUPED benefit.
    """
    print("=" * 70)
    print("Example 8: Quick Comparison Utility")
    print("=" * 70)

    print("\nCompare regular vs CUPED MDE:")
    print("  Sample size: 1,000 per group")
    print("  Correlation: 0.7")

    mde_regular, mde_cuped, improvement = compare_mde_with_without_cuped(
        mean=100,
        std=20,
        n=1000,
        correlation=0.7
    )

    print(f"\nResults:")
    print(f"  Regular MDE: {mde_regular:.2%}")
    print(f"  CUPED MDE: {mde_cuped:.2%}")
    print(f"  Improvement: {improvement:.1%}")
    print(f"\n→ With CUPED, can detect {improvement:.1%} smaller effects!")
    print()


if __name__ == "__main__":
    # Run all examples
    example_1_basic_mde_calculation()
    example_2_sample_size_calculation()
    example_3_using_historical_data()
    example_4_cuped_advantage()
    example_5_proportions_test()
    example_6_using_proportion_data()
    example_7_correlation_impact()
    example_8_comparison_utility()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nKey takeaways:")
    print("  1. Use historical data (SampleData/ProportionData) when available")
    print("  2. CUPED reduces sample size by up to 81% (with ρ=0.9)")
    print("  3. Higher baseline proportions need more users")
    print("  4. Smaller MDE requires more users")
    print("  5. correlation=0.7 is typical for good covariate")
