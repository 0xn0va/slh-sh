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
from slh.modules.extract.output import dist_output, annots_output
from slh.modules.extract.function import (
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
    html_id_element: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'div' element containing Covidence Number or ID in a div"
        ),
    ] = config_data["html_id_element"],
    html_dl_class: Annotated[
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

    study_headers = extract_dl(html, pdf_dir, html_id_element, html_dl_class)

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


## TODO: add --color option to search all PDFs in the pdf_path folder
@app.command()
def annots(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")],
    color: Annotated[str, typer.Option(help="Color of the annotations to extract")],
    all: Annotated[
        bool, typer.Option(help="Extract annotations from all PDFs in pdf_path folder")
    ] = False,
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    print(f"Fetching Annotations of {color} (themes,topic,colored texts) from {cov}...")

    pdf_dir = Path.cwd() / config_data["pdf_path"]
    pdf_path = None
    page_annots = None
    hex_color = None

    if all:
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            pdf_path = get_file_path(cov)
            res = extract_annots(cov, pdf_path, db)
            page_number = res[0]
            hex_color = res[1]
            page_annots = res[2]
            text = res[3]
            print(annots_output(page_number, hex_color, page_annots, text))
    elif cov != "":
        pdf_path = get_file_path(cov)
        res = extract_annots(cov, pdf_path, db)
        page_number = res[0]
        hex_color = res[1]
        page_annots = res[2]
        text = res[3]
        print(annots_output(page_number, hex_color, page_annots, text))
    else:
        print(
            """
[bold red]Please enter a covidence number using --cov [Covidence Number] or use --all[/bold red]
            """
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
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
    all: Annotated[bool, typer.Option(help="All PDFs")] = False,
):
    total_count = 0
    pdf_path = None
    found_in_page_numbers = []
    msg = f"""
Found {total_count} instances
Term: {term}
PDF path: {pdf_path}
        """

    if all:
        pdf_dir = Path.cwd() / config_data["pdf_path"]
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            total_count, found_in_page_numbers = extract_dist(pdf_path, term, db)
            print(msg)
            print(dist_output(found_in_page_numbers, output))
    elif cov != "":
        pdf_path = get_file_path(cov)
        total_count, found_in_page_numbers = extract_dist(pdf_path, term, db)
        print(msg)
        print(dist_output(found_in_page_numbers, output))
    else:
        print(
            """
[bold red]Please enter a covidence number using --cov [Covidence Number] or use --all[/bold red]
            """
        )
