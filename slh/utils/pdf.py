import fitz

from itertools import groupby


def get_pdf_text(page, rect):
    """Return text containted in the given rectangular highlighted area.

    Args:
        page (fitz.page): the associated page.
        rect (fitz.Rect): rectangular highlighted area.
    """
    words = page.get_text("words")  # list of words on page
    words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x
    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    group = groupby(mywords, key=lambda w: w[3])
    for y1, gwords in group:
        print(" ".join(w[4] for w in gwords))


def rgb_to_hex(rgb):
    """Converts an RGB tuple to a hex string.

    Args:
    rgb: A tuple of 3 floats, representing the red, green, and blue components
        of the color, in the range [0, 1].

    Returns:
    A string representing the color in hexadecimal format.
    """

    r, g, b = rgb
    hex_r = int(r * 255)
    hex_g = int(g * 255)
    hex_b = int(b * 255)
    return f"#{hex_r:02x}{hex_g:02x}{hex_b:02x}"
