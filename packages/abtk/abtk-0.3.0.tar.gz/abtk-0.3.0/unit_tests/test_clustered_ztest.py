"""
Unit tests for ClusteredZTest.

Tests for cluster-randomized z-test for proportions.
"""

import pytest
import numpy as np
from core.data_types import SampleData
from tests.parametric import ClusteredZTest


class TestClusteredZTestBasic:
    """Basic functionality tests."""

    def test_initialization(self):
        """Test basic initialization."""
        test = ClusteredZTest(alpha=0.05, test_type="relative")

        assert test.alpha == 0.05
        assert test.test_type == "relative"

    def test_requires_statsmodels(self):
        """Test imports statsmodels."""
        # Should not raise (statsmodels required)
        test = ClusteredZTest()
        assert test is not None


class TestClusteredZTestBinaryData:
    """Tests for binary data validation."""

    def test_binary_data_validation_success(self):
        """Should accept binary (0/1) data."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.binomial(1, 0.05, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.06, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest()
        results = test.compare([control, treatment])

        assert len(results) == 1

    def test_non_binary_data_raises(self):
        """Should raise error with non-binary data."""
        control = SampleData(
            data=np.random.normal(100, 20, 500),  # Not binary!
            clusters=np.repeat(range(5), 100),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(105, 20, 500),
            clusters=np.repeat(range(5, 10), 100),
            name="Treatment"
        )

        test = ClusteredZTest()

        with pytest.raises(ValueError, match="must be binary"):
            test.compare([control, treatment])

    def test_non_zero_one_values_raises(self):
        """Should raise if data not 0 or 1."""
        control = SampleData(
            data=np.array([0, 1, 2, 3, 4, 5]),  # Has values other than 0/1
            clusters=np.array([1, 1, 2, 2, 3, 3]),
            name="Control"
        )
        treatment = SampleData(
            data=np.array([0, 1, 0, 1, 0, 1]),
            clusters=np.array([4, 4, 5, 5, 6, 6]),
            name="Treatment"
        )

        test = ClusteredZTest()

        with pytest.raises(ValueError, match="must be binary"):
            test.compare([control, treatment])


class TestClusteredZTestResults:
    """Tests for test results."""

    def test_proportion_calculation(self):
        """Should calculate proportions correctly."""
        np.random.seed(42)

        # Control: 5% CTR
        control_data = np.random.binomial(1, 0.05, 1000)
        # Treatment: 6% CTR
        treatment_data = np.random.binomial(1, 0.06, 1000)

        control = SampleData(
            data=control_data,
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=treatment_data,
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(alpha=0.05, test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Check proportions
        p_control = result.method_params['proportion_control']
        p_treatment = result.method_params['proportion_treatment']

        assert 0 <= p_control <= 1
        assert 0 <= p_treatment <= 1
        assert abs(p_control - np.mean(control_data)) < 0.001
        assert abs(p_treatment - np.mean(treatment_data)) < 0.001

    def test_relative_effect_for_proportions(self):
        """Test relative effect: (p_treatment - p_control) / p_control."""
        np.random.seed(42)

        # Control: 10% conversion
        control = SampleData(
            data=np.random.binomial(1, 0.10, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        # Treatment: 12% conversion (+20% relative)
        treatment = SampleData(
            data=np.random.binomial(1, 0.12, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(test_type="relative")
        results = test.compare([control, treatment])
        result = results[0]

        # Relative effect should be around 0.20 (20%)
        assert result.effect > 0
        assert 0.05 < result.effect < 0.35  # Wide range due to randomness

    def test_absolute_effect_for_proportions(self):
        """Test absolute effect: p_treatment - p_control."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.binomial(1, 0.10, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.12, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(test_type="absolute")
        results = test.compare([control, treatment])
        result = results[0]

        # Absolute effect should be around 0.02 (2 percentage points)
        assert -0.05 < result.effect < 0.10

    def test_result_has_proportion_params(self):
        """Result should include proportion-specific params."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.binomial(1, 0.05, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.06, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest()
        results = test.compare([control, treatment])
        result = results[0]

        assert 'proportion_control' in result.method_params
        assert 'proportion_treatment' in result.method_params
        assert 'absolute_difference' in result.method_params

    def test_result_has_cluster_diagnostics(self):
        """Result should include cluster diagnostics."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.binomial(1, 0.05, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.06, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest()
        results = test.compare([control, treatment])
        result = results[0]

        assert 'n_clusters_control' in result.method_params
        assert 'n_clusters_treatment' in result.method_params
        assert 'icc_control' in result.method_params
        assert 'design_effect_control' in result.method_params


class TestClusteredZTestWarnings:
    """Tests for warning conditions."""

    def test_warns_extreme_low_proportion(self):
        """Should warn for proportions < 0.05."""
        np.random.seed(42)

        # Very low proportion (< 0.05)
        control = SampleData(
            data=np.random.binomial(1, 0.01, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.02, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(warn_extreme_proportions=True)

        # Should warn but not crash
        with pytest.warns(UserWarning, match="Extreme proportions"):
            results = test.compare([control, treatment])

        assert len(results) == 1

    def test_warns_extreme_high_proportion(self):
        """Should warn for proportions > 0.95."""
        np.random.seed(42)

        # Very high proportion (> 0.95)
        control = SampleData(
            data=np.random.binomial(1, 0.96, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.98, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(warn_extreme_proportions=True)

        with pytest.warns(UserWarning, match="Extreme proportions"):
            results = test.compare([control, treatment])

        assert len(results) == 1

    def test_no_warning_for_moderate_proportions(self):
        """Should not warn for proportions between 0.05 and 0.95."""
        np.random.seed(42)

        control = SampleData(
            data=np.random.binomial(1, 0.10, 1000),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.12, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(warn_extreme_proportions=True)

        # Should not warn
        results = test.compare([control, treatment])
        assert len(results) == 1


class TestClusteredZTestEdgeCases:
    """Edge cases and error conditions."""

    def test_zero_control_proportion_relative_raises(self):
        """Should raise when control proportion is zero for relative effect."""
        control = SampleData(
            data=np.zeros(1000, dtype=int),  # All zeros
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.05, 1000),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(test_type="relative")

        with pytest.raises(ValueError, match="control proportion is zero"):
            test.compare([control, treatment])

    def test_all_ones_data(self):
        """Should handle all-1s data."""
        control = SampleData(
            data=np.ones(1000, dtype=int),
            clusters=np.repeat(range(5), 200),
            name="Control"
        )
        treatment = SampleData(
            data=np.ones(1000, dtype=int),
            clusters=np.repeat(range(5, 10), 200),
            name="Treatment"
        )

        test = ClusteredZTest(test_type="absolute")

        # Should complete without error
        results = test.compare([control, treatment])
        result = results[0]

        # Effect should be near zero
        assert abs(result.effect) < 0.01

    def test_missing_clusters_raises(self):
        """Should raise if clusters attribute is None."""
        control = SampleData(
            data=np.random.binomial(1, 0.05, 1000),
            name="Control"
            # No clusters!
        )
        treatment = SampleData(
            data=np.random.binomial(1, 0.06, 1000),
            clusters=np.repeat(range(5), 200),
            name="Treatment"
        )

        test = ClusteredZTest()

        with pytest.raises(ValueError, match="missing clusters"):
            test.compare([control, treatment])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
