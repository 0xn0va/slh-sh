import typer
import os
import sys
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
from slh.utils.pdf import get_pdf_text

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
    db: Annotated[bool, typer.Option(help="Database")] = False,
):
    pdf_path = get_file_path(cov)

    # search the term in the pdf file text and print the distribution of the term
    doc = fitz.open(pdf_path)
    totalCount = 0
    foundInPageNumbers = {}
    themeID = 0
    for page in doc:
        # get the paragraph text of the page the term was found in
        foundinPage = 0
        res = page.search_for(term)

        if res != []:
            for rect in res:
                foundinPage += 1
                totalCount += 1
            foundInPageNumbers[page.number + 1] = foundinPage

    for i, j in foundInPageNumbers.items():
        print(f"Page: {i} Count: {j}")
        blocks = doc.load_page(page_id=i - 1).get_textpage("blocks").extractBLOCKS()
        # print(blocks)
        paragraphText = blocks[4]
        for block in blocks:
            paragraphText = block[4]
            # check if term is in paragraph text
            if term in paragraphText:
                print(paragraphText)


    if db:
        conn: sql.connect = sql.connect(configData["sqlite_db"])
        curr: sql.Cursor = conn.cursor()
        curr.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='distribution'"
        )
        dbRes = curr.fetchone()
        if dbRes == None:
            print("Distribution Table not found in database")
            return
        # select theme id from themes table where term = term
        curr.execute(
            f"SELECT id FROM themes WHERE term ='{term}'",
        )
        dbRes: str = curr.fetchone()
        if dbRes == None:
            print("Term not found in themes table")
        else:
            themeID = int(dbRes[0])
            # if term found in themes table insert total number into themes table where studyID = cov
            curr.execute(
                "INSERT INTO themes (studiesID, color, hex, term, totalCount) VALUES (?, ?, ?, ?, ?)",
                (cov, dbRes[2], dbRes[3], term, totalCount),
            )
        for i, j in foundInPageNumbers.items():
            curr.execute(
                "INSERT INTO distribution (studiesID, themeID, term, pageNum, count) VALUES (?, ?, ?, ?, ?)",
                (cov, themeID, term, i, j),
            )
        conn.commit()
        conn.close()
    print(
        f"""
Found {totalCount} instances
Term: {term}
PDF path: {pdf_path}
        """
    )
    if output == "":
        print(foundInPageNumbers)
    elif output == "json":
        # convert to json format
        print(json.dumps(foundInPageNumbers, indent=4))
    elif output == "yaml":
        # convert to yaml format
        print(yaml.dump(foundInPageNumbers, indent=4))
    elif output == "csv":
        # convert to csv format
        print("Pagenumber,Count")
        for key, value in foundInPageNumbers.items():
            print(f"{key},{value}")


@app.command()
# get annots [search term] --output json/yaml/csv --wide # prints the annotations (themes) of the search term with its color
def annots(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")],
    output: Annotated[
        str,
        typer.Option(help="Output format, available options are Json, YAML and CSV"),
    ] = "standard",
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
