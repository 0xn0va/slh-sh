import typer
import os
import json
import yaml
import fitz

from rich import print
from pathlib import Path
from typing_extensions import Annotated

from slh.utils.config import load_config
from slh.utils.pdf import get_pdf_text, rgb_to_hex
from slh.utils.file import get_file_path
from slh.utils.extract_output import dist_output
from slh.utils.extract import (
    extract_cit,
    extract_bib,
    extract_dl,
    extract_filename,
    extract_keywords,
    extract_annots,
    extract_dist,
)


app = typer.Typer()
config_path = Path.cwd() / "config.yaml"
config_data = load_config()


##
## Citation
##


@app.command("cit")
def cit(
    # needs csv?
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = config_data[
        "csv_export"
    ],
):
    input(
        f"""
        Press Enter to generate citations:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {config_data["gs_url"]}

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
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = config_data[
        "csv_export"
    ],
):
    input(
        f"""
        Press Enter to generate bibliographies:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {config_data["gs_url"]}

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
    ] = config_data["html_export"],
    pdfdir: Annotated[str, typer.Argument(help="Directory to save PDFs")] = config_data[
        "pdf_path"
    ],
    idelement: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'div' element containing Covidence Number or ID in a div"
        ),
    ] = config_data["html_id_element"],
    dllinkelement: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'a' element containing the URL of the PDF"
        ),
    ] = config_data["html_dl_class"],
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
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = config_data[
        "csv_export"
    ],
    rename: Annotated[bool, typer.Option(help="Also Rename the PDFs")] = False,
):
    """

    To link the Filenames on Google Sheet with the PDFs on Google Drive: https://github.com/0xnovasky/SLRsLittleHelper/tree/main/slh

    """
    print(f"Extracting filenames from {csv}...")

    fileNames = extract_filename(csv, rename)

    print(fileNames)
    print(
        f"Updated database with {len(fileNames)} filenames on studies Table, Filenames column..."
    )
    if rename:
        print(
            f"Renamed {len(fileNames)} PDFs in {config_data['pdf_path']} folder with the filenames..."
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
            help="Extract keywords from all PDFs in config_data['pdf_path'] folder"
        ),
    ] = False,
    db: Annotated[bool, typer.Option(help="SQLite database file")] = False,
):
    print(f"Keywords {cov}...")

    pdf_dir = Path.cwd() / config_data["pdf_path"]
    pdf_path = None

    if all:
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            pdf_path = get_file_path(cov)
            all_keywords = extract_keywords(cov, pdf_path, db)
        print(all_keywords)
        print(
            f"Extracted keywords from {len(all_keywords)} PDFs and added them to the Database..."
        )
    elif cov != "":
        pdf_path = get_file_path(cov)
        keywords = extract_keywords(cov, pdf_path, db)
        print(
            f"Extracted keywords {keywords} from {pdf_path} and added them to the Database..."
        )
    else:
        print(
            "Please enter a covidence number using --cov [Covidence Number] or use --all"
        )


##
## Annotations
##


## TODO: add --all option to search all PDFs in the pdf_path folder
## TODO: add --color option to search all PDFs in the pdf_path folder
## TODO: go through all pages
@app.command()
def annots(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")],
    color: Annotated[str, typer.Option(help="Color of the annotations to extract")],
):
    print(f"Fetching Annotations of {color} (themes,topic,colored texts) from {cov}...")

    pdf_dir = Path.cwd() / config_data["pdf_path"]
    pdf_path = None

    if all:
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            pdf_path = get_file_path(cov)
            # TODO: write the rest
    elif cov != "":
        pdf_path = get_file_path(cov)

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
    else:
        print(
            "Please enter a covidence number using --cov [Covidence Number] or use --all"
        )


##
## Distribution
##


@app.command()
def dist(
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")] = "",
    output: Annotated[
        str,
        typer.Option(help="Output format, available options are Json, YAML and CSV"),
    ] = "",
    db: Annotated[bool, typer.Option(help="Database")] = False,
    all: Annotated[bool, typer.Option(help="All PDFs")] = False,
):
    if all:
        pdf_dir = Path.cwd() / config_data["pdf_path"]
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            total_count, found_in_page_numbers = extract_dist(pdf_path, term, db)
    elif cov != "":
        pdf_path = get_file_path(cov)
        total_count, found_in_page_numbers = extract_dist(pdf_path, term, db)
    else:
        print(
            "Please enter a covidence number using --cov [Covidence Number] or use --all"
        )

    print(
        f"""
Found {total_count} instances
Term: {term}
PDF path: {pdf_path}
        """
    )
    print(dist_output(found_in_page_numbers, output))
