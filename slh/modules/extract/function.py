import os
import time
import re
import fitz
import requests
import pandas as pd
import sqlite3 as sql

from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

from slh.utils.config import load_config
from slh.utils.file import file_name_generator
from slh.utils.pdf import (
    rgb_to_hex,
    get_pdf_text,
    is_color_close,
)

config_data = load_config()


##
## Extract Citation
##


def extract_cit():
    """Extracts the citation from the file name and updates the citation column in the studies table

    Returns:
        list, list: List of citations, List of rows with None values
    """

    # APA 7 Citation
    conn: sql.connect = sql.connect(config_data["sqlite_db"])
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
            fileName: str = file_name_generator(row[0], row[1], row[2])

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
        csv (file): csv file

    Returns:
        list: List of bibliographies
    """
    csv_df = pd.read_csv(csv)
    # convert column 'Published Year' from int to string in csv_df
    csv_df["Published Year"] = csv_df["Published Year"].astype(str)
    # replace all NaN values with 'None" in csv_df
    csv_df = csv_df.fillna("None")

    conn: sql.connect = sql.connect(config_data["sqlite_db"])
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
    for index, row in csv_df.iterrows():
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


def extract_dl(html, pdf_dir, html_id_element, html_dl_class):
    """Extracts the download link from the html file and downloads the pdf file

    Args:
        html (file): html file name from config.yaml
        pdf_dir (str): pdf folder name from config.yaml
        html_id_element (str): id element of html_dl_class name from cli option or config.yaml
        html_dl_class (str): download link element that contains a element and a URL, from cli option or config.yaml

    Raises:
        Exception: Bad response status code, remove the section of the HTML file containing this link and try again.

    Returns:    TODO: return the pdf file name
        Soup result: result of the soup.find_all
    """
    with open(html, "r") as f:
        html_string = f.read()

    soup = BeautifulSoup(html_string, "html.parser")

    study_headers = soup.find_all("div", class_=html_id_element)

    for study_header in study_headers:
        study_header_number = re.findall("#(\d+)", study_header.text)[0]
        download_link_element = study_header.parent.find("a", class_=html_dl_class)
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
        csv (file): csv file
        rename (bool): rename the pdf file

    Returns:
        LIST: List of file names
    """
    csv_df = pd.read_csv(csv)
    # convert column 'Published Year' from int to string in csv_df
    csv_df["Published Year"] = csv_df["Published Year"].astype(str)
    # replace all NaN values with 'None" in csv_df
    csv_df = csv_df.fillna("None")

    conn: sql.connect = sql.connect(config_data["sqlite_db"])
    curr: sql.Cursor = conn.cursor()

    # Check if Filename column exists in studies table if not Add Filename column to studies table
    curr.execute("PRAGMA table_info(studies)")
    rows = curr.fetchall()
    if "Filename" not in [row[1] for row in rows]:
        curr.execute("ALTER TABLE studies ADD COLUMN Filename TEXT")
    conn.commit()

    file_names = []
    for i in csv_df["Authors"]:
        # select covidence # from csv_df where authors is i
        covidence_number: str = csv_df.loc[csv_df["Authors"] == i][
            "Covidence #"
        ].values[0]
        # select publicaiton year from csv_df where authors is i
        year: str = csv_df.loc[csv_df["Authors"] == i]["Published Year"].values[0]

        file_name: str = file_name_generator(covidence_number, i, year)
        curr.execute(
            f"UPDATE studies SET Filename = '{file_name}' WHERE Covidence ='{covidence_number}'"
        )
        conn.commit()
        if rename:
            pdf_path = os.path.join(config_data["pdf_path"], f"{covidence_number}.pdf")
            if os.path.exists(pdf_path) and not pdf_path.endswith(f"{file_name}.pdf"):
                os.rename(
                    pdf_path, os.path.join(config_data["pdf_path"], f"{file_name}.pdf")
                )
            else:
                print("file exists")
        file_names.append(file_name)

    conn.close()

    return file_names


##
## Extract Keywords
##


def extract_keywords(cov, pdf_path, db=False):
    """Extracts the keywords from the pdf file and updates the keywords column in the studies table

    Args:
        cov (int): Covidence number
        pdf_path (path): Path to the pdf file
        db (bool, optional): Save to database? Defaults to False.

    Returns:
        _type_: _description_
    """
    conn: sql.connect = sql.connect(config_data["sqlite_db"])
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


##
## Extract Annotations
##


