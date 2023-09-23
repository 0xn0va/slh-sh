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
from slh.utils.pdf import print_pdf_text, rgb_to_hex
from slh.utils.file import get_file_path, fileNameGenerator


app = typer.Typer()
config_path = Path.cwd() / "config.yaml"
configData = load_config()


# TODO: make arguments and configs both accesible e.g. --sqlite


@app.command()
# TODO: make a func from name generator from filename command so
# this can create cit from authors column not filename user can choose if from db or csv
def cit(
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

    # APA 7 Citation
    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()
    # Check if Citation column exists in studies table if not Add Citation column to studies table
    curr.execute("PRAGMA table_info(studies)")
    rows = curr.fetchall()
    if "Citation" not in [row[1] for row in rows]:
        curr.execute("ALTER TABLE studies ADD COLUMN Citation TEXT")
    conn.commit()

    curr.execute("SELECT Covidence, Authors, Published_Year FROM studies")
    rows = curr.fetchall()
    # create apa 7 citation from rows
    citations = []
    authorNoneRemoved = []
    for row in rows:
        if None in row:
            print(f"{row} is none")
            authorNoneRemoved.append(row)
        else:
            fileName: str = fileNameGenerator(row[0], row[1], row[2])

            fileName = fileName.split("_")

            year = fileName[-1]
            if len(fileName) == 3:  # 1 author
                authorsName = fileName[1]
                citation = f"({authorsName}, {year})"
            elif len(fileName) == 4:  # 2 authors
                authorsName = f"{fileName[1]} & {fileName[2]}"
                citation = f"({authorsName}, {year})"
            elif len(fileName) == 5:  # more than 2 authors using first author and et al
                authorsName = f"{fileName[1]} et al."
                citation = f"({authorsName}, {year})"

            citation = f"({authorsName}, {row[2]})"

            # update citation column in studies table with the citation
            curr.execute(
                f"UPDATE studies SET Citation = '{citation}' WHERE Covidence = '{fileName[0]}'"
            )
            conn.commit()
            citations.append(citation)

    conn.close()
    print(citations)
    print(f"{len(citations)} citations added to the database")
    print(authorNoneRemoved)


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

    csvDF = pd.read_csv(csv)
    # convert column 'Published Year' from int to string in csvDF
    csvDF["Published Year"] = csvDF["Published Year"].astype(str)
    # replace all NaN values with 'None" in csvDF
    csvDF = csvDF.fillna("None")

    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()
    # Check if Bibliography column exists in studies table if not Add Bibliography column to studies table
    curr.execute("PRAGMA table_info(studies)")
    rows = curr.fetchall()
    if "Bibliography" not in [row[1] for row in rows]:
        curr.execute("ALTER TABLE studies ADD COLUMN Bibliography TEXT")
    conn.commit()

    # APA 7 Bibliography
    # create apa 7 bib from csv
    bibs = []
    for index, row in csvDF.iterrows():
        bib = {
            "covidenceNumber": row["Covidence #"],
            "author": row["Authors"],
            "year": row["Published Year"],
            "title": row["Title"],
            "journal": row["Journal"],
            "volume": row["Volume"],
            "issue": row["Issue"],
            "pages": row["Pages"],
        }
        bibs.append(bib)

    for bib in bibs:
        bibliography: str = f"{bib['author']} ({bib['year']}). {bib['title']}. {bib['journal']} {bib['volume']}({bib['issue']}), {bib['pages']}."
        cov: str = f"{bib['covidenceNumber']}"

        # Update the studies table with the bibliography
        curr.execute(
            "UPDATE studies SET Bibliography = ? WHERE Covidence = ?",
            (bibliography, cov),
        )
        conn.commit()

    conn.close()
    print(bibs)


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
    ] = "study-header",
    dllinkelement: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'a' element containing the URL of the PDF"
        ),
    ] = "action-link download",
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

    # Read the HTML file into a string.
    with open(html, "r") as f:
        html_string = f.read()

    # Create a BeautifulSoup object from the HTML string.
    soup = BeautifulSoup(html_string, "html.parser")

    # Find all of the elements with the class `study-header`.
    study_headers = soup.find_all("div", class_=idelement)

    # Iterate over the study headers and download the corresponding files.
    for study_header in study_headers:
        # Extract the study header number.
        study_header_number = re.findall("#(\d+)", study_header.text)[0]

        # Find the download link element.
        download_link_element = study_header.parent.find("a", class_=dllinkelement)

        # Extract the download link.
        download_link = download_link_element["href"]

        print(
            f"""
            :runner: Downloading PDF with ID {study_header_number} and URL {download_link}..."""
        )

        pdf_path = os.path.join(pdf_dir, f"{study_header_number}.pdf")

        if not os.path.exists(pdf_path):
            response = requests.get(download_link)
            if response.status_code == 200:
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                print(f"PDF downloaded: {pdf_path}")
                time.sleep(3)
            else:
                raise Exception(
                    f"""

                    [bold red]Error[/bold red]: {response.status_code}

                    Failed to download PDF: {download_link}, remove the section of the HTML file containing this link and try again.

                    """
                )
        else:
            print(f"PDF already exists: {pdf_path}")

    print(
        f"""
        :tada: {len(study_headers)} PDFs from {html} to {pdf_dir} downloaded.

        """
    )


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


# https://pymupdf.readthedocs.io/en/latest/page.html#page
# https://pymupdf.readthedocs.io/en/latest/vars.html#annotationtypes
# https://github.com/pymupdf/PyMuPDF/issues/318

# https://rgbcolorpicker.com/0-1


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
        print_pdf_text(page, annot.rect)
