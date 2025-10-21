"""
DataFrame helpers for converting pandas DataFrames to ABTK data types.

This module provides convenience functions for analysts who work with pandas DataFrames,
making it easy to convert DataFrames to SampleData or ProportionData for ABTK tests.
"""

from typing import List, Optional, Union
import pandas as pd
import numpy as np

from core.data_types import SampleData, ProportionData


def sample_data_from_dataframe(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    covariate_cols: Optional[Union[str, List[str]]] = None,
    strata_col: Optional[str] = None,
    paired_id_col: Optional[str] = None,
    group_names: Optional[List[str]] = None
) -> List[SampleData]:
    """
    Convert pandas DataFrame to list of SampleData objects.

    This is a convenience function for analysts working with pandas DataFrames.
    It automatically splits the DataFrame by group and creates SampleData objects.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing experiment data
    group_col : str
        Column name containing group labels (e.g., 'group', 'variant')
    metric_col : str
        Column name containing metric values (e.g., 'revenue', 'time_on_site')
    covariate_cols : str or list of str, optional
        Column name(s) for covariates (historical/baseline data).
        For variance reduction with CUPED or ANCOVA.
        - Single column: 'baseline_revenue'
        - Multiple columns: ['baseline_revenue', 'age', 'tenure']
    strata_col : str, optional
        Column name for strata (for stratified bootstrap).
        E.g., 'platform', 'country'
    paired_id_col : str, optional
        Column name for pair identifiers (for paired tests).
        E.g., 'user_id', 'match_id'
    group_names : list of str, optional
        Specific groups to extract. If None, uses all unique values in group_col.
        E.g., ['control', 'treatment']

    Returns
    -------
    list of SampleData
        List of SampleData objects, one per group

    Examples
    --------
    >>> import pandas as pd
    >>> from utils.dataframe_helpers import sample_data_from_dataframe
    >>> from tests.parametric import TTest
    >>>
    >>> # Simple A/B test
    >>> df = pd.DataFrame({
    ...     'group': ['control', 'control', 'treatment', 'treatment'],
    ...     'revenue': [100, 110, 105, 115]
    ... })
    >>>
    >>> samples = sample_data_from_dataframe(
    ...     df,
    ...     group_col='group',
    ...     metric_col='revenue'
    ... )
    >>>
    >>> test = TTest(alpha=0.05)
    >>> results = test.compare(samples)

    >>> # With covariates (for CUPED)
    >>> df = pd.DataFrame({
    ...     'group': ['control', 'control', 'treatment', 'treatment'],
    ...     'revenue': [100, 110, 105, 115],
    ...     'baseline_revenue': [90, 100, 92, 102]
    ... })
    >>>
    >>> samples = sample_data_from_dataframe(
    ...     df,
    ...     group_col='group',
    ...     metric_col='revenue',
    ...     covariate_cols='baseline_revenue'
    ... )
    >>>
    >>> from tests.parametric import CupedTTest
    >>> test = CupedTTest(alpha=0.05)
    >>> results = test.compare(samples)

    >>> # With multiple covariates (for ANCOVA)
    >>> df = pd.DataFrame({
    ...     'group': ['control', 'treatment'] * 100,
    ...     'revenue': np.random.normal(100, 10, 200),
    ...     'baseline_revenue': np.random.normal(95, 10, 200),
    ...     'age': np.random.randint(18, 65, 200),
    ...     'tenure_days': np.random.randint(1, 365, 200)
    ... })
    >>>
    >>> samples = sample_data_from_dataframe(
    ...     df,
    ...     group_col='group',
    ...     metric_col='revenue',
    ...     covariate_cols=['baseline_revenue', 'age', 'tenure_days']
    ... )
    >>>
    >>> from tests.parametric import AncovaTest
    >>> test = AncovaTest(alpha=0.05)
    >>> results = test.compare(samples)

    >>> # With strata (for stratified bootstrap)
    >>> df = pd.DataFrame({
    ...     'group': ['control', 'control', 'treatment', 'treatment'],
    ...     'revenue': [100, 110, 105, 115],
    ...     'platform': ['mobile', 'desktop', 'mobile', 'desktop']
    ... })
    >>>
    >>> samples = sample_data_from_dataframe(
    ...     df,
    ...     group_col='group',
    ...     metric_col='revenue',
    ...     strata_col='platform'
    ... )
    >>>
    >>> from tests.nonparametric import BootstrapTest
    >>> test = BootstrapTest(alpha=0.05, stratify=True)
    >>> results = test.compare(samples)

    >>> # With paired IDs (for paired tests)
    >>> df = pd.DataFrame({
    ...     'group': ['control', 'control', 'treatment', 'treatment'],
    ...     'revenue': [100, 110, 105, 115],
    ...     'user_id': [1, 2, 1, 2]  # User 1 and 2 are pairs
    ... })
    >>>
    >>> samples = sample_data_from_dataframe(
    ...     df,
    ...     group_col='group',
    ...     metric_col='revenue',
    ...     paired_id_col='user_id'
    ... )
    >>>
    >>> from tests.parametric import PairedTTest
    >>> test = PairedTTest(alpha=0.05)
    >>> results = test.compare(samples)

    Notes
    -----
    - Missing values (NaN) are automatically dropped with a warning
    - Groups are sorted alphabetically by default
    - For multiple covariates, they must all be numeric
    - Paired IDs can be any type (int, str, etc.)

    Raises
    ------
    ValueError
        If required columns are missing or data is invalid
    KeyError
        If specified column names don't exist in DataFrame
    """
    # Validate inputs
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be pandas DataFrame, got {type(df)}")

    required_cols = [group_col, metric_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # Get unique groups
    if group_names is None:
        group_names = sorted(df[group_col].unique())
    else:
        # Validate group_names exist
        missing_groups = set(group_names) - set(df[group_col].unique())
        if missing_groups:
            raise ValueError(f"Groups {missing_groups} not found in column '{group_col}'")

    samples = []

    for group_name in group_names:
        # Filter to group
        group_df = df[df[group_col] == group_name].copy()

        if len(group_df) == 0:
            raise ValueError(f"No data found for group '{group_name}'")

        # Extract metric data
        data = group_df[metric_col].values

        # Check for missing values
        if pd.isna(data).any():
            n_missing = pd.isna(data).sum()
            print(f"Warning: Dropping {n_missing} missing values in group '{group_name}'")
            data = data[~pd.isna(data)]

        if len(data) == 0:
            raise ValueError(f"No valid data for group '{group_name}' after dropping NaN")

        # Extract covariates if specified
        covariates = None
        if covariate_cols is not None:
            if isinstance(covariate_cols, str):
                covariate_cols = [covariate_cols]

            # Validate covariate columns exist
            missing_cov_cols = [col for col in covariate_cols if col not in group_df.columns]
            if missing_cov_cols:
                raise KeyError(f"Missing covariate columns: {missing_cov_cols}")

            # Extract covariates
            if len(covariate_cols) == 1:
                # Single covariate: 1D array
                covariates = group_df[covariate_cols[0]].values
            else:
                # Multiple covariates: 2D array
                covariates = group_df[covariate_cols].values

            # Check for missing values in covariates
            if pd.isna(covariates).any():
                n_missing = pd.isna(covariates).sum()
                print(f"Warning: Dropping {n_missing} missing covariate values in group '{group_name}'")

                # Remove rows with any missing covariate
                valid_mask = ~pd.isna(covariates).any(axis=1) if covariates.ndim == 2 else ~pd.isna(covariates)

                # Also filter data to match
                data = data[valid_mask]
                covariates = covariates[valid_mask]

            if len(covariates) == 0:
                raise ValueError(f"No valid covariates for group '{group_name}' after dropping NaN")

        # Extract strata if specified
        strata = None
        if strata_col is not None:
            if strata_col not in group_df.columns:
                raise KeyError(f"Strata column '{strata_col}' not found")

            strata = group_df[strata_col].values

            # Convert to strings
            strata = strata.astype(str)

        # Extract paired IDs if specified
        paired_ids = None
        if paired_id_col is not None:
            if paired_id_col not in group_df.columns:
                raise KeyError(f"Paired ID column '{paired_id_col}' not found")

            paired_ids = group_df[paired_id_col].values

        # Create SampleData
        sample = SampleData(
            data=data,
            covariates=covariates,
            strata=strata,
            paired_ids=paired_ids,
            name=str(group_name)
        )

        samples.append(sample)

    return samples


def proportion_data_from_dataframe(
    df: pd.DataFrame,
    group_col: str,
    successes_col: Optional[str] = None,
    trials_col: Optional[str] = None,
    binary_col: Optional[str] = None,
    group_names: Optional[List[str]] = None
) -> List[ProportionData]:
    """
    Convert pandas DataFrame to list of ProportionData objects.

    Supports two input formats:
    1. Aggregated data: Columns for successes and trials (e.g., clicks and impressions)
    2. Raw binary data: Column with 0/1 values (e.g., individual click events)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing experiment data
    group_col : str
        Column name containing group labels
    successes_col : str, optional
        Column name for number of successes (for aggregated data).
        E.g., 'clicks', 'conversions'
    trials_col : str, optional
        Column name for number of trials (for aggregated data).
        E.g., 'impressions', 'users'
    binary_col : str, optional
        Column name for binary outcomes (for raw data).
        Values should be 0/1, True/False, or convertible to int.
    group_names : list of str, optional
        Specific groups to extract. If None, uses all unique values in group_col.

    Returns
    -------
    list of ProportionData
        List of ProportionData objects, one per group

    Examples
    --------
    >>> import pandas as pd
    >>> from utils.dataframe_helpers import proportion_data_from_dataframe
    >>> from tests.parametric import ZTest
    >>>
    >>> # Format 1: Aggregated data (one row per group)
    >>> df_agg = pd.DataFrame({
    ...     'group': ['control', 'treatment'],
    ...     'clicks': [450, 520],
    ...     'impressions': [10000, 10000]
    ... })
    >>>
    >>> samples = proportion_data_from_dataframe(
    ...     df_agg,
    ...     group_col='group',
    ...     successes_col='clicks',
    ...     trials_col='impressions'
    ... )
    >>>
    >>> test = ZTest(alpha=0.05)
    >>> results = test.compare(samples)

    >>> # Format 2: Raw binary data (one row per trial/user)
    >>> df_raw = pd.DataFrame({
    ...     'group': ['control'] * 100 + ['treatment'] * 100,
    ...     'clicked': [0, 1, 0, 0, 1, ...],  # 0 or 1 for each user
    ... })
    >>>
    >>> samples = proportion_data_from_dataframe(
    ...     df_raw,
    ...     group_col='group',
    ...     binary_col='clicked'
    ... )
    >>>
    >>> test = ZTest(alpha=0.05)
    >>> results = test.compare(samples)

    >>> # Format 2 alternative: Boolean values
    >>> df_bool = pd.DataFrame({
    ...     'group': ['control', 'control', 'treatment', 'treatment'],
    ...     'converted': [True, False, True, True]
    ... })
    >>>
    >>> samples = proportion_data_from_dataframe(
    ...     df_bool,
    ...     group_col='group',
    ...     binary_col='converted'
    ... )

    Notes
    -----
    - Must provide either (successes_col + trials_col) OR binary_col, not both
    - For binary_col, values are converted to int (0/1)
    - Missing values are dropped with a warning
    - For aggregated data, can have multiple rows per group (they will be summed)

    Raises
    ------
    ValueError
        If inputs are invalid or conflicting parameters provided
    KeyError
        If specified column names don't exist
    """
    # Validate inputs
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be pandas DataFrame, got {type(df)}")

    if group_col not in df.columns:
        raise KeyError(f"Group column '{group_col}' not found")

    # Check parameter combinations
    has_aggregated = (successes_col is not None) and (trials_col is not None)
    has_binary = binary_col is not None

    if not has_aggregated and not has_binary:
        raise ValueError(
            "Must provide either (successes_col + trials_col) for aggregated data "
            "or binary_col for raw binary data"
        )

    if has_aggregated and has_binary:
        raise ValueError(
            "Cannot provide both aggregated data (successes_col + trials_col) "
            "and binary data (binary_col). Choose one format."
        )

    # Get unique groups
    if group_names is None:
        group_names = sorted(df[group_col].unique())

    samples = []

    for group_name in group_names:
        # Filter to group
        group_df = df[df[group_col] == group_name].copy()

        if len(group_df) == 0:
            raise ValueError(f"No data found for group '{group_name}'")

        if has_aggregated:
            # Aggregated format: sum successes and trials
            if successes_col not in group_df.columns:
                raise KeyError(f"Successes column '{successes_col}' not found")
            if trials_col not in group_df.columns:
                raise KeyError(f"Trials column '{trials_col}' not found")

            successes = group_df[successes_col].sum()
            trials = group_df[trials_col].sum()

            # Validate
            if pd.isna(successes) or pd.isna(trials):
                raise ValueError(f"Group '{group_name}' has missing successes or trials")

            if successes > trials:
                raise ValueError(f"Group '{group_name}': successes ({successes}) > trials ({trials})")

            if trials == 0:
                raise ValueError(f"Group '{group_name}' has zero trials")

        else:
            # Binary format: count successes
            if binary_col not in group_df.columns:
                raise KeyError(f"Binary column '{binary_col}' not found")

            binary_data = group_df[binary_col].values

            # Drop missing
            if pd.isna(binary_data).any():
                n_missing = pd.isna(binary_data).sum()
                print(f"Warning: Dropping {n_missing} missing values in group '{group_name}'")
                binary_data = binary_data[~pd.isna(binary_data)]

            if len(binary_data) == 0:
                raise ValueError(f"No valid data for group '{group_name}' after dropping NaN")

            # Convert to 0/1
            try:
                binary_data = binary_data.astype(int)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Cannot convert binary_col to integers for group '{group_name}'. "
                    f"Values must be 0/1, True/False, or numeric. Error: {e}"
                )

            # Validate binary
            if not np.all(np.isin(binary_data, [0, 1])):
                unique_vals = np.unique(binary_data)
                raise ValueError(
                    f"Binary column must contain only 0/1 values for group '{group_name}'. "
                    f"Found: {unique_vals}"
                )

            successes = int(binary_data.sum())
            trials = int(len(binary_data))

        # Create ProportionData
        sample = ProportionData(
            successes=successes,
            trials=trials,
            name=str(group_name)
        )

        samples.append(sample)

    return samples
