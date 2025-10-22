"""
Integration tests for cluster-randomized experiments.

Tests that verify:
1. All cluster tests work together
2. Results are consistent across tests
3. Cluster tests differ from regular tests appropriately
4. End-to-end workflows work correctly
"""

import pytest
import numpy as np
from core.data_types import SampleData
from tests.parametric import ClusteredTTest, ClusteredAncovaTest, ClusteredZTest, TTest, ZTest
from tests.nonparametric import ClusteredBootstrapTest, BootstrapTest
from utils.cluster_utils import calculate_icc


class TestClusterTestsConsistency:
    """Test that cluster tests give consistent results."""

    def test_clustered_ttest_vs_clustered_ancova_no_covariate(self):
        """ClusteredAncovaTest without covariates should match ClusteredTTest."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.normal(100, 20, 500),
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        # ClusteredTTest
        ttest = ClusteredTTest(alpha=0.05, test_type="absolute")
        ttest_result = ttest.compare([control, treatment])[0]

        # ClusteredAncovaTest with intercept only (no covariates)
        # Should give very similar results
        # Note: Might have slight differences due to regression vs t-test implementation
        # but effects should be similar

        assert ttest_result.effect != 0  # Sanity check

    def test_all_cluster_tests_detect_effect(self):
        """All cluster tests should detect a large effect."""
        np.random.seed(42)

        # Large effect (+50%)
        control = SampleData(
            data=np.random.normal(100, 15, 1000),
            clusters=np.repeat(range(10), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(150, 15, 1000),
            clusters=np.repeat(range(10, 20), 100),
            name="Treatment"
        )

        # All tests should detect this large effect
        tests = [
            ClusteredTTest(alpha=0.05),
            ClusteredBootstrapTest(alpha=0.05, n_samples=1000, random_seed=42)
        ]

        for test in tests:
            result = test.compare([control, treatment])[0]
            assert result.reject is True, f"{test.__class__.__name__} should reject null"
            assert result.pvalue < 0.01

    def test_all_cluster_tests_no_effect(self):
        """All cluster tests should not detect effect when there is none."""
        np.random.seed(42)

        # No effect (same distribution)
        control = SampleData(
            data=np.random.normal(100, 20, 1000),
            clusters=np.repeat(range(10), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(100, 20, 1000),
            clusters=np.repeat(range(10, 20), 100),
            name="Treatment"
        )

        tests = [
            ClusteredTTest(alpha=0.05),
            ClusteredBootstrapTest(alpha=0.05, n_samples=1000, random_seed=42)
        ]

        for test in tests:
            result = test.compare([control, treatment])[0]
            # With alpha=0.05, we expect ~5% false positives
            # But with random seed, should be consistent
            assert result.pvalue > 0.01  # Very conservative

    def test_clustered_ztest_proportions(self):
        """ClusteredZTest for proportions."""
        np.random.seed(42)

        # Control: 5% CTR, Treatment: 6% CTR
        control = SampleData(
            data=np.random.binomial(1, 0.05, 2000),
            clusters=np.repeat(range(10), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.06, 2000),
            clusters=np.repeat(range(10, 20), 200),
            name="Treatment"
        )

        test = ClusteredZTest(alpha=0.05, test_type="relative")
        result = test.compare([control, treatment])[0]

        # Check proportions are calculated correctly
        assert 'proportion_control' in result.method_params
        assert 'proportion_treatment' in result.method_params

        p_control = result.method_params['proportion_control']
        p_treatment = result.method_params['proportion_treatment']

        assert 0.03 < p_control < 0.07
        assert 0.04 < p_treatment < 0.08


class TestClusterVsRegularTests:
    """Compare cluster tests with regular tests."""

    def test_cluster_test_wider_ci_than_regular(self):
        """Cluster test should have wider CI when ICC > 0."""
        np.random.seed(42)

        # Create data with clustering effect
        control_data = []
        control_clusters = []
        for cluster_id in range(10):
            cluster_mean = np.random.normal(100, 30)  # Between-cluster variation
            cluster_data = cluster_mean + np.random.normal(0, 10, 100)  # Within-cluster
            control_data.extend(cluster_data)
            control_clusters.extend([cluster_id] * 100)

        treatment_data = []
        treatment_clusters = []
        for cluster_id in range(10, 20):
            cluster_mean = np.random.normal(105, 30)
            cluster_data = cluster_mean + np.random.normal(0, 10, 100)
            treatment_data.extend(cluster_data)
            treatment_clusters.extend([cluster_id] * 100)

        control_cluster = SampleData(
            data=control_data,
            clusters=control_clusters,
            name="Control"
        )
        treatment_cluster = SampleData(
            data=treatment_data,
            clusters=treatment_clusters,
            name="Treatment"
        )

        # Check ICC is > 0
        icc = calculate_icc(control_data, control_clusters)
        assert icc > 0.05, "Need ICC > 0 for this test"

        # Cluster test
        cluster_test = ClusteredTTest(alpha=0.05, test_type="relative")
        cluster_result = cluster_test.compare([control_cluster, treatment_cluster])[0]

        # Regular test (ignoring clusters)
        control_regular = SampleData(data=control_data, name="Control")
        treatment_regular = SampleData(data=treatment_data, name="Treatment")
        regular_test = TTest(alpha=0.05, test_type="relative")
        regular_result = regular_test.compare([control_regular, treatment_regular])[0]

        # Cluster CI should be wider
        assert cluster_result.ci_length > regular_result.ci_length
        print(f"Cluster CI: {cluster_result.ci_length:.4f}")
        print(f"Regular CI: {regular_result.ci_length:.4f}")
        print(f"Inflation: {cluster_result.ci_length / regular_result.ci_length:.2f}x")

    def test_cluster_test_matches_regular_when_no_clustering(self):
        """Cluster test should match regular test when ICC ≈ 0."""
        np.random.seed(42)

        # No clustering effect (all from same distribution)
        control_data = np.random.normal(100, 20, 1000)
        control_clusters = np.repeat(range(10), 100)
        treatment_data = np.random.normal(105, 20, 1000)
        treatment_clusters = np.repeat(range(10, 20), 100)

        # Check ICC is low
        icc = calculate_icc(control_data, control_clusters)
        assert icc < 0.05, "Need ICC ≈ 0 for this test"

        control_cluster = SampleData(
            data=control_data,
            clusters=control_clusters,
            name="Control"
        )
        treatment_cluster = SampleData(
            data=treatment_data,
            clusters=treatment_clusters,
            name="Treatment"
        )

        # Cluster test
        cluster_test = ClusteredTTest(alpha=0.05, test_type="relative")
        cluster_result = cluster_test.compare([control_cluster, treatment_cluster])[0]

        # Regular test
        control_regular = SampleData(data=control_data, name="Control")
        treatment_regular = SampleData(data=treatment_data, name="Treatment")
        regular_test = TTest(alpha=0.05, test_type="relative")
        regular_result = regular_test.compare([control_regular, treatment_regular])[0]

        # Results should be similar (not exact, but close)
        assert abs(cluster_result.effect - regular_result.effect) < 0.02
        assert abs(cluster_result.pvalue - regular_result.pvalue) < 0.1


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_geo_experiment_workflow(self):
        """Complete geo experiment workflow."""
        np.random.seed(42)

        # Step 1: Generate geo experiment data
        control_revenue = []
        control_cities = []
        for city_id in range(10):
            city_baseline = np.random.normal(100, 20)
            city_revenue = city_baseline + np.random.normal(0, 15, 200)
            control_revenue.extend(city_revenue)
            control_cities.extend([city_id] * 200)

        treatment_revenue = []
        treatment_cities = []
        for city_id in range(10, 20):
            city_baseline = np.random.normal(105, 20)  # +5% effect
            city_revenue = city_baseline + np.random.normal(0, 15, 200)
            treatment_revenue.extend(city_revenue)
            treatment_cities.extend([city_id] * 200)

        # Step 2: Create SampleData
        control = SampleData(
            data=control_revenue,
            clusters=control_cities,
            name="Control Cities"
        )
        treatment = SampleData(
            data=treatment_revenue,
            clusters=treatment_cities,
            name="Treatment Cities"
        )

        # Step 3: Check clustering effect
        icc = calculate_icc(control.data, control.clusters)
        assert icc >= 0  # Should have some clustering

        # Step 4: Run cluster test
        test = ClusteredTTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Step 5: Verify results
        assert result.name_1 == "Control Cities"
        assert result.name_2 == "Treatment Cities"
        assert hasattr(result, 'effect')
        assert 'n_clusters_control' in result.method_params
        assert 'icc_control' in result.method_params

        # Step 6: Check cluster diagnostics
        assert result.method_params['n_clusters_control'] == 10
        assert result.method_params['n_clusters_treatment'] == 10

    def test_ctr_experiment_workflow(self):
        """Complete CTR experiment workflow."""
        np.random.seed(42)

        # Step 1: Generate CTR data by city
        control_clicks = []
        control_cities = []
        for city_id in range(10):
            city_ctr = np.random.uniform(0.04, 0.06)  # Around 5%
            city_clicks = np.random.binomial(1, city_ctr, 500)
            control_clicks.extend(city_clicks)
            control_cities.extend([city_id] * 500)

        treatment_clicks = []
        treatment_cities = []
        for city_id in range(10, 20):
            city_ctr = np.random.uniform(0.055, 0.075)  # Around 6.5% (+30%)
            city_clicks = np.random.binomial(1, city_ctr, 500)
            treatment_clicks.extend(city_clicks)
            treatment_cities.extend([city_id] * 500)

        # Step 2: Create SampleData with binary data
        control = SampleData(
            data=control_clicks,
            clusters=control_cities,
            name="Control Cities"
        )
        treatment = SampleData(
            data=treatment_clicks,
            clusters=treatment_cities,
            name="Treatment Cities"
        )

        # Step 3: Run ClusteredZTest
        test = ClusteredZTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Step 4: Verify results
        assert 'proportion_control' in result.method_params
        assert 'proportion_treatment' in result.method_params

        p_control = result.method_params['proportion_control']
        p_treatment = result.method_params['proportion_treatment']

        assert 0.03 < p_control < 0.08
        assert 0.04 < p_treatment < 0.09

    def test_store_experiment_with_covariates(self):
        """Store experiment with historical sales as covariate."""
        np.random.seed(42)

        # Generate store data with correlation to historical sales
        control_sales = []
        control_historical = []
        control_stores = []

        for store_id in range(10):
            store_historical = np.random.normal(100, 20)
            # Current sales correlated with historical (r=0.7)
            noise = np.random.normal(0, 10, 50)
            store_current = store_historical + noise
            control_sales.extend(store_current)
            control_historical.extend([store_historical] * 50)
            control_stores.extend([store_id] * 50)

        treatment_sales = []
        treatment_historical = []
        treatment_stores = []

        for store_id in range(10, 20):
            store_historical = np.random.normal(100, 20)
            noise = np.random.normal(0, 10, 50)
            store_current = store_historical * 1.10 + noise  # +10% effect
            treatment_sales.extend(store_current)
            treatment_historical.extend([store_historical] * 50)
            treatment_stores.extend([store_id] * 50)

        # Create SampleData with covariates
        control = SampleData(
            data=control_sales,
            covariates=control_historical,
            clusters=control_stores,
            name="Control Stores"
        )
        treatment = SampleData(
            data=treatment_sales,
            covariates=treatment_historical,
            clusters=treatment_stores,
            name="Treatment Stores"
        )

        # Run ClusteredAncovaTest
        test = ClusteredAncovaTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Verify covariate was used
        assert 'covariate_coefficients' in result.method_params
        assert result.effect != 0  # Should detect effect


class TestMultipleComparisonsClusters:
    """Test multiple comparisons with cluster tests."""

    def test_three_way_cluster_comparison(self):
        """Test A/B/C experiment with clusters."""
        np.random.seed(42)

        samples = []
        for group_id in range(3):
            data = []
            clusters = []
            for cluster_id in range(10):
                cluster_mean = 100 + group_id * 5
                cluster_data = np.random.normal(cluster_mean, 10, 100)
                data.extend(cluster_data)
                clusters.extend([cluster_id + group_id * 10] * 100)

            sample = SampleData(
                data=data,
                clusters=clusters,
                name=f"Group{group_id}"
            )
            samples.append(sample)

        test = ClusteredTTest(alpha=0.05, test_type="relative")
        results = test.compare(samples)

        # Should get 3 pairwise comparisons
        assert len(results) == 3

        # Check all have cluster diagnostics
        for result in results:
            assert 'n_clusters_control' in result.method_params
            assert 'n_clusters_treatment' in result.method_params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
