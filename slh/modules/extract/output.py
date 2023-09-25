import json
import yaml


def annots_output(page_number, hex_color, page_annots, text):
    # TODO: translate hex color to color name based on Themes/Topics from db,
    return_msg = f"""
Page number: {page_number}
Hex color: {hex_color}
Page annotations: {page_annots}
Text: {text}
"""

    return return_msg


##
## Distribution output
##


def dist_output(found_in_page_numbers, output):
    """Return the distribution output in the specified format

    Args:
        found_in_page_numbers (dict): Dict of page numbers where the search term was found
        output (cli optopm): csv, json, yaml, or empty string

    Returns:
        str: Distribution output in the specified format (output) or error message
    """
    if output == "":
        return found_in_page_numbers
    elif output == "json":
        return json.dumps(found_in_page_numbers, indent=4)
    elif output == "yaml":
        return yaml.dump(found_in_page_numbers, indent=4)
    elif output == "csv":
        csv_return = "Page number,Count\n"
        for key, value in found_in_page_numbers.items():
            csv_return += f"{key},{value}\n"
        return csv_return
    else:
        return "Invalid output format"
