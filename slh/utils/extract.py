import os
import time
import re
import requests
import pandas as pd
import sqlite3 as sql

from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text


from slh.utils.config import load_config
from slh.utils.file import fileNameGenerator

configData = load_config()


##
## Extract Citation
##


def extract_cit():
    """Extracts the citation from the file name and updates the citation column in the studies table

    Returns:
        list, list: List of citations, List of rows with None values
    """

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

    return citations, authorNoneRemoved


##
## Extract Bibliography
##


def extract_bib(csv):
    """Extracts the bibliography from the csv file and updates the bibliography column in the studies table

    Args:
        csv (FILE): csv file

    Returns:
        list: List of bibliographies
    """
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
    # TODO: get them from db and remove the need to pass csv
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

    return bibs


##
## Extract Download
##


def extract_dl(html, pdf_dir, idelement, dllinkelement):
    """Extracts the download link from the html file and downloads the pdf file

    Args:
        html (FILE): html file name from config.yaml
        pdf_dir (str): pdf folder name from config.yaml
        idelement (str): id element of dllinkelement name from cli option or config.yaml
        dllinkelement (str): download link element that contains a element and a URL, from cli option or config.yaml

    Raises:
        Exception: Bad response status code, remove the section of the HTML file containing this link and try again.

    Returns:    TODO: return the pdf file name
        Soup result: result of the soup.find_all
    """
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

    return study_headers


##
## Extract Filename
##


def extract_filename(csv, rename=False):
    """Extracts the filename from the csv file and updates the filename column in the studies table

    Args: TODO: add name convention options
        csv (FILE): csv file
        rename (BOOL): rename the pdf file

    Returns:
        LIST: List of file names
    """
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

    return fileNames


##
## Extract Keywords
##


def extract_keywords(cov, pdf_path, db=False):
    """Extracts the keywords from the pdf file and updates the keywords column in the studies table

    Args:
        cov (INT): Covidence number
        pdf_path (PATH): Path to the pdf file
        db (bool, optional): Save to database? Defaults to False.

    Returns:
        _type_: _description_
    """
    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()
    # Check if Bibliography column exists in studies table if not Add Bibliography column to studies table
    curr.execute("PRAGMA table_info(studies)")

    rows = curr.fetchall()
    if "Keywords" not in [row[1] for row in rows]:
        curr.execute("ALTER TABLE studies ADD COLUMN Keywords TEXT")
    conn.commit()

    print(f"Extracting keywords of: {pdf_path}...")

    text = extract_text(pdf_path)
    regex = r"(?is)(keyword.*?)(?:(?:\r*\n){2})"
    matches = re.findall(regex, text)
    length = len(matches)

    all_keywords = []
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

    return all_keywords
