"""
Unit tests for ANCOVA test.
"""

import pytest
import numpy as np
from core.data_types import SampleData
from tests.parametric.ancova_test import AncovaTest


class TestAncovaTestInitialization:
    """Test AncovaTest initialization."""

    def test_default_initialization(self):
        """Test default parameters."""
        test = AncovaTest()

        assert test.alpha == 0.05
        assert test.test_type == "relative"
        assert test.check_interaction is False
        assert test.interaction_alpha == 0.10
        assert test.validate_assumptions is True
        assert test.use_robust_se is True

    def test_custom_parameters(self):
        """Test custom parameters."""
        test = AncovaTest(
            alpha=0.01,
            test_type="absolute",
            check_interaction=True,
            interaction_alpha=0.05,
            validate_assumptions=False,
            use_robust_se=False
        )

        assert test.alpha == 0.01
        assert test.test_type == "absolute"
        assert test.check_interaction is True
        assert test.interaction_alpha == 0.05
        assert test.validate_assumptions is False
        assert test.use_robust_se is False

    def test_invalid_test_type(self):
        """Test that invalid test_type raises error."""
        with pytest.raises(ValueError, match="Invalid test_type"):
            AncovaTest(test_type="invalid")

    def test_invalid_alpha(self):
        """Test that invalid alpha raises error."""
        with pytest.raises(ValueError):
            AncovaTest(alpha=-0.05)

        with pytest.raises(ValueError):
            AncovaTest(alpha=1.5)

    def test_invalid_interaction_alpha(self):
        """Test that invalid interaction_alpha raises error."""
        with pytest.raises(ValueError, match="interaction_alpha must be between"):
            AncovaTest(interaction_alpha=0)

        with pytest.raises(ValueError, match="interaction_alpha must be between"):
            AncovaTest(interaction_alpha=1.5)


class TestAncovaTestValidation:
    """Test input validation."""

    def test_requires_covariates(self):
        """Test that samples without covariates raise error."""
        control = SampleData(data=[100, 110, 95], name="Control")
        treatment = SampleData(data=[105, 115, 100], name="Treatment")

        test = AncovaTest()

        with pytest.raises(ValueError, match="missing covariates"):
            test.compare([control, treatment])

    def test_requires_positive_values_for_relative(self):
        """Test that non-positive values raise error for relative effect."""
        control = SampleData(
            data=[100, 110, 0, 105],  # Has zero
            covariates=[90, 100, 85, 95],
            name="Control"
        )
        treatment = SampleData(
            data=[105, 115, 100, 110],
            covariates=[92, 102, 87, 97],
            name="Treatment"
        )

        test = AncovaTest(test_type="relative")

        with pytest.raises(ValueError, match="all outcome values must be positive"):
            test.compare([control, treatment])

    def test_requires_sufficient_sample_size(self):
        """Test that insufficient sample size raises error."""
        # With 1 covariate, need at least 11 observations
        control = SampleData(
            data=[100, 110, 95],
            covariates=[90, 100, 85],
            name="Control"
        )
        treatment = SampleData(
            data=[105, 115, 100],
            covariates=[92, 102, 87],
            name="Treatment"
        )

        test = AncovaTest()

        with pytest.raises(ValueError, match="Insufficient sample size"):
            test.compare([control, treatment])

    def test_empty_sample_list(self):
        """Test with empty sample list."""
        test = AncovaTest()
        results = test.compare([])
        assert results == []


class TestAncovaTestSingleCovariate:
    """Test ANCOVA with single covariate."""

    def test_absolute_effect_single_covariate(self):
        """Test absolute effect with single covariate."""
        np.random.seed(42)

        # Generate data with known effect
        n = 50
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        # Outcome = 50 + 0.5 * covariate + 10 * treatment + noise
        control_data = 50 + 0.5 * control_cov + np.random.normal(0, 5, n)
        treatment_data = 50 + 0.5 * treatment_cov + 10 + np.random.normal(0, 5, n)

        control = SampleData(
            data=control_data,
            covariates=control_cov,
            name="Control"
        )
        treatment = SampleData(
            data=treatment_data,
            covariates=treatment_cov,
            name="Treatment"
        )

        test = AncovaTest(alpha=0.05, test_type="absolute", validate_assumptions=False)
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        # Check that effect is close to 10
        assert result.effect == pytest.approx(10, abs=3)

        # Check that it's significant
        assert result.reject == True
        assert result.pvalue < 0.05

        # Check confidence interval contains true effect
        assert result.left_bound < 10 < result.right_bound

    def test_relative_effect_single_covariate(self):
        """Test relative effect with single covariate."""
        np.random.seed(42)

        # Generate data with known relative effect (10%)
        n = 100
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        # log(Outcome) = 4 + 0.01 * covariate + 0.095 * treatment + noise
        # exp(0.095) - 1 ≈ 0.0996 ≈ 10%
        control_data = np.exp(4 + 0.01 * control_cov + np.random.normal(0, 0.1, n))
        treatment_data = np.exp(4 + 0.01 * treatment_cov + 0.095 + np.random.normal(0, 0.1, n))

        control = SampleData(
            data=control_data,
            covariates=control_cov,
            name="Control"
        )
        treatment = SampleData(
            data=treatment_data,
            covariates=treatment_cov,
            name="Treatment"
        )

        test = AncovaTest(alpha=0.05, test_type="relative", validate_assumptions=False)
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        # Check that effect is close to 10% (0.10)
        assert result.effect == pytest.approx(0.10, abs=0.05)

        # Check that it's in percentage form
        assert 0 < result.effect < 1  # Should be decimal form (0.1 = 10%)

        # Check CI is also in relative form
        assert result.left_bound < result.effect < result.right_bound


