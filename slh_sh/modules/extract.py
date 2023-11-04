import os
import time
import re
import fitz
import requests
import pandas as pd

import sys

from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

from slh_sh.utils.log import logger
from slh_sh.utils.db import get_db
from slh_sh.utils.file import file_name_generator, get_conf, get_random_string
from slh_sh.utils.pdf import (
    rgb_to_hex,
    get_pdf_text,
    is_color_close,
)
from slh_sh.modules.sync import (
    update_sheet_cell,
    get_spreadsheet_by_url,
    get_worksheet_by_name,
    get_worksheet_id_col_index_values,
    get_worksheet_updating_col_index_header,
    get_worksheet_headers_row_values,
    create_new_worksheet,
)
from slh_sh.data.models import (
    Study,
    Theme,
    Annotation,
    Distribution,
)


##
## Extract Citation
##


def extract_cit(db=False):
    """Extracts and generates APA 7 citation from the file name in db and updates the citation column in the studies table

    Returns:
        list, list: List of citations, List of rows with None values
    """

    dbs = get_db()
    rows = dbs.query(Study).all()

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

            if db:
                dbs.query(Study).filter(Study.covidence_id == fileName[0]).update(
                    {Study.citation: citation}
                )
                dbs.commit()
            citations.append(citation)

    return citations, authorNoneRemoved


##
## Extract Bibliography
##


def extract_bib(csv, db=False):
    """Extracts the bibliography from the csv file and updates the bibliography column in the studies table

    Args:
        csv (file): csv file

    Returns:
        list: List of bibliographies
    """
    csv_df = pd.read_csv(csv)
    csv_df["Published Year"] = csv_df["Published Year"].astype(str)
    csv_df = csv_df.fillna("None")

    dbs = get_db()

    bibs = []

    db_res = dbs.query(Study).all()

    for row in db_res:
        bib = {
            "covidence_number": row.covidence_id,
            "author": row.authors,
            "year": row.published_year,
            "title": row.title,
            "journal": row.journal,
            "volume": row.volume,
            "issue": row.issue,
            "pages": row.pages,
        }

        bibs.append(bib)

    for bib in bibs:
        bibliography: str = f"{bib['author']} ({bib['year']}). {bib['title']}. {bib['journal']} {bib['volume']}({bib['issue']}), {bib['pages']}."
        cov: str = f"{bib['covidence_number']}"

        if db:
            dbs.query(Study).filter(Study.covidence_id == cov).update(
                {Study.bibliography: bibliography}
            )
            dbs.commit()

    dbs.close()

    return bibs


##
## Extract Download
##


