Quickstart
==========

Installation
------------

You can install PILText using pip:

.. code-block:: bash

   pip install piltext

Basic Usage
-----------

PILText provides tools to create images with text using Pillow (PIL).

.. code-block:: python

   import piltext
   from piltext.image_handler import ImageHandler
   from piltext.text_box import TextBox

   # Create a new image with a text box
   handler = ImageHandler(width=400, height=200, background_color="white")
   text_box = TextBox(
       text="Hello World!",
       x=200,
       y=100,
       font_size=36,
       align="center",
       color="black"
   )

   # Draw the text on the image
   handler.draw_text_box(text_box)

   # Save the image
   handler.save("hello_world.png")

TOML Configuration
------------------

PILText supports TOML configuration files for easy image generation:

.. code-block:: toml

   [fonts]
   default_size = 24

   [image]
   width = 400
   height = 200

   [grid]
   rows = 2
   columns = 2
   margin_x = 5
   margin_y = 5

   [[grid.texts]]
   start = [0, 0]
   text = "Hello"
   anchor = "mm"

   [[grid.texts]]
   start = [0, 1]
   text = "World"
   anchor = "mm"

Render from CLI:

.. code-block:: bash

   piltext render config.toml --output output.png

Or from Python:

.. code-block:: python

   from piltext import ConfigLoader

   loader = ConfigLoader("config.toml")
   image = loader.render(output_path="output.png")

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

**Fonts Section:**

.. code-block:: toml

   [fonts]
   default_size = 20              # Default font size in pixels
   default_name = "Roboto-Bold"   # Default font name

   # Optional: Custom font directories
   directories = ["/path/to/fonts"]

   # Optional: Download fonts before rendering
   # From Google Fonts
   [[fonts.download]]
   part1 = "ofl"
   part2 = "roboto"
   font_name = "Roboto[wdth,wght].ttf"

   # From URL
   [[fonts.download]]
   url = "https://example.com/font.ttf"

**Image Section:**

.. code-block:: toml

   [image]
   width = 480                    # Image width in pixels
   height = 280                   # Image height in pixels
   inverted = false               # Invert colors
   mirror = false                 # Mirror horizontally
   orientation = 0                # Rotation angle

**Grid Section:**

.. code-block:: toml

   [grid]
   rows = 4                       # Number of rows
   columns = 7                    # Number of columns
   margin_x = 2                   # Horizontal margin in pixels
   margin_y = 2                   # Vertical margin in pixels

   # Merge cells: [[start_row, start_col], [end_row, end_col]]
   merge = [
     [[0, 0], [0, 3]],            # Merge row 0, columns 0-3
     [[1, 0], [2, 1]],            # Merge rows 1-2, columns 0-1
   ]

   # Text content
   [[grid.texts]]
   start = 0                      # Merged cell index
   text = "Header"
   font_variation = "Bold"
   fill = 255
   anchor = "mm"                  # Anchor: lt/mm/rs etc.

   [[grid.texts]]
   start = [1, 2]                 # Or use [row, col]
   text = "Cell Text"
   font_name = "CustomFont"
   fill = 128

**Anchor Options:**

The anchor parameter controls text positioning within a cell using a two-character code:

- **First character (horizontal):** ``l`` (left), ``m`` (middle), ``r`` (right)
- **Second character (vertical):** ``t`` (top), ``m`` (middle), ``b`` (bottom), ``s`` (baseline)

Common anchor values:

- ``lt`` - left-top (default)
- ``mm`` - middle-middle (centered)
- ``rb`` - right-bottom
- ``mt`` - middle-top
- ``lb`` - left-bottom
- ``rs`` - right-baseline

**Auto-Fit with Anchors:**

When no ``font_size`` is specified, text automatically scales to fit the cell. The anchor
determines where the fitted text is positioned:

.. code-block:: toml

    [grid]
    rows = 2
    columns = 2
    merge = [
      [[0, 0], [1, 1]],  # Large merged cell
    ]

    [[grid.texts]]
    start = [0, 0]
    text = "AUTO-FIT"
    anchor = "mm"        # Text fills cell, centered
    fill = 255

    [[grid.texts]]
    start = [0, 1]
    text = "12345"
    anchor = "rb"        # Text fills cell, positioned at bottom-right
    font_size = 20       # Fixed size (no auto-fit)

