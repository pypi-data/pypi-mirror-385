"""
Public API functions for Plotickz.
"""

import numpy as np
from typing import Optional, Tuple

from .core import (
    TikZFigure,
    Axes,
    PersistenceDiagramAxes,
    LineArtist,
    ScatterArtist,
    PersistenceArtist,
    NodeArtist,
    EdgeArtist,
    TriangleArtist,
    CoverArtist,
    Marker,
)
from .utils import convert_color

# Global state
_current_figure: Optional[TikZFigure] = None


def gcf() -> TikZFigure:
    """Get the current figure."""
    global _current_figure
    if _current_figure is None:
        _current_figure = TikZFigure()
    return _current_figure


def gca() -> Axes:
    """Get the current axes."""
    return gcf().axes[0]


def figure(figsize: Optional[Tuple[float, float]] = None, **kwargs) -> TikZFigure:
    """
    Create a new figure.

    Parameters
    ----------
    figsize : tuple of float, optional
        Figure size as (width, height). Default is (8, 6).
    """
    global _current_figure
    w, h = figsize or (8, 6)
    _current_figure = TikZFigure(w, h)
    return _current_figure


def plot(x, y=None, **kwargs):
    """
    Plot lines and/or markers.

    Parameters
    ----------
    x, y : array-like
        Data points
    color : str
        Line color
    linestyle : str
        'solid', 'dashed', 'dotted', 'dashdot'
    linewidth : float
        Line width
    marker : str
        Marker style ('o', 's', '^')
    markersize : float
        Marker size
    alpha : float
        Transparency
    label : str
        Legend label
    """
    ax = gca()
    if y is None:
        y = np.asarray(x).flatten()
        x = np.arange(len(y))
    else:
        x = np.asarray(x).flatten()
        y = np.asarray(y).flatten()

    color = convert_color(kwargs.get("color", "#1f77b4"))
    marker = None
    if kwargs.get("marker"):
        marker = Marker(
            kwargs.get("marker"),
            kwargs.get("markersize", 6) / 4,
            color,
            alpha=kwargs.get("alpha", 1.0),
        )

    ax.add_artist(
        LineArtist(
            x,
            y,
            color,
            kwargs.get("linestyle", "solid"),
            kwargs.get("linewidth", 1.0),
            kwargs.get("alpha", 1.0),
            marker,
            kwargs.get("label"),
        )
    )


def scatter(x, y, **kwargs):
    """
    Create a scatter plot.

    Parameters
    ----------
    x, y : array-like
        Data points
    s : float
        Marker size
    color : str
        Marker color
    marker : str
        Marker style
    alpha : float
        Transparency
    edgecolor : str
        Edge color
    edgewidth : float
        Edge width
    label : str
        Legend label
    """
    ax = gca()
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()

    color = convert_color(kwargs.get("color", "#1f77b4"))
    edgecolor = convert_color(kwargs.get("edgecolor"))
    if not edgecolor:
        edgecolor = color

    s = kwargs.get("s", 20)
    mark_size = np.sqrt(s) / 4 if np.isscalar(s) else 2

    marker = Marker(
        kwargs.get("marker", "o"),
        mark_size,
        color,
        edgecolor,
        kwargs.get("edgewidth", 1.0),
        kwargs.get("alpha", 1.0),
    )

    ax.add_artist(ScatterArtist(x, y, marker, kwargs.get("label")))


def persistence_diagram(birth, death, **kwargs):
    """
    Create a persistence diagram.

    Parameters
    ----------
    birth : array-like
        Birth times
    death : array-like
        Death times (use float('inf') for infinite features)
    color : str
        Marker color
    alpha : float
        Transparency
    label : str
        Legend label
    """
    fig = gcf()
    ax = fig.axes[0]
    if not isinstance(ax, PersistenceDiagramAxes):
        ax = PersistenceDiagramAxes(fig)
        fig.axes[0] = ax

    color = convert_color(kwargs.get("color", "#1f77b4"))
    marker = Marker("o", 2, color, alpha=kwargs.get("alpha", 1.0))
    ax.add_artist(PersistenceArtist(birth, death, marker, kwargs.get("label")))


