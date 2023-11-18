import typer
import os
import json
import sqlite3 as sql
import pyperclip

from rich import print
from typing_extensions import Annotated

# from scholarly import scholarly
from slh_sh.utils.file import get_conf

app = typer.Typer()


@app.command()
def info(
    cov: Annotated[str, typer.Argument(help="Covidence number")] = "",
    table: Annotated[str, typer.Option(help="Table name")] = "studies",
    idcol: Annotated[str, typer.Option(help="ID column name")] = "covidence_id",
    copy: Annotated[bool, typer.Option(help="Copy to clipboard")] = False,
):
    """Get info about a study and its Citation and Bibliography from a database table by ID."""

    if cov == "":
        for file_name in os.listdir(get_conf("pdf_path")):
            if not file_name.startswith("."):
                print(file_name)
        print(
            f"""

There are {len(os.listdir(get_conf("pdf_path")))} PDFs in {get_conf("pdf_path")}

"""
        )
    else:
        conn = sql.connect(get_conf("sqlite_db"))
        curr = conn.cursor()

        curr.execute(f"SELECT * FROM {table} WHERE {idcol} = {cov}")
        db_res = curr.fetchone()
        if db_res == None:
            print(f"Study with the ID: {cov} not found in database table: {table}!")
        else:
            result = {}

            for i, col in enumerate(db_res):
                result[curr.description[i][0]] = col

            # TODO: unify id column names in config.yaml and in code (covidence_id vs covidence) to ID
            curr.execute(
                f"SELECT citation, bibliography FROM studies WHERE covidence_id = {cov}"
            )
            db_citbib = curr.fetchone()

            conn.close()

            result["citation"] = db_citbib[0]
            result["bibliography"] = db_citbib[1]

            json_data = json.dumps(result, indent=4)
            print(json_data)

            if copy:
                text_output = ""
                for key, value in result.items():
                    if isinstance(value, str):
                        text_output += f"{key}: {value}\n"
                pyperclip.copy(text_output)

                print(
                    """

Copied to clipboard!

"""
                )
