import typer
import os
import re
import fitz
import json
import yaml
import sqlite3 as sql

from itertools import groupby
from pathlib import Path
from rich import print
from typing_extensions import Annotated

# from scholarly import scholarly

from slh.config import load_config

app = typer.Typer()
configData = load_config()


def print_pdf_text(page, rect):
    """Return text containted in the given rectangular highlighted area.

    Args:
        page (fitz.page): the associated page.
        rect (fitz.Rect): rectangular highlighted area.
    """
    words = page.get_text("words")  # list of words on page
    words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x
    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    group = groupby(mywords, key=lambda w: w[3])
    for y1, gwords in group:
        print(" ".join(w[4] for w in gwords))


#
# PorP output format
#
# 0,"X Chen","Information moderation principle on the regulatory sandbox",2023,"Economic Change and Restructuring","Springer","https://link.springer.com/article/10.1007/s10644-022-09415-2","",31,"2023-09-23 17:00:55","","10.1007/s10644-022-09415-2","","",,,,,0,0.00,0,1,1,"… the regulatory sandbox … regulatory sandbox (Arner et al. 2016; Allen 2017; Yang 2018; Zhang and Chen 2018), we examine the information moderation principle of a regulatory sandbox …","","https://scholar.google.com/scholar?q=related:ds6rWLL7zU4J:scholar.google.com/&scioq=intitle:regulatory+intitle:sandbox&hl=en&as_sdt=2007"

# Cites	Authors	Title	Year	Source	Publisher	ArticleURL	CitesURL	GSRank	QueryDate	Type	DOI	ISSN	CitationURL	Volume	Issue	StartPage	EndPage	ECC	CitesPerYear	CitesPerAuthor	AuthorCount	Age	Abstract	FullTextURL	RelatedURL
# 0	X Chen	Information moderation principle on the regulatory sandbox	2023	Economic Change and Restructuring	Springer	https://link.springer.com/article/10.1007/s10644-022-09415-2		31	2023-09-23 17:00:55		10.1007/s10644-022-09415-2							0	0.00	0	1	1	… the regulatory sandbox … regulatory sandbox (Arner et al. 2016; Allen 2017; Yang 2018; Zhang and Chen 2018), we examine the information moderation principle of a regulatory sandbox …		https://scholar.google.com/scholar?q=related:ds6rWLL7zU4J:scholar.google.com/&scioq=intitle:regulatory+intitle:sandbox&hl=en&as_sdt=2007

# Chen, X (2023). Information moderation principle on the regulatory sandbox. Economic Change and Restructuring, Springer, <https://doi.org/10.1007/s10644-022-09415-2>
# [
# 	{
# 		"title": "Information moderation principle on the regulatory sandbox",
# 		"source": "Economic Change and Restructuring",
# 		"publisher": "Springer",
# 		"doi": "10.1007/s10644-022-09415-2",
# 		"article_url": "https://link.springer.com/article/10.1007/s10644-022-09415-2",
# 		"related_url": "https://scholar.google.com/scholar?q=related:ds6rWLL7zU4J:scholar.google.com/&scioq=intitle:regulatory+intitle:sandbox&hl=en&as_sdt=2007",
# 		"abstract": "… the regulatory sandbox … regulatory sandbox (Arner et al. 2016; Allen 2017; Yang 2018; Zhang and Chen 2018), we examine the information moderation principle of a regulatory sandbox …",
# 		"rank": 31,
# 		"year": 2023,
# 		"volume": 0,
# 		"issue": 0,
# 		"startpage": 0,
# 		"endpage": 0,
# 		"cites": 0,
# 		"ecc": 0,
# 		"use": 1,
# 		"authors": [
# 			"X Chen"
# 		]
# 	}
# ]


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
    # get the file path for cov number
    pdf_dir = Path.cwd() / configData["pdf_path"]
    pdf_path = None
    pdf_cov = None
    # open a file if first element matches covidence number
    for file_name in os.listdir(pdf_dir):
        pdf_cov = re.findall(r"\d+", file_name)
        if pdf_cov and pdf_cov[0] == cov:
            pdf_path = os.path.join(pdf_dir, file_name)
            break

    if pdf_path is None:
        print(f"PDF not found for {cov}")
        return

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
