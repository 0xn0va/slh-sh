import typer
import os
import re
import fitz
import json
import yaml
import sqlite3 as sql

from pathlib import Path
from rich import print
from typing_extensions import Annotated

# from scholarly import scholarly

from slh.utils.config import load_config
from slh.utils.file import get_file_path

app = typer.Typer()
configData = load_config()


@app.command()
def info(
    cov: Annotated[str, typer.Argument(help="Covidence number")] = "",
    output: Annotated[str, typer.Option(help="Output format")] = "",
    wide: Annotated[bool, typer.Option(help="Wide format")] = False,
    # list: Annotated[bool, typer.Option(help="List all PDFs")] = False,
):
    if cov == "":
        print(
            f"""

There are {len(os.listdir(configData["pdf_path"]))} PDFs in {configData["pdf_path"]}

"""
        )
        if not wide:
            for file_name in os.listdir(configData["pdf_path"]):
                if not file_name.startswith("."):
                    print(file_name)
        else:
            print(
                "Print complete status for each file, including annotations, keywords, etc."
            )
    else:
        print(f"Info {cov}...")


@app.command()
# get dist [search term] --cov --output json/yaml/csv --wide # prints the distribution of the search term with its study details (title, authors, year, etc.)
def dist(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    output: Annotated[
        str,
        typer.Option(help="Output format, available options are Json, YAML and CSV"),
    ] = "",
    all: Annotated[bool, typer.Option(help="All")] = False,
    db: Annotated[bool, typer.Option(help="Database")] = False,
):
    pdf_path = get_file_path(cov)

    # search the term in the pdf file text and print the distribution of the term
    doc = fitz.open(pdf_path)
    pageNumbers = []
    found = 0
    for page in doc:
        res = page.search_for(term)
        for rect in res:
            found += 1
            pageNumbers.append(page.number)

    if db:
        conn: sql.connect = sql.connect(configData["sqlite_db"])
        curr: sql.Cursor = conn.cursor()
        rows = curr.fetchall()
        if "Distribution" not in [row[1] for row in rows]:
            print("Distribution Table not found in database")
            return
        # insert each into Distribution table
        # curr.execute()
        # if term found in themes table, insert total number into themes table
        # curr.execute(
        #     "INSERT INTO themes (Covidence, Term, Count) VALUES (?, ?, ?)",
        #     (cov, term, found),
        # )

    # count the number of instances of each number in pageNumber list
    pageNumbers = {str(i): pageNumbers.count(i) for i in pageNumbers}

    print(
        f"""
Found {found} instances
Term: {term}
PDF path: {pdf_path}
        """
    )
    print(
        f"""
'Pagenumber': Count[int]
        """
    )
    # convert pageNumber dict to json and print
    if output == "":
        print(pageNumbers)
    elif output == "json":
        # convert to json format
        print(json.dumps(pageNumbers, indent=4))
    elif output == "yaml":
        # convert to yaml format
        print(yaml.dump(pageNumbers, indent=4))
    elif output == "csv":
        # convert to csv format
        print("Pagenumber,Count")
        for key, value in pageNumbers.items():
            print(f"{key},{value}")


@app.command()
# get annots [search term] --output json/yaml/csv --wide # prints the annotations (themes) of the search term with its color
def annots(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    output: Annotated[str, typer.Option(help="Output format")] = "standard",
    all: Annotated[bool, typer.Option(help="All")] = False,
    wide: Annotated[bool, typer.Option(help="Wide format")] = False,
):
    print(f"Annots {term}...")


# @app.command()
# def scholar(
#     term: Annotated[str, typer.Argument(help="Search term")],
# ):
#     print(f"Searching Google Scholar for: {term}...")

#     search_query = scholarly.search_pubs(term)
#     print(next(search_query))


@app.command()
# themes table: id, color, hex, term
# Color = Theme = annotation (Topic) defined in Config.yaml e.g "Theme1": "Blue:Challenges in AI Laws"
# get theme [red] --dist --cov --term --wide --output json/yaml/csv
def theme(
    color: Annotated[str, typer.Argument(help="Theme color")],
    dist: Annotated[str, typer.Option(help="Distribution")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    term: Annotated[str, typer.Option(help="Term")],
    output: Annotated[str, typer.Option(help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(help="Wide format")] = False,
):
    print(f"Color {color}...")


@app.command()
# get search [search term] --cov --dist --output json/yaml/csv --wide # prints the study details (title, authors, year, etc.) of the search term with its keywords
def search(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    dist: Annotated[str, typer.Option(help="Distribution")],
    output: Annotated[str, typer.Option(help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(help="Wide format")] = False,
):
    print(f"Search {term}...")


@app.command()
# get keywords [search term] --cov --output json/yaml/csv --wide # prints the keywords of the search term with its study details (title, authors, year, etc.)
def keywords(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    output: Annotated[str, typer.Option(help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(help="Wide format")] = False,
):
    print(f"Keywords {term}...")
