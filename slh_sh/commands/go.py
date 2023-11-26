import typer
import webbrowser
import sqlite3 as sql

from pathlib import Path
from rich import print
from typing_extensions import Annotated

from slh_sh.utils.file import get_file_path, get_conf
from slh_sh.utils.log import logger

app = typer.Typer()


@app.command()
def gd(
    url: Annotated[str, typer.Argument(help="Google Drive URL")] = get_conf("gd_url")
):
    """Opens the Google Drive folder in browser."""
    print(f"Opening Google Drive: {url}...")
    webbrowser.open(url)
    logger().info(f"Opened Google Drive: {url}")


@app.command()
def gs(
    url: Annotated[str, typer.Argument(help="Google Sheet URL")] = get_conf("gs_url")
):
    """Opens the Google Sheet in browser."""
    print(f"Opening Google Sheet: {url}...")
    webbrowser.open(url)
    logger().info(f"Opened Google Sheet: {url}")


@app.command()
# https://www.foxit.com/pdf-reader/
def pdf(
    id: Annotated[str, typer.Argument(help="ID, e.g. Covidence number")] = "",
    # page: Annotated[str, typer.Option(help="Page number")] = "",
):
    """Opens a PDF file in the default PDF reader."""
    pdf_path = get_file_path(id)
    print(pdf_path)
    if pdf_path is None:
        print(f"PDF not found for {id}")
        typer.Exit()
    else:
        typer.launch(pdf_path)
    logger().info(f"Opened PDF: {pdf_path}")


@app.command()
# https://sqlitebrowser.org/dl/
def db(
    sql: Annotated[str, typer.Argument(help="Name of SQLite database")] = get_conf(
        "sqlite_db"
    )
):
    """Opens the SQLite database in the default database viewer."""
    print(f"Opening SQLite database: {sql}...")

    sql_path = Path.cwd() / sql

    if sql_path is None:
        print(f"SQLite database not found")
        typer.Exit()
    webbrowser.open(sql_path.as_uri())
    logger().info(f"Opened SQLite database: {sql_path}")


@app.command()
def doi(
    id: Annotated[
        str, typer.Argument(help="ID of the study e.g Covidence Number")
    ] = get_conf("default_id"),
):
    """Opens the DOI of a study by ID in browser."""

    conn = sql.connect(get_conf("sqlite_db"))
    curr = conn.cursor()
    curr.execute(f"SELECT doi FROM studies WHERE {get_conf('default_id')} = {id}")
    doi = curr.fetchone()
    conn.close()
    if doi == None:
        print(f"DOI with the ID: {id} not found in database table: studies!")
    else:
        doi = doi[0]
        print(f"Opening DOI: {doi}...")
        webbrowser.open(f"https://doi.org/{doi}")
    logger().info(f"Opened DOI: {doi}")