def extract_dl(html, pdf_dir, html_id_element, html_dl_class):
    """Extracts the download link from the html file and downloads the pdf files

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


def extract_filename(csv, rename=False, db=False):
    """Extracts the filename from the csv file and updates the filename column in the studies table

    Args: TODO: add name convention options
        csv (file): csv file
        rename (bool): rename the pdf file

    Returns:
        list: List of file names
    """
    csv_df = pd.read_csv(csv)
    csv_df["Published Year"] = csv_df["Published Year"].astype(str)
    csv_df = csv_df.fillna("None")

    file_names = []
    for i in csv_df["Authors"]:
        # select covidence # from csv_df where authors is i
        covidence_number: str = csv_df.loc[csv_df["Authors"] == i][
            "Covidence #"
        ].values[0]
        # select publicaiton year from csv_df where authors is i
        year: str = csv_df.loc[csv_df["Authors"] == i]["Published Year"].values[0]

        file_name: str = file_name_generator(covidence_number, i, year)

        if db:
            dbs = get_db()
            dbs.query(Study).filter(Study.covidence_id == covidence_number).update(
                {Study.filename: file_name}
            )
            dbs.commit()
            dbs.close()

        if rename:
            pdf_path = os.path.join(get_conf("pdf_path"), f"{covidence_number}.pdf")
            if os.path.exists(pdf_path) and not pdf_path.endswith(f"{file_name}.pdf"):
                os.rename(
                    pdf_path, os.path.join(get_conf("pdf_path"), f"{file_name}.pdf")
                )
            else:
                print("file exists")

        file_names.append(file_name)

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
            dbs = get_db()
            dbs.query(Study).filter(Study.covidence_id == cov).update(
                {Study.keywords: keywords}
            )
            dbs.commit()
            dbs.close()

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
    total_count = 0
    page_annots = []
    page_number = 0
    return_list = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            count = 0
            page_number = page.number + 1
            page_annots = page.annots()
            for annot in page_annots:
                if annot.type[1] == "Highlight":
                    annot_color = annot.colors["stroke"]
                    hex_color = rgb_to_hex(annot_color)
                    annot_rgb_fixed = tuple(int(color * 255) for color in annot_color)
                    if color != "":
                        dbs = get_db()
                        theme_data = (
                            dbs.query(Theme).filter(Theme.color == hex_color).first()
                        )
                        theme_color = theme_data.color
                        theme_term = theme_data.term
                        theme_hex_color = theme_data.hex
                        color_matched = is_color_close(annot_color, theme_hex_color)
                        if color_matched:
                            text = get_pdf_text(page, annot.rect)
                            if any(d["text"] == text for d in return_list):
                                continue
                            else:
                                total_count += 1
                                count += 1
                                item = {
                                    "covidence_number": cov,
                                    "count": count,
                                    "searched_color": color,
                                    "page_number": page_number,
                                    "annot_rgb_color": annot_rgb_fixed,
                                    "annot_hex_color": hex_color,
                                    "theme_hex_color": theme_hex_color,
                                    "theme_term": theme_term,
                                    "theme_color": theme_color,
                                    "text": text,
                                }
                                return_list.append(item)
                    else:
                        text = get_pdf_text(page, annot.rect)
                        if any(d["text"] == text for d in return_list):
                            continue
                        else:
                            total_count += 1
                            count += 1
                            item = {
                                "covidence_number": cov,
                                "count": count,
                                "page_number": page_number,
                                "annot_rgb_color": annot_rgb_fixed,
                                "annot_hex_color": hex_color,
                                "text": text,
                            }
                            return_list.append(item)

        if db:
            dbs = get_db()
            theme_id = dbs.query(Theme).filter(Theme.color == hex_color).first().id
            for i in return_list:
                dbs.add(
                    Annotation(
                        studies_id=cov,
                        theme_id=theme_id,
                        count=i["count"],
                        page_number=i["page_number"],
                        annot_rgb_color=i["annot_rgb_color"],
                        annot_hex_color=i["annot_hex_color"],
                        text=i["text"],
                    )
                )
            dbs.commit()
            dbs.close()

    return total_count, return_list


##
## Extract Distribution
##


def extract_dist(pdf_path: str, term: str, cov: str, db=False):
    """Extracts the distribution of the term from the pdf file and updates the distribution table in the database

    Args:
        pdf_path (path): The full path to the pdf file
        term (str): The term to search for in the pdf file
        cov (int): Internal Study ID from the database e.g. Covidence number
        db (bool, optional): Save to the database? - Defaults to False.

    Returns:
        total_count (int), return_list (list): Total count of the term found in the pdf file, and the list of the distribution of the term
    """
    total_count = 0
    return_list = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            count = 0
            res = page.search_for(term)
            if res != []:
                for rect in res:
                    text = get_pdf_text(page, rect)
                    if any(d["text"] == text for d in return_list):
                        continue
                    else:
                        page_number = page.number + 1
                        # get citation from the database for cov
                        dbs = get_db()
                        citation = (
                            dbs.query(Study)
                            .filter(Study.covidence_id == cov)
                            .first()
                            .citation
                        )
                        text = f" {text} {citation} page {page_number}."
                        total_count += 1
                        count += 1
                        item: dict = {
                            "studies_id": cov,
                            "count": count,
                            "page_number": page_number,
                            "term": term,
                            "text": text,
                        }
                        return_list.append(item)

    if db:
        dbs = get_db()
        dbs.begin()
        dbs.query(Study).filter(Study.covidence_id == cov).update(
            {Study.total_distribution: total_count}
        )
        study_id = dbs.query(Study).filter(Study.covidence_id == cov).first().id
        theme_id = dbs.query(Theme).filter(Theme.term == term).first().id

        for i in return_list:
            # check if the text already exists in the distribution table
            if dbs.query(Distribution).filter(Distribution.text == i["text"]).first():
                continue
            else:
                dbs.add(
                    Distribution(
                        studies_id=study_id,
                        theme_id=theme_id,
                        count=i["count"],
                        page_number=i["page_number"],
                        term=i["term"],
                        text=i["text"],
                    )
                )
        dbs.commit()
        dbs.close()

    return total_count, return_list


def extract_total_dist_sheet_sync():
    """Extracts the total distribution from the database and updates the Distribution Worksheet in the Google Sheet

    Returns:
        bool: True if updated successfully, False if not
    """
    gs = get_conf("gs_url")
    ws = get_worksheet_by_name(gs, get_conf("gs_studies_sheet_name"))
    headers_row_values = get_worksheet_headers_row_values(ws)
    id_col_values = get_worksheet_id_col_index_values(
        ws, get_conf("gs_studies_id_column_name")
    )
    updating_col_index_header = get_worksheet_updating_col_index_header(
        headers_row_values, "Distribution"
    )
    dbs = get_db()
    rows = dbs.query(Study).all()
    for row in rows:
        # update distribution column in google sheet from total_distribution column in database
        cov = row.covidence_id
        td = row.total_distribution  # db result
        try:
            # update sheet cell with td value where covidence number matches cov
            res = update_sheet_cell(
                ws, id_col_values, cov, updating_col_index_header, td
            )
            time.sleep(3)
        except:
            logger().warning(
                f"Google API rate limit reached, or other API error, please try again later!"
            )
            continue
    return res


def extract_dist_ws_sheet_sync(cov: str):
    """Extracts the distribution from the database and updates the Distribution Worksheet in the Google Sheet

    Returns:
        bool: True if updated successfully, False if not
    """

    new_ws_name = f"Distribution-{get_random_string()}"
    sheet = get_spreadsheet_by_url(get_conf("gs_url"))
    new_ws = create_new_worksheet(sheet, new_ws_name)
    dbs = get_db()
    if cov == "":
        dist_rows = dbs.query(Distribution).all()
    else:
        study_cov = dbs.query(Study).filter(Study.covidence_id == cov).first()
        dist_rows = (
            dbs.query(Distribution)
            .filter(Distribution.studies_id == study_cov.id)
            .all()
        )
    # dist_rows = dbs.query(Distribution).all()
    dist_rows_df = pd.DataFrame(
        [
            {
                "covidence_number": dbs.query(Study)
                .filter(Study.id == dist_row.studies_id)
                .first()
                .covidence_id,
                "page_number": str(dist_row.page_number),
                "text": dist_row.text,
                "term": dist_row.term,
                "count": dist_row.count,
            }
            for dist_row in dist_rows
        ]
    )
    # add occurrence column, group by covidence_number and page_number
    dist_rows_df["occurrence"] = dist_rows_df.groupby(
        ["covidence_number", "page_number"]
    )["text"].transform("size")
    dist_rows_df["total_occurrence"] = dist_rows_df.groupby(["covidence_number"])[
        "text"
    ].transform("size")
    # convert covidence_number and page_number to int
    dist_rows_df["covidence_number"] = dist_rows_df["covidence_number"].astype(int)
    dist_rows_df["page_number"] = dist_rows_df["page_number"].astype(int)
    # sort by covidence_number and page_number
    dist_rows_df = dist_rows_df.sort_values(
        by=["covidence_number", "page_number"], ascending=True
    )
    dist_rows_df = dist_rows_df.reset_index(drop=True)
    # build a list for each cov where text has same page number, add text to list
    dist_cov_list = []
    for cov in dist_rows_df["covidence_number"].unique():
        dist_cov_list.append(
            dist_rows_df.loc[dist_rows_df["covidence_number"] == cov].values.tolist()
        )
    # append dist_values to new_ws
    dist_values = dist_rows_df.values.tolist()
    for dist_value in dist_values:
        # covidence_number
        cov = dist_value[0]
        # Searched term
        term = dist_value[3]
        # Total number of blocks the searched term found in the page
        total_occurence = dist_value[6]
        # Number of blocks the searched term found in the page
        occurernce = dist_value[5]
        # Page number
        page_number = dist_value[1]
        # total number of searched term found in the block of text
        count = dist_value[4]
        # block of text
        text = dist_value[2]
        try:
            res = new_ws.append_row(
                [
                    cov,
                    term,
                    total_occurence,
                    occurernce,
                    page_number,
                    count,
                    text,
                ],
                include_values_in_response=True,
            )
            logger().info(f"Added to worksheet")
            # get the url for the first cell of the new appended row
            # cell = new_ws.find(cov)
            # print(res)
            # cell =  res
            # cell_url = cell.url
            # res = total_dist_linker(cov, cell_url)
            time.sleep(2)
        except:
            logger().warning(
                f"Google API rate limit reached, or other API error, please try again later!, res: {res}"
            )
            continue
    return True


# def total_dist_linker(cov, dist_sheet_link):
#     # get the studies worksheet from google sheets
#     gs = get_conf("gs_url")
#     ws = get_worksheet_by_name(gs, get_conf("gs_studies_sheet_name"))
#     # get the total distribution cell from the studies worksheet for the row that Covidence number matches cov
#     id_col_values = get_worksheet_id_col_index_values(
#         ws, get_conf("gs_studies_id_column_name")
#     )
#     updating_col_index_header = get_worksheet_updating_col_index_header(
#         get_worksheet_headers_row_values(ws), "Distribution"
#     )
#     print(id_col_values)
#     print(updating_col_index_header)

#     # update the total distribution cell for the row that Covidence number matches cov with the dist_sheet_link hyperlink
#     res = update_sheet_cell(
#         ws, id_col_values, cov, updating_col_index_header, dist_sheet_link
#     )

#     return res
