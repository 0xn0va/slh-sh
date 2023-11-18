import typer
import sqlite3 as sql
import csv as csvimport

from typing_extensions import Annotated
from rich import print

from slh_sh.utils.file import get_conf

app = typer.Typer()


@app.command("csv")  # TODO: REFACTOR
# TODO: Adding new CSV file creates new DB, asks for DB name, and adds them to Config.yaml
def csv(
    csv: Annotated[
        str,
        typer.Argument(
            help=f"""
        Imports a CSV file into a SQLite database.

        1. Export the CSV file  from Covidence via Export > REFERENCES > Options [Full text review] > Format [CSV]
2. Rename to {get_conf("csv_export")}
3. Place it in the project directory.
    """
        ),
    ] = get_conf("csv_export"),
):
    input(
        f"""
        Press Enter to import:

        CSV File: {csv}
        Sqlite Database Name: {get_conf("sqlite_db")}

        Press Ctrl+C to cancel.
        """
    )
    print(
        f"""
        Importing {csv} to {get_conf('sqlite_db')}...
        """
    )

    with open(get_conf("csv_export"), "r") as f:
        reader = csvimport.reader(f)
        # Read the first line of the file to get the CSV headers
        headers = next(reader)

        headers = [header.replace(" ", "_").replace("_#", "") for header in headers]

        conn = sql.connect(get_conf("sqlite_db"))
        curr = conn.cursor()

        # check if gs_studies_id_column_name is not empty in config.yaml
        if get_conf("gs_studies_id_column_name") == "":
            print(
                "gs_studies_id_column_name is empty in config.yaml incremental number will be used as id."
            )
            # Create a new table in the SQLite database with the same columns as the CSV file headers and add an id column
            curr.execute(
                f"""CREATE TABLE IF NOT EXISTS studies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {", ".join(headers)}
            )"""
            )
        else:
            # Create a new table in the SQLite database with the same columns as the CSV file headers
            curr.execute(
                f"""CREATE TABLE IF NOT EXISTS studies (
                {", ".join(headers)}
            )"""
            )

            # Iterate over the rows of the CSV file and insert each row into the table in the database
            rows = []
            for row in reader:
                rows.append(tuple(row))

            # check if the study is already in the database based on the covidence number as id if not insert it
            for row in rows:
                curr.execute(
                    f"SELECT * FROM studies WHERE covidence_id = ?", (row[12],)
                )
                if len(curr.fetchall()) > 0:
                    print(
                        f":information_desk_person: {row[12]} is already in the database."
                    )
                else:
                    curr.execute(
                        # insert row into sqlite db
                        f"INSERT INTO studies ({', '.join(headers.lower())}) VALUES ({', '.join([f'?' for i in range(len(headers.lower()))])})",
                        row,
                    )
                    print(f":star: {row[12]} added to the database.")

    print(
        f"""
        :tada: {len(rows)} studies processed.

        """
    )

    f.close()
    conn.commit()
    conn.close()