**Embedding Visualizations:**

You can embed dial, squares, and plot visualizations directly in grid cells:

.. code-block:: toml

   [grid]
   rows = 2
   columns = 3
   margin_x = 5
   margin_y = 5

   # Dial visualization
   [[grid.texts]]
   start = [0, 0]
   [grid.texts.dial]
   percentage = 0.75
   arc_start = 135
   arc_end = 45
   fill_color = "black"
   empty_color = "white"

   # Text label
   [[grid.texts]]
   start = [0, 1]
   text = "75%"
   anchor = "mm"

   # Squares visualization
   [[grid.texts]]
   start = [1, 0]
   [grid.texts.squares]
   percentage = 0.60
   fill_color = "black"
   empty_color = "white"

   # Plot visualization
   [[grid.texts]]
   start = [0, 2]
   [grid.texts.plot]
   type = "line"
   data = [20, 22, 19, 25, 23]
   fg_color = "#4CAF50"
   show_grid = true

The ``dial``, ``squares``, and ``plot`` parameters are the same as the standalone sections.
Visualizations auto-size to fit the cell dimensions.

**Dial, Squares, and Plot Sections:**

Create standalone visualizations:

.. code-block:: toml

   # Dial visualization
   [dial]
   percentage = 0.75              # Fill percentage (0.0-1.0)
   size = 250                     # Diameter in pixels
   arc_start = 135                # Start angle in degrees
   arc_end = 45                   # End angle in degrees
   line_width = 20                # Arc thickness in pixels
   fill_color = "black"           # Filled portion color
   empty_color = "white"          # Empty portion color

   # Squares visualization
   [squares]
   percentage = 0.60              # Fill percentage (0.0-1.0)
   squares_x = 10                 # Number of squares horizontally
   squares_y = 10                 # Number of squares vertically
   fill_color = "black"           # Filled squares color
   empty_color = "white"          # Empty squares color

**Plot Visualizations:**

Create data plots without matplotlib:

.. code-block:: toml

   # Line plot with single series
   [[grid.texts]]
   start = [0, 0]
   [grid.texts.plot]
   type = "line"                  # Plot type: 'line', 'bar', 'scatter'
   data = [20, 22, 19, 25, 23]    # Y-values (x auto-generated as 0,1,2,...)
   fg_color = "#4CAF50"           # Line/bar/marker color
   show_grid = true               # Show background grid
   show_legend = false            # Show legend (for multiple series)
   title = "Temperature"          # Plot title
   xlabel = "Hour"                # X-axis label
   ylabel = "°C"                  # Y-axis label
   line_width = 2                 # Line width (for line plots)
   marker_size = 4                # Marker size (for scatter plots)
   bar_width_ratio = 0.8          # Bar width ratio (for bar plots)

   # Bar plot with (x,y) tuples
   [[grid.texts]]
   start = [0, 1]
   [grid.texts.plot]
   type = "bar"
   data = [[0, 10], [1, 15], [2, 13], [3, 18]]
   fg_color = "#2196F3"

   # Multi-series line plot
   [[grid.texts]]
   start = [1, 0]
   [grid.texts.plot]
   type = "line"
   title = "Weather Data"
   show_legend = true

   [[grid.texts.plot.series]]
   name = "Temperature"
   data = [20, 22, 21, 23]
   color = "#FF5722"

   [[grid.texts.plot.series]]
   name = "Humidity"
   data = [60, 55, 58, 52]
   color = "#2196F3"

**Plot Data Formats:**

Plots support three data formats:

1. **Y-values only** - List of numbers with auto-generated x-coordinates:

   .. code-block:: toml

      data = [10, 15, 13, 18, 16]
      # Becomes: [(0,10), (1,15), (2,13), (3,18), (4,16)]

2. **(X, Y) tuples** - List of coordinate pairs:

   .. code-block:: toml

      data = [[0, 10], [1, 15], [2, 13], [3, 18]]

