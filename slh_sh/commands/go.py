import typer
import webbrowser

from pathlib import Path
from rich import print
from typing_extensions import Annotated

from slh_sh.utils.file import get_file_path, get_conf

app = typer.Typer()


@app.command()
def gd(
    url: Annotated[str, typer.Argument(help="Google Drive URL")] = get_conf("gd_url")
):
    print(f"Opening Google Drive: {url}...")
    webbrowser.open(url)


@app.command()
def gs(
    url: Annotated[str, typer.Argument(help="Google Sheet URL")] = get_conf("gs_url")
):
    print(f"Opening Google Sheet: {url}...")
    webbrowser.open(url)


@app.command()
# https://www.foxit.com/pdf-reader/
def pdf(
    cov: Annotated[str, typer.Argument(help="Covidence number")] = "",
    # page: Annotated[str, typer.Option(help="Page number")] = "",
):
    pdf_path = get_file_path(cov)
    print(pdf_path)
    if pdf_path is None:
        print(f"PDF not found for {cov}")
        typer.Exit()
    else:
        typer.launch(pdf_path)
    ##
    ## Opens a PDF on certain page, Not Supported by PDF reader Apps or OS
    ##
    # if page != "":
    #     # open the pdf file with the page number with local pdf reader
    #     # open_pdf(cov, page)
    #     print(pdf_path)
    #     # check if os is windows
    #     if os.name == "nt":
    #         subprocess.run(["acroread", "--goto", str(page), pdf_path])
    #     # check if os is mac
    #     # elif os.name == "darwin":
    #     #     subprocess.run(["open", "-a", "Preview", pdf_path])
    #     # check if os is linux
    #     # elif os.name == "posix":
    #     #     subprocess.run(["xdg-open", pdf_path])
    #     else:
    #         print("OS not supported")


@app.command()
# https://sqlitebrowser.org/dl/
def db(
    sql: Annotated[str, typer.Argument(help="Name of SQLite database")] = get_conf(
        "sqlite_db"
    )
):
    print(f"Opening SQLite database: {sql}...")

    sql_path = Path.cwd() / sql

    if sql_path is None:
        print(f"SQLite database not found")
        typer.Exit()
    webbrowser.open(sql_path.as_uri())
