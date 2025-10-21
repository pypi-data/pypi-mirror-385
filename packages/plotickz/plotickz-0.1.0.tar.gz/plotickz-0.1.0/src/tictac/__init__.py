"""
Plotickz - A matplotlib-like API for generating pure TikZ diagrams.
"""

__version__ = "0.1.0"

from .api import (
    # Figure management
    figure,
    gcf,
    gca,
    # Basic plotting
    plot,
    scatter,
    # Axes configuration
    xlabel,
    ylabel,
    title,
    xlim,
    ylim,
    xscale,
    yscale,
    grid,
    legend,
    axis,
    # Specialized plots
    persistence_diagram,
    draw_nodes,
    draw_edges,
    draw_triangles,
    draw_cover,
    # Output
    show,
    savefig,
)

__all__ = [
    "__version__",
    "figure",
    "gcf",
    "gca",
    "plot",
    "scatter",
    "xlabel",
    "ylabel",
    "title",
    "xlim",
    "ylim",
    "xscale",
    "yscale",
    "grid",
    "legend",
    "axis",
    "persistence_diagram",
    "draw_nodes",
    "draw_edges",
    "draw_triangles",
    "draw_cover",
    "show",
    "savefig",
]
