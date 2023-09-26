import typer
import os
import yaml


def saveConfigFile(
    project_name, gs_url, csv_export, html_export, google_credentials, sqlite_db
):
    """Generates and saves config.yaml file

    Returns:
        str: message
    """
    config = {
        "project_name": project_name,
        # URL to Google Sheet
        "gs_url": gs_url,
        # URL to Google Drive
        "gd_url": "",
        # Name of the default CSV file
        "csv_export": csv_export,
        # Name of the default HTML file
        "html_export": html_export,
        # Name of id of html element
        "html_id_element": "study-header",
        # Name of download class in html element
        "html_dl_class": "action-link download",
        # Name of the default Google Credentials file
        "google_credentials": google_credentials,
        # Name of the default SQLite Database file
        "sqlite_db": sqlite_db,
        # Name of the default PDF folder
        "pdf_path": "studies_pdf",
        # Number of the header row in Google Sheet
        "gs_header_row_number": "3",
        # Name of the Studies sheet in Google Sheet
        "gs_studies_sheet_name": "Studies",
        # Name of the ID column in Google Sheet
        "gs_studies_id_column_name": "Covidence",
        # Themes, Searches, and Sources will be added to database with sync yaml command
        # Themes (colors) for the annotations
        "themes": {
            # Theme name (color)
            "blue": {
                # Theme color in hex
                "hex": "#3389FF",
                # Theme annotation (Topic)
                "term": "Challenges in AI Laws",
            },
            "red": {
                "hex": "#FF3333",
                "term": "Challenges in AI Ethics",
            },
            "vio": {
                "hex": "#CC33FF",
                "term": "Challenges in AI Politics",
            },
        },
        # Searches (keywords) for the studies
        "searches": {
            "search_1": "AI and Regulations",
            "search_2": "AI, Regulations",
        },
        # Sources (where the study is found)
        "sources": {
            "source_1": "Google Scholar",
            "source_2": "Scopus",
            "source_3": "University Library",
        },
    }

    config_yaml_path = os.path.join(".", "config.yaml")
    if os.path.exists(config_yaml_path):
        yes = typer.prompt(
            f"""

            Config file already exists at {config_yaml_path}.

            Enter (y) to overwrite the file.

            Press Ctrl+C to exit.

            """
        )
        if yes == "y":
            with open(config_yaml_path, "w") as f:
                f.write(
                    """#
# Config file for slh
#
# project_name - Name of the project directory
# gs_url - URL to Google Sheet
# gd_url - URL to Google Drive
# csv_export - Name of the default CSV file
# html_export - Name of the default HTML file
# html_id_element - Name of id of html element
# html_dl_class - Name of download class in html element
# google_credentials - Name of the default Google Credentials file
# sqlite_db - Name of the default SQLite Database file
# pdf_path - Full path of the PDF folder e.g /Users/Sara/Downloads/uni/Thesis/SLR_Thesis_Lib
# gs_header_row_number - Number of the header row in Google Sheet
# gs_studies_sheet_name - Name of the Studies sheet in Google Sheet
# gs_studies_id_column_name - Name of the ID column in Google Sheet
# themes - Themes (colors) for the annotations
# searches - Searches (keywords) for the studies
# sources - Sources (where the study is found)
#
# Themes, Searches, and Sources will be added to database with sync yaml command
#
# yamllint disable rule:line-length
"""
                )
                yaml.dump(
                    config,
                    f,
                    indent=4,
                    width=100,
                    allow_unicode=True,
                    default_flow_style=False,
                    explicit_start=True,
                    encoding="utf-8",
                    sort_keys=False,
                    line_break=None,
                )
            return f"Config file created at {config_yaml_path}"
