import os
import unittest

from piltext import FontManager, ImageDrawer, TextBox


class TestTextBox(unittest.TestCase):
    def setUp(self):
        self.fontdirs = [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        ]
        self.font_manager = FontManager(fontdirs=self.fontdirs)
        self.image_drawer = ImageDrawer(255, 127, font_manager=self.font_manager)
        self.text_box = TextBox("Test", font_manager=self.font_manager)

    def test_fit_text_box(self):
        draw = self.image_drawer.draw
        self.text_box.text = "123456789 abcdef"
        max_width = 254
        max_height = 16
        font = self.text_box.fit_text(
            draw, max_width, max_height, font_name="Roboto-Bold", start_font_size=1
        )

        width, height = self.font_manager.calculate_text_size(
            draw, self.text_box.text, font
        )
        self.assertTrue(width <= max_width)
        self.assertTrue(height <= max_height)

    def test_fit_text_minimum_size(self):
        draw = self.image_drawer.draw
        self.text_box.text = "Very Long Text That Cannot Fit"
        font = self.text_box.fit_text(draw, 10, 10, font_name="Roboto-Bold")
        self.assertEqual(font.size, 1)

    def test_draw_text(self):
        draw = self.image_drawer.draw
        font = self.font_manager.build_font("Roboto-Bold", 20)
        self.text_box.draw_text(draw, (10, 10), font, fill="black")
        img = self.image_drawer.get_image()
        self.assertIsNotNone(img)

    def test_draw_text_with_kwargs(self):
        draw = self.image_drawer.draw
        font = self.font_manager.build_font("Roboto-Bold", 20)
        self.text_box.draw_text(
            draw, (10, 10), font, fill="red", stroke_width=2, stroke_fill="blue"
        )
        img = self.image_drawer.get_image()
        self.assertIsNotNone(img)

    def test_get_wrapped_text_lines(self):
        draw = self.image_drawer.draw
        font = self.font_manager.build_font("Roboto-Bold", 20)
        text = "This is a long text that needs to be wrapped"
        lines = self.text_box.get_wrapped_text_lines(draw, text, font, 100)
        self.assertIsInstance(lines, list)
        self.assertGreater(len(lines), 1)

    def test_get_wrapped_text_lines_single_line(self):
        draw = self.image_drawer.draw
        font = self.font_manager.build_font("Roboto-Bold", 20)
        text = "Short"
        lines = self.text_box.get_wrapped_text_lines(draw, text, font, 500)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "Short")

    def test_get_wrapped_text_lines_long_word(self):
        draw = self.image_drawer.draw
        font = self.font_manager.build_font("Roboto-Bold", 20)
        text = "VeryLongWordThatExceedsMaxWidth another word"
        lines = self.text_box.get_wrapped_text_lines(draw, text, font, 50)
        self.assertIsInstance(lines, list)
        self.assertGreater(len(lines), 0)


if __name__ == "__main__":
    unittest.main()
