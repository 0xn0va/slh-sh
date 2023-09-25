import typer
import os

from rich import print
from pathlib import Path
from typing_extensions import Annotated

from slh.utils.config import load_config
from slh.utils.file import get_file_path
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
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the citations from the database

    Args:
        db (Annotated[bool, typer.Option, optional): Defaults to "Save to SQLite database file")]=False.
    """
    input(
        f"""
        Press Enter to generate citations:

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
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the bibliographies from the CSV export

    Args:
        csv (Annotated[str, typer.Argument, optional): Defaults to "Covidence CSV Export")]="",
        db (Annotated[bool, typer.Option, optional): Defaults to "Save to SQLite database file")]=False,
    """
    input(
        f"""
        Press Enter to generate bibliographies:

        CSV File: {csv}
        Format: APA 7
        Google Sheet's URL: {config_data["gs_url"]}

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
    """Downloads the PDFs from the HTML export

    Args:
        html (Annotated[ str, typer.Argument, optional): Defaults to "HTML export containing Covidence Number and Download Links" ), ]=config_data["html_export"],
        pdfdir (Annotated[str, typer.Argument, optional): Defaults to "Directory to save PDFs" ), ]=config_data["pdf_path"],
        html_id_element (Annotated[ str, typer.Argument, optional): Defaults to "Class name of the 'div' element containing Covidence Number or ID in a div" ), ]=config_data["html_id_element"],
        html_dl_class (Annotated[ str, typer.Argument, optional): Defaults to "Class name of the 'a' element containing the URL of the PDF" ), ]=config_data["html_dl_class"],
    """
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
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
):
    """Extracts the filenames from the PDFs

    To link the Filenames on Google Sheet with the PDFs on Google Drive visit the project's page.

    Args:
        csv (Annotated[str, typer.Argument, optional): Defaults to "Covidence CSV Export")]="",
        rename (Annotated[bool, typer.Option, optional): Defaults to "Also Rename the PDFs")]=False,
        db (Annotated[bool, typer.Option, optional): Defaults to "Save to SQLite database file")]=False,
    """

    print(f"Extracting filenames from {csv}...")
    fileNames = extract_filename(csv, rename, db)
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
    """Extracts the keywords from the PDFs

    Args:
        cov (Annotated[str, typer.Option, optional): Defaults to "Covidence number to extract keywords")]="".
        all (Annotated[ bool, typer.Option, optional): Defaults to "Extract keywords from all PDFs in config_data['pdf_path'] folder" ), ]=False.
        db (Annotated[bool, typer.Option, optional): Defaults to "SQLite database file")]=False.
    """
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
    """Extracts the annotations from the PDFs

    Args:
        cov (Annotated[str, typer.Option, optional): Defaults to "Covidence number to extract keywords")]="".
        color (Annotated[ str, typer.Option, optional): Defaults to "Color of the annotations to extract" ), ]="".
        all (Annotated[ bool, typer.Option, optional): Defaults to "Extract annotations from all PDFs in pdf_path folder" ), ]=False.
        db (Annotated[bool, typer.Option, optional): Defaults to "Save to SQLite database file")]=False.
    """
    print(f"Fetching Annotations of {color} (themes,topic,colored texts) from {cov}...")

    pdf_dir = Path.cwd() / config_data["pdf_path"]
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
    term: Annotated[str, typer.Argument(help="Search term")],
    cov: Annotated[str, typer.Option(help="Covidence number")] = "",
    output: Annotated[
        str,
        typer.Option(help="Output format, available options are Json, YAML and CSV"),
    ] = "",
    db: Annotated[bool, typer.Option(help="Save to SQLite database file")] = False,
    all: Annotated[bool, typer.Option(help="All PDFs")] = False,
):
    """Extracts the distribution of a search term in the PDFs

    Args:
        term (Annotated[str, typer.Argument, optional): Defaults to "Search term")].
        cov (Annotated[str, typer.Option, optional): Defaults to "Covidence number")]="",
        output (Annotated[ str, typer.Option, optional): Defaults to "Output format, available options are Json, YAML and CSV" ), ]="",
        db (Annotated[bool, typer.Option, optional): Defaults to "Save to SQLite database file")]=False,
        all (Annotated[bool, typer.Option, optional): Defaults to "All PDFs")]=False,
    """
    total_count = 0
    pdf_path = None

    if all:
        pdf_dir = Path.cwd() / config_data["pdf_path"]
        for file_name in os.listdir(pdf_dir):
            cov = file_name.split("_")[0].remove("#")
            total_count, dist_list = extract_dist(pdf_path, term, db)
            print(total_count, dist_list)
    elif cov != "":
        pdf_path = get_file_path(cov)
        total_count, dist_list = extract_dist(pdf_path, term, db)
        print(total_count, dist_list)
    else:
        print(
            """
[bold red]Please enter a covidence number using --cov [Covidence Number] or use --all[/bold red]
            """
        )
