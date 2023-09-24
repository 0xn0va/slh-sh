import json
import yaml

##
## Distribution output
##


def dist_output(foundInPageNumbers, output):
    """Return the distribution output in the specified format

    Args:
        foundInPageNumbers (dict): Dict of page numbers where the search term was found
        output (cli optopm): csv, json, yaml, or empty string

    Returns:
        str: Distribution output in the specified format (output) or error message
    """
    if output == "":
        return foundInPageNumbers
    elif output == "json":
        return json.dumps(foundInPageNumbers, indent=4)
    elif output == "yaml":
        return yaml.dump(foundInPageNumbers, indent=4)
    elif output == "csv":
        csv_return = "Pagenumber,Count\n"
        for key, value in foundInPageNumbers.items():
            csv_return += f"{key},{value}\n"
        return csv_return
    else:
        return "Invalid output format"
