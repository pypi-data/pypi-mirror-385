"""
Unit tests for ClusteredTTest.

Tests for cluster-randomized t-test with cluster-robust standard errors.
"""

import pytest
import numpy as np
from core.data_types import SampleData
from tests.parametric import ClusteredTTest


class TestClusteredTTestBasic:
    """Basic functionality tests."""

    def test_initialization(self):
        """Test basic initialization."""
        test = ClusteredTTest(alpha=0.05, test_type="relative", min_clusters=5)

        assert test.alpha == 0.05
        assert test.test_type == "relative"
        assert test.min_clusters == 5

    def test_invalid_test_type_raises(self):
        """Should raise error with invalid test_type."""
        with pytest.raises(ValueError, match='test_type must be'):
            ClusteredTTest(test_type="invalid")

    def test_invalid_alpha_raises(self):
        """Should raise error with invalid alpha."""
        with pytest.raises(ValueError):
            ClusteredTTest(alpha=1.5)

    def test_repr(self):
        """Test string representation."""
        test = ClusteredTTest(alpha=0.05, test_type="relative", min_clusters=5)

        repr_str = repr(test)

        assert "ClusteredTTest" in repr_str
        assert "alpha=0.05" in repr_str
        assert "test_type='relative'" in repr_str


class TestClusteredTTestCompare:
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

        test = ClusteredTTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        assert result.name_1 == "Control"
        assert result.name_2 == "Treatment"
        assert hasattr(result, 'effect')
        assert hasattr(result, 'pvalue')
        assert hasattr(result, 'left_bound')
        assert hasattr(result, 'right_bound')

    def test_compare_multiple_samples(self):
        """Test pairwise comparisons with 3 samples."""
        np.random.seed(42)

        samples = []
        for i in range(3):
            sample = SampleData(
                data=np.random.normal(100 + i*5, 20, 500),
                clusters=np.repeat(range(i*5, i*5+5), 100),
                name=f"Group{i}"
            )
            samples.append(sample)

        test = ClusteredTTest(alpha=0.05)
        results = test.compare(samples)

        # 3 samples → 3 pairwise comparisons
        assert len(results) == 3

    def test_compare_no_clusters_raises(self):
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

        test = ClusteredTTest()

        with pytest.raises(ValueError, match="does not have clusters"):
            test.compare([control, treatment])

    def test_compare_too_few_clusters_raises(self):
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

        test = ClusteredTTest(min_clusters=3)

        with pytest.raises(ValueError, match="at least 3 clusters"):
            test.compare([control, treatment])

    def test_compare_empty_samples_returns_empty(self):
        """Empty samples list should return empty results."""
        test = ClusteredTTest()
        results = test.compare([])

        assert results == []


class TestClusteredTTestResults:
    """Tests for test results and diagnostics."""

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

        test = ClusteredTTest(alpha=0.05)
        results = test.compare([control, treatment])
        result = results[0]

        # Check cluster diagnostics
        assert 'n_clusters_control' in result.method_params
        assert 'n_clusters_treatment' in result.method_params
        assert 'icc_control' in result.method_params
        assert 'icc_treatment' in result.method_params
        assert 'design_effect_control' in result.method_params
        assert 'design_effect_treatment' in result.method_params
        assert 'cluster_size_cv_control' in result.method_params

        assert result.method_params['n_clusters_control'] == 5
        assert result.method_params['n_clusters_treatment'] == 5

    def test_relative_effect_calculation(self):
        """Test relative effect calculation."""
        np.random.seed(42)

        # Control: mean ≈ 100
        # Treatment: mean ≈ 110 (+10%)
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

        test = ClusteredTTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Effect should be close to 0.10 (10%)
        assert result.effect > 0
        assert 0.05 < result.effect < 0.15

    def test_absolute_effect_calculation(self):
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

        test = ClusteredTTest(alpha=0.05, test_type="absolute")
        results = test.compare([control, treatment])
        result = results[0]

        # Effect should be close to 10
        assert result.effect > 0
        assert 5 < result.effect < 15

    def test_confidence_interval_contains_effect(self):
        """CI should contain the true effect."""
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

        test = ClusteredTTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # CI should contain effect
        assert result.left_bound <= result.effect <= result.right_bound


class TestClusteredTTestVsRegularTTest:
    """Compare cluster test with regular t-test."""

    def test_cluster_ci_wider_than_regular(self):
        """Cluster test CI should be wider when ICC > 0."""
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

        # Cluster test
        cluster_test = ClusteredTTest(alpha=0.05, test_type="relative")
        cluster_result = cluster_test.compare([control, treatment])[0]

        # Regular test (ignoring clusters)
        from tests.parametric import TTest
        regular_test = TTest(alpha=0.05, test_type="relative")
        control_no_cluster = SampleData(data=control_data, name="Control")
        treatment_no_cluster = SampleData(data=treatment_data, name="Treatment")
        regular_result = regular_test.compare([control_no_cluster, treatment_no_cluster])[0]

        # Cluster CI should be wider (accounts for clustering)
        assert cluster_result.ci_length > regular_result.ci_length


class TestClusteredTTestEdgeCases:
    """Edge cases and error conditions."""

    def test_zero_control_mean_relative_raises(self):
        """Should raise when control mean is zero for relative effect."""
        control = SampleData(
            data=np.zeros(500),
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(10, 5, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredTTest(test_type="relative")

        with pytest.raises(ValueError, match="control mean is zero"):
            test.compare([control, treatment])

    def test_unbalanced_cluster_sizes(self):
        """Should handle imbalanced cluster sizes."""
        np.random.seed(42)

        # Imbalanced clusters
        cluster_sizes = [50, 100, 150, 200, 250]
        control_data = []
        control_clusters = []
        for i, size in enumerate(cluster_sizes):
            data = np.random.normal(100, 20, size)
            control_data.extend(data)
            control_clusters.extend([i] * size)

        control = SampleData(
            data=control_data,
            clusters=control_clusters,
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredTTest(warn_cv=0.5)
        results = test.compare([control, treatment])

        # Should complete without error
        assert len(results) == 1

    def test_high_icc_detected(self):
        """Should detect high ICC in diagnostics."""
        np.random.seed(42)

        # Create data with high ICC
        control_data = []
        control_clusters = []
        for cluster_id in range(5):
            cluster_mean = 100 + cluster_id * 50  # Large between-cluster variation
            cluster_data = cluster_mean + np.random.normal(0, 2, 100)  # Small within
            control_data.extend(cluster_data)
            control_clusters.extend([cluster_id] * 100)

        treatment_data = []
        treatment_clusters = []
        for cluster_id in range(5, 10):
            cluster_mean = 105 + cluster_id * 50
            cluster_data = cluster_mean + np.random.normal(0, 2, 100)
            treatment_data.extend(cluster_data)
            treatment_clusters.extend([cluster_id] * 100)

        control = SampleData(data=control_data, clusters=control_clusters)
        treatment = SampleData(data=treatment_data, clusters=treatment_clusters)

        test = ClusteredTTest()
        results = test.compare([control, treatment])
        result = results[0]

        # Should have high ICC
        assert result.method_params['icc_control'] > 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
