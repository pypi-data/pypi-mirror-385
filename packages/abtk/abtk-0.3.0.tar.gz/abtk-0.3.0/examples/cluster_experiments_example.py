"""
Cluster-Randomized Experiments Examples

This file demonstrates all 4 cluster tests with realistic examples:
1. Geo experiment (ClusteredTTest)
2. Store experiment with covariates (ClusteredAncovaTest)
3. CTR experiment (ClusteredZTest)
4. Non-normal data (ClusteredBootstrapTest)
5. ICC calculation and interpretation
6. Design effect impact
"""

import numpy as np
from core.data_types import SampleData
from tests.parametric import ClusteredTTest, ClusteredAncovaTest, ClusteredZTest
from tests.nonparametric import ClusteredBootstrapTest
from utils.cluster_utils import calculate_icc, calculate_design_effect


def print_section(title):
    """Print section separator"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_results(result):
    """Pretty print test results"""
    print(f"Effect: {result.effect:.2%}")
    print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
    print(f"P-value: {result.pvalue:.4f}")
    print(f"Significant: {'Yes ✓' if result.reject else 'No ✗'}")


def print_cluster_diagnostics(result):
    """Print cluster-specific diagnostics"""
    print("\nCluster Diagnostics:")
    print(f"  N clusters (control): {result.method_params['n_clusters_control']}")
    print(f"  N clusters (treatment): {result.method_params['n_clusters_treatment']}")
    print(f"  ICC (control): {result.method_params['icc_control']:.3f}")
    print(f"  ICC (treatment): {result.method_params['icc_treatment']:.3f}")
    print(f"  Design Effect (control): {result.method_params['design_effect_control']:.2f}")
    print(f"  Design Effect (treatment): {result.method_params['design_effect_treatment']:.2f}")
    print(f"  Cluster size CV (control): {result.method_params['cluster_size_cv_control']:.2f}")


# =============================================================================
# Example 1: Geo Experiment (Cities) - ClusteredTTest
# =============================================================================

print_section("Example 1: Geo Experiment (Cities) - ClusteredTTest")

print("Scenario: Testing a new feature across 10 cities")
print("- 5 cities in control, 5 cities in treatment")
print("- 200 users per city (1000 users total per group)")
print("- Metric: Average session time (seconds)")
print("- Expected effect: +5%")

np.random.seed(42)

# Simulate control cities
control_data = []
control_clusters = []

for city_id in range(1, 6):
    # Each city has its own baseline (city-level effect)
    # This creates ICC > 0
    city_baseline = np.random.normal(300, 30)  # City mean varies

    # Users within city have individual variation
    city_users = city_baseline + np.random.normal(0, 50, 200)

    control_data.extend(city_users)
    control_clusters.extend([city_id] * 200)

# Simulate treatment cities (+5% effect)
treatment_data = []
treatment_clusters = []

for city_id in range(6, 11):
    city_baseline = np.random.normal(315, 30)  # +5% effect (300 * 1.05 = 315)
    city_users = city_baseline + np.random.normal(0, 50, 200)

    treatment_data.extend(city_users)
    treatment_clusters.extend([city_id] * 200)

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

print(f"\nControl mean: {control.mean:.1f}s")
print(f"Treatment mean: {treatment.mean:.1f}s")

# Calculate ICC to verify clustering matters
icc_control = calculate_icc(control.data, control.clusters, method="anova")
print(f"\nICC (control): {icc_control:.3f}")

if icc_control > 0.05:
    print("→ ICC > 0.05: Clustering matters! Use cluster tests.")
else:
    print("→ ICC < 0.05: Small clustering effect.")

# Run ClusteredTTest
test = ClusteredTTest(alpha=0.05, test_type="relative", min_clusters=5)
results = test.compare([control, treatment])
result = results[0]

print("\n--- ClusteredTTest Results ---")
print_results(result)
print_cluster_diagnostics(result)

# Compare with regular TTest (wrong!)
print("\n⚠️ Comparison: What if we ignored clustering?")
from tests.parametric import TTest

regular_test = TTest(alpha=0.05, test_type="relative")
regular_result = regular_test.compare([control, treatment])[0]

print(f"Regular TTest CI: [{regular_result.left_bound:.2%}, {regular_result.right_bound:.2%}]")
print(f"Cluster TTest CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
print(f"CI inflation: {result.ci_length / regular_result.ci_length:.2f}x wider (due to clustering)")


# =============================================================================
# Example 2: Store Experiment with Covariates - ClusteredAncovaTest
# =============================================================================

print_section("Example 2: Store Experiment with Covariates - ClusteredAncovaTest")

print("Scenario: Testing a new promotion across 20 stores")
print("- 10 stores in control, 10 stores in treatment")
print("- 50 transactions per store (500 per group)")
print("- Metric: Average basket size ($)")
print("- Covariate: Historical average basket size (for variance reduction)")

np.random.seed(123)

# Simulate control stores
control_sales = []
control_historical = []
control_store_ids = []

for store_id in range(1, 11):
    # Historical average for this store
    store_historical_avg = np.random.normal(50, 10)

    # Current sales correlated with historical (correlation = 0.7)
    noise = np.random.normal(0, 5, 50)
    store_sales = store_historical_avg + noise

    control_sales.extend(store_sales)
    control_historical.extend([store_historical_avg] * 50)
    control_store_ids.extend([store_id] * 50)

# Simulate treatment stores (+10% effect)
treatment_sales = []
treatment_historical = []
treatment_store_ids = []

for store_id in range(11, 21):
    store_historical_avg = np.random.normal(50, 10)

    # +10% treatment effect
    noise = np.random.normal(0, 5, 50)
    store_sales = store_historical_avg * 1.10 + noise

    treatment_sales.extend(store_sales)
    treatment_historical.extend([store_historical_avg] * 50)
    treatment_store_ids.extend([store_id] * 50)

# Create SampleData with covariates
control = SampleData(
    data=control_sales,
    covariates=control_historical,
    clusters=control_store_ids,
    name="Control Stores"
)
treatment = SampleData(
    data=treatment_sales,
    covariates=treatment_historical,
    clusters=treatment_store_ids,
    name="Treatment Stores"
)

print(f"\nControl mean: ${control.mean:.2f}")
print(f"Treatment mean: ${treatment.mean:.2f}")

# Run ClusteredAncovaTest (with covariate)
test_ancova = ClusteredAncovaTest(
    alpha=0.05,
    test_type="relative",
    validate_assumptions=True
)
results_ancova = test_ancova.compare([control, treatment])
result_ancova = results_ancova[0]

print("\n--- ClusteredAncovaTest Results (with covariate) ---")
print_results(result_ancova)
print_cluster_diagnostics(result_ancova)

# Compare with ClusteredTTest (without covariate)
test_no_cov = ClusteredTTest(alpha=0.05, test_type="relative")

# Remove covariates for comparison
control_no_cov = SampleData(
    data=control_sales,
    clusters=control_store_ids,
    name="Control Stores"
)
treatment_no_cov = SampleData(
    data=treatment_sales,
    clusters=treatment_store_ids,
    name="Treatment Stores"
)

results_no_cov = test_no_cov.compare([control_no_cov, treatment_no_cov])
result_no_cov = results_no_cov[0]

print("\n--- Variance Reduction from Covariate ---")
print(f"ClusteredTTest CI length: {result_no_cov.ci_length:.4f}")
print(f"ClusteredAncovaTest CI length: {result_ancova.ci_length:.4f}")
reduction = 1 - (result_ancova.ci_length / result_no_cov.ci_length)
print(f"Variance reduction: {reduction:.1%} (CI is {1/(1-reduction):.1f}x narrower!)")


# =============================================================================
# Example 3: CTR Experiment - ClusteredZTest
# =============================================================================

print_section("Example 3: CTR Experiment (Cities) - ClusteredZTest")

print("Scenario: Testing a new ad design across 10 cities")
print("- 5 cities in control, 5 cities in treatment")
print("- 1000 impressions per city")
print("- Metric: Click-through rate (CTR)")
print("- Expected effect: +20% relative (5% → 6% CTR)")

np.random.seed(456)

# Simulate control cities (5% CTR)
control_clicks = []
control_city_ids = []

for city_id in range(1, 6):
    # Each city has slightly different baseline CTR
    city_ctr = np.random.uniform(0.04, 0.06)  # Around 5%

    # Generate binary outcomes
    city_clicks = np.random.binomial(1, city_ctr, 1000)

    control_clicks.extend(city_clicks)
    control_city_ids.extend([city_id] * 1000)

# Simulate treatment cities (6% CTR, +20% relative)
treatment_clicks = []
treatment_city_ids = []

for city_id in range(6, 11):
    city_ctr = np.random.uniform(0.05, 0.07)  # Around 6%
    city_clicks = np.random.binomial(1, city_ctr, 1000)

    treatment_clicks.extend(city_clicks)
    treatment_city_ids.extend([city_id] * 1000)

# Create SampleData with binary data
control = SampleData(
    data=control_clicks,  # Binary: 0/1
    clusters=control_city_ids,
    name="Control Cities"
)
treatment = SampleData(
    data=treatment_clicks,
    clusters=treatment_city_ids,
    name="Treatment Cities"
)

print(f"\nControl CTR: {np.mean(control_clicks):.2%}")
print(f"Treatment CTR: {np.mean(treatment_clicks):.2%}")

# Run ClusteredZTest
test_ztest = ClusteredZTest(alpha=0.05, test_type="relative")
results_ztest = test_ztest.compare([control, treatment])
result_ztest = results_ztest[0]

print("\n--- ClusteredZTest Results ---")
print(f"Relative CTR lift: {result_ztest.effect:.2%}")
print(f"95% CI: [{result_ztest.left_bound:.2%}, {result_ztest.right_bound:.2%}]")
print(f"P-value: {result_ztest.pvalue:.4f}")
print(f"Significant: {'Yes ✓' if result_ztest.reject else 'No ✗'}")

print(f"\nControl CTR: {result_ztest.method_params['proportion_control']:.2%}")
print(f"Treatment CTR: {result_ztest.method_params['proportion_treatment']:.2%}")
print(f"Absolute difference: {result_ztest.method_params['absolute_difference']:.4f}")
print_cluster_diagnostics(result_ztest)


# =============================================================================
# Example 4: Non-Normal Data - ClusteredBootstrapTest
# =============================================================================

print_section("Example 4: Non-Normal Data (Skewed) - ClusteredBootstrapTest")

print("Scenario: Testing revenue impact across 12 cities")
print("- 6 cities in control, 6 cities in treatment")
print("- 200 users per city")
print("- Metric: Revenue per user (heavily right-skewed)")
print("- Distribution: Exponential (most users $0-50, some $200+)")

np.random.seed(789)

# Simulate control cities (exponential distribution)
control_revenue = []
control_city_ids = []

for city_id in range(1, 7):
    # Each city has different baseline revenue
    city_baseline = np.random.uniform(40, 60)

    # Exponential distribution (skewed)
    city_revenue = np.random.exponential(city_baseline, 200)

    control_revenue.extend(city_revenue)
    control_city_ids.extend([city_id] * 200)

# Simulate treatment cities (+15% effect on median)
treatment_revenue = []
treatment_city_ids = []

for city_id in range(7, 13):
    city_baseline = np.random.uniform(46, 69)  # +15%
    city_revenue = np.random.exponential(city_baseline, 200)

    treatment_revenue.extend(city_revenue)
    treatment_city_ids.extend([city_id] * 200)

# Create SampleData
control = SampleData(
    data=control_revenue,
    clusters=control_city_ids,
    name="Control Cities"
)
treatment = SampleData(
    data=treatment_revenue,
    clusters=treatment_city_ids,
    name="Treatment Cities"
)

print(f"\nControl mean: ${np.mean(control_revenue):.2f}")
print(f"Control median: ${np.median(control_revenue):.2f}")
print(f"Treatment mean: ${np.mean(treatment_revenue):.2f}")
print(f"Treatment median: ${np.median(treatment_revenue):.2f}")
print("\n→ Data is heavily right-skewed (mean >> median)")
print("→ Use ClusteredBootstrapTest with median")

# Run ClusteredBootstrapTest with median
test_bootstrap = ClusteredBootstrapTest(
    alpha=0.05,
    stat_func=np.median,  # Robust to outliers
    n_samples=10000,
    test_type="relative"
)
results_bootstrap = test_bootstrap.compare([control, treatment])
result_bootstrap = results_bootstrap[0]

print("\n--- ClusteredBootstrapTest Results (median) ---")
print(f"Median effect: {result_bootstrap.effect:.2%}")
print(f"95% CI: [{result_bootstrap.left_bound:.2%}, {result_bootstrap.right_bound:.2%}]")
print(f"P-value: {result_bootstrap.pvalue:.4f}")
print(f"Significant: {'Yes ✓' if result_bootstrap.reject else 'No ✗'}")

print(f"\nBootstrap distribution:")
print(f"  Mean: {result_bootstrap.method_params['bootstrap_mean']:.4f}")
print(f"  Std: {result_bootstrap.method_params['bootstrap_std']:.4f}")
print(f"  Normal: {'Yes' if result_bootstrap.method_params['bootstrap_is_normal'] else 'No'}")
print_cluster_diagnostics(result_bootstrap)


# =============================================================================
# Example 5: ICC Calculation and Interpretation
# =============================================================================

print_section("Example 5: ICC Calculation and Interpretation")

print("Demonstrating how to check if clustering matters\n")

# Scenario 1: Low ICC (clustering doesn't matter)
print("Scenario 1: Individual randomization (low ICC)")
low_icc_data = []
low_icc_clusters = []

for cluster_id in range(1, 6):
    # Very little cluster effect
    cluster_data = np.random.normal(100, 20, 100)  # All from same distribution
    low_icc_data.extend(cluster_data)
    low_icc_clusters.extend([cluster_id] * 100)

icc_low = calculate_icc(low_icc_data, low_icc_clusters, method="anova")
print(f"ICC: {icc_low:.4f}")
print("→ ICC < 0.01: No clustering effect, use regular tests (TTest, ZTest)")

# Scenario 2: Moderate ICC (clustering matters)
print("\nScenario 2: Cluster randomization (moderate ICC)")
mod_icc_data = []
mod_icc_clusters = []

for cluster_id in range(1, 6):
    # Strong cluster effect
    cluster_mean = np.random.normal(100, 30)  # Each cluster different
    cluster_data = cluster_mean + np.random.normal(0, 10, 100)  # Small within-cluster variation
    mod_icc_data.extend(cluster_data)
    mod_icc_clusters.extend([cluster_id] * 100)

icc_mod = calculate_icc(mod_icc_data, mod_icc_clusters, method="anova")
print(f"ICC: {icc_mod:.4f}")
print("→ ICC > 0.05: Moderate clustering, use cluster tests (ClusteredTTest, etc.)")


# =============================================================================
# Example 6: Design Effect Impact
# =============================================================================

print_section("Example 6: Design Effect Impact on Power")

print("Demonstrating how clustering reduces effective sample size\n")

# Calculate design effect for different scenarios
cluster_sizes = [100] * 10  # 10 clusters, 100 observations each
total_n = sum(cluster_sizes)

print(f"Total sample size: {total_n}")
print(f"Number of clusters: {len(cluster_sizes)}")
print(f"Average cluster size: {np.mean(cluster_sizes):.0f}\n")

for icc in [0.01, 0.05, 0.10, 0.20]:
    de = calculate_design_effect(cluster_sizes, icc)
    n_eff = total_n / de

    print(f"ICC = {icc:.2f}:")
    print(f"  Design Effect: {de:.2f}")
    print(f"  Effective n: {n_eff:.0f} (out of {total_n})")
    print(f"  Power loss: {(1 - n_eff/total_n)*100:.1f}%")
    print(f"  CI inflation: {np.sqrt(de):.2f}x wider\n")

print("→ Higher ICC → Higher Design Effect → Lower Effective Sample Size")
print("→ Need more clusters (not more obs per cluster) to increase power")


# =============================================================================
# Summary
# =============================================================================

print_section("Summary: When to Use Each Cluster Test")

print("""
1. ClusteredTTest
   - Continuous metrics (revenue, time, etc.)
   - Normal distribution
   - No covariates
   - Example: Geo experiment for session time

2. ClusteredAncovaTest
   - Continuous metrics
   - Have covariates (for variance reduction)
   - Want narrower CI (30-50% reduction)
   - Example: Store experiment with historical sales

3. ClusteredZTest
   - Binary metrics (CTR, CVR)
   - Proportions between 0.05 and 0.95
   - Need individual-level binary data
   - Example: Ad CTR experiment by city

4. ClusteredBootstrapTest
   - Any distribution (no assumptions)
   - Outliers or skewed data
   - Custom statistics (median, percentiles)
   - Example: Revenue (exponential distribution)

Key Reminders:
- Check ICC first (use calculate_icc())
- Need 5+ clusters per group (10+ recommended)
- Cluster tests have wider CI than regular tests (accounts for clustering)
- Use covariates when available (ClusteredAncovaTest)
- Watch for cluster size imbalance (check CV)
""")

print("\n" + "=" * 80)
print("  Examples complete! See docs/user-guide/cluster-experiments.md for more.")
print("=" * 80)