3. **Multiple series** - Named series with individual colors:

   .. code-block:: toml

      [[grid.texts.plot.series]]
      name = "Series A"
      data = [10, 15, 13]
      color = "#4CAF50"

      [[grid.texts.plot.series]]
      name = "Series B"
      data = [8, 12, 18]
      color = "#2196F3"

CLI Commands
------------

Rendering
~~~~~~~~~

Render from config file:

.. code-block:: bash

   # Save to file
   piltext render config.toml -o output.png

   # Display in terminal (requires rich-pixels)
   piltext render config.toml -d

   # Display as ASCII art
   piltext render config.toml -a

   # Display as simple ASCII art (uses only space, dot, hash)
   piltext render config.toml -a -s

   # Control display width
   piltext render config.toml -a --display-width 100

   # Save and display
   piltext render config.toml -o output.png -d

Font Management
~~~~~~~~~~~~~~~

List available fonts:

.. code-block:: bash

   # List font names
   piltext font list

   # List with full paths
   piltext font list --fullpath

List font directories:

.. code-block:: bash

   piltext font dirs

Download Google Fonts:

.. code-block:: bash

   piltext font download ofl roboto Roboto-Regular.ttf

Download from URL:

.. code-block:: bash

   piltext font download-url https://example.com/font.ttf

List font variations:

.. code-block:: bash

   piltext font variations Roboto[wdth,wght]

Delete all fonts:

.. code-block:: bash

   # With confirmation
   piltext font delete-all

   # Skip confirmation
   piltext font delete-all -y

Font Management (Python)
------------------------

PILText includes a font manager to handle font loading and selection:

.. code-block:: python

   from piltext.font_manager import FontManager

   # Initialize font manager
   font_manager = FontManager()

   # Add a font path
   font_manager.add_font_path("path/to/custom_font.ttf")

   # Use Google Fonts
   font_manager.use_google_font("Roboto")

   # Get a font instance
   font = font_manager.get_font(font_name="Roboto", size=24)

Text Grids (Python)
-------------------

PILText supports grid-based text layouts:

.. code-block:: python

   from piltext.text_grid import TextGrid

   # Create a text grid with 2 rows and 3 columns
   grid = TextGrid(rows=2, cols=3, width=600, height=400)

   # Add text to specific cells
   grid.add_text("Cell 1", row=0, col=0)
   grid.add_text("Cell 2", row=0, col=1)
   grid.add_text("Cell 3", row=0, col=2)
   grid.add_text("Cell 4", row=1, col=0)
   grid.add_text("Cell 5", row=1, col=1)
   grid.add_text("Cell 6", row=1, col=2)

   # Render the grid
   img = grid.render()
   img.save("text_grid.png")

Plot Visualizations (Python)
-----------------------------

Create data plots without matplotlib:

.. code-block:: python

   from piltext import FontManager, ImagePlot

   # Initialize font manager
   fm = FontManager()

   # Simple line plot with y-values only
   data = [20, 22, 19, 25, 23, 27, 24]
   plot = ImagePlot(data, fm, plot_type='line',
                    title='Temperature',
                    xlabel='Hour', ylabel='°C')
   img = plot.render()
   img.save("line_plot.png")

   # Bar chart with (x, y) tuples
   data = [(0, 10), (1, 15), (2, 13), (3, 18)]
   plot = ImagePlot(data, fm, plot_type='bar',
                    fg_color='#2196F3',
                    title='Sales')
   img = plot.render()
   img.save("bar_chart.png")

   # Multi-series line plot
   data = {
       'Temperature': [20, 22, 21, 23, 24],
       'Humidity': [60, 55, 58, 52, 50]
   }
   plot = ImagePlot(data, fm, plot_type='line',
                    fg_color=['#FF5722', '#2196F3'],
                    show_legend=True)
   img = plot.render()
   img.save("multi_series.png")

Examples
--------

PILText includes example configuration files in the ``examples/`` directory:

- ``example_simple.toml`` - Basic text grid
- ``example_grid_with_plots.toml`` - Grid with embedded plots
- ``example_plot.toml`` - Standalone plot examples
- ``example_dial.toml`` - Dial visualizations
- ``example_squares.toml`` - Square visualizations

Try them with:

.. code-block:: bash

   piltext render examples/example_grid_with_plots.toml -o output.png
