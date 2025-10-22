"""
Unit tests for multiple comparisons corrections.
"""

import pytest
import numpy as np
from core.test_result import TestResult
from utils.corrections import (
    adjust_pvalues,
    _bonferroni_correction,
    _sidak_correction,
    _holm_correction,
    _benjamini_hochberg_correction,
    _benjamini_yekutieli_correction
)


def create_test_result(pvalue: float, alpha: float = 0.05) -> TestResult:
    """Helper to create a TestResult with specific p-value."""
    return TestResult(
        name_1="Control",
        value_1=100.0,
        std_1=10.0,
        size_1=100,
        name_2="Treatment",
        value_2=105.0,
        std_2=10.0,
        size_2=100,
        method_name="test",
        method_params={},
        alpha=alpha,
        pvalue=pvalue,
        effect=0.05,
        ci_length=0.02,
        left_bound=0.03,
        right_bound=0.07,
        reject=(pvalue < alpha)
    )


class TestBonferroniCorrection:
    """Test Bonferroni correction."""

    def test_bonferroni_basic(self):
        """Test basic Bonferroni correction: p_adj = min(p * n, 1)."""
        pvalues = np.array([0.01, 0.02, 0.03, 0.04])
        adjusted = _bonferroni_correction(pvalues)

        expected = np.array([0.04, 0.08, 0.12, 0.16])
        np.testing.assert_allclose(adjusted, expected)

    def test_bonferroni_cap_at_one(self):
        """Test that adjusted p-values are capped at 1.0."""
        pvalues = np.array([0.5, 0.6, 0.7])
        adjusted = _bonferroni_correction(pvalues)

        expected = np.array([1.0, 1.0, 1.0])
        np.testing.assert_allclose(adjusted, expected)

    def test_bonferroni_single_test(self):
        """Test that single test is not corrected."""
        pvalues = np.array([0.03])
        adjusted = _bonferroni_correction(pvalues)

        np.testing.assert_allclose(adjusted, pvalues)


class TestSidakCorrection:
    """Test Šidák correction."""

    def test_sidak_basic(self):
        """Test Šidák correction: p_adj = 1 - (1 - p)^n."""
        pvalues = np.array([0.01, 0.02, 0.03])
        adjusted = _sidak_correction(pvalues)

        # Expected: 1 - (1 - p)^3
        expected = 1.0 - np.power(1.0 - pvalues, 3)
        np.testing.assert_allclose(adjusted, expected)

    def test_sidak_less_conservative_than_bonferroni(self):
        """Test that Šidák is less conservative than Bonferroni."""
        pvalues = np.array([0.01, 0.02, 0.03, 0.04])

        sidak = _sidak_correction(pvalues)
        bonferroni = _bonferroni_correction(pvalues)

        # Šidák should give smaller (less conservative) adjusted p-values
        assert np.all(sidak <= bonferroni)


class TestHolmCorrection:
    """Test Holm-Bonferroni correction."""

    def test_holm_basic(self):
        """Test Holm step-down procedure."""
        pvalues = np.array([0.01, 0.04, 0.03, 0.05])
        adjusted = _holm_correction(pvalues)

        # Sorted p-values: [0.01, 0.03, 0.04, 0.05]
        # Adjustments: 0.01*4=0.04, 0.03*3=0.09, 0.04*2=0.08, 0.05*1=0.05
        # Enforcing monotonicity: [0.04, 0.09, 0.09, 0.09]
        # In original order:
        expected = np.array([0.04, 0.09, 0.09, 0.09])
        np.testing.assert_allclose(adjusted, expected)

    def test_holm_monotonicity(self):
        """Test that adjusted p-values are monotonic when sorted."""
        pvalues = np.array([0.001, 0.01, 0.03, 0.04, 0.05])
        adjusted = _holm_correction(pvalues)

        # Sort by original p-values
        sort_idx = np.argsort(pvalues)
        adjusted_sorted = adjusted[sort_idx]

        # Check monotonicity
        assert np.all(adjusted_sorted[1:] >= adjusted_sorted[:-1])

    def test_holm_more_powerful_than_bonferroni(self):
        """Test that Holm is more powerful (less conservative) than Bonferroni."""
        pvalues = np.array([0.001, 0.01, 0.03, 0.04, 0.05])

        holm = _holm_correction(pvalues)
        bonferroni = _bonferroni_correction(pvalues)

        # Holm should give smaller or equal adjusted p-values
        assert np.all(holm <= bonferroni)


