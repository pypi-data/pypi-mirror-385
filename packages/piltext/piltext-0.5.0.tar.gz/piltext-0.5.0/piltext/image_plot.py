"""
Plot visualization for data representation without matplotlib.

This module provides the ImagePlot class for creating line, bar, and scatter
plot visualizations using only PIL/Pillow. Supports multiple series, custom
styling, axes, grids, and legends.

Examples
--------
Create a simple line plot with y-values only:

>>> from piltext import FontManager, ImagePlot
>>> fm = FontManager()
>>> data = [0, 2, 4, 3, 5]
>>> plot = ImagePlot(data, fm, plot_type='line')
>>> img = plot.render()
>>> img.save("line_plot.png")

Create a line plot with (x, y) tuples:

>>> data = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 5)]
>>> plot = ImagePlot(data, fm, plot_type='line')
>>> img = plot.render()

Create a bar plot with multiple series:

>>> data = {
...     'Series A': [10, 15, 13],
...     'Series B': [8, 12, 18]
... }
>>> plot = ImagePlot(data, fm, plot_type='bar', title='Comparison')
>>> img = plot.render()
"""

from typing import Optional, Union

from PIL import Image

from .font_manager import FontManager
from .image_drawer import ImageDrawer


class ImagePlot:
    """
    Create plot visualizations (line, bar, scatter) without matplotlib.

    ImagePlot creates data visualizations using only PIL/Pillow, supporting
    line plots, bar charts, and scatter plots with customizable styling,
    axes, grids, and legends.

    Parameters
    ----------
    data : list or dict
        Plot data. Can be:
        - List of y-values (x-coordinates auto-generated as 0, 1, 2, ...)
        - List of (x, y) tuples for single series
        - Dict mapping series names to list of y-values or (x, y) tuples
    font_manager : FontManager
        Font manager for text rendering.
    plot_type : str, optional
        Type of plot: 'line', 'bar', or 'scatter'. Default is 'line'.
    width : int, optional
        Width of the output image in pixels. Default is 400.
    height : int, optional
        Height of the output image in pixels. Default is 300.
    bg_color : str, optional
        Background color. Default is 'white'.
    fg_color : str or list, optional
        Foreground color(s) for data series. Can be a single color string or
        list of colors for multiple series. Default is '#4CAF50'.
    grid_color : str, optional
        Grid line color. Default is '#e0e0e0'.
    axis_color : str, optional
        Axis line and tick color. Default is 'black'.
    title : str, optional
        Plot title text. Default is None.
    xlabel : str, optional
        X-axis label text. Default is None.
    ylabel : str, optional
        Y-axis label text. Default is None.
    show_grid : bool, optional
        Whether to show background grid. Default is True.
    show_legend : bool, optional
        Whether to show legend for multiple series. Default is True.
    show_axis : bool, optional
        Whether to show X and Y axes. Default is True.
    line_width : int, optional
        Line width for line plots. Default is 2.
    marker_size : int, optional
        Marker size for scatter plots and line plot markers. Default is 4.
    marker_color : str or list, optional
        Marker color(s) for scatter plots. Can be a single color string or
        list of colors for multiple series. If None, uses fg_color. Default is None.
    marker_symbol : str, optional
        Marker symbol for scatter plots: 'circle', 'square', 'triangle', or 'diamond'.
        Default is 'circle'.
    left_padding : int, optional
        Left padding around the plot area in pixels. Default is 40.
    right_padding : int, optional
        Right padding around the plot area in pixels. Default is 40.
    top_padding : int, optional
        Top padding around the plot area in pixels. Default is 40.
    bottom_padding : int, optional
        Bottom padding around the plot area in pixels. Default is 40.
    font_name : str, optional
        Font name for labels. Uses FontManager default if None.
    font_size : int, optional
        Font size for labels. Default is 10.
    font_variation : str, optional
        Font variation (e.g., 'Bold', 'Italic').
    bar_width_ratio : float, optional
        Ratio of bar width to available space (0.0 to 1.0). Default is 0.8.
    antialias : bool, optional
        Whether to use anti-aliasing for smoother diagonal lines. Default is True.
    scale_factor : int, optional
        Supersampling scale factor for anti-aliasing (2 or 4). Default is 2.

    Attributes
    ----------
    data : dict
        Normalized data structure with series names as keys.
    plot_type : str
        Type of plot being rendered.

    Examples
    --------
    Create a scatter plot with y-values only:

    >>> from piltext import FontManager, ImagePlot
    >>> fm = FontManager()
    >>> data = [5, 7, 4, 8]
    >>> plot = ImagePlot(data, fm, plot_type='scatter', marker_size=6)
    >>> img = plot.render()

    Create a line plot with (x, y) tuples:

    >>> data = [(1, 5), (2, 7), (3, 4), (4, 8)]
    >>> plot = ImagePlot(data, fm, plot_type='line')
    >>> img = plot.render()

    Create a multi-series line plot with y-values:

    >>> data = {
    ...     'Temperature': [20, 22, 21, 23],
    ...     'Humidity': [60, 55, 58, 52]
    ... }
    >>> plot = ImagePlot(data, fm, title='Weather Data',
    ...                  xlabel='Hour', ylabel='Value')
    """

    DEFAULT_COLORS = [
        "#4CAF50",
        "#2196F3",
        "#FF5722",
        "#FFC107",
        "#9C27B0",
        "#00BCD4",
        "#FF9800",
        "#E91E63",
    ]

    def __init__(
        self,
        data: Union[
            list[float],
            list[tuple[float, float]],
            dict[str, Union[list[float], list[tuple[float, float]]]],
        ],
        font_manager: FontManager,
        plot_type: str = "line",
        width: int = 400,
        height: int = 300,
        bg_color: str = "white",
        fg_color: Union[str, list[str]] = "#4CAF50",
        grid_color: str = "#e0e0e0",
        axis_color: str = "black",
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        show_grid: bool = True,
        show_legend: bool = True,
        show_axis: bool = True,
        line_width: int = 2,
        marker_size: int = 4,
        marker_color: Optional[Union[str, list[str]]] = None,
        marker_symbol: str = "circle",
        left_padding: int = 40,
        right_padding: int = 40,
        top_padding: int = 40,
        bottom_padding: int = 40,
        font_name: Optional[str] = None,
        font_size: int = 10,
        font_variation: Optional[str] = None,
        bar_width_ratio: float = 0.8,
        antialias: bool = True,
        scale_factor: int = 2,
    ):
        self.font_manager = font_manager
        self.plot_type = plot_type.lower()
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.grid_color = grid_color
        self.axis_color = axis_color
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.show_grid = show_grid
        self.show_legend = show_legend
        self.show_axis = show_axis
        self.line_width = line_width
        self.marker_size = marker_size
        self.marker_symbol = marker_symbol.lower()
        self.left_padding = left_padding
        self.right_padding = right_padding
        self.top_padding = top_padding
        self.bottom_padding = bottom_padding
        self.font_name = font_name
        self.font_size = font_size
        self.font_variation = font_variation
        self.bar_width_ratio = max(0.1, min(1.0, bar_width_ratio))
        self.antialias = antialias
        self.scale_factor = max(1, min(4, scale_factor)) if antialias else 1

        if isinstance(data, dict):
            self.data = {
                name: self._normalize_series(series) for name, series in data.items()
            }
        else:
            self.data = {"Series 1": self._normalize_series(data)}

        if isinstance(fg_color, list):
            self.colors = fg_color
        else:
            self.colors = [fg_color] + self.DEFAULT_COLORS[1:]

        if marker_color is None:
            self.marker_colors = self.colors
        elif isinstance(marker_color, list):
            self.marker_colors = marker_color
        else:
            self.marker_colors = [marker_color] + self.DEFAULT_COLORS[1:]

        self._validate_data()

    def _normalize_series(
        self, series: Union[list[float], list[tuple[float, float]]]
    ) -> list[tuple[float, float]]:
        """
        Normalize series data to (x, y) tuples.

        If data is a list of numbers, converts to [(0, val), (1, val), ...].
        If data is already a list of tuples, returns as-is.

        Parameters
        ----------
        series : list[float] | list[tuple[float, float]]
            Series data as y-values only or (x, y) tuples.

        Returns
        -------
        list[tuple[float, float]]
            Normalized series data as (x, y) tuples.
        """
        if not series:
            return []

        first_element = series[0]
        if isinstance(first_element, (tuple, list)):
            return list(series)  # type: ignore[arg-type]
        else:
            return [(float(i), float(val)) for i, val in enumerate(series)]  # type: ignore[arg-type]

    def _validate_data(self) -> None:
        """Validate that data is in the correct format."""
        if not self.data:
            raise ValueError("Data cannot be empty")

        for series_name, points in self.data.items():
            if not points:
                raise ValueError(f"Series '{series_name}' has no data points")
            if not all(isinstance(p, (tuple, list)) and len(p) == 2 for p in points):
                raise ValueError(
                    f"Series '{series_name}' must contain (x, y) tuples or lists"
                )

    def set_padding(self, padding: int) -> None:
        """
        Modify all paddings to the specified value.

        Parameters
        ----------
        padding : int
            New padding value in pixels.

        Examples
        --------
        >>> plot = ImagePlot(data, font_manager)
        >>> plot.set_padding(50)
        """
        self.left_padding = padding
        self.right_padding = padding
        self.top_padding = padding
        self.bottom_padding = padding

    def _store_original_dimensions(self) -> dict:
        """Store original dimensions before scaling for anti-aliasing."""
        return {
            "width": self.width,
            "height": self.height,
            "left_padding": self.left_padding,
            "right_padding": self.right_padding,
            "top_padding": self.top_padding,
            "bottom_padding": self.bottom_padding,
            "line_width": self.line_width,
            "marker_size": self.marker_size,
            "font_size": self.font_size,
        }

    def _scale_dimensions(self, factor: int) -> None:
        """Scale all dimensions by factor for supersampling."""
        self.width *= factor
        self.height *= factor
        self.left_padding *= factor
        self.right_padding *= factor
        self.top_padding *= factor
        self.bottom_padding *= factor
        self.line_width *= factor
        self.marker_size *= factor
        self.font_size *= factor

    def _restore_original_dimensions(self, original_dims: Optional[dict]) -> None:
        """Restore original dimensions after downsampling."""
        if original_dims is None:
            return
        for key, value in original_dims.items():
            setattr(self, key, value)

    def render(self) -> Image.Image:
        """
        Render the plot as a PIL Image.

        Returns
        -------
        PIL.Image.Image
            The rendered plot image.

        Examples
        --------
        >>> plot = ImagePlot(data, font_manager)
        >>> img = plot.render()
        >>> img.save("output.png")
        """
        original_dims = None
        if self.antialias and self.scale_factor > 1:
            original_dims = self._store_original_dimensions()
            self._scale_dimensions(self.scale_factor)

        drawer = ImageDrawer(self.width, self.height, font_manager=self.font_manager)

        drawer.draw.rectangle([0, 0, self.width, self.height], fill=self.bg_color)

        title_height = 0
        if self.title:
            title_height = self.font_size + 10

        legend_width = 0
        if self.show_legend and len(self.data) > 1:
            legend_width = 100

        xlabel_height = 0
        if self.xlabel:
            xlabel_height = self.font_size + 10
        elif self.show_axis:
            xlabel_height = self.font_size + 5

        ylabel_width = 0
        if self.ylabel:
            ylabel_width = self.font_size + 10
        elif self.show_axis:
            ylabel_width = 40

        self.plot_x = self.left_padding + ylabel_width
        self.plot_y = self.top_padding + title_height
        self.plot_width = (
            self.width
            - self.left_padding
            - self.right_padding
            - ylabel_width
            - legend_width
        )
        self.plot_height = (
            self.height
            - self.top_padding
            - self.bottom_padding
            - title_height
            - xlabel_height
        )

        self._calculate_bounds()

        if self.title:
            self._draw_title(drawer)

        if self.show_grid:
            self._draw_grid(drawer)
        if self.show_axis:
            self._draw_axes(drawer)

        if self.plot_type == "line":
            self._draw_line_plot(drawer)
        elif self.plot_type == "bar":
            self._draw_bar_plot(drawer)
        elif self.plot_type == "scatter":
            self._draw_scatter_plot(drawer)

        if self.show_legend and len(self.data) > 1:
            self._draw_legend(drawer)

        img = drawer.get_image()

        if self.antialias and self.scale_factor > 1 and original_dims is not None:
            img = img.resize(
                (original_dims["width"], original_dims["height"]),
                Image.Resampling.LANCZOS,
            )
            self._restore_original_dimensions(original_dims)

        return img

    def _calculate_bounds(self) -> None:
        """Calculate min and max values for x and y axes."""
        all_x = []
        all_y = []

        for points in self.data.values():
            for x, y in points:
                all_x.append(float(x))
                all_y.append(float(y))

        self.x_min = min(all_x)
        self.x_max = max(all_x)
        self.y_min = min(all_y)
        self.y_max = max(all_y)

        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min

        if x_range == 0:
            self.x_min -= 0.5
            self.x_max += 0.5
            x_range = 1

        if y_range == 0:
            self.y_min -= 0.5
            self.y_max += 0.5
            y_range = 1

        margin_ratio = 0.05 if self.show_axis or self.show_grid else 0.0

        self.x_min -= x_range * margin_ratio
        self.x_max += x_range * margin_ratio
        self.y_min -= y_range * margin_ratio
        self.y_max += y_range * margin_ratio

    def _scale_point(self, x: float, y: float) -> tuple[int, int]:
        """
        Transform data coordinates to pixel coordinates.

        Parameters
        ----------
        x : float
            X coordinate in data space.
        y : float
            Y coordinate in data space.

        Returns
        -------
        tuple of (int, int)
            Pixel coordinates (px, py).
        """
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min

        px = self.plot_x + int(((x - self.x_min) / x_range) * self.plot_width)
        py = (
            self.plot_y
            + self.plot_height
            - int(((y - self.y_min) / y_range) * self.plot_height)
        )

        return px, py

    def _draw_title(self, drawer: ImageDrawer) -> None:
        """Draw the plot title."""
        if self.title is None:
            return

        title_x = self.width // 2
        title_y = self.bottom_padding // 2

        try:
            drawer.draw_text(
                self.title,
                (title_x, title_y),
                font_size=self.font_size + 4,
                font_name=self.font_name,
                font_variation=self.font_variation,
                fill=self.axis_color,
                anchor="mm",
            )
        except Exception:
            pass

    def _draw_grid(self, drawer: ImageDrawer) -> None:
        """Draw background grid lines."""
        num_grid_lines = 5

        for i in range(num_grid_lines + 1):
            y = self.plot_y + int((i / num_grid_lines) * self.plot_height)
            drawer.draw.line(
                [
                    (self.plot_x, y),
                    (self.plot_x + self.plot_width, y),
                ],
                fill=self.grid_color,
                width=1,
            )

            x = self.plot_x + int((i / num_grid_lines) * self.plot_width)
            drawer.draw.line(
                [
                    (x, self.plot_y),
                    (x, self.plot_y + self.plot_height),
                ],
                fill=self.grid_color,
                width=1,
            )

    def _draw_axes(self, drawer: ImageDrawer) -> None:
        """Draw X and Y axes with tick marks and labels."""
        drawer.draw.line(
            [
                (self.plot_x, self.plot_y),
                (self.plot_x, self.plot_y + self.plot_height),
            ],
            fill=self.axis_color,
            width=2,
        )

        drawer.draw.line(
            [
                (self.plot_x, self.plot_y + self.plot_height),
                (self.plot_x + self.plot_width, self.plot_y + self.plot_height),
            ],
            fill=self.axis_color,
            width=2,
        )

        num_ticks = 5

        for i in range(num_ticks + 1):
            y = self.plot_y + int((i / num_ticks) * self.plot_height)
            drawer.draw.line(
                [(self.plot_x - 5, y), (self.plot_x, y)],
                fill=self.axis_color,
                width=1,
            )

            y_value = self.y_max - (i / num_ticks) * (self.y_max - self.y_min)
            label = self._format_tick_label(y_value)

            try:
                drawer.draw_text(
                    label,
                    (self.plot_x - 10, y),
                    font_size=self.font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill=self.axis_color,
                    anchor="rm",
                )
            except Exception:
                pass

        for i in range(num_ticks + 1):
            x = self.plot_x + int((i / num_ticks) * self.plot_width)
            drawer.draw.line(
                [
                    (x, self.plot_y + self.plot_height),
                    (x, self.plot_y + self.plot_height + 5),
                ],
                fill=self.axis_color,
                width=1,
            )

            x_value = self.x_min + (i / num_ticks) * (self.x_max - self.x_min)
            label = self._format_tick_label(x_value)

            try:
                drawer.draw_text(
                    label,
                    (x, self.plot_y + self.plot_height + 10),
                    font_size=self.font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill=self.axis_color,
                    anchor="mt",
                )
            except Exception:
                pass

        if self.xlabel is not None:
            try:
                drawer.draw_text(
                    self.xlabel,
                    (
                        self.plot_x + self.plot_width // 2,
                        self.plot_y + self.plot_height + self.bottom_padding // 2,
                    ),
                    font_size=self.font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill=self.axis_color,
                    anchor="mm",
                )
            except Exception:
                pass

        if self.ylabel is not None:
            try:
                drawer.draw_text(
                    self.ylabel,
                    (self.left_padding // 2, self.plot_y + self.plot_height // 2),
                    font_size=self.font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill=self.axis_color,
                    anchor="mm",
                )
            except Exception:
                pass

    def _format_tick_label(self, value: float) -> str:
        """
        Format a numeric value for axis tick labels.

        Parameters
        ----------
        value : float
            Numeric value to format.

        Returns
        -------
        str
            Formatted string representation.
        """
        if abs(value) < 0.01 and value != 0:
            return f"{value:.2e}"
        elif abs(value) < 1:
            return f"{value:.2f}"
        elif abs(value) < 100:
            return f"{value:.1f}"
        else:
            return f"{int(value)}"

    def _draw_line_plot(self, drawer: ImageDrawer) -> None:
        """Draw line plot with connected data points."""
        for idx, (_series_name, points) in enumerate(self.data.items()):
            color = self.colors[idx % len(self.colors)]

            sorted_points = sorted(points, key=lambda p: p[0])

            for i in range(len(sorted_points) - 1):
                x1, y1 = sorted_points[i]
                x2, y2 = sorted_points[i + 1]

                px1, py1 = self._scale_point(x1, y1)
                px2, py2 = self._scale_point(x2, y2)

                drawer.draw.line(
                    [(px1, py1), (px2, py2)], fill=color, width=self.line_width
                )

            if self.marker_size > 0:
                marker_color = self.marker_colors[idx % len(self.marker_colors)]
                for x, y in sorted_points:
                    px, py = self._scale_point(x, y)
                    self._draw_marker(drawer, px, py, marker_color)

    def _draw_bar_plot(self, drawer: ImageDrawer) -> None:
        """Draw bar plot with vertical bars."""
        num_series = len(self.data)
        all_x_values = sorted(
            set(x for points in self.data.values() for x, _ in points)
        )
        num_x_values = len(all_x_values)

        if num_x_values == 0:
            return

        x_spacing = self.plot_width / num_x_values
        total_bar_width = x_spacing * self.bar_width_ratio
        bar_width = total_bar_width / num_series
        bar_gap = (x_spacing - total_bar_width) / 2

        y_zero_px = self._scale_point(0, 0)[1]
        y_zero_px = max(self.plot_y, min(self.plot_y + self.plot_height, y_zero_px))

        for idx, (_series_name, points) in enumerate(self.data.items()):
            color = self.colors[idx % len(self.colors)]

            point_dict = {x: y for x, y in points}

            for i, x_val in enumerate(all_x_values):
                if x_val not in point_dict:
                    continue

                y_val = point_dict[x_val]

                bar_x = self.plot_x + i * x_spacing + bar_gap + idx * bar_width
                _, bar_y = self._scale_point(x_val, y_val)

                drawer.draw.rectangle(
                    [
                        (int(bar_x), bar_y),
                        (int(bar_x + bar_width), y_zero_px),
                    ],
                    fill=color,
                    outline=self.axis_color,
                )

    def _draw_scatter_plot(self, drawer: ImageDrawer) -> None:
        """Draw scatter plot with individual markers."""
        if self.marker_size == 0:
            return

        for idx, (_series_name, points) in enumerate(self.data.items()):
            marker_color = self.marker_colors[idx % len(self.marker_colors)]

            for x, y in points:
                px, py = self._scale_point(x, y)
                self._draw_marker(drawer, px, py, marker_color)

    def _draw_marker(self, drawer: ImageDrawer, px: int, py: int, color: str) -> None:
        """
        Draw a marker at the specified pixel coordinates.

        Parameters
        ----------
        drawer : ImageDrawer
            The image drawer instance.
        px : int
            X pixel coordinate.
        py : int
            Y pixel coordinate.
        color : str
            Marker color.
        """
        if self.marker_symbol == "circle":
            drawer.draw.ellipse(
                [
                    (px - self.marker_size, py - self.marker_size),
                    (px + self.marker_size, py + self.marker_size),
                ],
                fill=color,
                outline=self.axis_color,
            )
        elif self.marker_symbol == "square":
            drawer.draw.rectangle(
                [
                    (px - self.marker_size, py - self.marker_size),
                    (px + self.marker_size, py + self.marker_size),
                ],
                fill=color,
                outline=self.axis_color,
            )
        elif self.marker_symbol == "triangle":
            half_size = self.marker_size
            drawer.draw.polygon(
                [
                    (px, py - half_size),
                    (px - half_size, py + half_size),
                    (px + half_size, py + half_size),
                ],
                fill=color,
                outline=self.axis_color,
            )
        elif self.marker_symbol == "diamond":
            half_size = self.marker_size
            drawer.draw.polygon(
                [
                    (px, py - half_size),
                    (px + half_size, py),
                    (px, py + half_size),
                    (px - half_size, py),
                ],
                fill=color,
                outline=self.axis_color,
            )

    def _draw_legend(self, drawer: ImageDrawer) -> None:
        """Draw legend for multiple series."""
        legend_x = self.plot_x + self.plot_width + 10
        legend_y = self.plot_y + 10

        legend_item_height = self.font_size + 8

        for idx, series_name in enumerate(self.data.keys()):
            color = self.colors[idx % len(self.colors)]
            item_y = legend_y + idx * legend_item_height

            drawer.draw.rectangle(
                [
                    (legend_x, item_y),
                    (legend_x + 12, item_y + 12),
                ],
                fill=color,
                outline=self.axis_color,
            )

            try:
                drawer.draw_text(
                    series_name,
                    (legend_x + 18, item_y + 6),
                    font_size=self.font_size,
                    font_name=self.font_name,
                    font_variation=self.font_variation,
                    fill=self.axis_color,
                    anchor="lm",
                )
            except Exception:
                pass
