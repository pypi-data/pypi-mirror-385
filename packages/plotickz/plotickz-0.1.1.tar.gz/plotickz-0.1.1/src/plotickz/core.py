"""
Core classes for Plotickz.
"""

import numpy as np
import math
import re
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List


# --- Basic Components ---


class Marker:
    """Encapsulates the logic for drawing a single marker in TikZ."""

    def __init__(
        self, style, size, face_color, edge_color=None, edge_width=1.0, alpha=1.0
    ):
        self.style = style
        self.size = size
        self.face_color = face_color
        self.edge_color = edge_color or face_color
        self.edge_width = edge_width
        self.alpha = alpha

    def get_render_opts(self) -> str:
        """Generates the TikZ options string for this marker."""
        fill_opts = f"fill={self.face_color}, fill opacity={self.alpha:.2f}"
        draw_opts = f"draw={self.edge_color}, draw opacity={self.alpha:.2f}"
        line_width_opt = f", line width={self.edge_width}pt" if self.edge_color else ""
        return f"{fill_opts}, {draw_opts}{line_width_opt}"

    def render_tikz(self, tx: float, ty: float) -> str:
        """Returns the TikZ command to draw the marker at a given coordinate."""
        opts = self.get_render_opts()
        if self.style == "o":
            return f"\\filldraw[{opts}] ({tx:.3f},{ty:.3f}) circle ({self.size}pt);"
        elif self.style == "s":
            s = self.size * 1.5
            return f"\\filldraw[{opts}] ({tx - s:.3f},{ty - s:.3f}) rectangle ({tx + s:.3f},{ty + s:.3f});"
        elif self.style == "^":
            s = self.size * 1.5
            return f"\\filldraw[{opts}] ({tx:.3f},{ty + s:.3f}) -- ({tx - s:.3f},{ty - s/2:.3f}) -- ({tx + s:.3f},{ty - s/2:.3f}) -- cycle;"
        return ""


# --- Coordinate Transformation ---