class TestAncovaTestMultipleCovariates:
    """Test ANCOVA with multiple covariates."""

    def test_absolute_effect_multiple_covariates(self):
        """Test absolute effect with multiple covariates."""
        np.random.seed(42)

        n = 100
        # 3 covariates
        control_cov = np.random.normal(100, 10, (n, 3))
        treatment_cov = np.random.normal(100, 10, (n, 3))

        # Outcome = 50 + 0.5*X1 + 0.3*X2 + 0.2*X3 + 15*treatment + noise
        control_data = (
            50 +
            0.5 * control_cov[:, 0] +
            0.3 * control_cov[:, 1] +
            0.2 * control_cov[:, 2] +
            np.random.normal(0, 5, n)
        )
        treatment_data = (
            50 +
            0.5 * treatment_cov[:, 0] +
            0.3 * treatment_cov[:, 1] +
            0.2 * treatment_cov[:, 2] +
            15 +  # Treatment effect
            np.random.normal(0, 5, n)
        )

        control = SampleData(
            data=control_data,
            covariates=control_cov,
            name="Control"
        )
        treatment = SampleData(
            data=treatment_data,
            covariates=treatment_cov,
            name="Treatment"
        )

        test = AncovaTest(alpha=0.05, test_type="absolute", validate_assumptions=False)
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        # Check that effect is close to 15
        assert result.effect == pytest.approx(15, abs=4)

        # Check metadata includes number of covariates
        assert result.method_params['n_covariates'] == 3

        # Check R-squared is reasonable (should be high with good covariates)
        assert result.method_params['r_squared'] > 0.5

    def test_multiple_covariates_improves_precision(self):
        """Test that multiple covariates reduce CI width."""
        np.random.seed(42)

        n = 100
        # Single covariate
        control_cov_1 = np.random.normal(100, 10, n)
        treatment_cov_1 = np.random.normal(100, 10, n)

        # Multiple covariates
        control_cov_3 = np.column_stack([
            control_cov_1,
            np.random.normal(50, 5, n),
            np.random.normal(10, 2, n)
        ])
        treatment_cov_3 = np.column_stack([
            treatment_cov_1,
            np.random.normal(50, 5, n),
            np.random.normal(10, 2, n)
        ])

        # Same outcome generation (all covariates matter)
        control_data = (
            50 +
            0.5 * control_cov_3[:, 0] +
            0.3 * control_cov_3[:, 1] +
            0.2 * control_cov_3[:, 2] +
            np.random.normal(0, 5, n)
        )
        treatment_data = (
            50 +
            0.5 * treatment_cov_3[:, 0] +
            0.3 * treatment_cov_3[:, 1] +
            0.2 * treatment_cov_3[:, 2] +
            10 +  # Treatment effect
            np.random.normal(0, 5, n)
        )

        # Test with 1 covariate
        control_1 = SampleData(data=control_data, covariates=control_cov_1, name="Control")
        treatment_1 = SampleData(data=treatment_data, covariates=treatment_cov_1, name="Treatment")

        test_1 = AncovaTest(test_type="absolute", validate_assumptions=False)
        result_1 = test_1.compare([control_1, treatment_1])[0]

        # Test with 3 covariates
        control_3 = SampleData(data=control_data, covariates=control_cov_3, name="Control")
        treatment_3 = SampleData(data=treatment_data, covariates=treatment_cov_3, name="Treatment")

        test_3 = AncovaTest(test_type="absolute", validate_assumptions=False)
        result_3 = test_3.compare([control_3, treatment_3])[0]

        # CI should be narrower with more relevant covariates
        assert result_3.ci_length < result_1.ci_length

        # R-squared should be higher with more covariates
        assert result_3.method_params['r_squared'] > result_1.method_params['r_squared']


