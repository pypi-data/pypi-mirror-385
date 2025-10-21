"""
Utility functions for TicTac.
"""


def convert_color(color: str) -> str:
    """
    Convert a color to TikZ format.

    Converts hex colors (#RRGGBB) to TikZ color definitions.
    Named colors are passed through unchanged.

    Parameters
    ----------
    color : str
        Color specification

    Returns
    -------
    str
        TikZ-compatible color
    """
    if not color or not color.startswith("#"):
        return color

    h = color.lstrip("#")
    try:
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        return f"color_r{r}g{g}b{b}"
    except (ValueError, IndexError):
        return color
