import typer
import time

from pathlib import Path
from rich import print

from slh_sh.utils.config import saveConfigFile

# from slh_sh.utils.db import create_db

slh_version: str = "0.1.8"

app = typer.Typer()

default_project_name: str = (
    f"slr-ai-thesis-{time.strftime('%Y')}-{time.strftime('%m')}-{time.strftime('%d')}"
)


@app.command()
def version():
    print(
        f"""

            SLRs Little Helper (slh) {slh_version}

        """
    )


@app.command()
def list():
    """List all available commands and their descriptions."""
    print(
        f"""

            SLRs Little Helper (slh) {slh_version}

            Usage: slh-sh [OPTIONS] COMMAND [ARGS]...

            Example:
                # slh-sh --help
                # slh-sh self --help
                # slh-sh extract cit --help

            Commands:
                - self
                    - init      # Initializes the project, questionaire or default config file
                    - list      # Lists all available commands
                    - check     # Checks if there is a new version
                    - update    # Updates to the latest version.
                    - backup    # Creates compressed backup file from the project directory.
                    - restore   # Restores the project directory from the backup file
                    - logs      # Shows the logs
                    - version   # Shows the version
                - add
                    - csv       # Loads studies.csv into sqlite database.
                - extract
                    - cit       # Extracts and generates APA 7 citation from the file name in db and updates the citation column in the studies table.
                    - bib       # Extracts the bibliography from the csv file and updates the bibliography column in the studies table.
                    - dl        # Extracts the download link from the html file and downloads the pdf files.
                    - filename  # Extracts the filename from the csv file and updates the filename column in the studies table.
                    - keywords  # Extracts the keywords from the pdf file and updates the keywords column in the studies table.
                    - annots    # Extracts the annotations from the pdf file and updates the annotations table in the database.
                    - dist      # Extracts the distribution of the term from the pdf file and updates the distribution table in the database.
                - sync
                    - update    # Update the Google Sheets with data from Database.
                    - fetch     # Fetch and save data from Google Sheet to a new database table.
                    - config    # Iterate over Themes, Searches, and Sources in config.yaml and insert into database.
                - get
                    - info      # Get info about a study and its Citation and Bibliography from a database table by ID.
                - go
                    - gd        # Opens the Google Drive folder.
                    - gs        # Opens the Google Sheet.
                    - pdf       # Opens a PDF file in the default PDF reader.
                    - db        # Opens the SQLite database file in the default database viewer.
                    - doi       # Opens the DOI URL in the default browser.
        """
    )


@app.command()
def check():
    print("Check... - Not Implemented Yet")


@app.command()
def update():
    print("Update... - Not Implemented Yet")


@app.command()
def backup():
    print("Backup... - Not Implemented Yet")


@app.command()
def restore():
    print("Restore... - Not Implemented Yet")


@app.command()
def logs():
    print("Logs... - Not Implemented Yet")


@app.command()
def init(config: bool = typer.Option(False, help="Only create config file")):
    print(
        """

        Good day researcher! :wave:

        Welcome to slh-sh :space_invader:

        It stands for SLRs Little Helper

        A CLI tool to help you with your Systematic Literature Review. :books:

        Visit https://slh.sh for more info.

        """
    )
    if config:
        res = saveConfigFile(
            default_project_name,
            "",
            "studies.csv",
            "export.html",
            "credentials.json",
            "slh.db",
        )
        print(res)
        return
    else:
        if typer.confirm(
            """

            Choose (Y) if you want to start initialization questionaire.

            Choose (n) to initialize with the default config file.

            """
        ):
            project_name = typer.prompt(
                """

                What is the name of your project? (e.g. slr-2023-4-19)

                    [ ] - A folder with this name will be created in your current directory.

                    Press Enter to use the default name.

                """,
                default=f"slr-ai-thesis-{time.strftime('%Y')}-{time.strftime('%m')}-{time.strftime('%d')}",
            )

            csv_export = typer.prompt(
                """

                What is the CSV filename?

                    e.g. studies.csv exported from Covidence

                    Press Enter to use the default name.

                """,
                default="studies.csv",
            )

            gs_url = typer.prompt(
                """

                What is the Google Sheet's URL?

                """
            )

            html_export = typer.prompt(
                """

                What is the HTML Export file name?

                    e.g. export.html containing ID and Download links

                    Press Enter to use the default name.

                """,
                default="export.html",
            )

            google_credentials = typer.prompt(
                """

                What is the name to your Google Credentials?

                    e.g. credentials.json

                    Press Enter to use the default name.

                """,
                default="credentials.json",
            )

            sqlite_db = typer.prompt(
                """

                What is the name to your SQLite Database?

                    e.g. slh.db

                    [ ] - It will be created by init command.

                    Press Enter to use the default name.

                """,
                default="slh.db",
            )

            # Create the project directory
            project_dir = Path.cwd() / project_name
            if not project_dir.is_dir():
                project_dir.mkdir()

            # # Create the sqlite database
            # sqlite_db_path = project_dir / sqlite_db
            # create_db(sqlite_db_path)

            if typer.confirm(
                """

                Do you want to create a new config file?

                """
            ):
                saveConfigFile(
                    project_name,
                    gs_url,
                    csv_export,
                    html_export,
                    google_credentials,
                    sqlite_db,
                )
        else:
            res = saveConfigFile(
                default_project_name,
                "",
                "studies.csv",
                "export.html",
                "credentials.json",
                "slh.db",
            )
            print(res)

        print(
            f"""

            :star: Project directory created at {project_dir}
            :star: Config file created at {project_dir}/config.yaml
            :star: sqlite database created at {project_dir}/{sqlite_db}

            [bold]Hooray! :space_invader:[/bold]

            Next Steps:

                - [yellow]Move credentials.json to the {project_dir}[/yellow]
                - [yellow]Move studies.csv to the {project_dir}[/yellow]
                - [yellow]Move export.html to the {project_dir}[/yellow]
                # [yellow]cd {project_dir}[/yellow]
                # [yellow]slh --help[/yellow]
                # [yellow]slh load csv[/yellow] # to load studies.csv into sqlite database

            """
        )
