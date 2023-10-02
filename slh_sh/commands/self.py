import typer
import time

from pathlib import Path
from rich import print

from slh_sh.utils.config import saveConfigFile
from slh_sh.utils.db import create_db


app = typer.Typer()

default_project_name = (
    f"slr-ai-thesis-{time.strftime('%Y')}-{time.strftime('%m')}-{time.strftime('%d')}"
)


@app.command()
def check():
    print("Check...")


@app.command()
def version():
    print(
        """

            SLRs Little Helper (slh) v0.0.1

        """
    )


@app.command()
def update():
    print("Update...")


@app.command()
def backup():
    print("Backup...")


@app.command()
def restore():
    print("Restore...")


@app.command()
def logs():
    print("Logs...")


@app.command()
def list():
    """List all available commands and their descriptions."""
    # # Get a list of all commands in the app
    # typer_commands = app.registered_commands
    # print(typer_commands)

    # # Print a header
    # print("Available commands:")

    # # Iterate over the commands and print their names and descriptions
    # for command in typer_commands:
    #     name = command.__dict__["name"]
    #     print(f"- {name}: {command.help}")


@app.command()
def init(config: bool = typer.Option(False, help="Only create config file")):
    print(
        """

        Good day researcher! :wave:

        Welcome to slh :space_invader:

        It stands for SLRs Little Helper

        A CLI tool to help you with your Systematic Literature Review. :books:

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

            # Create the sqlite database
            sqlite_db_path = project_dir / sqlite_db
            create_db(sqlite_db_path)

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
