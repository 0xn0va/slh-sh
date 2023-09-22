from pathlib import Path
import typer
from rich import print
# import json
import yaml
import time
import os

global_config_path: Path = Path.cwd() / "config.yaml"
if global_config_path.is_file():
    import commands.extract as extract
    import commands.get as get
    import commands.add as add
    import commands.go as go
    import commands.sync as sync
    import commands.self as self
else:
    print(
        '''
        [bold red]Alert![/bold red]

        Config file does not exist in current directory.

        Run [yellow]slh init[/yellow] to create one :rocket:
        ''')

# TODO: add new db tables: Annotations, Colors (theme list),
# Sources (add Source column to Studies), Searches (add Search column to Studies)

# https://til.simonwillison.net/homebrew/packaging-python-cli-for-homebrew

# TODO: refactor cov to id in all commands

app = typer.Typer()

APP_NAME = "slh"
APP_DIR = typer.get_app_dir(APP_NAME)
DEFAULT_PROJECT_NAME = f"slr-ai-thesis-{time.strftime('%Y')}-{time.strftime('%m')}-{time.strftime('%d')}"


@app.command()
def version():
    print('''

            SLRs Little Helper (slh) v0.0.1

        ''')


def saveConfigFile(project_name, gs_url, csv_export, html_export, google_credentials, sqlite_db):
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
        # Name of the default Google Credentials file
        "google_credentials": google_credentials,
        # Name of the default SQLite Database file
        "sqlite_db": sqlite_db,
        # Name of the default PDF folder
        "studies_pdf": "studies_pdf",
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

    fileYamlpath = os.path.join(".", 'config.yaml')
    if os.path.exists(fileYamlpath):
        yes = typer.prompt(
            f'''

            Config file already exists at {fileYamlpath}.

            Enter (y) to overwrite the file.

            Press Ctrl+C to exit.

            ''')
        if yes == "y":
            with open(fileYamlpath, "w") as f:
                f.write('''#
# Config file for slh
#
# project_name - Name of the project directory
# gs_url - URL to Google Sheet
# gd_url - URL to Google Drive
# csv_export - Name of the default CSV file
# html_export - Name of the default HTML file
# google_credentials - Name of the default Google Credentials file
# sqlite_db - Name of the default SQLite Database file
# studies_pdf - Name of the default PDF folder
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
''')
                yaml.dump(config, f, indent=4, width=100, allow_unicode=True, default_flow_style=False, explicit_start=True,
                          encoding='utf-8', sort_keys=False, line_break=None)
            return f"Config file created at {fileYamlpath}"


@app.command()
def init(
    config: bool = typer.Option(False, help="Only create config file")
):
    print('''

        Good day researcher! :wave:

        Welcome to slh :space_invader:

        It stands for SLRs Little Helper

        A CLI tool to help you with your Systematic Literature Review. :books:

        ''')
    if config:
        res = saveConfigFile(DEFAULT_PROJECT_NAME, "", "studies.csv",
                             "export.html", "credentials.json", "slh.db")
        print(res)
        return
    else:
        if typer.confirm(
            '''

            Choose (Y) if you want to start initialization questionaire.

            Choose (n) to initialize with the default config file.

            '''):

            project_name = typer.prompt(
                '''

                What is the name of your project? (e.g. slr-2023-4-19)

                    [ ] - A folder with this name will be created in your current directory.

                    Press Enter to use the default name.

                ''', default=f"slr-ai-thesis-{time.strftime('%Y')}-{time.strftime('%m')}-{time.strftime('%d')}")

            csv_export = typer.prompt(
                '''

                What is the CSV filename?

                    e.g. studies.csv exported from Covidence

                    Press Enter to use the default name.

                ''', default="studies.csv")

            gs_url = typer.prompt(
                '''

                What is the Google Sheet's URL?

                ''')

            html_export = typer.prompt(
                '''

                What is the HTML Export file name?

                    e.g. export.html containing ID and Download links

                    Press Enter to use the default name.

                ''', default="export.html")

            google_credentials = typer.prompt(
                '''

                What is the name to your Google Credentials?

                    e.g. credentials.json

                    Press Enter to use the default name.

                ''', default="credentials.json")

            sqlite_db = typer.prompt(
                '''

                What is the name to your SQLite Database?

                    e.g. slh.db

                    [ ] - It will be created by init command.

                    Press Enter to use the default name.

                ''', default="slh.db")

            # Create the project directory
            project_dir = Path.cwd() / project_name
            if not project_dir.is_dir():
                project_dir.mkdir()

            if typer.confirm(
                '''

                Do you want to create a new config file?

                '''):
                saveConfigFile(project_name, gs_url, csv_export,
                               html_export, google_credentials, sqlite_db)
        else:
            res = saveConfigFile(DEFAULT_PROJECT_NAME, "", "studies.csv",
                                 "export.html", "credentials.json", "slh.db")
            print(res)

        print(f'''

            :star: Project directory created at {project_dir}
            :star: Config file created at {project_dir}/config.yaml
            :star: sqlite database location is {project_dir}/{sqlite_db}

            [bold]Hooray! :space_invader:[/bold]

            Next Steps:

                - [yellow]Move credentials.json to the {project_dir}[/yellow]
                - [yellow]Move studies.csv to the {project_dir}[/yellow]
                - [yellow]Move export.html to the {project_dir}[/yellow]
                # [yellow]cd {project_dir}[/yellow]
                # [yellow]slh --help[/yellow]
                # [yellow]slh load csv[/yellow] # to load studies.csv into sqlite database

            ''')


if global_config_path.is_file():
    app.add_typer(extract.app, name="extract")
    app.add_typer(get.app, name="get")
    app.add_typer(add.app, name="add")
    app.add_typer(go.app, name="go")
    app.add_typer(sync.app, name="sync")
    app.add_typer(self.app, name="self")


if __name__ == '__main__':
    app()
