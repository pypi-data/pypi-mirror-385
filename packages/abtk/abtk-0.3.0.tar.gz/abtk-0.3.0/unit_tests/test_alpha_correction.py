"""
Unit tests for alpha correction functions in sample_size_calculator.

Tests for:
- calculate_number_of_comparisons()
- adjust_alpha_for_multiple_comparisons()
"""

import pytest
import numpy as np
from utils.sample_size_calculator import (
    calculate_number_of_comparisons,
    adjust_alpha_for_multiple_comparisons
)


class TestCalculateNumberOfComparisons:
    """Test calculate_number_of_comparisons function."""

    def test_vs_control_two_groups(self):
        """Test vs_control with 2 groups (A/B)."""
        n = calculate_number_of_comparisons(num_groups=2, comparison_type="vs_control")
        assert n == 1  # Only A vs B

    def test_vs_control_three_groups(self):
        """Test vs_control with 3 groups (A/B/C)."""
        n = calculate_number_of_comparisons(num_groups=3, comparison_type="vs_control")
        assert n == 2  # B vs A, C vs A

    def test_vs_control_four_groups(self):
        """Test vs_control with 4 groups (A/B/C/D)."""
        n = calculate_number_of_comparisons(num_groups=4, comparison_type="vs_control")
        assert n == 3  # B vs A, C vs A, D vs A

    def test_pairwise_two_groups(self):
        """Test pairwise with 2 groups."""
        n = calculate_number_of_comparisons(num_groups=2, comparison_type="pairwise")
        assert n == 1  # C(2,2) = 1

    def test_pairwise_three_groups(self):
        """Test pairwise with 3 groups."""
        n = calculate_number_of_comparisons(num_groups=3, comparison_type="pairwise")
        assert n == 3  # C(3,2) = 3

    def test_pairwise_four_groups(self):
        """Test pairwise with 4 groups."""
        n = calculate_number_of_comparisons(num_groups=4, comparison_type="pairwise")
        assert n == 6  # C(4,2) = 6

    def test_pairwise_five_groups(self):
        """Test pairwise with 5 groups."""
        n = calculate_number_of_comparisons(num_groups=5, comparison_type="pairwise")
        assert n == 10  # C(5,2) = 10

    def test_invalid_num_groups(self):
        """Test that num_groups < 2 raises error."""
        with pytest.raises(ValueError, match="Must have at least 2 groups"):
            calculate_number_of_comparisons(num_groups=1)

        with pytest.raises(ValueError, match="Must have at least 2 groups"):
            calculate_number_of_comparisons(num_groups=0)

    def test_invalid_comparison_type(self):
        """Test that invalid comparison_type raises error."""
        with pytest.raises(ValueError, match="Invalid comparison_type"):
            calculate_number_of_comparisons(num_groups=3, comparison_type="invalid")