def extract_annots(cov: int, color: str, pdf_path: str, db: bool = False):
    """Extracts the annotations from the pdf file and updates the annotations table in the database

    Args:
        cov (int): Covidence number
        color (str): Color of the annotations to extract
        pdf_path (str): Path to the pdf file
        db (bool, optional): Defaults to False

    Returns:
        total_count (int), return_list (list): Total count of the annotations found in the pdf file, and the list of the annotations
    """
    doc = fitz.open(pdf_path)
    total_count = 0
    page_annots = []
    page_number = 0
    return_list = []

    for page in doc:
        found_in_page = 0
        page_number = page.number + 1
        page_annots = page.annots()

        for annot in page_annots:
            if annot.type[1] == "Highlight":
                annot_color = annot.colors["stroke"]
                hex_color = rgb_to_hex(annot_color)
                annot_rgb_fixed = tuple(int(color * 255) for color in annot_color)
                if color != "":
                    # TODO: get theme info from db
                    theme_hex_color = "#a28ae5"
                    theme_description = "Regulatory Sandbox"
                    theme_color = "Magenta"
                    color_matched = is_color_close(annot_color, theme_hex_color)
                    if color_matched:
                        text = get_pdf_text(page, annot.rect)
                        if any(d["paragraph_text"] == text for d in return_list):
                            continue
                        else:
                            total_count += 1
                            found_in_page += 1
                            item = {
                                "covidence_number": cov,
                                "found_in_page": found_in_page,
                                "searched_color": color,
                                "page_number": page_number,
                                "annot_rgb_color": annot_rgb_fixed,
                                "annot_hex_color": hex_color,
                                "theme_hex_color": theme_hex_color,
                                "theme_description": theme_description,
                                "theme_color": theme_color,
                                "paragraph_text": text,
                            }
                            return_list.append(item)
                else:
                    text = get_pdf_text(page, annot.rect)
                    if any(d["paragraph_text"] == text for d in return_list):
                        continue
                    else:
                        total_count += 1
                        found_in_page += 1
                        item = {
                            "covidence_number": cov,
                            "found_in_page": found_in_page,
                            "page_number": page_number,
                            "annot_rgb_color": annot_rgb_fixed,
                            "annot_hex_color": hex_color,
                            "paragraph_text": text,
                        }
                        return_list.append(item)

        # if db:
        #     conn: sql.connect = sql.connect(config_data["sqlite_db"])
        #     curr: sql.Cursor = conn.cursor()
        #     curr.execute(
        #         "SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'"
        #     )
        #     db_res = curr.fetchone()
        #     if db_res == None:
        #         print("Annotations Table not found in database")
        #         return
        #     curr.execute(
        #         "INSERT INTO annotations (studiesID, themesID, annotation, pageNumber, text) VALUES (?, ?, ?, ?, ?)",
        #         (cov, themeID, "", page_number, hex_color, annot_list),
        #     )
        #     conn.commit()
        #     conn.close()

    return total_count, return_list


##
## Extract Distribution
##


def extract_dist(pdf_path, term, cov, db=False):
    """Extracts the distribution of the term from the pdf file and updates the distribution table in the database

    Args:
        pdf_path (path): The full path to the pdf file
        term (str): The term to search for in the pdf file
        cov (sid): Internal Study ID from the database e.g. Covidence number
        db (bool, optional): Save to the database? - Defaults to False.

    Returns:
        total_count (int), return_list (list): Total count of the term found in the pdf file, and the list of the distribution of the term
    """
    # search the term in the pdf file text and print the distribution of the term
    doc = fitz.open(pdf_path)
    total_count = 0
    return_list = []
    for page in doc:
        # get the paragraph text of the page the term was found in
        found_in_page = 0
        res = page.search_for(term)

        if res != []:
            for rect in res:
                text = get_pdf_text(page, rect)
                if any(d["paragraph_text"] == text for d in return_list):
                    continue
                else:
                    total_count += 1
                    found_in_page += 1
                    item: dict = {
                        "page_number": page.number + 1,
                        "term": term,
                        "found_in_page": found_in_page,
                        "paragraph_text": text,
                    }
                    return_list.append(item)

    # if db:
    #     conn: sql.connect = sql.connect(config_data["sqlite_db"])
    #     curr: sql.Cursor = conn.cursor()
    #     curr.execute(
    #         "SELECT name FROM sqlite_master WHERE type='table' AND name='distribution'"
    #     )
    #     db_res = curr.fetchone()
    #     if db_res == None:
    #         print("Distribution Table not found in database")
    #         return
    #     curr.execute(
    #         f"SELECT id FROM themes WHERE term ='{term}'",
    #     )
    #     db_res: str = curr.fetchone()
    #     if db_res == None:
    #         print("Term not found in themes table")
    #     else:
    #         theme_id = int(db_res[0])
    #         curr.execute(
    #             "INSERT INTO themes (studiesID, color, hex, term, totalCount) VALUES (?, ?, ?, ?, ?)",
    #             (cov, db_res[2], db_res[3], term, total_count),
    #         )
    #     for i, j in found_in_page_numbers.items():
    #         curr.execute(
    #             "INSERT INTO distribution (studiesID, themeID, term, pageNum, count) VALUES (?, ?, ?, ?, ?)",
    #             (cov, theme_id, term, i, j),
    #         )
    #     conn.commit()
    #     conn.close()

    return total_count, return_list
