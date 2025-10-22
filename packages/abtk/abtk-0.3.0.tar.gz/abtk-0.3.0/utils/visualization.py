"""
Visualization utilities for A/B test results.

This module provides plotting functions for visualizing test results.
Requires matplotlib (optional dependency).

Installation:
    pip install matplotlib

Or with extras:
    pip install -e ".[viz]"
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def plot_quantile_effects(
    result,  # QuantileTestResult
    figsize=(12, 6),
    show_ci=True,
    highlight_significant=True,
    title=None,
    ax=None,
    **kwargs
):
    """
    Plot quantile treatment effects with confidence intervals.

    Creates a scatter plot showing treatment effects at different quantiles
    with confidence intervals. Significant effects are highlighted.

    Parameters
    ----------
    result : QuantileTestResult
        Results from QuantileAnalyzer.compare()
    figsize : tuple, default=(12, 6)
        Figure size in inches (width, height)
    show_ci : bool, default=True
        If True, shows confidence intervals as vertical lines
    highlight_significant : bool, default=True
        If True, uses different colors for significant vs non-significant effects
    title : str, optional
        Plot title. If None, generates automatic title.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates new figure.
    **kwargs : dict
        Additional arguments passed to matplotlib (e.g., dpi=150)

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : matplotlib.axes.Axes
        The axes object

    Raises
    ------
    ImportError
        If matplotlib is not installed

    Examples
    --------
    >>> from tests.nonparametric import BootstrapTest
    >>> from utils.quantile_analysis import QuantileAnalyzer
    >>> from utils.visualization import plot_quantile_effects
    >>> import matplotlib.pyplot as plt
    >>>
    >>> # Run quantile analysis
    >>> bootstrap = BootstrapTest(alpha=0.05, n_samples=10000)
    >>> analyzer = QuantileAnalyzer(test=bootstrap)
    >>> results = analyzer.compare([control, treatment])
    >>>
    >>> # Plot results
    >>> result = results[0]
    >>> fig, ax = plot_quantile_effects(result)
    >>> plt.show()
    >>>
    >>> # Save to file
    >>> fig, ax = plot_quantile_effects(result)
    >>> plt.savefig('quantile_effects.png', dpi=300, bbox_inches='tight')
    >>>
    >>> # Customize
    >>> fig, ax = plot_quantile_effects(
    ...     result,
    ...     figsize=(14, 7),
    ...     show_ci=True,
    ...     highlight_significant=True,
    ...     title="Treatment Effects Across Distribution"
    ... )

    Notes
    -----
    The plot shows:
    - Point estimates as dots (green=significant, gray=not significant)
    - Confidence intervals as vertical lines
    - Horizontal line at zero for reference
    - X-axis: Quantiles (labeled as percentages)
    - Y-axis: Treatment effect (percentage if relative, raw if absolute)

    Interpretation:
    - Effects above zero indicate treatment > control at that quantile
    - Effects below zero indicate treatment < control at that quantile
    - Varying effects across quantiles suggest heterogeneous treatment effects
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Visualization requires matplotlib. Install with:\n"
            "  pip install matplotlib\n"
            "Or install with extras:\n"
            "  pip install -e \".[viz]\""
        )

    # Create figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, **kwargs)
    else:
        fig = ax.figure

    quantiles = result.quantiles
    effects = result.effects
    ci_lower = result.ci_lower
    ci_upper = result.ci_upper
    significant = result.reject

    # Convert to percentage if relative
    if result.test_type == "relative":
        effects = effects * 100
        ci_lower = ci_lower * 100
        ci_upper = ci_upper * 100
        ylabel = "Treatment Effect (%)"
    else:
        ylabel = "Treatment Effect"

    # Plot confidence intervals
    if show_ci:
        for i, q in enumerate(quantiles):
            if highlight_significant:
                color = '#2ecc71' if significant[i] else '#95a5a6'  # Green or gray
                alpha = 0.8 if significant[i] else 0.4
                linewidth = 2.5 if significant[i] else 2
            else:
                color = '#3498db'  # Blue
                alpha = 0.7
                linewidth = 2

            ax.plot(
                [q, q],
                [ci_lower[i], ci_upper[i]],
                color=color,
                linewidth=linewidth,
                alpha=alpha,
                zorder=2
            )

    # Plot point estimates
    if highlight_significant:
        # Significant points
        sig_mask = significant
        if sig_mask.any():
            ax.scatter(
                quantiles[sig_mask],
                effects[sig_mask],
                s=150,
                color='#27ae60',  # Dark green
                edgecolors='white',
                linewidths=2,
                zorder=5,
                label='Significant'
            )

        # Non-significant points
        nonsig_mask = ~significant
        if nonsig_mask.any():
            ax.scatter(
                quantiles[nonsig_mask],
                effects[nonsig_mask],
                s=150,
                color='#7f8c8d',  # Gray
                edgecolors='white',
                linewidths=2,
                alpha=0.6,
                zorder=5,
                label='Not significant'
            )
    else:
        ax.scatter(
            quantiles,
            effects,
            s=150,
            color='#3498db',  # Blue
            edgecolors='white',
            linewidths=2,
            zorder=5
        )

    # Zero reference line
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.4, zorder=1)

    # Labels and title
    ax.set_xlabel('Quantile', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=13, fontweight='bold')

    if title is None:
        title = f"Quantile Treatment Effects: {result.name_1} vs {result.name_2}"
    ax.set_title(title, fontsize=15, fontweight='bold', pad=20)

    # Legend
    if highlight_significant and (significant.any() or (~significant).any()):
        ax.legend(loc='best', framealpha=0.9, fontsize=11)

    # Grid
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=1)
    ax.set_axisbelow(True)

    # Format x-axis as percentages
    ax.set_xticks(quantiles)
    ax.set_xticklabels([f'{int(q*100)}%' for q in quantiles], fontsize=11)

    # Format y-axis
    ax.tick_params(axis='y', labelsize=11)

    # Add subtle background
    ax.set_facecolor('#fafafa')

    # Tight layout
    plt.tight_layout()

    return fig, ax


