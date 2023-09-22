from .config import load_config
import typer
from typing_extensions import Annotated
from rich import print
import webbrowser
import os
from pathlib import Path
import sys
import subprocess

app = typer.Typer()
configData = load_config()


@app.command()
def gd(
    url: Annotated[str, typer.Argument(
        help="Google Drive URL")] = configData["gd_url"]
):
    print(f"Opening Google Drive: {url}...")
    webbrowser.open(url)


@app.command()
def gs(
    url: Annotated[str, typer.Argument(
        help="Google Sheet URL")] = configData["gs_url"]
):
    print(f"Opening Google Sheet: {url}...")
    webbrowser.open(url)


@app.command()
def pdf(
    cov: Annotated[str, typer.Argument(
        help="Covidence number")],
    page: Annotated[str, typer.Option(
        help="Page number")] = ""

):
    pdf_path = None
    pdf_dir = Path.cwd() / "studies_pdf"
    for file_name in os.listdir(pdf_dir):
        if file_name.startswith(cov+"_"):
            pdf_path = os.path.join(pdf_dir, file_name)
            break

    if pdf_path is None:
        print(f"PDF not found for {cov}")
        sys.exit()

    if page != "":
        # open the pdf file with the page number with local pdf reader
        # open_pdf(cov, page)
        print(pdf_path)
        # check if os is windows
        if os.name == "nt":
            subprocess.run(["acroread", "--goto", str(page), pdf_path])
        # check if os is mac
        # elif os.name == "darwin":
        #     subprocess.run(["open", "-a", "Preview", pdf_path])
        # check if os is linux
        # elif os.name == "posix":
        #     subprocess.run(["xdg-open", pdf_path])
        else:
            print("OS not supported")

    else:
        typer.launch(pdf_path)


@app.command()
def db(
    sql: Annotated[str, typer.Argument(
        help="Name of SQLite database")] = configData["sqlite_db"]
):
    print(f"Opening SQLite database: {sql}...")

    sql_path = Path.cwd() / sql

    if sql_path is None:
        print(f"SQLite database not found")
        sys.exit()
    webbrowser.open(sql_path.as_uri())
