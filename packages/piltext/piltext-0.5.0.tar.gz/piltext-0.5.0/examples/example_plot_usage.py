"""
Example script demonstrating ImagePlot usage.

This script creates various plot types (line, bar, scatter) and saves them
as PNG images without using matplotlib.
"""

from piltext import FontManager, ImagePlot


def main():
    fm = FontManager()

    print("Creating line plot...")
    data_line = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 5), (5, 6)]
    plot_line = ImagePlot(
        data_line,
        fm,
        plot_type="line",
        title="Temperature Over Time",
        xlabel="Hours",
        ylabel="Temperature (°C)",
    )
    img_line = plot_line.render()
    img_line.save("example_line_plot.png")
    print("  Saved: example_line_plot.png")

    print("Creating bar plot...")
    data_bar = [(0, 10), (1, 15), (2, 13), (3, 18), (4, 16)]
    plot_bar = ImagePlot(
        data_bar,
        fm,
        plot_type="bar",
        title="Monthly Sales",
        xlabel="Month",
        ylabel="Sales ($1000)",
        fg_color="#2196F3",
    )
    img_bar = plot_bar.render()
    img_bar.save("example_bar_plot.png")
    print("  Saved: example_bar_plot.png")

    print("Creating scatter plot...")
    data_scatter = [(1, 5), (2, 7), (3, 4), (4, 8), (5, 6), (6, 9), (7, 5)]
    plot_scatter = ImagePlot(
        data_scatter,
        fm,
        plot_type="scatter",
        title="Data Distribution",
        marker_size=6,
        fg_color="#FF5722",
    )
    img_scatter = plot_scatter.render()
    img_scatter.save("example_scatter_plot.png")
    print("  Saved: example_scatter_plot.png")

    print("Creating multi-series line plot...")
    data_multi = {
        "Series A": [(0, 20), (1, 22), (2, 21), (3, 23), (4, 24)],
        "Series B": [(0, 15), (1, 17), (2, 16), (3, 18), (4, 19)],
    }
    plot_multi = ImagePlot(
        data_multi,
        fm,
        plot_type="line",
        title="Comparison of Two Series",
        xlabel="Time",
        ylabel="Value",
        width=500,
        height=350,
    )
    img_multi = plot_multi.render()
    img_multi.save("example_multi_series_plot.png")
    print("  Saved: example_multi_series_plot.png")

    print("Creating plot with y-values only...")
    data_y_only = [20, 22, 19, 25, 23, 27, 24]
    plot_y_only = ImagePlot(
        data_y_only,
        fm,
        plot_type="line",
        title="Simple Y-Values Data",
        xlabel="Index",
        ylabel="Value",
        show_grid=True,
    )
    img_y_only = plot_y_only.render()
    img_y_only.save("example_y_values_plot.png")
    print("  Saved: example_y_values_plot.png")

    print("\nAll plots created successfully!")


if __name__ == "__main__":
    main()
