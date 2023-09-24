import typer
import os
import re
import time
import fitz
import requests
import pandas as pd
import sqlite3 as sql

from rich import print
from pathlib import Path
from bs4 import BeautifulSoup
from typing_extensions import Annotated
from pdfminer.high_level import extract_text

from slh.utils.config import load_config
from slh.utils.pdf import get_pdf_text, rgb_to_hex
from slh.utils.file import get_file_path, fileNameGenerator
from slh.utils.extract import extract_cit, extract_bib, extract_dl


app = typer.Typer()
config_path = Path.cwd() / "config.yaml"
configData = load_config()


##
## Citation
##


@app.command("cit")
def cit(
    # needs csv?
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = configData[
        "csv_export"
    ],
):
    input(
        f"""
        Press Enter to generate citations:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {configData["gs_url"]}

        Press Ctrl+C to cancel.
        """
    )

    print(f"Extracting citations from db...")

    citations, authorNoneRemoved = extract_cit()

    print(citations)
    print(f"{len(citations)} citations added to the database")
    print(authorNoneRemoved)


##
## Bibliography
##


@app.command()
def bib(
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = configData[
        "csv_export"
    ],
):
    input(
        f"""
        Press Enter to generate bibliographies:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {configData["gs_url"]}

        Press Ctrl+C to cancel.
        """
    )

    bibs = extract_bib(csv)

    print("Bibliographies added to the database:")
    print(bibs)


##
## Download
##


@app.command()
def dl(
    html: Annotated[
        str,
        typer.Argument(
            help="HTML export containing Covidence Number and Download Links"
        ),
    ] = configData["html_export"],
    pdfdir: Annotated[str, typer.Argument(help="Directory to save PDFs")] = configData[
        "pdf_path"
    ],
    idelement: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'div' element containing Covidence Number or ID in a div"
        ),
    ] = configData["html_id_element"],
    dllinkelement: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'a' element containing the URL of the PDF"
        ),
    ] = configData["html_dl_class"],
):
    input(
        f"""
        Press Enter to download PDFs:

        HTML export File: {html}
        Study Folder: {pdfdir}

        Press Ctrl+C to cancel.
        """
    )

    print(
        f"""

            Downloading PDFs from {html}...

            """
    )

    # Create the PDF directory if it doesn't exist.
    pdf_dir = Path.cwd() / pdfdir
    if not pdf_dir.is_dir():
        pdf_dir.mkdir()

    study_headers = extract_dl(html, pdf_dir, idelement, dllinkelement)

    print(
        f"""
        :tada: {len(study_headers)} PDFs from {html} to {pdf_dir} downloaded.

        """
    )


##
## Filename
##


@app.command()
def filename(
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = configData[
        "csv_export"
    ],
    rename: Annotated[bool, typer.Option(help="Also Rename the PDFs")] = False,
):
    """

    To link the Filenames on Google Sheet with the PDFs on Google Drive: https://github.com/0xnovasky/SLRsLittleHelper/tree/main/slh

    """
    print(f"Extracting filenames from {csv}...")

    csvDF = pd.read_csv(csv)
    # convert column 'Published Year' from int to string in csvDF
    csvDF["Published Year"] = csvDF["Published Year"].astype(str)
    # replace all NaN values with 'None" in csvDF
    csvDF = csvDF.fillna("None")

    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()

    # Check if Filename column exists in studies table if not Add Filename column to studies table
    curr.execute("PRAGMA table_info(studies)")
    rows = curr.fetchall()
    if "Filename" not in [row[1] for row in rows]:
        curr.execute("ALTER TABLE studies ADD COLUMN Filename TEXT")
    conn.commit()

    # TODO: make the arguments accessible to get naming schema from the command line and config file and add help

    fileNames = []
    for i in csvDF["Authors"]:
        # select covidence # from csvDF where authors is i
        covidenceNumber: str = csvDF.loc[csvDF["Authors"] == i]["Covidence #"].values[0]
        # select publicaiton year from csvDF where authors is i
        year: str = csvDF.loc[csvDF["Authors"] == i]["Published Year"].values[0]

        fileName: str = fileNameGenerator(covidenceNumber, i, year)
        curr.execute(
            f"UPDATE studies SET Filename = '{fileName}' WHERE Covidence ='{covidenceNumber}'"
        )
        conn.commit()
        if rename:
            pdf_path = os.path.join(configData["pdf_path"], f"{covidenceNumber}.pdf")
            if os.path.exists(pdf_path) and not pdf_path.endswith(f"{fileName}.pdf"):
                os.rename(
                    pdf_path, os.path.join(configData["pdf_path"], f"{fileName}.pdf")
                )
            else:
                print("file exists")
        fileNames.append(fileName)

    conn.close()

    print(fileNames)
    print(
        f"Updated database with {len(fileNames)} filenames on studies Table, Filenames column..."
    )
    if rename:
        print(
            f"Renamed {len(fileNames)} PDFs in {configData['pdf_path']} folder with the filenames..."
        )