class TestAdjustAlphaForMultipleComparisons:
    """Test adjust_alpha_for_multiple_comparisons function."""

    # =============================================================================
    # Bonferroni correction tests
    # =============================================================================

    def test_bonferroni_two_comparisons(self):
        """Test Bonferroni with 2 comparisons."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=2,
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.025, abs=1e-6)  # 0.05 / 2

    def test_bonferroni_three_comparisons(self):
        """Test Bonferroni with 3 comparisons."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=3,
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.0167, abs=1e-4)  # 0.05 / 3

    def test_bonferroni_with_num_groups(self):
        """Test Bonferroni using num_groups parameter."""
        # A/B/C test: 3 groups, vs_control → 2 comparisons
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=3,
            comparison_type="vs_control",
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.025, abs=1e-6)  # 0.05 / 2

    def test_bonferroni_pairwise(self):
        """Test Bonferroni with pairwise comparisons."""
        # A/B/C test: 3 groups, pairwise → 3 comparisons
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=3,
            comparison_type="pairwise",
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.0167, abs=1e-4)  # 0.05 / 3

    # =============================================================================
    # Sidak correction tests
    # =============================================================================

    def test_sidak_two_comparisons(self):
        """Test Sidak with 2 comparisons."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=2,
            method="sidak"
        )
        # Formula: 1 - (1 - 0.05)^(1/2) = 1 - 0.95^0.5 = 0.0253
        expected = 1 - (1 - 0.05) ** (1/2)
        assert alpha_adj == pytest.approx(expected, abs=1e-6)

    def test_sidak_three_comparisons(self):
        """Test Sidak with 3 comparisons."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=3,
            method="sidak"
        )
        # Formula: 1 - (1 - 0.05)^(1/3)
        expected = 1 - (1 - 0.05) ** (1/3)
        assert alpha_adj == pytest.approx(expected, abs=1e-6)

    def test_sidak_with_num_groups(self):
        """Test Sidak using num_groups parameter."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=3,
            comparison_type="vs_control",
            method="sidak"
        )
        # 3 groups, vs_control → 2 comparisons
        expected = 1 - (1 - 0.05) ** (1/2)
        assert alpha_adj == pytest.approx(expected, abs=1e-6)

    # =============================================================================
    # Comparison between methods
    # =============================================================================

    def test_sidak_less_conservative_than_bonferroni(self):
        """Test that Sidak gives slightly larger alpha than Bonferroni."""
        alpha_bonf = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=3,
            method="bonferroni"
        )
        alpha_sidak = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=3,
            method="sidak"
        )
        # Sidak should be slightly less conservative (larger alpha)
        assert alpha_sidak > alpha_bonf

    def test_methods_converge_for_small_alpha(self):
        """Test that Bonferroni and Sidak are similar for small alpha."""
        alpha = 0.01
        num_comp = 5

        alpha_bonf = adjust_alpha_for_multiple_comparisons(
            alpha=alpha,
            num_comparisons=num_comp,
            method="bonferroni"
        )
        alpha_sidak = adjust_alpha_for_multiple_comparisons(
            alpha=alpha,
            num_comparisons=num_comp,
            method="sidak"
        )

        # Difference should be very small
        difference = abs(alpha_sidak - alpha_bonf)
        assert difference < 0.0001

    # =============================================================================
    # Edge cases
    # =============================================================================

    def test_single_comparison(self):
        """Test that single comparison returns original alpha."""
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_comparisons=1,
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.05, abs=1e-6)

    def test_different_alphas(self):
        """Test with different alpha values."""
        # Alpha = 0.01
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.01,
            num_comparisons=2,
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.005, abs=1e-6)

        # Alpha = 0.10
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.10,
            num_comparisons=2,
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.05, abs=1e-6)

    # =============================================================================
    # Validation tests
    # =============================================================================

    def test_invalid_alpha_zero(self):
        """Test that alpha=0 raises error."""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            adjust_alpha_for_multiple_comparisons(alpha=0, num_comparisons=2)

    def test_invalid_alpha_one(self):
        """Test that alpha=1 raises error."""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            adjust_alpha_for_multiple_comparisons(alpha=1, num_comparisons=2)

    def test_invalid_alpha_negative(self):
        """Test that negative alpha raises error."""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            adjust_alpha_for_multiple_comparisons(alpha=-0.05, num_comparisons=2)

    def test_invalid_alpha_greater_than_one(self):
        """Test that alpha > 1 raises error."""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            adjust_alpha_for_multiple_comparisons(alpha=1.5, num_comparisons=2)

    def test_no_parameters_provided(self):
        """Test that error is raised if neither num_groups nor num_comparisons provided."""
        with pytest.raises(ValueError, match="Must provide either 'num_groups' or 'num_comparisons'"):
            adjust_alpha_for_multiple_comparisons(alpha=0.05)

    def test_both_parameters_provided(self):
        """Test that error is raised if both num_groups and num_comparisons provided."""
        with pytest.raises(ValueError, match="Provide either 'num_groups' OR 'num_comparisons'"):
            adjust_alpha_for_multiple_comparisons(
                alpha=0.05,
                num_groups=3,
                num_comparisons=2
            )

    def test_invalid_method(self):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid method"):
            adjust_alpha_for_multiple_comparisons(
                alpha=0.05,
                num_comparisons=2,
                method="invalid"
            )

    # =============================================================================
    # Integration tests
    # =============================================================================

    def test_abcd_test_vs_control(self):
        """Test A/B/C/D test with vs_control comparisons."""
        # 4 groups → 3 comparisons (B vs A, C vs A, D vs A)
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=4,
            comparison_type="vs_control",
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.05 / 3, abs=1e-6)

    def test_abcd_test_pairwise(self):
        """Test A/B/C/D test with pairwise comparisons."""
        # 4 groups → 6 comparisons (all pairs)
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=4,
            comparison_type="pairwise",
            method="bonferroni"
        )
        assert alpha_adj == pytest.approx(0.05 / 6, abs=1e-6)

    def test_realistic_scenario(self):
        """Test realistic scenario: A/B/C test with Bonferroni."""
        # Scenario: 1 control + 2 treatments, alpha=0.05
        alpha_adj = adjust_alpha_for_multiple_comparisons(
            alpha=0.05,
            num_groups=3,
            comparison_type="vs_control",
            method="bonferroni"
        )

        # Should be 0.025 (0.05 / 2)
        assert alpha_adj == pytest.approx(0.025, abs=1e-6)

        # Verify we can use this in sample size calculation
        # (just check it doesn't raise error)
        from utils.sample_size_calculator import calculate_sample_size_ttest
        n = calculate_sample_size_ttest(
            baseline_mean=100,
            std=20,
            mde=0.05,
            alpha=alpha_adj
        )
        assert n > 0  # Should give valid sample size
