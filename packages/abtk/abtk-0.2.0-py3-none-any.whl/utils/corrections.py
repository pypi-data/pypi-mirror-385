"""
Multiple comparisons corrections for p-values.

This module provides corrections for the multiple testing problem that arises
when performing multiple hypothesis tests simultaneously. Without correction,
the family-wise error rate increases with the number of comparisons.

Supported methods:
- Bonferroni: Conservative, controls FWER
- Šidák: Less conservative than Bonferroni, controls FWER
- Holm-Bonferroni: Step-down procedure, more powerful than Bonferroni
- Benjamini-Hochberg: Controls FDR, less conservative
- Benjamini-Yekutieli: Controls FDR with dependent tests
"""

from typing import List, Literal
import numpy as np
from core.test_result import TestResult


def adjust_pvalues(
    results: List[TestResult],
    method: Literal["bonferroni", "sidak", "holm", "benjamini-hochberg", "benjamini-yekutieli"] = "bonferroni",
    alpha: float = None
) -> List[TestResult]:
    """
    Adjust p-values for multiple comparisons.

    This function takes a list of test results and returns new TestResult objects
    with adjusted p-values and corrected reject decisions. Original p-values are
    preserved in pvalue_original field.

    Parameters
    ----------
    results : List[TestResult]
        List of test results to adjust
    method : str, default="bonferroni"
        Correction method:
        - "bonferroni": α_corrected = α / n_tests (most conservative)
        - "sidak": α_corrected = 1 - (1 - α)^(1/n_tests) (less conservative)
        - "holm": Step-down Bonferroni (sequential rejection)
        - "benjamini-hochberg": FDR control (assumes independence)
        - "benjamini-yekutieli": FDR control (allows dependence)
    alpha : float, optional
        Significance level. If None, uses alpha from first result.

    Returns
    -------
    List[TestResult]
        New list of TestResult objects with adjusted p-values.
        Each result has:
        - pvalue: adjusted p-value
        - pvalue_original: original uncorrected p-value
        - reject: decision based on adjusted p-value
        - correction_method: name of correction method used

    Examples
    --------
    >>> from tests.parametric import TTest
    >>> from utils.corrections import adjust_pvalues
    >>>
    >>> # Multiple comparisons
    >>> test = TTest(alpha=0.05)
    >>> results = test.compare([control, treatment1, treatment2, treatment3])
    >>>
    >>> # Apply Bonferroni correction
    >>> adjusted = adjust_pvalues(results, method="bonferroni")
    >>> for r in adjusted:
    ...     print(f"Original p={r.pvalue_original:.4f}, Adjusted p={r.pvalue:.4f}")
    >>>
    >>> # Apply Benjamini-Hochberg (FDR control)
    >>> adjusted = adjust_pvalues(results, method="benjamini-hochberg")

    Notes
    -----
    Family-Wise Error Rate (FWER) methods:
    - Bonferroni: Most conservative, p_adj = min(p * n, 1)
    - Šidák: Less conservative, assumes independence
    - Holm: Sequential procedure, more powerful than Bonferroni

    False Discovery Rate (FDR) methods:
    - Benjamini-Hochberg: Controls FDR when tests are independent
    - Benjamini-Yekutieli: Controls FDR with arbitrary dependence

    Choosing a method:
    - Use FWER methods (Bonferroni, Holm) when you want strong control
    - Use FDR methods (Benjamini-Hochberg) for exploratory analysis
    - Holm is generally preferred over Bonferroni (more powerful)
    - Use Benjamini-Yekutieli if tests are correlated

    References
    ----------
    - Bonferroni, C. E. (1936). Teoria statistica delle classi e calcolo delle probabilità
    - Holm, S. (1979). A simple sequentially rejective multiple test procedure
    - Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate
    - Benjamini, Y., & Yekutieli, D. (2001). The control of the false discovery rate
    """
    if not results:
        return []

    if len(results) == 1:
        # No correction needed for single comparison
        return results

    # Get alpha from first result if not provided
    if alpha is None:
        alpha = results[0].alpha

    n = len(results)
    pvalues = np.array([r.pvalue for r in results])

    # Calculate adjusted p-values based on method
    if method == "bonferroni":
        pvalues_adjusted = _bonferroni_correction(pvalues)
    elif method == "sidak":
        pvalues_adjusted = _sidak_correction(pvalues)
    elif method == "holm":
        pvalues_adjusted = _holm_correction(pvalues)
    elif method == "benjamini-hochberg":
        pvalues_adjusted = _benjamini_hochberg_correction(pvalues)
    elif method == "benjamini-yekutieli":
        pvalues_adjusted = _benjamini_yekutieli_correction(pvalues)
    else:
        raise ValueError(
            f"Unknown correction method: {method}. "
            f"Use 'bonferroni', 'sidak', 'holm', 'benjamini-hochberg', or 'benjamini-yekutieli'"
        )

    # Create new TestResult objects with adjusted values
    adjusted_results = []
    for i, result in enumerate(results):
        # Create a copy with adjusted p-value
        adjusted_result = TestResult(
            name_1=result.name_1,
            value_1=result.value_1,
            std_1=result.std_1,
            size_1=result.size_1,
            name_2=result.name_2,
            value_2=result.value_2,
            std_2=result.std_2,
            size_2=result.size_2,
            method_name=result.method_name,
            method_params=result.method_params,
            alpha=alpha,
            pvalue=pvalues_adjusted[i],  # Adjusted p-value
            effect=result.effect,
            ci_length=result.ci_length,
            left_bound=result.left_bound,
            right_bound=result.right_bound,
            reject=(pvalues_adjusted[i] < alpha),  # Decision based on adjusted p-value
            effect_distribution=result.effect_distribution,
            # Additional fields for correction tracking
            pvalue_original=result.pvalue,  # Store original p-value
            correction_method=method,
            cov_value_1=result.cov_value_1 if hasattr(result, 'cov_value_1') else None,
            cov_value_2=result.cov_value_2 if hasattr(result, 'cov_value_2') else None
        )
        adjusted_results.append(adjusted_result)

    return adjusted_results


