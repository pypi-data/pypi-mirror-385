"""
ANCOVA (Analysis of Covariance) / Regression Adjustment test.

ANCOVA uses linear regression to estimate treatment effect while adjusting
for multiple covariates. It's more flexible than CUPED and can handle
multiple pre-experiment variables simultaneously.

Model:
------
For absolute effect:
    Y = β₀ + β₁·Treatment + β₂·X₁ + β₃·X₂ + ... + ε
    Treatment effect = β₁

For relative effect:
    log(Y) = β₀ + β₁·Treatment + β₂·X₁ + β₃·X₂ + ... + ε
    Treatment effect = exp(β₁) - 1

Where:
- Y is the outcome metric
- Treatment is binary indicator (0=control, 1=treatment)
- X₁, X₂, ... are covariates (pre-experiment data)
- β₁ is the treatment effect (adjusted for covariates)
"""

from typing import List, Literal, Optional
import logging
from itertools import combinations
import numpy as np
import pandas as pd
import scipy.stats as sps

try:
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import het_breuschpagan, linear_rainbow
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha


class AncovaTest(BaseTestProcessor):
    """
    ANCOVA (Analysis of Covariance) / Regression Adjustment test.

    Uses linear regression (OLS) to estimate treatment effect while adjusting for
    multiple covariates. More flexible than CUPED - can use multiple covariates
    and provides full regression diagnostics.

    Note: This class can also be imported as `OLSTest` for practitioners who
    prefer the OLS terminology:
        from tests.parametric import AncovaTest  # Statistical name
        from tests.parametric import OLSTest     # Practitioner name (same class)

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level for hypothesis testing
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate:
        - 'relative': Uses log(Y) transformation, effect returned as percentage
                     (e.g., 0.1 = 10% increase)
        - 'absolute': Uses Y directly, effect in absolute units
    check_interaction : bool, default=False
        If True, checks for heterogeneous treatment effects (interaction between
        treatment and covariates). Useful to understand if effect varies by
        covariate levels (e.g., stronger for high-value users).
    interaction_alpha : float, default=0.10
        Significance level for interaction terms (typically more lenient)
    validate_assumptions : bool, default=True
        If True, validates regression assumptions:
        - Linearity (Rainbow test)
        - Homoscedasticity (Breusch-Pagan test)
        - Normality of residuals (Jarque-Bera test)
        - Multicollinearity (VIF)
        Set to False for simulations to improve speed.
    use_robust_se : bool, default=True
        If True, uses heteroscedasticity-robust standard errors (HC3).
        Recommended to keep True for robustness.
    logger : logging.Logger, optional
        Logger instance for warnings and diagnostics

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> import numpy as np
    >>>
    >>> # Example 1: Single covariate
    >>> control = SampleData(
    ...     data=[100, 110, 95, 105],          # Current metric
    ...     covariates=[90, 100, 85, 95],      # Historical data
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 115, 100, 110],
    ...     covariates=[92, 102, 87, 97],
    ...     name="Treatment"
    ... )
    >>>
    >>> test = AncovaTest(alpha=0.05, test_type="relative")
    >>> results = test.compare([control, treatment])
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")  # e.g., "Effect: 9.50%"
    >>> print(f"P-value: {result.pvalue:.4f}")

    >>> # Example 2: Multiple covariates
    >>> control = SampleData(
    ...     data=[100, 110, 95, 105],
    ...     covariates=np.array([
    ...         [90, 5, 1],    # [prev_revenue, prev_sessions, platform]
    ...         [100, 8, 1],
    ...         [85, 3, 0],
    ...         [95, 6, 0]
    ...     ]),
    ...     name="Control"
    ... )
    >>> treatment = SampleData(
    ...     data=[105, 115, 100, 110],
    ...     covariates=np.array([
    ...         [92, 5, 1],
    ...         [102, 9, 1],
    ...         [87, 4, 0],
    ...         [97, 7, 0]
    ...     ]),
    ...     name="Treatment"
    ... )
    >>>
    >>> test = AncovaTest(alpha=0.05, check_interaction=True)
    >>> results = test.compare([control, treatment])

    Notes
    -----
    Use ANCOVA when:
    - You have pre-experiment data (covariates)
    - You want variance reduction (like CUPED but more flexible)
    - You have multiple covariates to adjust for
    - You want to check for heterogeneous treatment effects

    Comparison to other methods:
    - vs CUPED: ANCOVA can use multiple covariates, provides full diagnostics
    - vs Paired t-test: ANCOVA doesn't require pairing, more flexible
    - vs Regular t-test: ANCOVA reduces variance using covariates

    Requirements:
    - Both samples must have covariates
    - Sample size should be n > k + 10 (k = number of covariates)
    - For relative effect, all outcome values must be positive

    The treatment effect is the regression coefficient for the treatment
    indicator, adjusted for all covariates. Confidence intervals and p-values
    account for the regression uncertainty.

    References
    ----------
    - Deng, A., et al. (2013). Improving the sensitivity of online controlled
      experiments by utilizing pre-experiment data. WSDM.
    - Gelman, A., & Hill, J. (2006). Data analysis using regression and
      multilevel/hierarchical models. Cambridge University Press.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        check_interaction: bool = False,
        interaction_alpha: float = 0.10,
        validate_assumptions: bool = True,
        use_robust_se: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        # Check statsmodels availability
        if not STATSMODELS_AVAILABLE:
            raise ImportError(
                "AncovaTest requires statsmodels. Install it with: pip install statsmodels"
            )

        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Invalid test_type. Use "relative" or "absolute"')

        if not 0 < interaction_alpha < 1:
            raise ValueError("interaction_alpha must be between 0 and 1")

        # Initialize base class
        super().__init__(
            test_name="ancova-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type,
            check_interaction=check_interaction,
            interaction_alpha=interaction_alpha,
            validate_assumptions=validate_assumptions,
            use_robust_se=use_robust_se
        )

        # Test-specific parameters
        self.test_type = test_type
        self.check_interaction = check_interaction
        self.interaction_alpha = interaction_alpha
        self.validate_assumptions = validate_assumptions
        self.use_robust_se = use_robust_se

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise ANCOVA tests.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare (must have covariates)

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results
        """
        if not samples or len(samples) < 2:
            return []

        # Validate samples
        validate_samples(samples, min_samples=2)

        # Check that all samples have covariates
        for sample in samples:
            if sample.covariates is None:
                raise ValueError(
                    f"Sample '{sample.name}' is missing covariates. "
                    "ANCOVA requires covariates for adjustment."
                )

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using ANCOVA.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline, must have covariates)
        sample2 : SampleData
            Second sample (treatment/variant, must have covariates)

        Returns
        -------
        TestResult
            Test result with treatment effect, p-value, confidence interval
        """
        try:
            # Validate covariates
            if sample1.covariates is None or sample2.covariates is None:
                raise ValueError("Both samples must have covariates for ANCOVA")

            # Prepare data for regression
            df = self._prepare_regression_data(sample1, sample2)

            # Validate for relative effect
            if self.test_type == "relative":
                if (df['outcome'] <= 0).any():
                    raise ValueError(
                        "For relative effect (log transformation), all outcome values must be positive. "
                        f"Found {(df['outcome'] <= 0).sum()} non-positive values."
                    )
                # Transform outcome
                df['outcome_transformed'] = np.log(df['outcome'])
            else:
                df['outcome_transformed'] = df['outcome']

            # Check sample size adequacy
            n_total = len(df)
            n_covariates = df.filter(regex='^covariate_').shape[1]

            if n_total < n_covariates + 10:
                raise ValueError(
                    f"Insufficient sample size for ANCOVA. "
                    f"Need at least {n_covariates + 10} observations, got {n_total}. "
                    f"(Rule of thumb: n > k + 10, where k = {n_covariates} covariates)"
                )

            # Build and fit main regression model
            model, model_results = self._fit_regression_model(df)

            # Extract treatment effect
            treatment_coef = model_results.params['treatment']
            treatment_se = model_results.bse['treatment']
            treatment_pvalue = model_results.pvalues['treatment']

            # Get confidence interval
            ci = model_results.conf_int(alpha=self.alpha)
            ci_lower = ci.loc['treatment', 0]
            ci_upper = ci.loc['treatment', 1]

            # Convert to relative effect if needed
            if self.test_type == "relative":
                effect = np.exp(treatment_coef) - 1
                left_bound = np.exp(ci_lower) - 1
                right_bound = np.exp(ci_upper) - 1
            else:
                effect = treatment_coef
                left_bound = ci_lower
                right_bound = ci_upper

            ci_length = right_bound - left_bound
            reject = treatment_pvalue < self.alpha

            # Check for heterogeneous effects (interactions)
            interaction_info = {}
            if self.check_interaction:
                interaction_info = self._check_interactions(df)

            # Validate regression assumptions
            validation_info = {}
            if self.validate_assumptions:
                validation_info = self._validate_assumptions(model_results, df)

            # Build method_params with diagnostics
            method_params = self.test_params.copy()
            method_params.update({
                "n_covariates": n_covariates,
                "r_squared": model_results.rsquared,
                "adj_r_squared": model_results.rsquared_adj,
                "n_obs": n_total,
            })

            if interaction_info:
                method_params.update(interaction_info)

            if validation_info:
                method_params.update(validation_info)

            # Calculate point estimates for sample statistics
            stat1 = np.mean(sample1.data)
            stat2 = np.mean(sample2.data)

            # Create result object
            result = TestResult(
                name_1=sample1.name or "sample_1",
                value_1=stat1,
                std_1=np.std(sample1.data),
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=stat2,
                std_2=np.std(sample2.data),
                size_2=sample2.sample_size,
                method_name=self.test_name,
                method_params=method_params,
                alpha=self.alpha,
                pvalue=treatment_pvalue,
                effect=effect,
                ci_length=ci_length,
                left_bound=left_bound,
                right_bound=right_bound,
                reject=reject
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in AncovaTest compare_samples: {str(e)}", exc_info=True)
            raise

    def _prepare_regression_data(self, sample1: SampleData, sample2: SampleData) -> pd.DataFrame:
        """
        Prepare data for regression analysis.

        Creates a single DataFrame with:
        - outcome: combined outcome variable
        - treatment: binary indicator (0=sample1, 1=sample2)
        - covariate_0, covariate_1, ...: covariates

        Returns
        -------
        pd.DataFrame
            Prepared data for regression
        """
        # Combine outcomes
        outcome = np.concatenate([sample1.data, sample2.data])

        # Create treatment indicator
        treatment = np.concatenate([
            np.zeros(sample1.sample_size),
            np.ones(sample2.sample_size)
        ])

        # Handle covariates (can be 1D or 2D)
        cov1 = sample1.covariates
        cov2 = sample2.covariates

        # Ensure 2D
        if cov1.ndim == 1:
            cov1 = cov1.reshape(-1, 1)
        if cov2.ndim == 1:
            cov2 = cov2.reshape(-1, 1)

        # Combine covariates
        covariates = np.vstack([cov1, cov2])

        # Create DataFrame
        df = pd.DataFrame({
            'outcome': outcome,
            'treatment': treatment
        })

        # Add covariates
        n_covariates = covariates.shape[1]
        for i in range(n_covariates):
            df[f'covariate_{i}'] = covariates[:, i]

        return df

    def _fit_regression_model(self, df: pd.DataFrame):
        """
        Fit OLS regression model.

        Model: outcome_transformed ~ treatment + covariate_0 + covariate_1 + ...

        Returns
        -------
        tuple
            (model, results) - statsmodels objects
        """
        # Prepare design matrix (X)
        covariate_cols = [col for col in df.columns if col.startswith('covariate_')]
        X_cols = ['treatment'] + covariate_cols
        X = df[X_cols]
        X = sm.add_constant(X)  # Add intercept

        # Outcome (y)
        y = df['outcome_transformed']

        # Fit OLS
        model = sm.OLS(y, X)

        if self.use_robust_se:
            # Use robust standard errors (HC3)
            results = model.fit(cov_type='HC3')
        else:
            results = model.fit()

        return model, results

    def _check_interactions(self, df: pd.DataFrame) -> dict:
        """
        Check for heterogeneous treatment effects (interactions).

        Fits model: outcome ~ treatment * (covariate_0 + covariate_1 + ...)

        Returns
        -------
        dict
            Interaction diagnostics
        """
        covariate_cols = [col for col in df.columns if col.startswith('covariate_')]

        # Build interaction terms
        interaction_terms = []
        for cov in covariate_cols:
            df[f'treatment_x_{cov}'] = df['treatment'] * df[cov]
            interaction_terms.append(f'treatment_x_{cov}')

        # Prepare design matrix with interactions
        X_cols = ['treatment'] + covariate_cols + interaction_terms
        X = df[X_cols]
        X = sm.add_constant(X)

        # Outcome
        y = df['outcome_transformed']

        # Fit model with interactions
        model = sm.OLS(y, X)

        if self.use_robust_se:
            results = model.fit(cov_type='HC3')
        else:
            results = model.fit()

        # Check significance of interaction terms
        significant_interactions = []
        interaction_pvalues = {}

        for i, cov in enumerate(covariate_cols):
            interaction_term = f'treatment_x_{cov}'
            if interaction_term in results.params.index:
                pvalue = results.pvalues[interaction_term]
                interaction_pvalues[f'covariate_{i}'] = pvalue

                if pvalue < self.interaction_alpha:
                    significant_interactions.append(f'covariate_{i}')

        has_heterogeneous_effect = len(significant_interactions) > 0

        if has_heterogeneous_effect and self.logger:
            self.logger.warning(
                f"Heterogeneous treatment effect detected! "
                f"Effect varies by: {significant_interactions}. "
                f"Consider segmented analysis."
            )

        return {
            "has_heterogeneous_effect": has_heterogeneous_effect,
            "significant_interactions": significant_interactions,
            "interaction_pvalues": interaction_pvalues
        }

    def _validate_assumptions(self, model_results, df: pd.DataFrame) -> dict:
        """
        Validate regression assumptions.

        Checks:
        1. Linearity (Rainbow test)
        2. Homoscedasticity (Breusch-Pagan test)
        3. Normality of residuals (Jarque-Bera test)
        4. Multicollinearity (VIF)

        Returns
        -------
        dict
            Validation diagnostics and warnings
        """
        validation = {}
        warnings = []

        try:
            # 1. Linearity - Rainbow test
            # Tests if relationship is linear (null hypothesis: linear)
            rainbow_stat, rainbow_pvalue = linear_rainbow(model_results)
            validation['linearity_test_pvalue'] = rainbow_pvalue

            if rainbow_pvalue < 0.05:
                warnings.append(
                    f"Linearity assumption may be violated (Rainbow test p={rainbow_pvalue:.4f}). "
                    "Consider transformations or non-linear models."
                )

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Could not perform Rainbow test: {str(e)}")

        try:
            # 2. Homoscedasticity - Breusch-Pagan test
            # Tests if error variance is constant (null hypothesis: homoscedastic)
            covariate_cols = [col for col in df.columns if col.startswith('covariate_')]
            X_cols = ['treatment'] + covariate_cols
            X = df[X_cols]
            X = sm.add_constant(X)

            bp_stat, bp_pvalue, _, _ = het_breuschpagan(model_results.resid, X)
            validation['homoscedasticity_test_pvalue'] = bp_pvalue

            if bp_pvalue < 0.05:
                if self.use_robust_se:
                    warnings.append(
                        f"Heteroscedasticity detected (Breusch-Pagan p={bp_pvalue:.4f}). "
                        "Using robust standard errors to account for this."
                    )
                else:
                    warnings.append(
                        f"Heteroscedasticity detected (Breusch-Pagan p={bp_pvalue:.4f}). "
                        "Standard errors may be incorrect. Consider using robust SE."
                    )

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Could not perform Breusch-Pagan test: {str(e)}")

        # 3. Normality of residuals - Jarque-Bera test (built into statsmodels)
        try:
            jb_stat = model_results.jarque_bera[0]
            jb_pvalue = model_results.jarque_bera[1]
            validation['normality_test_pvalue'] = jb_pvalue

            if jb_pvalue < 0.05:
                if len(df) > 30:
                    warnings.append(
                        f"Residuals are not normally distributed (Jarque-Bera p={jb_pvalue:.4f}). "
                        "However, with n>30, inference is still valid due to CLT."
                    )
                else:
                    warnings.append(
                        f"Residuals are not normally distributed (Jarque-Bera p={jb_pvalue:.4f}). "
                        "With small sample size, inference may be unreliable."
                    )
        except (AttributeError, KeyError):
            # jarque_bera not available in this version of statsmodels
            # Use scipy's jarque_bera test instead
            from scipy.stats import jarque_bera
            residuals = model_results.resid
            jb_stat, jb_pvalue = jarque_bera(residuals)
            validation['normality_test_pvalue'] = jb_pvalue

            if jb_pvalue < 0.05:
                if len(df) > 30:
                    warnings.append(
                        f"Residuals are not normally distributed (Jarque-Bera p={jb_pvalue:.4f}). "
                        "However, with n>30, inference is still valid due to CLT."
                    )
                else:
                    warnings.append(
                        f"Residuals are not normally distributed (Jarque-Bera p={jb_pvalue:.4f}). "
                        "With small sample size, inference may be unreliable."
                    )

        try:
            # 4. Multicollinearity - VIF
            # VIF > 10 indicates problematic multicollinearity
            covariate_cols = [col for col in df.columns if col.startswith('covariate_')]
            X_cols = ['treatment'] + covariate_cols
            X = df[X_cols]

            vif_values = {}
            max_vif = 0

            for i, col in enumerate(X_cols):
                vif = variance_inflation_factor(X.values, i)
                vif_values[col] = vif
                max_vif = max(max_vif, vif)

            validation['vif_values'] = vif_values
            validation['max_vif'] = max_vif

            if max_vif > 10:
                high_vif_vars = [var for var, vif in vif_values.items() if vif > 10]
                warnings.append(
                    f"High multicollinearity detected (max VIF={max_vif:.2f}). "
                    f"Variables with VIF>10: {high_vif_vars}. "
                    "Standard errors may be inflated."
                )

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Could not calculate VIF: {str(e)}")

        # Log warnings
        if warnings and self.logger:
            for warning in warnings:
                self.logger.warning(warning)

        validation['validation_warnings'] = warnings

        return {'validation': validation}
