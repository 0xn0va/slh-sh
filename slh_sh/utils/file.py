import os
import yaml
import random
import string

from pathlib import Path


def get_conf(key: str) -> str:
    """Returns the value of the given key in the config file.

    Args:
        key (str): Key in the config file.

    Returns:
        str: Value of the given key.
    """
    config_path = Path.cwd() / "config.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        return "config.yaml file does not exist."

    return config[key]


def get_pdf_dir() -> str:
    """Returns the path to the PDF directory.

    Returns:
        str: Path to the PDF directory.
    """
    return Path.cwd() / get_conf("pdf_path")


def get_file_path(id):
    """Return the file path for the given covidence number.

    Args:
        id: ID column of the study specified in the config file and exists in the file name.
    """
    pdf_dir = get_pdf_dir()
    pdf_path = None
    pdf_id = None

    for file_name in os.listdir(pdf_dir):
        pdf_id: str = file_name.split("_")[0].replace("#", "")
        if pdf_id == str(id):
            pdf_path = os.path.join(pdf_dir, file_name)

    return pdf_path


def file_name_generator(id: str, authors: str, year: str) -> list[str]:
    """Generates a file name for the given covidence number, authors and year.

    Args:
        id (str): ID column of the study specified in the config file and exists in the file name e.g. Covidence Number.
        authors (str): Authors column
        year (str): Publication year column

    Returns:
        list[str]: Retuns a list of file names.
    """
    if ";" not in authors:
        last_name: str = authors.split(",")[0].strip()
        name: str = f"{id}_{last_name}_{year}"
        return name
    elif authors.count(";") == 1:
        last_name_1: str = authors.split(";")[0].split(",")[0].strip()
        last_name_2: str = authors.split(";")[1].split(",")[0].strip()
        name: str = f"{id}_{last_name_1}_{last_name_2}_{year}"
        return name
    elif authors.count(";") > 1:
        last_name: str = authors.split(";")[0].split(",")[0].strip()
        name = f"{id}_{last_name}_et_al_{year}"
        return name
    else:
        return None


def get_random_string():
    """Generates a random string.

    Returns:
        str: Random lowercase 4 letters string.
    """
    random_string = "".join(random.choices(string.ascii_lowercase, k=4))
    return random_string
