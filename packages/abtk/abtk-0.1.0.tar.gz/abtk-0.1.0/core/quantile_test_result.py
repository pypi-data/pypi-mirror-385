"""
Results from quantile treatment effect analysis.

This module defines the QuantileTestResult class which stores results
from analyzing treatment effects at multiple quantiles of the distribution.
"""

from dataclasses import dataclass
import numpy as np
from typing import Tuple, Optional


@dataclass
class QuantileTestResult:
    """
    Results from quantile treatment effect (QTE) analysis.

    Contains treatment effects for multiple quantiles with confidence intervals
    and significance tests for each quantile.

    Parameters
    ----------
    name_1 : str
        Name of first sample (e.g., "Control")
    name_2 : str
        Name of second sample (e.g., "Treatment")
    quantiles : np.ndarray
        Array of quantiles analyzed (e.g., [0.25, 0.5, 0.75, 0.9, 0.95])
    effects : np.ndarray
        Treatment effect at each quantile
    ci_lower : np.ndarray
        Lower bounds of confidence intervals
    ci_upper : np.ndarray
        Upper bounds of confidence intervals
    pvalues : np.ndarray
        P-values for each quantile
    reject : np.ndarray
        Boolean array indicating significance at each quantile
    alpha : float
        Significance level used
    test_type : str
        Type of effect ("relative" or "absolute")
    n_samples : int
        Number of bootstrap samples used
    base_test_name : str
        Name of underlying bootstrap test used

    Examples
    --------
    >>> from utils.quantile_analysis import QuantileAnalyzer
    >>> from tests.nonparametric import BootstrapTest
    >>>
    >>> bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
    >>> analyzer = QuantileAnalyzer(test=bootstrap)
    >>> results = analyzer.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(result.to_dataframe())
    >>>
    >>> # Get effect at specific quantile
    >>> median_effect = result.get_effect(0.5)
    >>>
    >>> # Find where effects are significant
    >>> sig_quantiles = result.significant_quantiles()
    """

    name_1: str
    name_2: str

    quantiles: np.ndarray       # [0.25, 0.5, 0.75, 0.9, 0.95]
    effects: np.ndarray         # Effect at each quantile
    ci_lower: np.ndarray        # CI lower bounds
    ci_upper: np.ndarray        # CI upper bounds
    pvalues: np.ndarray         # P-value for each quantile
    reject: np.ndarray          # Significance (bool)

    alpha: float
    test_type: str              # "relative" or "absolute"
    n_samples: int              # Number of bootstrap samples
    base_test_name: str         # "bootstrap-test", "paired-bootstrap-test", etc.

    def get_effect(self, quantile: float) -> float:
        """
        Get treatment effect for specific quantile.

        Parameters
        ----------
        quantile : float
            Quantile to retrieve (between 0 and 1)

        Returns
        -------
        float
            Treatment effect at the closest quantile

        Examples
        --------
        >>> effect_at_median = result.get_effect(0.5)
        >>> effect_at_90th = result.get_effect(0.9)
        """
        idx = np.argmin(np.abs(self.quantiles - quantile))
        return self.effects[idx]

    def get_ci(self, quantile: float) -> Tuple[float, float]:
        """
        Get confidence interval for specific quantile.

        Parameters
        ----------
        quantile : float
            Quantile to retrieve (between 0 and 1)

        Returns
        -------
        tuple
            (lower_bound, upper_bound) for the confidence interval

        Examples
        --------
        >>> ci_lower, ci_upper = result.get_ci(0.5)
        >>> print(f"Median effect CI: [{ci_lower:.2%}, {ci_upper:.2%}]")
        """
        idx = np.argmin(np.abs(self.quantiles - quantile))
        return (self.ci_lower[idx], self.ci_upper[idx])

    def get_pvalue(self, quantile: float) -> float:
        """
        Get p-value for specific quantile.

        Parameters
        ----------
        quantile : float
            Quantile to retrieve (between 0 and 1)

        Returns
        -------
        float
            P-value at the closest quantile
        """
        idx = np.argmin(np.abs(self.quantiles - quantile))
        return self.pvalues[idx]

    def is_significant(self, quantile: float) -> bool:
        """
        Check if effect is significant at specific quantile.

        Parameters
        ----------
        quantile : float
            Quantile to check (between 0 and 1)

        Returns
        -------
        bool
            True if effect is significant at this quantile
        """
        idx = np.argmin(np.abs(self.quantiles - quantile))
        return self.reject[idx]

    def to_dataframe(self):
        """
        Convert results to pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: quantile, effect, ci_lower, ci_upper,
            pvalue, significant

        Examples
        --------
        >>> df = result.to_dataframe()
        >>> print(df)
           quantile    effect  ci_lower  ci_upper   pvalue  significant
        0      0.25  0.020000 -0.010000  0.050000  0.15000        False
        1      0.50  0.050000  0.020000  0.080000  0.01000         True
        2      0.75  0.080000  0.040000  0.120000  0.00100         True
        3      0.90  0.120000  0.070000  0.170000  0.00010         True
        4      0.95  0.150000  0.090000  0.210000  0.00001         True
        """
        import pandas as pd
        return pd.DataFrame({
            'quantile': self.quantiles,
            'effect': self.effects,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'pvalue': self.pvalues,
            'significant': self.reject
        })

    def significant_quantiles(self) -> np.ndarray:
        """
        Return quantiles where effect is significant.

        Returns
        -------
        np.ndarray
            Array of quantiles where effect is significant at alpha level

        Examples
        --------
        >>> sig = result.significant_quantiles()
        >>> print(f"Effect is significant at: {sig}")
        Effect is significant at: [0.5  0.75 0.9  0.95]
        """
        return self.quantiles[self.reject]

    def summary(self) -> str:
        """
        Generate a text summary of the results.

        Returns
        -------
        str
            Formatted summary of quantile treatment effects

        Examples
        --------
        >>> print(result.summary())
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"Quantile Treatment Effects: {self.name_1} vs {self.name_2}")
        lines.append("=" * 70)
        lines.append(f"Base test: {self.base_test_name}")
        lines.append(f"Bootstrap samples: {self.n_samples}")
        lines.append(f"Test type: {self.test_type}")
        lines.append(f"Alpha: {self.alpha}")
        lines.append("")

        # Format based on test type
        if self.test_type == "relative":
            lines.append(f"{'Quantile':<10} {'Effect':<12} {'95% CI':<25} {'P-value':<10} {'Sig':<5}")
            lines.append("-" * 70)
            for i, q in enumerate(self.quantiles):
                effect_str = f"{self.effects[i]:>7.2%}"
                ci_str = f"[{self.ci_lower[i]:>6.2%}, {self.ci_upper[i]:>6.2%}]"
                pval_str = f"{self.pvalues[i]:.4f}"
                sig_str = "✓" if self.reject[i] else "✗"
                lines.append(f"{q:<10.2f} {effect_str:<12} {ci_str:<25} {pval_str:<10} {sig_str:<5}")
        else:  # absolute
            lines.append(f"{'Quantile':<10} {'Effect':<12} {'95% CI':<25} {'P-value':<10} {'Sig':<5}")
            lines.append("-" * 70)
            for i, q in enumerate(self.quantiles):
                effect_str = f"{self.effects[i]:>7.2f}"
                ci_str = f"[{self.ci_lower[i]:>6.2f}, {self.ci_upper[i]:>6.2f}]"
                pval_str = f"{self.pvalues[i]:.4f}"
                sig_str = "✓" if self.reject[i] else "✗"
                lines.append(f"{q:<10.2f} {effect_str:<12} {ci_str:<25} {pval_str:<10} {sig_str:<5}")

        lines.append("")
        sig_quantiles = self.significant_quantiles()
        if len(sig_quantiles) > 0:
            lines.append(f"Significant quantiles: {', '.join([f'{q:.2f}' for q in sig_quantiles])}")
        else:
            lines.append("No significant effects detected at any quantile.")

        lines.append("=" * 70)

        return "\n".join(lines)
