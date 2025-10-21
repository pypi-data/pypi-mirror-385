"""
DataFrame Usage Examples

This example demonstrates how to use ABTK with pandas DataFrames using
the dataframe_helpers utilities. This is the recommended approach for
beginners and most common use cases.
"""

import numpy as np
import pandas as pd

from utils.dataframe_helpers import sample_data_from_dataframe, proportion_data_from_dataframe
from tests.parametric import TTest, CupedTTest, ZTest
from tests.nonparametric import BootstrapTest
from utils.corrections import adjust_pvalues


def example_1_basic_ab_test():
    """
    Example 1: Basic A/B test with continuous metric.

    Scenario: Testing a new checkout flow on revenue per user.
    """
    print("=" * 70)
    print("Example 1: Basic A/B Test with DataFrame")
    print("=" * 70)

    # Simulate experiment data
    np.random.seed(42)
    n_per_group = 1000

    df = pd.DataFrame({
        'user_id': range(2000),
        'variant': ['control'] * n_per_group + ['treatment'] * n_per_group,
        'revenue': (
            list(np.random.normal(100, 20, n_per_group)) +  # Control
            list(np.random.normal(105, 20, n_per_group))    # Treatment: +5% lift
        )
    })

    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())

    # Convert DataFrame to SampleData objects
    samples = sample_data_from_dataframe(
        df,
        group_col='variant',
        metric_col='revenue'
    )

    print(f"\nCreated {len(samples)} samples:")
    for sample in samples:
        print(f"  - {sample.name}: n={len(sample.data)}, mean={sample.data.mean():.2f}")

    # Run T-Test
    test = TTest(alpha=0.05, test_type="relative")
    results = test.compare(samples)

    result = results[0]
    print(f"\nResults:")
    print(f"  Effect: {result.effect:.2%}")
    print(f"  P-value: {result.pvalue:.4f}")
    print(f"  Significant: {result.reject}")
    print(f"  95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
    print()


def example_2_with_covariates():
    """
    Example 2: A/B test with covariates (CUPED).

    Scenario: Testing price change with historical revenue as covariate.
    """
    print("=" * 70)
    print("Example 2: A/B Test with Covariates (CUPED)")
    print("=" * 70)

    np.random.seed(42)
    n_per_group = 500

    # Simulate correlated baseline and current metrics
    baseline_control = np.random.normal(100, 15, n_per_group)
    baseline_treatment = np.random.normal(100, 15, n_per_group)

    # Current metric is correlated with baseline (rho=0.7)
    df = pd.DataFrame({
        'user_id': range(1000),
        'variant': ['control'] * n_per_group + ['treatment'] * n_per_group,
        'current_revenue': np.concatenate([
            baseline_control * 0.7 + np.random.normal(0, 10, n_per_group),
            baseline_treatment * 0.7 + np.random.normal(8, 10, n_per_group)  # +8 lift
        ]),
        'baseline_revenue': np.concatenate([baseline_control, baseline_treatment])
    })

    print(f"\nDataFrame columns: {list(df.columns)}")
    print(f"Correlation between current and baseline: {df['current_revenue'].corr(df['baseline_revenue']):.3f}")

    # Convert DataFrame with covariates
    samples = sample_data_from_dataframe(
        df,
        group_col='variant',
        metric_col='current_revenue',
        covariate_cols='baseline_revenue'  # Enable variance reduction
    )

    # Compare: Regular T-Test vs CUPED T-Test
    print("\n--- Regular T-Test (no variance reduction) ---")
    test_regular = TTest(alpha=0.05, test_type="absolute")
    results_regular = test_regular.compare(samples)
    result_regular = results_regular[0]
    print(f"  Effect: {result_regular.effect:.2f}")
    print(f"  P-value: {result_regular.pvalue:.4f}")
    print(f"  CI width: {result_regular.ci_length:.2f}")

    print("\n--- CUPED T-Test (with variance reduction) ---")
    test_cuped = CupedTTest(alpha=0.05, test_type="absolute")
    results_cuped = test_cuped.compare(samples)
    result_cuped = results_cuped[0]
    print(f"  Effect: {result_cuped.effect:.2f}")
    print(f"  P-value: {result_cuped.pvalue:.4f}")
    print(f"  CI width: {result_cuped.ci_length:.2f}")
    print(f"  CI reduction: {(1 - result_cuped.ci_length/result_regular.ci_length):.1%}")
    print()


def example_3_proportions_aggregated():
    """
    Example 3: Proportion test with aggregated data.

    Scenario: Testing ad creative on click-through rate (CTR).
    """
    print("=" * 70)
    print("Example 3: Proportion Test - Aggregated Data")
    print("=" * 70)

    # Aggregated data: one row per variant
    df = pd.DataFrame({
        'ad_variant': ['control', 'treatment_a', 'treatment_b'],
        'clicks': [450, 520, 485],
        'impressions': [10000, 10000, 10000]
    })

    print(f"\nAggregated data:")
    print(df)
    print(f"\nCTRs: {(df['clicks'] / df['impressions'] * 100).values}")

    # Convert to ProportionData
    samples = proportion_data_from_dataframe(
        df,
        group_col='ad_variant',
        successes_col='clicks',
        trials_col='impressions'
    )

    print(f"\nCreated {len(samples)} samples:")
    for sample in samples:
        ctr = sample.successes / sample.trials
        print(f"  - {sample.name}: {sample.successes}/{sample.trials} = {ctr:.2%}")

    # Run Z-Test
    test = ZTest(alpha=0.05, test_type="relative")
    results = test.compare(samples)

    # Apply Bonferroni correction (3 tests)
    adjusted = adjust_pvalues(results, method="bonferroni")

    print(f"\nResults (with Bonferroni correction for {len(results)} comparisons):")
    for result in adjusted:
        print(f"\n  {result.name_1} vs {result.name_2}:")
        print(f"    Effect: {result.effect:.2%}")
        print(f"    P-value (adjusted): {result.pvalue:.4f}")
        print(f"    Significant: {result.reject}")
    print()


def example_4_proportions_raw_binary():
    """
    Example 4: Proportion test with raw binary data.

    Scenario: Testing signup flow on conversion rate (user-level data).
    """
    print("=" * 70)
    print("Example 4: Proportion Test - Raw Binary Data")
    print("=" * 70)

    np.random.seed(42)
    n_per_group = 2000

    # User-level binary data (0 or 1)
    df = pd.DataFrame({
        'user_id': range(4000),
        'flow_variant': ['old_flow'] * n_per_group + ['new_flow'] * n_per_group,
        'converted': (
            list(np.random.binomial(1, 0.10, n_per_group)) +  # Old: 10% CVR
            list(np.random.binomial(1, 0.12, n_per_group))    # New: 12% CVR
        )
    })

    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nConversion rates by variant:")
    print(df.groupby('flow_variant')['converted'].agg(['sum', 'count', 'mean']))

    # Convert binary column to ProportionData
    samples = proportion_data_from_dataframe(
        df,
        group_col='flow_variant',
        binary_col='converted'  # Use binary column (not aggregated)
    )

    print(f"\nCreated {len(samples)} samples:")
    for sample in samples:
        cvr = sample.successes / sample.trials
        print(f"  - {sample.name}: {sample.successes}/{sample.trials} = {cvr:.2%}")

    # Run Z-Test
    test = ZTest(alpha=0.05, test_type="relative")
    results = test.compare(samples)

    result = results[0]
    print(f"\nResults:")
    print(f"  Effect: {result.effect:.2%}")
    print(f"  P-value: {result.pvalue:.4f}")
    print(f"  Significant: {result.reject}")
    print(f"  95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
    print()


def example_5_multiple_variants():
    """
    Example 5: Multi-variant test with multiple comparisons correction.

    Scenario: Testing 5 different landing pages.
    """
    print("=" * 70)
    print("Example 5: Multi-Variant Test (A/B/C/D/E)")
    print("=" * 70)

    np.random.seed(42)
    n_per_group = 300

    # 5 variants with different effect sizes
    variants = ['control', 'variant_a', 'variant_b', 'variant_c', 'variant_d']
    effects = [0, 2, 5, 1, 8]  # Only variant_b and variant_d have real effects

    data = []
    for variant, effect in zip(variants, effects):
        data.extend([{
            'variant': variant,
            'time_on_site': val
        } for val in np.random.normal(100 + effect, 15, n_per_group)])

    df = pd.DataFrame(data)

    print(f"\nTesting {len(variants)} variants:")
    print(df.groupby('variant')['time_on_site'].agg(['count', 'mean', 'std']))

    # Convert DataFrame
    samples = sample_data_from_dataframe(
        df,
        group_col='variant',
        metric_col='time_on_site'
    )

    # Run Bootstrap test (more robust for this data)
    test = BootstrapTest(alpha=0.05, test_type="relative", n_samples=5000)
    results = test.compare(samples)

    print(f"\n--- Without Correction ({len(results)} comparisons) ---")
    for result in results:
        print(f"{result.name_1} vs {result.name_2}: "
              f"effect={result.effect:.2%}, p={result.pvalue:.4f}, sig={result.reject}")

    # Apply Holm correction
    adjusted = adjust_pvalues(results, method="holm")

    print(f"\n--- With Holm Correction ---")
    for result in adjusted:
        print(f"{result.name_1} vs {result.name_2}: "
              f"effect={result.effect:.2%}, p={result.pvalue:.4f}, sig={result.reject}")

    print("\nNote: With correction, only truly significant effects remain!")
    print()


def example_6_paired_data():
    """
    Example 6: Paired test with user IDs.

    Scenario: Before/after test on the same users.
    """
    print("=" * 70)
    print("Example 6: Paired Test with User IDs")
    print("=" * 70)

    np.random.seed(42)
    n_users = 500

    # Each user has before and after measurement
    user_ids = list(range(n_users)) * 2

    # After measurements have +5 lift on average
    before_vals = np.random.normal(100, 20, n_users)
    after_vals = before_vals + np.random.normal(5, 10, n_users)  # Correlated

    df = pd.DataFrame({
        'user_id': user_ids,
        'period': ['before'] * n_users + ['after'] * n_users,
        'metric': np.concatenate([before_vals, after_vals])
    })

    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nMeans by period:")
    print(df.groupby('period')['metric'].mean())

    # Convert with paired IDs
    samples = sample_data_from_dataframe(
        df,
        group_col='period',
        metric_col='metric',
        paired_id_col='user_id'  # Enable paired analysis
    )

    print(f"\nCreated {len(samples)} samples with paired IDs")

    # Compare: Regular vs Paired T-Test
    print("\n--- Regular T-Test (ignores pairing) ---")
    from tests.parametric import TTest
    test_regular = TTest(alpha=0.05, test_type="absolute")
    results_regular = test_regular.compare(samples)
    result_regular = results_regular[0]
    print(f"  Effect: {result_regular.effect:.2f}")
    print(f"  P-value: {result_regular.pvalue:.4f}")
    print(f"  CI width: {result_regular.ci_length:.2f}")

    print("\n--- Paired T-Test (uses pairing) ---")
    from tests.parametric import PairedTTest
    test_paired = PairedTTest(alpha=0.05, test_type="absolute")
    results_paired = test_paired.compare(samples)
    result_paired = results_paired[0]
    print(f"  Effect: {result_paired.effect:.2f}")
    print(f"  P-value: {result_paired.pvalue:.4f}")
    print(f"  CI width: {result_paired.ci_length:.2f}")
    print(f"  Power gain: {(1 - result_paired.ci_length/result_regular.ci_length):.1%}")
    print()


def example_7_missing_data():
    """
    Example 7: Handling missing data.

    Shows how the DataFrame helpers handle missing values.
    """
    print("=" * 70)
    print("Example 7: Handling Missing Data")
    print("=" * 70)

    # Create data with some missing values
    df = pd.DataFrame({
        'variant': ['control'] * 100 + ['treatment'] * 100,
        'revenue': list(np.random.normal(100, 10, 90)) + [np.nan] * 10 +
                   list(np.random.normal(105, 10, 95)) + [np.nan] * 5,
        'baseline': list(np.random.normal(95, 10, 85)) + [np.nan] * 15 +
                    list(np.random.normal(95, 10, 92)) + [np.nan] * 8
    })

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Missing values:")
    print(df.isnull().sum())

    # The helper automatically drops missing values with warnings
    print("\nConverting to SampleData (watch for warnings):")
    samples = sample_data_from_dataframe(
        df,
        group_col='variant',
        metric_col='revenue',
        covariate_cols='baseline'
    )

    print(f"\nFinal sample sizes:")
    for sample in samples:
        print(f"  - {sample.name}: n={len(sample.data)} "
              f"(dropped {100 - len(sample.data)} rows)")

    # Run test
    test = TTest(alpha=0.05)
    results = test.compare(samples)
    result = results[0]
    print(f"\nTest completed successfully with cleaned data")
    print(f"  P-value: {result.pvalue:.4f}")
    print()


if __name__ == "__main__":
    # Run all examples
    example_1_basic_ab_test()
    example_2_with_covariates()
    example_3_proportions_aggregated()
    example_4_proportions_raw_binary()
    example_5_multiple_variants()
    example_6_paired_data()
    example_7_missing_data()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nKey takeaways:")
    print("  1. DataFrame helpers simplify data preparation")
    print("  2. Support both continuous metrics and proportions")
    print("  3. Handle covariates, paired data, and categories")
    print("  4. Automatically clean missing data")
    print("  5. Work seamlessly with all ABTK tests")