##
## Keywords
##


@app.command()
def keywords(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")] = "",
    all: Annotated[
        bool,
        typer.Option(
            help="Extract keywords from all PDFs in configData['pdf_path'] folder"
        ),
    ] = False,
    db: Annotated[bool, typer.Option(help="SQLite database file")] = False,
):
    print(f"Keywords {cov}...")

    if db:
        conn: sql.connect = sql.connect(configData["sqlite_db"])
        curr: sql.Cursor = conn.cursor()
        # Check if Bibliography column exists in studies table if not Add Bibliography column to studies table
        curr.execute("PRAGMA table_info(studies)")
        rows = curr.fetchall()
        if "Keywords" not in [row[1] for row in rows]:
            curr.execute("ALTER TABLE studies ADD COLUMN Keywords TEXT")
        conn.commit()

    pdf_dir = Path.cwd() / configData["pdf_path"]
    pdf_path = None

    if all:
        all_keywords = []
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            pdf_path = get_file_path(cov)
            # pdf_path = os.path.join(pdf_dir, file_name)
            print(f"Extracting keywords of: {pdf_path}...")
            text = extract_text(pdf_path)
            regex = r"(?is)(keyword.*?)(?:(?:\r*\n){2})"
            matches = re.findall(regex, text)
            length = len(matches)
            if length == 0:
                print(f"Keywords not found for {pdf_path}")
                all_keywords.append(f"{cov} None")
            elif length >= 1:
                keywords = (
                    matches[0]
                    .replace("\n", " ")
                    .replace("Keywords:", "")
                    .replace("KEYWORDS:", "")
                    .replace("Keywords", "")
                    .replace("KEYWORDS", "")
                    .strip()
                )
                all_keywords.append(f"{cov} {keywords}")
                print(cov, keywords)
                if db:
                    curr.execute(
                        f"UPDATE studies SET Keywords = '{keywords}' WHERE Covidence = '{cov}'"
                    )
                    conn.commit()
        conn.close()
        print(all_keywords)
        print(
            f"Extracted keywords from {len(all_keywords)} PDFs and added them to the Database..."
        )

    elif cov != "":
        # open a file if first element matches covidence number
        # for file_name in os.listdir(pdf_dir):
        #     if file_name.startswith(cov + "_"):
        #         pdf_path = os.path.join(pdf_dir, file_name)
        #         break

        # if pdf_path is None:
        #     print(f"PDF not found for {cov}")
        #     return
        pdf_path = get_file_path(cov)

        text = extract_text(pdf_path)

        regex = r"(?is)(keyword.*?)(?:(?:\r*\n){2})"
        matches = re.findall(regex, text)

        if len(matches) == 0:
            print(f"Keywords not found for {pdf_path}")
        elif len(matches) >= 1:
            keywords = (
                matches[0]
                .replace("Keywords:", "")
                .replace("KEYWORDS:", "")
                .replace("Keywords", "")
                .replace("KEYWORDS", "")
                .strip()
            )
            if db:
                curr.execute(
                    f"UPDATE studies SET Keywords = '{keywords}' WHERE Covidence = '{cov}'"
                )
                conn.commit()
                conn.close()
                print(f"Added keywords of {cov} to db")
            print(f"Keywords for {cov} located at {pdf_path}:\n\n{keywords}")
    else:
        print(
            "Please enter a covidence number using --cov [Covidence Number] or use --all"
        )


##
## Annotations
##


@app.command()
def annots(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")],
    color: Annotated[str, typer.Option(help="Color of the annotations to extract")],
):
    print(f"Fetching Annotations of {color} (themes,topic,colored texts) from {cov}...")

    pdf_path = get_file_path(cov)

    # TODO: make this work with all pdfs
    doc = fitz.open(pdf_path)

    # TODO: make this work with all pages
    page = doc[0]
    annots = page.annots()
    print(annots)
    for annot in annots:
        if annot.type[1] == "Highlight":
            annotColor = annot.colors["stroke"]
            hex_color = rgb_to_hex(annotColor)
            # TODO: translate hex color to color name based on Themes/Topics from db,
            # check if config file is sync first
        print("------------------")
        print(f"info: {annot}")
        print(hex_color)
        get_pdf_text(page, annot.rect)