class TestBenjaminiHochbergCorrection:
    """Test Benjamini-Hochberg FDR correction."""

    def test_benjamini_hochberg_basic(self):
        """Test Benjamini-Hochberg step-up procedure."""
        pvalues = np.array([0.01, 0.04, 0.03, 0.05])
        adjusted = _benjamini_hochberg_correction(pvalues)

        # All adjusted p-values should be >= original
        assert np.all(adjusted >= pvalues)

    def test_benjamini_hochberg_less_conservative_than_bonferroni(self):
        """Test that BH is less conservative than Bonferroni."""
        pvalues = np.array([0.001, 0.01, 0.02, 0.03, 0.04])

        bh = _benjamini_hochberg_correction(pvalues)
        bonferroni = _bonferroni_correction(pvalues)

        # BH should give smaller adjusted p-values
        assert np.all(bh <= bonferroni)

    def test_benjamini_hochberg_monotonicity(self):
        """Test monotonicity when sorted."""
        pvalues = np.array([0.001, 0.01, 0.03, 0.04, 0.05])
        adjusted = _benjamini_hochberg_correction(pvalues)

        # Sort by original p-values
        sort_idx = np.argsort(pvalues)
        adjusted_sorted = adjusted[sort_idx]

        # Check monotonicity
        assert np.all(adjusted_sorted[1:] >= adjusted_sorted[:-1])


class TestBenjaminiYekutieliCorrection:
    """Test Benjamini-Yekutieli FDR correction."""

    def test_benjamini_yekutieli_basic(self):
        """Test Benjamini-Yekutieli correction."""
        pvalues = np.array([0.01, 0.04, 0.03, 0.05])
        adjusted = _benjamini_yekutieli_correction(pvalues)

        # All adjusted p-values should be >= original
        assert np.all(adjusted >= pvalues)

    def test_benjamini_yekutieli_more_conservative_than_bh(self):
        """Test that BY is more conservative than BH."""
        pvalues = np.array([0.001, 0.01, 0.02, 0.03, 0.04])

        by = _benjamini_yekutieli_correction(pvalues)
        bh = _benjamini_hochberg_correction(pvalues)

        # BY should give larger (more conservative) adjusted p-values
        assert np.all(by >= bh)


class TestAdjustPvalues:
    """Test main adjust_pvalues function."""

    def test_adjust_pvalues_bonferroni(self):
        """Test adjust_pvalues with Bonferroni method."""
        results = [
            create_test_result(0.01),
            create_test_result(0.02),
            create_test_result(0.03)
        ]

        adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        # Check that we have 3 results
        assert len(adjusted) == 3

        # Check adjusted p-values (should be p * 3)
        assert adjusted[0].pvalue == pytest.approx(0.03)
        assert adjusted[1].pvalue == pytest.approx(0.06)
        assert adjusted[2].pvalue == pytest.approx(0.09)

        # Check original p-values preserved
        assert adjusted[0].pvalue_original == pytest.approx(0.01)
        assert adjusted[1].pvalue_original == pytest.approx(0.02)
        assert adjusted[2].pvalue_original == pytest.approx(0.03)

        # Check correction method stored
        assert adjusted[0].correction_method == "bonferroni"

    def test_adjust_pvalues_reject_decisions(self):
        """Test that reject decisions are updated after correction."""
        results = [
            create_test_result(0.01),  # Would reject without correction
            create_test_result(0.02),  # Would reject without correction
            create_test_result(0.03)   # Would reject without correction
        ]

        adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        # After Bonferroni correction with n=3:
        # p=0.01 -> 0.03 (reject)
        # p=0.02 -> 0.06 (not reject)
        # p=0.03 -> 0.09 (not reject)
        assert adjusted[0].reject is True
        assert adjusted[1].reject is False
        assert adjusted[2].reject is False

    def test_adjust_pvalues_holm(self):
        """Test adjust_pvalues with Holm method."""
        results = [
            create_test_result(0.01),
            create_test_result(0.04),
            create_test_result(0.03)
        ]

        adjusted = adjust_pvalues(results, method="holm", alpha=0.05)

        # Check that original p-values are preserved
        assert adjusted[0].pvalue_original == pytest.approx(0.01)
        assert adjusted[1].pvalue_original == pytest.approx(0.04)
        assert adjusted[2].pvalue_original == pytest.approx(0.03)

        # Check correction method
        assert adjusted[0].correction_method == "holm"

    def test_adjust_pvalues_benjamini_hochberg(self):
        """Test adjust_pvalues with Benjamini-Hochberg method."""
        results = [
            create_test_result(0.01),
            create_test_result(0.02),
            create_test_result(0.03),
            create_test_result(0.04)
        ]

        adjusted = adjust_pvalues(results, method="benjamini-hochberg", alpha=0.05)

        # BH should be less conservative than Bonferroni
        bonferroni = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        for i in range(len(results)):
            assert adjusted[i].pvalue <= bonferroni[i].pvalue

    def test_adjust_pvalues_single_test(self):
        """Test that single test returns unchanged result."""
        results = [create_test_result(0.03)]

        adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        # Single test should not be corrected
        assert len(adjusted) == 1
        assert adjusted[0].pvalue == pytest.approx(0.03)

    def test_adjust_pvalues_empty_list(self):
        """Test with empty list."""
        adjusted = adjust_pvalues([], method="bonferroni")
        assert adjusted == []

    def test_adjust_pvalues_invalid_method(self):
        """Test with invalid correction method."""
        results = [create_test_result(0.01), create_test_result(0.02)]

        with pytest.raises(ValueError, match="Unknown correction method"):
            adjust_pvalues(results, method="invalid_method")

    def test_adjust_pvalues_uses_alpha_from_results(self):
        """Test that alpha is taken from first result if not provided."""
        results = [
            create_test_result(0.01, alpha=0.1),
            create_test_result(0.02, alpha=0.1)
        ]

        adjusted = adjust_pvalues(results, method="bonferroni")

        # Should use alpha=0.1 from first result
        assert adjusted[0].alpha == 0.1

    def test_adjust_pvalues_override_alpha(self):
        """Test that provided alpha overrides alpha from results."""
        results = [
            create_test_result(0.01, alpha=0.1),
            create_test_result(0.02, alpha=0.1)
        ]

        adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        # Should use provided alpha=0.05
        assert adjusted[0].alpha == 0.05