def draw_nodes(
    pos: dict,
    size: float = 30,
    color: str = "black",
    marker: str = "o",
    alpha: float = 1.0,
    labels: Optional[dict] = None,
    label_pos: str = "above",
    **kwargs,
):
    """
    Draw graph nodes.

    Parameters
    ----------
    pos : dict
        Node positions {node_id: (x, y)}
    size : float
        Node size
    color : str
        Node color
    marker : str
        Marker style
    alpha : float
        Transparency
    labels : dict
        Node labels
    label_pos : str
        Label position
    """
    ax = gca()
    node_marker = Marker(
        marker,
        np.sqrt(size) / 3,
        convert_color(color),
        alpha=alpha,
    )
    label_style = {"position": label_pos}
    ax.add_artist(
        NodeArtist(pos, node_marker, labels, label_style, kwargs.get("label"))
    )


def draw_edges(
    pos: dict,
    edges: list,
    width: float = 2.0,
    color: str = "black",
    alpha: float = 0.8,
    **kwargs,
):
    """
    Draw graph edges.

    Parameters
    ----------
    pos : dict
        Node positions
    edges : list
        Edge list [(node1, node2), ...]
    width : float
        Edge width
    color : str
        Edge color
    alpha : float
        Transparency
    """
    ax = gca()
    ax.add_artist(
        EdgeArtist(pos, edges, convert_color(color), width, alpha, kwargs.get("label"))
    )


def draw_triangles(
    pos: dict,
    triangles: Optional[list] = None,
    color: str = "#e63947",
    alpha: float = 0.2,
    **kwargs,
):
    """
    Draw filled triangles.

    Parameters
    ----------
    pos : dict
        Node positions
    triangles : list
        Triangle list [(node1, node2, node3), ...]
    color : str
        Fill color
    alpha : float
        Transparency
    """
    ax = gca()
    ax.add_artist(
        TriangleArtist(pos, triangles, convert_color(color), alpha, kwargs.get("label"))
    )


def draw_cover(
    pos: dict,
    radius: float,
    sets: list,
    color: str = "#14655d",
    alpha: float = 0.3,
    **kwargs,
):
    """
    Draw covers around node sets.

    Parameters
    ----------
    pos : dict
        Node positions
    radius : float
        Cover radius
    sets : list
        List of node sets [[nodes...], ...]
    color : str
        Fill color
    alpha : float
        Transparency
    """
    ax = gca()
    ax.add_artist(
        CoverArtist(pos, radius, sets, convert_color(color), alpha, kwargs.get("label"))
    )


def xlabel(label: str):
    """Set x-axis label."""
    gca().xlabel = label


def ylabel(label: str):
    """Set y-axis label."""
    gca().ylabel = label


def title(title_text: str):
    """Set figure title."""
    gcf().title = title_text


def grid(visible: bool = True):
    """Show/hide grid."""
    gca().grid = visible


def xlim(xmin: float, xmax: float):
    """Set x-axis limits."""
    gca().xlim = (xmin, xmax)


def ylim(ymin: float, ymax: float):
    """Set y-axis limits."""
    gca().ylim = (ymin, ymax)


def xscale(scale: str):
    """Set x-axis scale ('linear' or 'log')."""
    gca().xscale = scale


def yscale(scale: str):
    """Set y-axis scale ('linear' or 'log')."""
    gca().yscale = scale


def axis(state: str):
    """Turn axes on/off."""
    ax = gca()
    if state == "on":
        ax.frame_on = True
    elif state == "off":
        ax.frame_on = False
    else:
        raise ValueError("State must be 'on' or 'off'")


def legend(loc=None, visible=True):
    """
    Configure legend.

    Parameters
    ----------
    loc : str
        Location: 'upper left', 'upper right', 'lower left', 'lower right',
        'upper center', 'lower center', 'center left', 'center right',
        'center', 'best'
    visible : bool
        Show/hide legend
    """
    ax = gca()
    ax.legend_loc = loc
    ax.legend_visible = visible


def show() -> str:
    """Generate and return TikZ code."""
    return gcf().to_tikz()


def savefig(filename: str):
    """
    Save TikZ code to file.

    Parameters
    ----------
    filename : str
        Output filename. If ends with '.tex', creates complete LaTeX document.
    """
    code = gcf().to_tikz()
    with open(filename, "w") as f:
        if filename.endswith(".tex"):
            f.write("\\documentclass{standalone}\n")
            f.write("\\usepackage{tikz}\n")
            f.write("\\usepackage{xcolor}\n")
            f.write("\\begin{document}\n")
            f.write(code)
            f.write("\n\\end{document}\n")
        else:
            f.write(code)
    print(f"Saved to {filename}")
