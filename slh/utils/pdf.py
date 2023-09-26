import fitz
import math

from itertools import groupby


def get_pdf_text(page, rect):
    """Return text containted in the given rectangular highlighted area.

    Args:
        page (fitz.page): the associated page.
        rect (fitz.Rect): rectangular highlighted area.
    """
    words = page.get_text("blocks")  # list of words on page
    words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x
    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    group = groupby(mywords, key=lambda w: w[3])
    for y1, gwords in group:
        pdf_text = " ".join(w[4] for w in gwords)
        pdf_text = pdf_text.replace("\n", " ").strip()
        return pdf_text


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


def hex_to_rgb(hex_color):
    """
    Converts a hex color to RGB.

    Args:
        hex_color: A string representing the hex code of the color.

    Returns:
        A tuple of three integers representing the RGB values of the color.
    """

    # Split the hex color into three parts.
    red, green, blue = hex_color[1:3], hex_color[3:5], hex_color[5:7]

    # Convert each part from hexadecimal to decimal.
    red = int(red, 16)
    green = int(green, 16)
    blue = int(blue, 16)

    # Return the RGB values as a tuple.
    return (red, green, blue)


def is_color_close(rgb_color, hex_color, threshold=50):
    """
    Checks if a RGB color is close enough to the provided hex color.

    Args:
        rgb_color: A tuple of three integers representing the RGB values of the color.
        hex_color: A string representing the hex code of the color.
        threshold: The maximum distance between the two colors for them to be considered close.

    Returns:
        True if the two colors are close enough, False otherwise.
    """

    rgb_of_config_hex = hex_to_rgb(hex_color)
    rgb_fixed = tuple(int(color * 255) for color in rgb_color)

    # Calculate the distance between the two colors.
    distance = math.sqrt(
        (rgb_fixed[0] - rgb_of_config_hex[0]) ** 2
        + (rgb_fixed[1] - rgb_of_config_hex[1]) ** 2
        + (rgb_fixed[2] - rgb_of_config_hex[2]) ** 2
    )

    # Return True if the distance is less than or equal to the threshold.
    return distance <= threshold
