import typer
import os

from rich import print
from pathlib import Path
from typing_extensions import Annotated

from slh_sh.utils.file import get_pdf_dir, get_file_path, get_conf
from slh_sh.utils.log import logger, get_now
from slh_sh.modules.extract import (
    extract_cit,
    extract_bib,
    extract_dl,
    extract_filename,
    extract_keywords,
    extract_annots,
    extract_dist,
    extract_total_dist_sheet_sync,
    extract_dist_ws_sheet_sync,
)

app = typer.Typer()

##
## Citation
##


@app.command("cit")
def cit(
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the citations from the database"""
    input(
        f"""
        Press Enter to generate citations:

        Format: APA 7
        Google Sheet's URL: {get_conf("gs_url")}

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
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = get_conf(
        "csv_export"
    ),
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the bibliographies from the CSV export"""
    input(
        f"""
        Press Enter to generate bibliographies:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {get_conf("gs_url")}

        Press Ctrl+C to cancel.
        """
    )

    bibs = extract_bib(csv, db)

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
    ] = get_conf("html_export"),
    pdfdir: Annotated[str, typer.Argument(help="Directory to save PDFs")] = get_conf(
        "pdf_path"
    ),
    html_id_element: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'div' element containing Covidence Number or ID in a div"
        ),
    ] = get_conf("html_id_element"),
    html_dl_class: Annotated[
        str,
        typer.Argument(
            help="Class name of the 'a' element containing the URL of the PDF"
        ),
    ] = get_conf("html_dl_class"),
):
    """Downloads the PDFs from the HTML export"""
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
    csv: Annotated[str, typer.Argument(help="Covidence CSV Export")] = get_conf(
        "csv_export"
    ),
    rename: Annotated[bool, typer.Option(help="Also Rename the PDFs")] = False,
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the filenames from the PDFs"""

    print(f"Extracting filenames from {csv}...")
    fileNames = extract_filename(csv, rename, db)
    print(fileNames)
    print(
        f"Updated database with {len(fileNames)} filenames on studies Table, Filenames column..."
    )
    if rename:
        print(
            f"Renamed {len(fileNames)} PDFs in {get_conf('pdf_path')} folder with the filenames..."
        )


##
## Keywords
##


@app.command()
def keywords(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")] = "",
    all: Annotated[
        bool,
        typer.Option(help="Extract keywords from all PDFs in pdf_path folder"),
    ] = False,
    db: Annotated[bool, typer.Option(help="SQLite database file")] = False,
):
    """Extracts the keywords from the PDFs"""
    print(f"Keywords {cov}...")

    pdf_dir = get_pdf_dir()
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


@app.command()
def annots(
    cov: Annotated[str, typer.Option(help="Covidence number to extract keywords")] = "",
    color: Annotated[
        str, typer.Option(help="Color of the annotations to extract")
    ] = "",
    all: Annotated[
        bool, typer.Option(help="Extract annotations from all PDFs in pdf_path folder")
    ] = False,
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the annotations from the PDFs"""
    print(f"Fetching Annotations of {color} (themes,topic,colored texts) from {cov}...")

    pdf_dir = get_pdf_dir()
    pdf_path = None

    if all:
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            pdf_path = get_file_path(cov)
            res = extract_annots(cov, color, pdf_path, db)
            print(res)
    elif cov != "":
        pdf_path = get_file_path(cov)
        res = extract_annots(cov, color, pdf_path, db)
        print(res)
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
    term: Annotated[str, typer.Argument(help="Search term")] = "",
    cov: Annotated[str, typer.Option(help="Covidence number")] = "",
    output: Annotated[
        str,
        typer.Option(help="Output format, available options are Json, YAML and CSV"),
    ] = "",
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
    all: Annotated[bool, typer.Option(help="All PDFs")] = False,
    tdsheet: Annotated[
        bool,
        typer.Option(
            help="Apply to Distribution Column on gs_studies_sheet_name Worksheet of Google Sheet"
        ),
    ] = False,
    wsdsheet: Annotated[
        bool, typer.Option(help="Apply to Distribution Worksheet on Google Sheet")
    ] = False,
):
    """Extracts the distribution of a search term in the PDFs"""

    if tdsheet == True and all == True and term == "" and cov == "":
        res_total_dist_col = extract_total_dist_sheet_sync()
        print(
            f"Total distribution column update on Google Sheet Studies worksheet from db, {res_total_dist_col}"
        )
    elif wsdsheet == True and all == True and term == "" and cov == "":
        res_dist_ws = extract_dist_ws_sheet_sync()
        print(
            f"Total distribution worksheet update on Google Sheet from db, {res_dist_ws}"
        )
        # res_dist_ws = extract_dist_ws_sheet_sync()
    elif all and cov == "" and term != "":
        pdf_dir: str = get_pdf_dir()
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].replace("#", "")
            pdf_path: str = get_file_path(cov)
            if pdf_path.endswith(".pdf"):
                total_count, dist_list = extract_dist(pdf_path, term, cov, db)
                msg = {
                    "total_count": total_count,
                    "dist_list": dist_list,
                }
                print(msg)
            else:
                logger().info(f"{get_now()} {pdf_path} is not a PDF file.")
    elif cov != "" and term != "" and all == False:
        pdf_path = get_file_path(cov)
        total_count, dist_list = extract_dist(pdf_path, term, cov, db)
        msg = {
            "total_count": total_count,
            "dist_list": dist_list,
        }
        print(msg)
    elif cov != "" and term == "" and all == False and wsdsheet == True:
        res_dist_ws = extract_dist_ws_sheet_sync(cov)
        print(
            f"Total distribution worksheet update on Google Sheet from db, {res_dist_ws}"
        )
    else:
        print(
            """
[bold red]Please enter a covidence number using --cov [Covidence Number] or use --all[/bold red]
            """
        )
