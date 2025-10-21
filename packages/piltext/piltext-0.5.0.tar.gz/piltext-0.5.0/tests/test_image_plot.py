import io

import pytest
from PIL import Image

from piltext.font_manager import FontManager
from piltext.image_plot import ImagePlot


def test_image_plot_basic_line():
    font_manager = FontManager()
    data = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 5)]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert img.size == (400, 300)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    assert buf.tell() > 0


def test_image_plot_basic_bar():
    font_manager = FontManager()
    data = [(0, 10), (1, 15), (2, 13), (3, 18)]
    plot = ImagePlot(data, font_manager, plot_type="bar")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert img.size == (400, 300)


def test_image_plot_basic_scatter():
    font_manager = FontManager()
    data = [(1, 5), (2, 7), (3, 4), (4, 8), (5, 6)]
    plot = ImagePlot(data, font_manager, plot_type="scatter")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert img.size == (400, 300)


def test_image_plot_multiple_series():
    font_manager = FontManager()
    data = {
        "Series A": [(0, 5), (1, 7), (2, 6), (3, 8)],
        "Series B": [(0, 3), (1, 4), (2, 5), (3, 4)],
    }
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_with_title_and_labels():
    font_manager = FontManager()
    data = [(0, 0), (1, 1), (2, 4), (3, 9)]
    plot = ImagePlot(
        data,
        font_manager,
        plot_type="line",
        title="Test Plot",
        xlabel="X Axis",
        ylabel="Y Axis",
    )
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_custom_size():
    font_manager = FontManager()
    data = [(0, 0), (1, 1)]
    plot = ImagePlot(data, font_manager, width=600, height=400)
    img = plot.render()
    assert img.size == (600, 400)


def test_image_plot_custom_colors():
    font_manager = FontManager()
    data = [(0, 0), (1, 1), (2, 2)]
    plot = ImagePlot(
        data,
        font_manager,
        plot_type="line",
        fg_color="#FF5722",
        bg_color="#F0F0F0",
    )
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_with_grid():
    font_manager = FontManager()
    data = [(0, 0), (1, 1)]
    plot = ImagePlot(data, font_manager, show_grid=True)
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_without_grid():
    font_manager = FontManager()
    data = [(0, 0), (1, 1)]
    plot = ImagePlot(data, font_manager, show_grid=False)
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_with_legend():
    font_manager = FontManager()
    data = {
        "Series 1": [(0, 1), (1, 2)],
        "Series 2": [(0, 2), (1, 3)],
    }
    plot = ImagePlot(data, font_manager, show_legend=True)
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_without_legend():
    font_manager = FontManager()
    data = {
        "Series 1": [(0, 1), (1, 2)],
        "Series 2": [(0, 2), (1, 3)],
    }
    plot = ImagePlot(data, font_manager, show_legend=False)
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_negative_values():
    font_manager = FontManager()
    data = [(-2, -5), (-1, -2), (0, 0), (1, 3), (2, 5)]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_single_point():
    font_manager = FontManager()
    data = [(5, 10)]
    plot = ImagePlot(data, font_manager, plot_type="scatter")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_horizontal_line():
    font_manager = FontManager()
    data = [(0, 5), (1, 5), (2, 5), (3, 5)]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_vertical_line():
    font_manager = FontManager()
    data = [(2, 0), (2, 1), (2, 2), (2, 3)]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_empty_data_raises():
    font_manager = FontManager()
    with pytest.raises(ValueError, match="Data cannot be empty"):
        ImagePlot({}, font_manager)


def test_image_plot_invalid_data_format():
    font_manager = FontManager()
    with pytest.raises(ValueError, match="must contain"):
        ImagePlot([(1, 2, 3)], font_manager)


def test_image_plot_series_no_data_raises():
    font_manager = FontManager()
    with pytest.raises(ValueError, match="has no data points"):
        ImagePlot({"Empty": []}, font_manager)


def test_image_plot_multiple_colors():
    font_manager = FontManager()
    data = {
        "S1": [(0, 1)],
        "S2": [(0, 2)],
        "S3": [(0, 3)],
    }
    plot = ImagePlot(data, font_manager, fg_color=["#FF0000", "#00FF00", "#0000FF"])
    img = plot.render()
    assert isinstance(img, Image.Image)


@pytest.mark.parametrize("plot_type", ["line", "bar", "scatter"])
def test_image_plot_types(plot_type):
    font_manager = FontManager()
    data = [(0, 5), (1, 7), (2, 6)]
    plot = ImagePlot(data, font_manager, plot_type=plot_type)
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_custom_styling():
    font_manager = FontManager()
    data = [(0, 0), (1, 1), (2, 2)]
    plot = ImagePlot(
        data,
        font_manager,
        plot_type="line",
        line_width=3,
        marker_size=6,
        left_padding=50,
        right_padding=50,
        top_padding=50,
        bottom_padding=50,
        font_size=12,
    )
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_large_values():
    font_manager = FontManager()
    data = [(0, 1000), (1, 5000), (2, 10000)]
    plot = ImagePlot(data, font_manager, plot_type="bar")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_small_values():
    font_manager = FontManager()
    data = [(0, 0.001), (1, 0.005), (2, 0.003)]
    plot = ImagePlot(data, font_manager, plot_type="scatter")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_unsorted_data():
    font_manager = FontManager()
    data = [(3, 5), (1, 2), (4, 8), (2, 3), (0, 1)]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_bar_with_multiple_series():
    font_manager = FontManager()
    data = {
        "A": [(0, 10), (1, 15), (2, 13)],
        "B": [(0, 8), (1, 12), (2, 18)],
    }
    plot = ImagePlot(data, font_manager, plot_type="bar")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_y_values_only():
    font_manager = FontManager()
    data = [10, 15, 13, 18, 20]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert len(plot.data["Series 1"]) == 5
    assert plot.data["Series 1"][0] == (0, 10)
    assert plot.data["Series 1"][4] == (4, 20)


def test_image_plot_y_values_only_bar():
    font_manager = FontManager()
    data = [20, 22, 19, 25, 23, 27]
    plot = ImagePlot(data, font_manager, plot_type="bar")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert len(plot.data["Series 1"]) == 6


def test_image_plot_y_values_only_scatter():
    font_manager = FontManager()
    data = [5.5, 7.2, 6.1, 8.3]
    plot = ImagePlot(data, font_manager, plot_type="scatter")
    img = plot.render()
    assert isinstance(img, Image.Image)


def test_image_plot_y_values_only_multiple_series():
    font_manager = FontManager()
    data = {
        "Series A": [10, 15, 13],
        "Series B": [8, 12, 18],
    }
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert len(plot.data["Series A"]) == 3
    assert len(plot.data["Series B"]) == 3
    assert plot.data["Series A"][0] == (0, 10)
    assert plot.data["Series B"][2] == (2, 18)


def test_image_plot_y_values_only_negative():
    font_manager = FontManager()
    data = [-5, -2, 0, 3, 5]
    plot = ImagePlot(data, font_manager, plot_type="line")
    img = plot.render()
    assert isinstance(img, Image.Image)
    assert plot.data["Series 1"][0] == (0, -5)
    assert plot.data["Series 1"][2] == (2, 0)
