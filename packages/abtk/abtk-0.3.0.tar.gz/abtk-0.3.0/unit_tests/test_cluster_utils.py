"""
Unit tests for cluster utilities.

Tests for:
- calculate_icc()
- calculate_design_effect()
- validate_clusters()
"""

import pytest
import numpy as np
from core.data_types import SampleData
from utils.cluster_utils import (
    calculate_icc,
    calculate_design_effect,
    validate_clusters
)


class TestCalculateICC:
    """Tests for ICC calculation."""

    def test_icc_zero_no_clustering(self):
        """ICC should be near 0 when no clustering effect."""
        # All clusters have same distribution
        data = np.random.normal(100, 10, 1000)
        clusters = np.repeat(range(10), 100)

        icc = calculate_icc(data, clusters, method="anova")

        assert icc >= 0
        assert icc < 0.05  # Should be very low

    def test_icc_high_strong_clustering(self):
        """ICC should be high when strong clustering effect."""
        data = []
        clusters = []

        for cluster_id in range(10):
            # Each cluster has different mean
            cluster_mean = 100 + cluster_id * 20
            cluster_data = np.random.normal(cluster_mean, 5, 100)
            data.extend(cluster_data)
            clusters.extend([cluster_id] * 100)

        data = np.array(data)
        clusters = np.array(clusters)

        icc = calculate_icc(data, clusters, method="anova")

        assert icc > 0.2  # Should be high

    def test_icc_variance_method(self):
        """Test variance components method."""
        data = []
        clusters = []

        for cluster_id in range(5):
            cluster_mean = np.random.normal(100, 20)
            cluster_data = cluster_mean + np.random.normal(0, 10, 50)
            data.extend(cluster_data)
            clusters.extend([cluster_id] * 50)

        data = np.array(data)
        clusters = np.array(clusters)

        icc_anova = calculate_icc(data, clusters, method="anova")
        icc_variance = calculate_icc(data, clusters, method="variance")

        # Both methods should give similar results
        assert abs(icc_anova - icc_variance) < 0.1

    def test_icc_bounds(self):
        """ICC should be between 0 and 1."""
        np.random.seed(42)
        data = np.random.normal(100, 20, 500)
        clusters = np.repeat(range(10), 50)

        icc = calculate_icc(data, clusters)

        assert 0 <= icc <= 1

    def test_icc_single_cluster_raises(self):
        """Should raise error with single cluster."""
        data = np.array([1, 2, 3, 4, 5])
        clusters = np.array([1, 1, 1, 1, 1])

        with pytest.raises(ValueError, match="Need at least 2 clusters"):
            calculate_icc(data, clusters)

    def test_icc_invalid_method_raises(self):
        """Should raise error with invalid method."""
        data = np.array([1, 2, 3, 4, 5, 6])
        clusters = np.array([1, 1, 1, 2, 2, 2])

        with pytest.raises(ValueError, match="method must be"):
            calculate_icc(data, clusters, method="invalid")


class TestCalculateDesignEffect:
    """Tests for design effect calculation."""

    def test_design_effect_zero_icc(self):
        """DE should be 1.0 when ICC=0 (no clustering)."""
        cluster_sizes = [100] * 10
        icc = 0.0

        de = calculate_design_effect(cluster_sizes, icc)

        assert de == pytest.approx(1.0)

    def test_design_effect_formula(self):
        """DE = 1 + (m̄ - 1) × ICC."""
        cluster_sizes = [100, 100, 100]
        icc = 0.1

        de = calculate_design_effect(cluster_sizes, icc)

        # m̄ = 100, DE = 1 + (100-1)*0.1 = 10.9
        expected = 1 + (100 - 1) * 0.1
        assert de == pytest.approx(expected)

    def test_design_effect_increases_with_icc(self):
        """DE should increase as ICC increases."""
        cluster_sizes = [100] * 5

        de_low = calculate_design_effect(cluster_sizes, icc=0.01)
        de_med = calculate_design_effect(cluster_sizes, icc=0.10)
        de_high = calculate_design_effect(cluster_sizes, icc=0.20)

        assert de_low < de_med < de_high

    def test_design_effect_increases_with_cluster_size(self):
        """DE should increase as cluster size increases."""
        icc = 0.1

        de_small = calculate_design_effect([50] * 10, icc)
        de_medium = calculate_design_effect([100] * 10, icc)
        de_large = calculate_design_effect([200] * 10, icc)

        assert de_small < de_medium < de_large

    def test_design_effect_unbalanced_clusters(self):
        """DE with imbalanced cluster sizes."""
        cluster_sizes = [50, 100, 150, 200]
        icc = 0.1

        de = calculate_design_effect(cluster_sizes, icc)

        # m̄ = 125, DE = 1 + (125-1)*0.1 = 13.4
        mean_size = np.mean(cluster_sizes)
        expected = 1 + (mean_size - 1) * icc
        assert de == pytest.approx(expected)

    def test_design_effect_negative_icc_raises(self):
        """Should raise error with negative ICC."""
        cluster_sizes = [100] * 5

        with pytest.raises(ValueError, match="ICC must be between 0 and 1"):
            calculate_design_effect(cluster_sizes, icc=-0.1)

    def test_design_effect_icc_above_one_raises(self):
        """Should raise error with ICC > 1."""
        cluster_sizes = [100] * 5

        with pytest.raises(ValueError, match="ICC must be between 0 and 1"):
            calculate_design_effect(cluster_sizes, icc=1.5)


