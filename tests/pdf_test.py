import unittest
from slh_sh.utils.pdf import get_pdf_text, rgb_to_hex, hex_to_rgb, is_color_close

class TestPDFMethods(unittest.TestCase):

    def test_rgb_to_hex(self):
        self.assertEqual(rgb_to_hex((1, 1, 1)), '#ffffff')
        self.assertEqual(rgb_to_hex((0, 0, 0)), '#000000')
        self.assertEqual(rgb_to_hex((0.5, 0.5, 0.5)), '#7f7f7f')

    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb('#ffffff'), (255, 255, 255))
        self.assertEqual(hex_to_rgb('#000000'), (0, 0, 0))
        self.assertEqual(hex_to_rgb('#7f7f7f'), (127, 127, 127))

    def test_is_color_close(self):
        self.assertTrue(is_color_close((1, 1, 1), '#ffffff'))
        self.assertFalse(is_color_close((0, 0, 0), '#ffffff'))
        self.assertTrue(is_color_close((0.5, 0.5, 0.5), '#7f7f7f', 50))

    # Mocking required for get_pdf_text as it requires a fitz.page object and a fitz.Rect object
    # def test_get_pdf_text(self):
    #     self.assertEqual(get_pdf_text(page, rect), expected_result)

if __name__ == '__main__':
    unittest.main()