def plot_multiple_quantile_effects(
    results,  # List[QuantileTestResult]
    figsize=None,
    ncols=2,
    show_ci=True,
    highlight_significant=True,
    suptitle=None,
    **kwargs
):
    """
    Plot multiple quantile treatment effect results in a grid.

    Useful when comparing multiple treatment variants or multiple
    quantile analyses.

    Parameters
    ----------
    results : List[QuantileTestResult]
        List of results from QuantileAnalyzer.compare()
    figsize : tuple, optional
        Figure size. If None, calculated automatically.
    ncols : int, default=2
        Number of columns in subplot grid
    show_ci : bool, default=True
        Show confidence intervals
    highlight_significant : bool, default=True
        Highlight significant effects
    suptitle : str, optional
        Overall title for the figure
    **kwargs : dict
        Additional arguments passed to matplotlib

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    axes : np.ndarray
        Array of axes objects

    Examples
    --------
    >>> # Compare multiple treatments
    >>> results = analyzer.compare([control, t1, t2, t3])
    >>> fig, axes = plot_multiple_quantile_effects(results)
    >>> plt.show()
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Visualization requires matplotlib. Install with: pip install matplotlib"
        )

    n_results = len(results)
    nrows = (n_results + ncols - 1) // ncols

    if figsize is None:
        figsize = (6 * ncols, 5 * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)

    # Flatten axes for easier iteration
    if n_results == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    # Plot each result
    for i, result in enumerate(results):
        plot_quantile_effects(
            result,
            show_ci=show_ci,
            highlight_significant=highlight_significant,
            ax=axes[i]
        )

    # Hide extra subplots
    for i in range(n_results, len(axes)):
        axes[i].axis('off')

    # Overall title
    if suptitle:
        fig.suptitle(suptitle, fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()

    return fig, axes