class TestValidateClusters:
    """Tests for cluster validation."""

    def test_validate_clusters_success(self):
        """Valid clusters should pass validation."""
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

        validation = validate_clusters(control, treatment, min_clusters=5)

        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        assert validation['n_clusters_1'] == 5
        assert validation['n_clusters_2'] == 5

    def test_validate_clusters_too_few_raises(self):
        """Should raise error with < 3 clusters."""
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

        with pytest.raises(ValueError, match="at least 3 clusters"):
            validate_clusters(control, treatment, min_clusters=3)

    def test_validate_clusters_warns_below_min(self):
        """Should warn if < min_clusters."""
        control = SampleData(
            data=np.random.normal(100, 20, 400),
            clusters=np.repeat(range(4), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 400),
            clusters=np.repeat(range(4, 8), 100),
            name="Treatment"
        )

        validation = validate_clusters(control, treatment, min_clusters=5)

        assert validation['valid'] is True  # Passes but warns
        assert any('fewer than' in w for w in validation['warnings'])

    def test_validate_clusters_high_cv_warns(self):
        """Should warn if cluster size CV is high."""
        # Imbalanced cluster sizes
        cluster_ids = [1]*50 + [2]*100 + [3]*150 + [4]*200 + [5]*250

        control = SampleData(
            data=np.random.normal(100, 20, len(cluster_ids)),
            clusters=cluster_ids,
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(6, 11), 100),
            name="Treatment"
        )

        validation = validate_clusters(control, treatment, warn_cv=0.5)

        assert any('imbalanced' in w.lower() for w in validation['warnings'])

    def test_validate_clusters_returns_diagnostics(self):
        """Should return ICC, design effect, etc."""
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

        validation = validate_clusters(control, treatment)

        assert 'icc_1' in validation
        assert 'icc_2' in validation
        assert 'design_effect_1' in validation
        assert 'design_effect_2' in validation
        assert 'cluster_size_cv_1' in validation
        assert 'cluster_size_cv_2' in validation

    def test_validate_clusters_missing_clusters_raises(self):
        """Should raise if clusters attribute is None."""
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

        with pytest.raises(ValueError, match="missing clusters"):
            validate_clusters(control, treatment)

    def test_validate_clusters_single_obs_cluster_warns(self):
        """Should warn if any cluster has only 1 observation."""
        clusters = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]  # Cluster 1 has only 1 obs

        control = SampleData(
            data=np.random.normal(100, 20, len(clusters)),
            clusters=clusters,
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 400),
            clusters=np.repeat(range(5, 9), 100),
            name="Treatment"
        )

        validation = validate_clusters(control, treatment)

        assert any('size 1' in w for w in validation['warnings'])


class TestICCEdgeCases:
    """Edge cases for ICC calculation."""

    def test_icc_all_same_values(self):
        """ICC with no variation."""
        data = np.ones(100)
        clusters = np.repeat(range(10), 10)

        # Should handle gracefully (ICC undefined but won't crash)
        icc = calculate_icc(data, clusters)

        # ICC could be 0 or undefined, just check no crash
        assert isinstance(icc, (int, float))

    def test_icc_perfect_clustering(self):
        """ICC = 1 when all variation is between clusters."""
        data = []
        clusters = []

        for cluster_id in range(10):
            # No within-cluster variation
            data.extend([cluster_id * 10] * 50)
            clusters.extend([cluster_id] * 50)

        data = np.array(data, dtype=float)
        clusters = np.array(clusters)

        icc = calculate_icc(data, clusters)

        # Should be very close to 1
        assert icc > 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