class TestCorrectionScenarios:
    """Test real-world scenarios."""

    def test_three_treatments_bonferroni(self):
        """Test multiple treatments scenario with Bonferroni."""
        # Control vs Treatment1, Treatment2, Treatment3
        results = [
            create_test_result(0.01),  # Significant
            create_test_result(0.02),  # Borderline
            create_test_result(0.04)   # Borderline
        ]

        adjusted = adjust_pvalues(results, method="bonferroni", alpha=0.05)

        # With n=3, α_corrected = 0.05/3 ≈ 0.0167
        # p=0.01 * 3 = 0.03 < 0.05 → reject
        # p=0.02 * 3 = 0.06 > 0.05 → not reject
        # p=0.04 * 3 = 0.12 > 0.05 → not reject
        assert adjusted[0].reject is True
        assert adjusted[1].reject is False
        assert adjusted[2].reject is False

    def test_three_treatments_benjamini_hochberg(self):
        """Test multiple treatments with Benjamini-Hochberg (less conservative)."""
        results = [
            create_test_result(0.01),
            create_test_result(0.02),
            create_test_result(0.04)
        ]

        adjusted = adjust_pvalues(results, method="benjamini-hochberg", alpha=0.05)

        # BH is less conservative, may reject more
        # At least the first one should be rejected
        assert adjusted[0].reject is True

    def test_comparison_all_methods(self):
        """Compare all methods on same data."""
        pvalues_raw = [0.001, 0.01, 0.02, 0.03, 0.04, 0.05]
        results = [create_test_result(p) for p in pvalues_raw]

        bonf = adjust_pvalues(results, method="bonferroni", alpha=0.05)
        sidak = adjust_pvalues(results, method="sidak", alpha=0.05)
        holm = adjust_pvalues(results, method="holm", alpha=0.05)
        bh = adjust_pvalues(results, method="benjamini-hochberg", alpha=0.05)
        by = adjust_pvalues(results, method="benjamini-yekutieli", alpha=0.05)

        # Expected order of conservativeness (most to least):
        # Bonferroni > Šidák > Benjamini-Yekutieli > Holm ≈ Benjamini-Hochberg

        # Check that Bonferroni is most conservative (largest adjusted p-values)
        for i in range(len(results)):
            assert bonf[i].pvalue >= sidak[i].pvalue
            assert bonf[i].pvalue >= holm[i].pvalue
            assert bonf[i].pvalue >= bh[i].pvalue

        # Check that BY is more conservative than BH
        for i in range(len(results)):
            assert by[i].pvalue >= bh[i].pvalue
