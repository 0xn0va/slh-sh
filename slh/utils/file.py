import os

from pathlib import Path

from slh.utils.config import load_config

config_data = load_config()


def get_file_path(cov):
    """Return the file path for the given covidence number.

    Args:
        cov: ID column of the study specified in the config file and exists in the file name.
    """
    pdf_dir = Path.cwd() / config_data["pdf_path"]
    pdf_path = None
    pdf_cov = None

    for file_name in os.listdir(pdf_dir):
        pdf_cov: str = file_name.split("_")[0]
        pdf_cov = pdf_cov.replace("#", "")
        if pdf_cov == str(cov):
            pdf_path = os.path.join(pdf_dir, file_name)

    return pdf_path


def file_name_generator(covidence_number: str, authors: str, year: str) -> list[str]:
    """Generates a file name for the given covidence number, authors and year.

    Args:
        covidence_number (str): ID column of the study specified in the config file and exists in the file name.
        authors (str): Authors column
        year (str): Publication year column

    Returns:
        list[str]: Retuns a list of file names.
    """
    if ";" not in authors:
        last_name: str = authors.split(",")[0].strip()
        name: str = f"{covidence_number}_{last_name}_{year}"
        return name
    elif authors.count(";") == 1:
        last_name_1: str = authors.split(";")[0].split(",")[0].strip()
        last_name_2: str = authors.split(";")[1].split(",")[0].strip()
        name: str = f"{covidence_number}_{last_name_1}_{last_name_2}_{year}"
        return name
    elif authors.count(";") > 1:
        last_name: str = authors.split(";")[0].split(",")[0].strip()
        name = f"{covidence_number}_{last_name}_et_al_{year}"
        return name
    else:
        return None