class TestAncovaTestInteractions:
    """Test heterogeneous treatment effects (interactions)."""

    def test_no_interaction(self):
        """Test when there's no interaction (homogeneous effect)."""
        np.random.seed(42)

        n = 100
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        # No interaction: effect is constant 10 regardless of covariate
        control_data = 50 + 0.5 * control_cov + np.random.normal(0, 5, n)
        treatment_data = 50 + 0.5 * treatment_cov + 10 + np.random.normal(0, 5, n)

        control = SampleData(data=control_data, covariates=control_cov, name="Control")
        treatment = SampleData(data=treatment_data, covariates=treatment_cov, name="Treatment")

        test = AncovaTest(
            test_type="absolute",
            check_interaction=True,
            validate_assumptions=False
        )
        results = test.compare([control, treatment])

        result = results[0]

        # Should not detect heterogeneous effect
        assert result.method_params['has_heterogeneous_effect'] is False
        assert len(result.method_params['significant_interactions']) == 0

    def test_with_interaction(self):
        """Test when there's interaction (heterogeneous effect)."""
        np.random.seed(42)

        n = 200  # Larger sample for detecting interaction
        control_cov = np.random.normal(100, 20, n)
        treatment_cov = np.random.normal(100, 20, n)

        # With interaction: effect depends on covariate
        # Effect = 10 + 0.2 * (covariate - 100)
        # For cov=80: effect=6, for cov=120: effect=14
        control_data = 50 + 0.5 * control_cov + np.random.normal(0, 5, n)
        treatment_data = (
            50 + 0.5 * treatment_cov +
            10 + 0.2 * (treatment_cov - 100) +  # Interaction
            np.random.normal(0, 5, n)
        )

        control = SampleData(data=control_data, covariates=control_cov, name="Control")
        treatment = SampleData(data=treatment_data, covariates=treatment_cov, name="Treatment")

        test = AncovaTest(
            test_type="absolute",
            check_interaction=True,
            interaction_alpha=0.10,
            validate_assumptions=False
        )
        results = test.compare([control, treatment])

        result = results[0]

        # Should detect heterogeneous effect
        assert result.method_params['has_heterogeneous_effect'] is True
        assert 'covariate_0' in result.method_params['significant_interactions']


class TestAncovaTestValidationAssumptions:
    """Test validation of regression assumptions."""

    def test_validation_runs_without_error(self):
        """Test that validation doesn't crash on normal data."""
        np.random.seed(42)

        n = 100
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        control_data = 50 + 0.5 * control_cov + np.random.normal(0, 5, n)
        treatment_data = 50 + 0.5 * treatment_cov + 10 + np.random.normal(0, 5, n)

        control = SampleData(data=control_data, covariates=control_cov, name="Control")
        treatment = SampleData(data=treatment_data, covariates=treatment_cov, name="Treatment")

        test = AncovaTest(test_type="absolute", validate_assumptions=True)
        results = test.compare([control, treatment])

        result = results[0]

        # Check that validation info is present
        assert 'validation' in result.method_params
        validation = result.method_params['validation']

        # Should have test results
        assert 'linearity_test_pvalue' in validation or 'homoscedasticity_test_pvalue' in validation
        assert 'normality_test_pvalue' in validation
        assert 'max_vif' in validation

    def test_validation_disabled(self):
        """Test that validation can be disabled."""
        np.random.seed(42)

        n = 50
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        control_data = 50 + 0.5 * control_cov + np.random.normal(0, 5, n)
        treatment_data = 50 + 0.5 * treatment_cov + 10 + np.random.normal(0, 5, n)

        control = SampleData(data=control_data, covariates=control_cov, name="Control")
        treatment = SampleData(data=treatment_data, covariates=treatment_cov, name="Treatment")

        test = AncovaTest(test_type="absolute", validate_assumptions=False)
        results = test.compare([control, treatment])

        result = results[0]

        # Validation info should not be present
        assert 'validation' not in result.method_params


class TestAncovaTestComparisonWithOtherMethods:
    """Test that ANCOVA gives expected results compared to other methods."""

    def test_ancova_vs_ttest_without_covariates(self):
        """
        Test that ANCOVA with uncorrelated covariate gives similar results to t-test.
        """
        np.random.seed(42)

        n = 100
        # Uncorrelated covariate (doesn't affect outcome)
        control_cov = np.random.normal(100, 10, n)
        treatment_cov = np.random.normal(100, 10, n)

        # Outcome independent of covariate
        control_data = 100 + np.random.normal(0, 10, n)
        treatment_data = 110 + np.random.normal(0, 10, n)  # 10% effect

        control = SampleData(data=control_data, covariates=control_cov, name="Control")
        treatment = SampleData(data=treatment_data, covariates=treatment_cov, name="Treatment")

        # ANCOVA
        ancova = AncovaTest(test_type="absolute", validate_assumptions=False)
        ancova_result = ancova.compare([control, treatment])[0]

        # T-test (without covariates)
        from tests.parametric.ttest import TTest
        control_no_cov = SampleData(data=control_data, name="Control")
        treatment_no_cov = SampleData(data=treatment_data, name="Treatment")

        ttest = TTest(test_type="absolute")
        ttest_result = ttest.compare([control_no_cov, treatment_no_cov])[0]

        # Effects should be similar (covariate doesn't help)
        assert ancova_result.effect == pytest.approx(ttest_result.effect, abs=2)

        # P-values should be similar
        assert abs(ancova_result.pvalue - ttest_result.pvalue) < 0.1