class CoordinateTransformer:
    def __init__(self, xlim, ylim, xscale, yscale, width, height):
        self.xlim, self.ylim, self.xscale, self.yscale, self.width, self.height = (
            xlim,
            ylim,
            xscale,
            yscale,
            width,
            height,
        )
        if self.xscale == "log":
            self.log_xmin, self.log_xrange = math.log10(self.xlim[0]), math.log10(
                self.xlim[1]
            ) - math.log10(self.xlim[0])
        if self.yscale == "log":
            self.log_ymin, self.log_yrange = math.log10(self.ylim[0]), math.log10(
                self.ylim[1]
            ) - math.log10(self.ylim[0])

    def is_valid(self, x, y):
        return (self.xscale != "log" or x > 0) and (self.yscale != "log" or y > 0)

    def transform_x(self, x):
        return (
            (math.log10(x) - self.log_xmin) / self.log_xrange * self.width
            if self.xscale == "log"
            else (x - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * self.width
        )

    def transform_y(self, y):
        return (
            (math.log10(y) - self.log_ymin) / self.log_yrange * self.height
            if self.yscale == "log"
            else (y - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * self.height
        )


# --- Artist Classes ---


class Artist(ABC):
    """Abstract Base Class for any object that can be drawn on an Axes."""

    def __init__(self, label=None):
        self.label = label

    @abstractmethod
    def get_data_limits(self) -> List[Tuple[float, float]]:
        """Return the data points to be used for calculating axis limits."""
        pass

    @abstractmethod
    def render_tikz(self, transformer, axes) -> str:
        """Render the artist into a TikZ string."""
        pass

    def get_colors(self) -> set:
        """Return all colors used by this artist for definition."""
        return set()


class LineArtist(Artist):
    def __init__(
        self,
        x,
        y,
        color,
        linestyle,
        linewidth,
        alpha,
        marker: Optional[Marker],
        label=None,
    ):
        super().__init__(label)
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.color = color
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.alpha = alpha
        self.marker = marker

    def get_data_limits(self) -> List[Tuple[float, float]]:
        return list(zip(self.x, self.y))

    def get_colors(self) -> set:
        colors = {self.color}
        if self.marker:
            colors.add(self.marker.face_color)
            colors.add(self.marker.edge_color)
        return colors

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        valid_coords = [
            (transformer.transform_x(xi), transformer.transform_y(yi))
            for xi, yi in zip(self.x, self.y)
            if transformer.is_valid(xi, yi)
        ]
        if not valid_coords:
            return ""
        if self.linestyle != "none" and len(valid_coords) > 1:
            line_opts = [self.color, f"opacity={self.alpha:.2f}"]
            if self.linestyle == "dashed":
                line_opts.append("dashed")
            elif self.linestyle == "dotted":
                line_opts.append("dotted")
            elif self.linestyle == "dashdot":
                line_opts.append("dash dot")
            if self.linewidth < 1:
                line_opts.append("thin")
            elif self.linewidth > 2:
                line_opts.append("very thick")
            elif self.linewidth > 1:
                line_opts.append("thick")
            path = " -- ".join([f"({c[0]:.3f},{c[1]:.3f})" for c in valid_coords])
            tikz_code.append(f"\\draw[{', '.join(line_opts)}] {path};")
        if self.marker:
            for tx, ty in valid_coords:
                tikz_code.append(f"  {self.marker.render_tikz(tx, ty)}")
        return "\n".join(tikz_code)


class ScatterArtist(Artist):
    def __init__(self, x, y, marker: Marker, label=None):
        super().__init__(label)
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.marker = marker

    def get_data_limits(self) -> List[Tuple[float, float]]:
        return list(zip(self.x, self.y))

    def get_colors(self) -> set:
        return {self.marker.face_color, self.marker.edge_color}

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        for xi, yi in zip(self.x, self.y):
            if not transformer.is_valid(xi, yi):
                continue
            tx, ty = transformer.transform_x(xi), transformer.transform_y(yi)
            tikz_code.append(f"  {self.marker.render_tikz(tx, ty)}")
        return "\n".join(tikz_code)


class PersistenceArtist(ScatterArtist):
    def get_data_limits(self) -> List[Tuple[float, float]]:
        return [
            (xi, yi if yi != float("inf") else xi) for xi, yi in zip(self.x, self.y)
        ]

    def render_tikz(self, transformer, axes) -> str:
        if not isinstance(axes, PersistenceDiagramAxes):
            raise TypeError(
                "PersistenceArtist can only be rendered on a PersistenceDiagramAxes."
            )
        tikz_code = []
        inf_y_transformed = transformer.transform_y(axes.infinity_line)
        for xi, yi in zip(self.x, self.y):
            tx = transformer.transform_x(xi)
            ty = (
                transformer.transform_y(yi) if yi != float("inf") else inf_y_transformed
            )
            if tx < 0 or (ty < 0 and yi != float("inf")):
                continue
            tikz_code.append(f"  {self.marker.render_tikz(tx, ty)}")
        return "\n".join(tikz_code)


class NodeArtist(Artist):
    """Artist for drawing graph nodes."""

    def __init__(
        self, pos, node_marker: Marker, labels=None, label_style=None, label=None
    ):
        super().__init__(label)
        self.pos = pos
        self.node_marker = node_marker
        self.labels = labels
        self.label_style = label_style or {"position": "above"}

    def get_data_limits(self) -> List[Tuple[float, float]]:
        return list(self.pos.values())

    def get_colors(self) -> set:
        return {self.node_marker.face_color, self.node_marker.edge_color}

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        for node_id, pos in self.pos.items():
            tx, ty = transformer.transform_x(pos[0]), transformer.transform_y(pos[1])
            tikz_code.append(self.node_marker.render_tikz(tx, ty))
        if self.labels:
            pos_opt = self.label_style["position"]
            for node_id, label_text in self.labels.items():
                if node_id in self.pos:
                    pos = self.pos[node_id]
                    tx, ty = transformer.transform_x(pos[0]), transformer.transform_y(
                        pos[1]
                    )
                    tikz_code.append(
                        f"\\node[{pos_opt}] at ({tx:.3f},{ty:.3f}) {{{label_text}}};"
                    )
        return "\n  ".join(tikz_code)


class EdgeArtist(Artist):
    """Artist for drawing graph edges."""

    def __init__(self, pos, edges, color, width, alpha, label=None):
        super().__init__(label)
        self.pos = pos
        self.edges = edges or []
        self.color = color
        self.width = width
        self.alpha = alpha

    def get_data_limits(self) -> List[Tuple[float, float]]:
        return list(self.pos.values())

    def get_colors(self) -> set:
        return {self.color}

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        if self.edges:
            line_opts = [self.color, f"opacity={self.alpha}"]
            width = self.width
            if width < 1:
                line_opts.append("thin")
            elif width > 2:
                line_opts.append("very thick")
            elif width > 1:
                line_opts.append("thick")
            opts = ", ".join(line_opts)
            for edge in self.edges:
                if len(edge) == 2:
                    u, v = edge
                    if u in self.pos and v in self.pos:
                        p1, p2 = self.pos[u], self.pos[v]
                        tp1 = (
                            transformer.transform_x(p1[0]),
                            transformer.transform_y(p1[1]),
                        )
                        tp2 = (
                            transformer.transform_x(p2[0]),
                            transformer.transform_y(p2[1]),
                        )
                        tikz_code.append(
                            f"\\draw[{opts}] ({tp1[0]:.3f},{tp1[1]:.3f}) -- ({tp2[0]:.3f},{tp2[1]:.3f});"
                        )
        return "\n  ".join(tikz_code)


class TriangleArtist(Artist):
    """An artist for drawing filled triangles."""

    def __init__(self, pos, triangles, color, alpha=0.2, label=None):
        super().__init__(label)
        self.pos = pos
        self.triangles = triangles or []
        self.color = color
        self.alpha = alpha

    def get_data_limits(self) -> List[Tuple[float, float]]:
        return list(self.pos.values())

    def get_colors(self) -> set:
        return {self.color}

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        if self.triangles:
            opts = f"fill={self.color}, opacity={self.alpha}, draw=none"
            for tri in self.triangles:
                if len(tri) != 3:
                    continue
                p1, p2, p3 = self.pos[tri[0]], self.pos[tri[1]], self.pos[tri[2]]
                tp1 = (transformer.transform_x(p1[0]), transformer.transform_y(p1[1]))
                tp2 = (transformer.transform_x(p2[0]), transformer.transform_y(p2[1]))
                tp3 = (transformer.transform_x(p3[0]), transformer.transform_y(p3[1]))
                tikz_code.append(
                    f"\\fill[{opts}] ({tp1[0]:.3f},{tp1[1]:.3f}) -- ({tp2[0]:.3f},{tp2[1]:.3f}) -- ({tp3[0]:.3f},{tp3[1]:.3f}) -- cycle;"
                )
        return "\n  ".join(tikz_code)


class CoverArtist(Artist):
    """Artist for drawing covers (circles) with scoping for non-intersection within sets."""

    def __init__(self, pos, radius, sets, color, alpha=0.3, label=None):
        super().__init__(label)
        self.pos = pos
        self.radius = radius
        self.sets = sets
        self.color = color
        self.alpha = alpha

    def get_data_limits(self) -> List[Tuple[float, float]]:
        limits = []
        for node_id, node_pos in self.pos.items():
            limits.append((node_pos[0] - self.radius, node_pos[1] - self.radius))
            limits.append((node_pos[0] + self.radius, node_pos[1] + self.radius))
        return limits

    def get_colors(self) -> set:
        return {self.color}

    def render_tikz(self, transformer, axes) -> str:
        tikz_code = []
        for i, node_set in enumerate(self.sets):
            if not node_set:
                continue
            circles = []
            for node_id in node_set:
                if node_id in self.pos:
                    node_pos = self.pos[node_id]
                    tx = transformer.transform_x(node_pos[0])
                    ty = transformer.transform_y(node_pos[1])
                    tr = transformer.transform_x(
                        node_pos[0] + self.radius
                    ) - transformer.transform_x(node_pos[0])
                    circles.append(f"({tx:.3f},{ty:.3f}) circle ({tr:.3f})")
            if circles:
                tikz_code.append(f"% Cover set {i+1}: {node_set}")
                tikz_code.append("\\begin{scope}")
                tikz_code.append(f"  \\fill[{self.color}, opacity={self.alpha}]")
                for circle in circles:
                    tikz_code.append(f"    {circle}")
                tikz_code[-1] += ";"
                tikz_code.append("\\end{scope}")
        return "\n".join(tikz_code)


# --- Axes Classes ---


class Axes:
    def __init__(self, figure):
        self.figure = figure
        self.artists = []
        self.xlabel = None
        self.ylabel = None
        self.grid = False
        self.xlim = None
        self.ylim = None
        self.xticks = None
        self.yticks = None
        self.xscale = "linear"
        self.yscale = "linear"
        self.x_minor_ticks = []
        self.y_minor_ticks = []
        self.frame_on = True
        self.legend_loc = None
        self.legend_visible = True

    def add_artist(self, artist: Artist):
        self.artists.append(artist)

    def compute_limits(self):
        all_points = [p for artist in self.artists for p in artist.get_data_limits()]
        if not all_points:
            self.xlim = self.xlim or ((0.1, 10) if self.xscale == "log" else (0, 10))
            self.ylim = self.ylim or ((0.1, 10) if self.yscale == "log" else (0, 10))
            return
        x_vals = [p[0] for p in all_points if self.xscale != "log" or p[0] > 0]
        y_vals = [p[1] for p in all_points if self.yscale != "log" or p[1] > 0]
        if not x_vals:
            x_vals = [0.1, 10]
        if not y_vals:
            y_vals = [0.1, 10]
        if self.xlim is None:
            self.xlim = (
                (
                    10 ** np.floor(np.log10(min(x_vals))),
                    10 ** np.ceil(np.log10(max(x_vals))),
                )
                if self.xscale == "log"
                else (
                    min(x_vals) - 0.1 * (max(x_vals) - min(x_vals)),
                    max(x_vals) + 0.1 * (max(x_vals) - min(x_vals)),
                )
            )
        if self.ylim is None:
            self.ylim = (
                (
                    10 ** np.floor(np.log10(min(y_vals))),
                    10 ** np.ceil(np.log10(max(y_vals))),
                )
                if self.yscale == "log"
                else (
                    min(y_vals) - 0.1 * (max(y_vals) - min(y_vals)),
                    max(y_vals) + 0.1 * (max(y_vals) - min(y_vals)),
                )
            )

    def generate_ticks(self):
        def nice_linear_ticks(vmin, vmax, max_ticks=7):
            vrange = vmax - vmin
            if vrange <= 0:
                return [vmin] if vrange == 0 else []
            raw_step = vrange / (max_ticks - 1)
            magnitude = 10 ** math.floor(math.log10(raw_step))
            step = magnitude * next(
                (s for s in [1, 2, 2.5, 5, 10] if magnitude * s >= raw_step), 10
            )
            start = math.floor(vmin / step) * step
            return [v for v in np.arange(start, vmax * 1.0001, step) if v >= vmin]

        def nice_log_ticks(vmin, vmax):
            major_ticks, minor_ticks = [], []
            min_decade, max_decade = math.floor(
                math.log10(max(vmin, 1e-10))
            ), math.ceil(math.log10(vmax))
            for exp in range(min_decade, max_decade + 1):
                if vmin <= 10**exp <= vmax:
                    major_ticks.append(10**exp)
            if not major_ticks:
                if vmin == 10 ** math.floor(math.log10(vmin)):
                    major_ticks.append(vmin)
                if vmax == 10 ** math.ceil(math.log10(vmax)):
                    major_ticks.append(vmax)
            if max_decade - min_decade <= 6:
                for exp in range(min_decade - 1, max_decade + 1):
                    for mult in range(2, 10):
                        if vmin <= mult * (10**exp) <= vmax:
                            minor_ticks.append(mult * (10**exp))
            return sorted(major_ticks), sorted(minor_ticks)

        if self.xticks is None:
            if self.xscale == "log":
                self.xticks, self.x_minor_ticks = nice_log_ticks(
                    self.xlim[0], self.xlim[1]
                )
            else:
                self.xticks = nice_linear_ticks(self.xlim[0], self.xlim[1])
        if self.yticks is None:
            if self.yscale == "log":
                self.yticks, self.y_minor_ticks = nice_log_ticks(
                    self.ylim[0], self.ylim[1]
                )
            else:
                self.yticks = nice_linear_ticks(self.ylim[0], self.ylim[1])

    def format_number(self, x, scale_type="linear"):
        if x == 0:
            return "0"
        if (
            scale_type == "log"
            and x > 0
            and abs(math.log10(x) - round(math.log10(x))) < 1e-10
        ):
            return f"$10^{{{int(round(math.log10(x)))}}}$"
        if abs(x) >= 10000 or (0 < abs(x) < 0.001):
            return f"{x:.1e}"
        if x == int(x):
            return str(int(x))
        return f"{x:.2f}".rstrip("0").rstrip(".")

    def render_frame_and_grid(self, transformer) -> List[str]:
        code = ["% Axes and Grid"]
        if self.frame_on:
            code.append(f"\\draw[->, thick] (-0.2,0) -- ({self.figure.width + 0.5},0);")
            code.append(
                f"\\draw[->, thick] (0,-0.2) -- (0,{self.figure.height + 0.5});"
            )
        if self.grid:
            for xt in self.xticks:
                x_pos = transformer.transform_x(xt)
                if 0 <= x_pos <= self.figure.width:
                    code.append(
                        f"\\draw[gray!30, very thin] ({x_pos:.3f},0) -- ({x_pos:.3f},{self.figure.height});"
                    )
            for yt in self.yticks:
                y_pos = transformer.transform_y(yt)
                if 0 <= y_pos <= self.figure.height:
                    code.append(
                        f"\\draw[gray!30, very thin] (0,{y_pos:.3f}) -- ({self.figure.width},{y_pos:.3f});"
                    )
            for xt in self.x_minor_ticks:
                x_pos = transformer.transform_x(xt)
                if 0 <= x_pos <= self.figure.width:
                    code.append(
                        f"\\draw[gray!15, ultra thin] ({x_pos:.3f},0) -- ({x_pos:.3f},{self.figure.height});"
                    )
            for yt in self.y_minor_ticks:
                y_pos = transformer.transform_y(yt)
                if 0 <= y_pos <= self.figure.height:
                    code.append(
                        f"\\draw[gray!15, ultra thin] (0,{y_pos:.3f}) -- ({self.figure.width},{y_pos:.3f});"
                    )
        return code

    def render_ticks_and_labels(self, transformer) -> List[str]:
        if not self.frame_on:
            return []
        code = ["% Ticks and Labels"]
        for xt in self.xticks:
            x_pos = transformer.transform_x(xt)
            if 0 <= x_pos <= self.figure.width:
                code.append(f"\\draw[thick] ({x_pos:.3f},-0.1) -- ({x_pos:.3f},0.1);")
                code.append(
                    f"\\node[below] at ({x_pos:.3f},-0.15) {{\\small {self.format_number(xt, self.xscale)}}};"
                )
        for xt in self.x_minor_ticks:
            x_pos = transformer.transform_x(xt)
            if 0 <= x_pos <= self.figure.width:
                code.append(f"\\draw[thin] ({x_pos:.3f},-0.05) -- ({x_pos:.3f},0.05);")
        for yt in self.yticks:
            y_pos = transformer.transform_y(yt)
            if 0 <= y_pos <= self.figure.height:
                code.append(f"\\draw[thick] (-0.1,{y_pos:.3f}) -- (0.1,{y_pos:.3f});")
                code.append(
                    f"\\node[left] at (-0.15,{y_pos:.3f}) {{\\small {self.format_number(yt, self.yscale)}}};"
                )
        for yt in self.y_minor_ticks:
            y_pos = transformer.transform_y(yt)
            if 0 <= y_pos <= self.figure.height:
                code.append(f"\\draw[thin] (-0.05,{y_pos:.3f}) -- (0.05,{y_pos:.3f});")
        if self.xlabel:
            code.append(
                f"\\node[below] at ({self.figure.width/2:.3f},-0.8) {{{self.xlabel}}};"
            )
        if self.ylabel:
            code.append(
                f"\\node[rotate=90, above] at (-0.8,{self.figure.height/2:.3f}) {{{self.ylabel}}};"
            )
        return code

    def render_legend(self, transformer) -> List[str]:
        if not self.legend_visible:
            return []
        legend_items = [artist for artist in self.artists if artist.label]
        if not legend_items:
            return []
        legend_x, legend_y = self._calculate_legend_position()
        code = ["% Legend"]
        for i, artist in enumerate(legend_items):
            y_offset = legend_y - i * 0.5
            if isinstance(artist, LineArtist):
                ls = [artist.color]
                if artist.linestyle == "dashed":
                    ls.append("dashed")
                elif artist.linestyle == "dotted":
                    ls.append("dotted")
                code.append(
                    f"\\draw[{', '.join(ls)}] ({legend_x:.3f},{y_offset:.3f}) -- ({legend_x + 0.5:.3f},{y_offset:.3f});"
                )
                if artist.marker:
                    code.append(artist.marker.render_tikz(legend_x + 0.25, y_offset))
            elif isinstance(artist, (ScatterArtist, PersistenceArtist)):
                code.append(artist.marker.render_tikz(legend_x + 0.25, y_offset))
            elif isinstance(artist, NodeArtist):
                code.append(artist.node_marker.render_tikz(legend_x + 0.25, y_offset))
            elif isinstance(artist, EdgeArtist):
                ls = [artist.color, f"opacity={artist.alpha}"]
                if artist.width < 1:
                    ls.append("thin")
                elif artist.width > 2:
                    ls.append("very thick")
                elif artist.width > 1:
                    ls.append("thick")
                code.append(
                    f"\\draw[{', '.join(ls)}] ({legend_x:.3f},{y_offset:.3f}) -- ({legend_x + 0.5:.3f},{y_offset:.3f});"
                )
            elif isinstance(artist, TriangleArtist):
                code.append(
                    f"\\fill[{artist.color}, opacity={artist.alpha}] ({legend_x + 0.1:.3f},{y_offset - 0.15:.3f}) rectangle ({legend_x + 0.4:.3f},{y_offset + 0.15:.3f});"
                )
            elif isinstance(artist, CoverArtist):
                code.append(
                    f"\\fill[{artist.color}, opacity={artist.alpha}] ({legend_x + 0.25:.3f},{y_offset:.3f}) circle (0.15);"
                )
            code.append(
                f"\\node[right] at ({legend_x + 0.6:.3f},{y_offset:.3f}) {{\\small {artist.label}}};"
            )
        return code

    def _calculate_legend_position(self) -> Tuple[float, float]:
        """Calculate the legend position based on the location string."""
        if self.legend_loc is None:
            return self.figure.width * 0.7, self.figure.height * 0.9
        margin_x = 0.5
        margin_y = 0.5
        loc = self.legend_loc.lower()
        if loc == "upper left":
            return margin_x, self.figure.height - margin_y
        elif loc == "upper right":
            return self.figure.width - 2.0, self.figure.height - margin_y
        elif loc == "lower left":
            return margin_x, 2.0
        elif loc == "lower right":
            return self.figure.width - 2.0, 2.0
        elif loc == "upper center":
            return self.figure.width / 2 - 1.0, self.figure.height - margin_y
        elif loc == "lower center":
            return self.figure.width / 2 - 1.0, 2.0
        elif loc == "center left":
            return margin_x, self.figure.height / 2
        elif loc == "center right":
            return self.figure.width - 2.0, self.figure.height / 2
        elif loc == "center":
            return self.figure.width / 2 - 1.0, self.figure.height / 2
        elif loc == "best":
            return self.figure.width - 2.0, self.figure.height - margin_y
        else:
            return self.figure.width * 0.7, self.figure.height * 0.9

    def render_tikz(self) -> str:
        self.compute_limits()
        self.generate_ticks()
        transformer = CoordinateTransformer(
            self.xlim,
            self.ylim,
            self.xscale,
            self.yscale,
            self.figure.width,
            self.figure.height,
        )
        tikz_parts = []
        tikz_parts.extend(self.render_frame_and_grid(transformer))
        tikz_parts.extend(self.render_ticks_and_labels(transformer))
        tikz_parts.append("% Plot data")
        for artist in self.artists:
            tikz_parts.append(artist.render_tikz(transformer, self))
        tikz_parts.extend(self.render_legend(transformer))
        return "\n  ".join(tikz_parts)


class PersistenceDiagramAxes(Axes):
    """A specialized Axes for persistence diagrams."""

    def __init__(self, figure):
        super().__init__(figure)
        self.axis_offset = 0.0
        self.infinity_line = None
        self.legend_loc = "lower right"
        self.xlabel = "Birth"
        self.ylabel = "Death"

    def compute_limits(self):
        super().compute_limits()
        self.infinity_line = self.ylim[1]

    def render_frame_and_grid(self, transformer) -> List[str]:
        off = self.axis_offset
        max_coord = max(self.figure.width, self.figure.height)
        inf_y = transformer.transform_y(self.infinity_line)
        code = ["% Persistence Diagram Frame"]
        code.append(
            f"\\fill[gray!20, opacity=0.5] (-{off:.2f},-{off:.2f}) -- ({max_coord},-{off:.2f}) -- ({max_coord},{max_coord}) -- (-{off:.2f},-{off:.2f}) -- cycle;"
        )
        code.append(
            f"\\draw[->, thick] (-{off:.2f},-{off:.2f}) -- ({self.figure.width + 0.5},-{off:.2f});"
        )
        code.append(
            f"\\draw[->, thick] (-{off:.2f},-{off:.2f}) -- (-{off:.2f},{self.figure.height + 0.5});"
        )
        code.append(
            f"\\draw[dashed, gray, thick] (-{off:.2f},-{off:.2f}) -- ({max_coord},{max_coord});"
        )
        code.append(
            f"\\draw[dashed, black] (-{off:.2f},{inf_y:.3f}) node[left, black] {{$\\infty$}} -- ({self.figure.width},{inf_y:.3f});"
        )
        return code

    def render_ticks_and_labels(self, transformer) -> List[str]:
        code = ["% Ticks and Labels (Persistence)"]
        axis_y, axis_x = -self.axis_offset, -self.axis_offset
        for xt in self.xticks:
            if xt >= self.xlim[1]:
                continue
            x_pos = transformer.transform_x(xt)
            if 0 <= x_pos <= self.figure.width:
                code.append(
                    f"\\draw[thick] ({x_pos:.3f},{axis_y-0.1:.3f}) -- ({x_pos:.3f},{axis_y+0.1:.3f});"
                )
                code.append(
                    f"\\node[below] at ({x_pos:.3f},{axis_y-0.15:.3f}) {{\\small {self.format_number(xt)}}};"
                )
        for yt in self.yticks:
            if yt >= self.ylim[1]:
                continue
            y_pos = transformer.transform_y(yt)
            if 0 <= y_pos <= self.figure.height:
                code.append(
                    f"\\draw[thick] ({axis_x-0.1:.3f},{y_pos:.3f}) -- ({axis_x+0.1:.3f},{y_pos:.3f});"
                )
                code.append(
                    f"\\node[left] at ({axis_x-0.15:.3f},{y_pos:.3f}) {{\\small {self.format_number(yt)}}};"
                )
        if self.xlabel:
            code.append(
                f"\\node[below] at ({self.figure.width/2:.3f},-0.8) {{{self.xlabel}}};"
            )
        if self.ylabel:
            code.append(
                f"\\node[rotate=90, above] at (-0.8,{self.figure.height/2:.3f}) {{{self.ylabel}}};"
            )
        return code


# --- Figure Class ---


class TikZFigure:
    def __init__(self, width=8, height=6):
        self.width, self.height, self.title = width, height, None
        self.axes = [Axes(self)]

    def to_tikz(self) -> str:
        color_defs = {
            c
            for ax in self.axes
            for artist in ax.artists
            for c in artist.get_colors()
            if c and c.startswith("color_")
        }
        tikz_code = ["\\begin{tikzpicture}"]
        if color_defs:
            tikz_code.append("  % Color definitions")
            for color_id in sorted(color_defs):
                match = re.match(r"color_r(\d+)g(\d+)b(\d+)", color_id)
                if match:
                    r, g, b = map(int, match.groups())
                    tikz_code.append(
                        f"  \\definecolor{{{color_id}}}{{rgb}}{{{r/255:.3f},{g/255:.3f},{b/255:.3f}}}"
                    )
        tikz_code.append(self.axes[0].render_tikz())
        if self.title:
            tikz_code.append(
                f"  \\node[above] at ({self.width/2:.3f},{self.height + 0.3}) {{\\large \\textbf{{{self.title}}}}}; "
            )
        tikz_code.append("\\end{tikzpicture}")
        return "\n".join(tikz_code)
