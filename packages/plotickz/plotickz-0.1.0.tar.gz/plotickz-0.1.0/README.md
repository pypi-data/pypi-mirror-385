consider renaming to matplotickz
Consider using [jupyter-tickz](https://jupyter-tikz.readthedocs.io/stable/#basic-usage)

# Plotickz

A Python library that provides a matplotlib-like API for generating pure TikZ diagrams. Create publication-ready LaTeX figures with familiar matplotlib syntax.

## Features

- **Familiar API**: Uses matplotlib-like functions (`plot()`, `scatter()`, `xlabel()`, etc.)
- **Pure TikZ Output**: Generates clean TikZ code without external dependencies
- **Multiple Plot Types**: Line plots, scatter plots, log scales, persistence diagrams, and graph visualizations
- **Customizable**: Full control over colors, markers, line styles, and more
- **LaTeX-Ready**: Output can be directly included in LaTeX documents

## Installation

```bash
pip install plotickz
```

Or install from source:

```bash
git clone https://github.com/yourusername/plotickz.git
cd plotickz
pip install -e .
```

## Quick Start

```python
import plotickz as plz
import numpy as np

# Create data
x = np.linspace(0, 2*np.pi, 50)
y = np.sin(x)

# Create plot
plz.figure(figsize=(10, 6))
plz.plot(x, y, color="#2E86AB", linewidth=2, label="sin(x)")
plz.xlabel("x (radians)")
plz.ylabel("y")
plz.title("Sine Wave")
plz.grid(True)
plz.legend()

# Generate TikZ code
tikz_code = plz.show()
print(tikz_code)

# Or save to file
plz.savefig("sine_wave.tex")
```

## API Reference

### Figure Management

- `figure(figsize=(width, height))` - Create a new figure
- `gcf()` - Get current figure
- `gca()` - Get current axes

### Plotting Functions

- `plot(x, y, **kwargs)` - Create a line plot

  - `color`: Line color (hex or named)
  - `linestyle`: 'solid', 'dashed', 'dotted', 'dashdot'
  - `linewidth`: Line width in points
  - `marker`: Marker style ('o', 's', '^')
  - `markersize`: Size of markers
  - `alpha`: Transparency (0-1)
  - `label`: Legend label

- `scatter(x, y, **kwargs)` - Create a scatter plot
  - `s`: Marker size
  - `color`: Marker color
  - `marker`: Marker style
  - `alpha`: Transparency
  - `edgecolor`: Marker edge color
  - `edgewidth`: Marker edge width
  - `label`: Legend label

### Axes Configuration

- `xlabel(label)` - Set x-axis label
- `ylabel(label)` - Set y-axis label
- `title(title)` - Set plot title
- `xlim(xmin, xmax)` - Set x-axis limits
- `ylim(ymin, ymax)` - Set y-axis limits
- `xscale(scale)` - Set x-axis scale ('linear' or 'log')
- `yscale(scale)` - Set y-axis scale ('linear' or 'log')
- `grid(visible)` - Show/hide grid
- `legend(loc, visible)` - Configure legend
- `axis(state)` - Turn axes on/off

### Specialized Plots

- `persistence_diagram(birth, death, **kwargs)` - Create persistence diagrams
- `draw_nodes(pos, **kwargs)` - Draw graph nodes
- `draw_edges(pos, edges, **kwargs)` - Draw graph edges
- `draw_triangles(pos, triangles, **kwargs)` - Draw filled triangles
- `draw_cover(pos, radius, sets, **kwargs)` - Draw covers around node sets

### Output

- `show()` - Return TikZ code as string
- `savefig(filename)` - Save TikZ code to file
  - `.tex` files include full LaTeX document
  - Other extensions save raw TikZ code

## Examples

### Basic Line Plot

```python
import plotickz as plz
import numpy as np

x = np.linspace(0, 2 * np.pi, 50)
y1 = np.sin(x)
y2 = np.cos(x)

plz.figure(figsize=(10, 7))
plz.plot(x, y1, color="#2E86AB", linestyle="solid", linewidth=1.5, label="sin(x)")
plz.plot(x, y2, color="#A23B72", linestyle="dashed", linewidth=1.5, label="cos(x)")
plz.xlabel("x (radians)")
plz.ylabel("y")
plz.title("Trigonometric Functions")
plz.grid(True)
plz.xlim(0, 2 * np.pi)
plz.ylim(-1.5, 1.5)
plz.legend("upper right")
print(plz.show())
```

### Scatter Plot

```python
import plotickz as plz
import numpy as np

np.random.seed(42)
x = np.random.randn(30) * 2 + 5
y = 2 * np.random.randn(30) + 3

plz.figure(figsize=(10, 8))
plz.scatter(x, y, s=30, color="#FF5733", marker="o", alpha=0.7, label="Data points")
plz.xlabel("X values")
plz.ylabel("Y values")
plz.title("Scatter Plot Example")
plz.grid(True)
plz.legend()
print(plz.show())
```

### Combined Plot with Scatter and Line

```python
import plotickz as plz
import numpy as np

np.random.seed(123)
x = np.linspace(0, 10, 20)
y_true = 2 * x + 1
y_measured = y_true + np.random.randn(20) * 2

plz.figure(figsize=(10, 7))
plz.scatter(
    x, y_measured, s=50, color="#3498DB", marker="o",
    alpha=0.6, label="Measured", edgecolor="#2C3E50", edgewidth=0.8
)
plz.plot(x, y_true, color="#E74C3C", linestyle="solid", linewidth=2, label="True line")
plz.xlabel("X")
plz.ylabel("Y")
plz.title("Linear Fit with Scatter Data")
plz.grid(True)
plz.legend("lower right")
print(plz.show())
```

### Logarithmic Scale Plot

```python
import plotickz as plz
import numpy as np

training_times = np.array([100, 3700, 800, 1200, 500])
fid_scores = np.array([5, 10, 13, 7, 8])

plz.figure(figsize=(10, 7))
plz.xscale("log")
plz.scatter(training_times, fid_scores, s=100, color="#2E86AB", marker="o", alpha=0.8)

x_trend = np.logspace(2, 3.6, 50)
y_trend = 20 - 3 * np.log10(x_trend)
plz.plot(x_trend, y_trend, color="#E74C3C", linestyle="dashed", linewidth=1.5)

plz.xlabel("Training Time with A100 (log-scale)")
plz.ylabel("FID (J)")
plz.title("Training Efficiency - Log Scale X-axis")
plz.grid(True)
plz.xlim(50, 10000)
plz.ylim(0, 25)
print(plz.show())
```

### Log-Log Plot

```python
import plotickz as plz
import numpy as np

x = np.logspace(0, 4, 50)
y = 1000 * x ** (-0.7)

plz.figure(figsize=(10, 7))
plz.xscale("log")
plz.yscale("log")
plz.plot(x, y, color="#E91E63", linestyle="solid", linewidth=2, label="Power Law")

x_points = np.logspace(0.5, 3.5, 10)
y_points = 1000 * x_points ** (-0.7) * (1 + 0.2 * np.random.randn(10))
plz.scatter(x_points, y_points, s=40, color="#9C27B0", alpha=0.7, label="Data")

plz.xlabel("X (log scale)")
plz.ylabel("Y (log scale)")
plz.title("Power Law Relationship")
plz.grid(True)
plz.legend()
print(plz.show())
```

### Persistence Diagram

```python
import plotickz as plz

plz.figure(figsize=(7, 7))

# H_0 features (connected components)
birth_0 = [0, 1.0, 1.5, 0.8, 2.5]
death_0 = [3.5, float("inf"), 2.8, 2.2, float("inf")]
plz.persistence_diagram(birth_0, death_0, color="#5b8def", label="$H_0$")

# H_1 features (loops)
birth_1 = [1.8, 2.2, 3.0]
death_1 = [3.2, 2.5, 4.2]
plz.persistence_diagram(birth_1, death_1, color="#e3773d", label="$H_1$")

# H_2 features (voids)
birth_2 = [2.8, 3.5]
death_2 = [3.5, 4.0]
plz.persistence_diagram(birth_2, death_2, color="#27a165", label="$H_2$")

plz.title("Persistence Diagram")
plz.xlim(-0.5, 5)
plz.ylim(-0.5, 5)
plz.legend()
print(plz.show())
```

### Graph Visualization with Filled Triangle

```python
import plotickz as plz

plz.figure(figsize=(6, 5))

# Node positions
pos = {
    "A": (0, 0),
    "B": (3, 0),
    "C": (1.5, 2.598),  # Equilateral triangle
    "D": (4.5, 2.598),
}

# Edges
edges = [("A", "B"), ("B", "C"), ("C", "A"), ("B", "D"), ("C", "D")]

# Triangle to fill
triangles = [("A", "B", "C")]

# Draw the graph
plz.draw_triangles(pos, triangles, color="#e63947", alpha=0.2)
plz.draw_edges(pos, edges, width=2, color="#000000")
plz.draw_nodes(
    pos, size=20, color="#000000",
    labels={k: k for k in pos.keys()}, label_pos="above right"
)

plz.title("Graph with Filled Simplex")
plz.axis("off")  # Hide axes for cleaner graph visualization
print(plz.show())
```

### Graph with Covers

```python
import plotickz as plz

plz.figure(figsize=(10, 8))

# Node positions
pos = {
    1: (1, 2),
    2: (2, 2),
    3: (3, 1),
    4: (5, 2),
    5: (6, 2),
    6: (7, 2),
    7: (4, 4),
}

# Edges
edges = [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (4, 6), (7, 2), (7, 5)]

# Define sets for covers - nodes in same set won't have intersecting covers
cover_sets = [[1, 2, 3], [4, 5, 6], [7]]

# Draw covers first (background)
plz.draw_cover(pos, radius=0.7, sets=cover_sets, color="#14655d", alpha=0.3)

# Draw edges
plz.draw_edges(pos, edges, width=1.0, color="black")

# Draw nodes on top
plz.draw_nodes(pos, size=25, color="black", labels={i: str(i) for i in pos.keys()})

plz.title("Graph with Covers (Scoped by Sets)")
plz.axis("off")
plz.xlim(0, 8)
plz.ylim(0, 5)
print(plz.show())
```

## Output Format

The library generates clean TikZ code that can be:

1. **Included directly in LaTeX**:

```latex
\documentclass{article}
\usepackage{tikz}
\begin{document}
% Paste the output from plz.show() here
\end{document}
```

2. **Saved as standalone document**:

```python
plz.savefig("figure.tex")  # Creates compilable LaTeX document
```

3. **Integrated into larger documents**:

```latex
\input{figure.tikz}  # Include raw TikZ code
```

## Requirements

- Python 3.6+
- NumPy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This library provides a matplotlib-compatible interface for generating TikZ diagrams, making it easy to create publication-quality figures for LaTeX documents.
