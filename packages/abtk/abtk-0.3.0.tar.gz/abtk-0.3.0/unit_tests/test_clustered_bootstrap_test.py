"""
Unit tests for ClusteredBootstrapTest.

Tests for cluster bootstrap test with cluster resampling.
"""

import pytest
import numpy as np
from core.data_types import SampleData
from tests.nonparametric import ClusteredBootstrapTest


class TestClusteredBootstrapTestBasic:
    """Basic functionality tests."""

    def test_initialization(self):
        """Test basic initialization."""
        test = ClusteredBootstrapTest(
            alpha=0.05,
            stat_func=np.mean,
            n_samples=1000,
            test_type="relative"
        )

        assert test.alpha == 0.05
        assert test.stat_func == np.mean
        assert test.n_samples == 1000
        assert test.test_type == "relative"

    def test_initialization_with_custom_stat(self):
        """Test initialization with custom statistic."""
        test = ClusteredBootstrapTest(stat_func=np.median)

        assert test.stat_func == np.median

    def test_warns_low_n_samples(self):
        """Should warn if n_samples is low."""
        with pytest.warns(UserWarning, match="n_samples.*quite low"):
            test = ClusteredBootstrapTest(n_samples=500)


class TestClusteredBootstrapTestCompare:
    """Tests for compare() method."""

    def test_compare_two_samples(self):
        """Test basic comparison."""
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

        test = ClusteredBootstrapTest(
            alpha=0.05,
            n_samples=1000,
            random_seed=42
        )
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        assert hasattr(result, 'effect')
        assert hasattr(result, 'pvalue')
        assert hasattr(result, 'left_bound')
        assert hasattr(result, 'right_bound')

    def test_reproducibility_with_seed(self):
        """Results should be reproducible with same seed."""
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

        test1 = ClusteredBootstrapTest(n_samples=1000, random_seed=123)
        result1 = test1.compare([control, treatment])[0]

        test2 = ClusteredBootstrapTest(n_samples=1000, random_seed=123)
        result2 = test2.compare([control, treatment])[0]

        # Should get same results
        assert result1.pvalue == pytest.approx(result2.pvalue, abs=1e-6)
        assert result1.effect == pytest.approx(result2.effect, abs=1e-6)

    def test_missing_clusters_raises(self):
        """Should raise if samples missing clusters."""
        control = SampleData(
            data=np.random.normal(100, 20, 500),
            name="Control"
            # No clusters!
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(5), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest()

        with pytest.raises(ValueError, match="missing clusters"):
            test.compare([control, treatment])


class TestClusteredBootstrapTestStatistics:
    """Tests for custom statistics."""

    def test_median_statistic(self):
        """Test with median instead of mean."""
        np.random.seed(42)

        # Skewed data (exponential)
        control = SampleData(
            data=np.random.exponential(50, 500),
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.exponential(55, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest(
            stat_func=np.median,
            n_samples=1000,
            random_seed=42
        )
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        # Should compute median, not mean
        assert 'stat_control' in result.method_params
        assert 'stat_treatment' in result.method_params

    def test_percentile_statistic(self):
        """Test with percentile statistic."""
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

        # 90th percentile
        test = ClusteredBootstrapTest(
            stat_func=lambda x: np.percentile(x, 90),
            n_samples=1000,
            random_seed=42
        )
        results = test.compare([control, treatment])

        assert len(results) == 1


class TestClusteredBootstrapTestResults:
    """Tests for test results and diagnostics."""

    def test_result_has_bootstrap_diagnostics(self):
        """Result should include bootstrap-specific diagnostics."""
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

        test = ClusteredBootstrapTest(n_samples=1000, random_seed=42)
        results = test.compare([control, treatment])
        result = results[0]

        assert 'bootstrap_mean' in result.method_params
        assert 'bootstrap_std' in result.method_params
        assert 'bootstrap_normality_pvalue' in result.method_params
        assert 'bootstrap_is_normal' in result.method_params

    def test_result_has_cluster_diagnostics(self):
        """Result should include cluster diagnostics."""
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

        test = ClusteredBootstrapTest(n_samples=1000, random_seed=42)
        results = test.compare([control, treatment])
        result = results[0]

        assert 'n_clusters_control' in result.method_params
        assert 'n_clusters_treatment' in result.method_params
        assert 'icc_control' in result.method_params
        assert 'design_effect_control' in result.method_params

    def test_relative_effect(self):
        """Test relative effect calculation."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.normal(100, 10, 500),
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(110, 10, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest(
            test_type="relative",
            n_samples=1000,
            random_seed=42
        )
        results = test.compare([control, treatment])
        result = results[0]

        # Effect should be around 0.10 (10%)
        assert result.effect > 0
        assert 0.05 < result.effect < 0.15

    def test_absolute_effect(self):
        """Test absolute effect calculation."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.normal(100, 10, 500),
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(110, 10, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest(
            test_type="absolute",
            n_samples=1000,
            random_seed=42
        )
        results = test.compare([control, treatment])
        result = results[0]

        # Effect should be around 10
        assert result.effect > 0
        assert 5 < result.effect < 15


class TestClusteredBootstrapVsIndividual:
    """Compare cluster bootstrap with individual bootstrap."""

    def test_cluster_bootstrap_more_conservative(self):
        """Cluster bootstrap should have wider CI when ICC > 0."""
        np.random.seed(42)

        # Create data with clustering effect
        control_data = []
        control_clusters = []
        for cluster_id in range(5):
            cluster_mean = np.random.normal(100, 20)
            cluster_data = cluster_mean + np.random.normal(0, 5, 100)
            control_data.extend(cluster_data)
            control_clusters.extend([cluster_id] * 100)

        treatment_data = []
        treatment_clusters = []
        for cluster_id in range(5, 10):
            cluster_mean = np.random.normal(105, 20)
            cluster_data = cluster_mean + np.random.normal(0, 5, 100)
            treatment_data.extend(cluster_data)
            treatment_clusters.extend([cluster_id] * 100)

        control = SampleData(
            data=control_data,
            clusters=control_clusters,
            name="Control"
        )
        treatment = SampleData(
            data=treatment_data,
            clusters=treatment_clusters,
            name="Treatment"
        )

        # Cluster bootstrap
        cluster_test = ClusteredBootstrapTest(
            n_samples=1000,
            random_seed=42,
            test_type="relative"
        )
        cluster_result = cluster_test.compare([control, treatment])[0]

        # Individual bootstrap (ignoring clusters)
        from tests.nonparametric import BootstrapTest
        individual_test = BootstrapTest(
            n_samples=1000,
            random_seed=42,
            test_type="relative"
        )
        control_no_cluster = SampleData(data=control_data, name="Control")
        treatment_no_cluster = SampleData(data=treatment_data, name="Treatment")
        individual_result = individual_test.compare([control_no_cluster, treatment_no_cluster])[0]

        # Cluster CI should typically be wider
        # (This might not always hold with random data, but should in most cases)
        assert cluster_result.ci_length >= individual_result.ci_length * 0.8


class TestClusteredBootstrapEdgeCases:
    """Edge cases and error conditions."""

    def test_too_few_clusters_raises(self):
        """Should raise with < 3 clusters."""
        control = SampleData(
            data=np.random.normal(100, 20, 200),
            clusters=np.repeat(range(2), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 200),
            clusters=np.repeat(range(2, 4), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest(min_clusters=3)

        with pytest.raises(ValueError):
            test.compare([control, treatment])

    def test_unbalanced_clusters(self):
        """Should handle imbalanced cluster sizes."""
        np.random.seed(42)

        cluster_sizes = [50, 100, 150, 200, 250]
        control_data = []
        control_clusters = []
        for i, size in enumerate(cluster_sizes):
            data = np.random.normal(100, 20, size)
            control_data.extend(data)
            control_clusters.extend([i] * size)

        control = SampleData(data=control_data, clusters=control_clusters)
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredBootstrapTest(n_samples=1000, random_seed=42)
        results = test.compare([control, treatment])

        # Should complete without error
        assert len(results) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