def _bonferroni_correction(pvalues: np.ndarray) -> np.ndarray:
    """
    Bonferroni correction: p_adjusted = min(p * n, 1.0)

    Most conservative method. Controls family-wise error rate (FWER).
    """
    n = len(pvalues)
    return np.minimum(pvalues * n, 1.0)


def _sidak_correction(pvalues: np.ndarray) -> np.ndarray:
    """
    Šidák correction: p_adjusted = 1 - (1 - p)^n

    Less conservative than Bonferroni. Assumes independence.
    """
    n = len(pvalues)
    return 1.0 - np.power(1.0 - pvalues, n)


def _holm_correction(pvalues: np.ndarray) -> np.ndarray:
    """
    Holm-Bonferroni step-down procedure.

    More powerful than Bonferroni while still controlling FWER.

    Procedure:
    1. Sort p-values in ascending order
    2. For rank i: p_adjusted[i] = max(p[i] * (n - i), p_adjusted[i-1])
    3. Return in original order
    """
    n = len(pvalues)

    # Get sort order
    sort_idx = np.argsort(pvalues)
    pvalues_sorted = pvalues[sort_idx]

    # Apply step-down procedure
    adjusted_sorted = np.zeros(n)
    for i in range(n):
        adjusted_sorted[i] = pvalues_sorted[i] * (n - i)

    # Enforce monotonicity (each adjusted p-value >= previous)
    for i in range(1, n):
        if adjusted_sorted[i] < adjusted_sorted[i - 1]:
            adjusted_sorted[i] = adjusted_sorted[i - 1]

    # Cap at 1.0
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)

    # Return in original order
    adjusted = np.zeros(n)
    adjusted[sort_idx] = adjusted_sorted

    return adjusted


def _benjamini_hochberg_correction(pvalues: np.ndarray) -> np.ndarray:
    """
    Benjamini-Hochberg FDR correction.

    Controls false discovery rate. Less conservative than FWER methods.
    Assumes independence or positive dependence.

    Procedure:
    1. Sort p-values in ascending order
    2. For rank i: p_adjusted[i] = min(p[i] * n / (i+1), p_adjusted[i+1])
    3. Return in original order
    """
    n = len(pvalues)

    # Get sort order
    sort_idx = np.argsort(pvalues)
    pvalues_sorted = pvalues[sort_idx]

    # Apply step-up procedure (work backwards)
    adjusted_sorted = np.zeros(n)
    adjusted_sorted[n - 1] = pvalues_sorted[n - 1]

    for i in range(n - 2, -1, -1):
        adjusted_sorted[i] = min(
            pvalues_sorted[i] * n / (i + 1),
            adjusted_sorted[i + 1]
        )

    # Cap at 1.0
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)

    # Return in original order
    adjusted = np.zeros(n)
    adjusted[sort_idx] = adjusted_sorted

    return adjusted


def _benjamini_yekutieli_correction(pvalues: np.ndarray) -> np.ndarray:
    """
    Benjamini-Yekutieli FDR correction.

    More conservative than Benjamini-Hochberg. Works with arbitrary dependence.

    Uses correction factor: c(n) = sum(1/i for i in 1..n)
    """
    n = len(pvalues)

    # Calculate correction factor for dependence
    c_n = np.sum(1.0 / np.arange(1, n + 1))

    # Get sort order
    sort_idx = np.argsort(pvalues)
    pvalues_sorted = pvalues[sort_idx]

    # Apply step-up procedure with correction factor
    adjusted_sorted = np.zeros(n)
    adjusted_sorted[n - 1] = pvalues_sorted[n - 1]

    for i in range(n - 2, -1, -1):
        adjusted_sorted[i] = min(
            pvalues_sorted[i] * n * c_n / (i + 1),
            adjusted_sorted[i + 1]
        )

    # Cap at 1.0
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)

    # Return in original order
    adjusted = np.zeros(n)
    adjusted[sort_idx] = adjusted_sorted

    return adjusted
