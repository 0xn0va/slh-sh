from .config import load_config
import typer
from typing_extensions import Annotated
from rich import print

app = typer.Typer()
configData = load_config()

# https://towardsdatascience.com/extracting-taxonomic-data-from-a-journal-articles-using-natural-language-processing-ab794d048da9
# https://github.com/melanielaffin/taxonomy/blob/master/taxonomic.py


@app.command()
# [cov]
def info(
    cov: Annotated[str, typer.Argument(
        help="Covidence number")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Info {cov}...")


@app.command()
# themes table: id, color, hex, term
# Color = Theme = annotation (Topic) defined in Config.yaml e.g "Theme1": "Blue:Challenges in AI Laws"
# get theme [red] --dist --cov --term --wide --output json/yaml/csv
def theme(
    color: Annotated[str, typer.Argument(
        help="Theme color")],
    dist: Annotated[str, typer.Option(
        help="Distribution")],
    cov: Annotated[str, typer.Option(
        help="Covidence number")],
    term: Annotated[str, typer.Option(
        help="Term")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Color {color}...")


@app.command()
# get search [search term] --cov --dist --output json/yaml/csv --wide # prints the study details (title, authors, year, etc.) of the search term with its keywords
def search(
    term: Annotated[str, typer.Argument(
        help="Search term")],
    cov: Annotated[str, typer.Option(
        help="Covidence number")],
    dist: Annotated[str, typer.Option(
        help="Distribution")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Search {term}...")


@app.command()
# get annots [search term] --output json/yaml/csv --wide # prints the annotations (themes) of the search term with its color
def annots(
    term: Annotated[str, typer.Argument(
        help="Search term")],
    cov: Annotated[str, typer.Option(
        help="Covidence number")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    all: Annotated[bool, typer.Option(
        help="All")] = False,
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Annots {term}...")


@app.command()
# get dist [search term] --cov --output json/yaml/csv --wide # prints the distribution of the search term with its study details (title, authors, year, etc.)
def dist(
    term: Annotated[str, typer.Argument(
        help="Search term")],
    cov: Annotated[str, typer.Option(
        help="Covidence number")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Dist {term}...")


@app.command()
# get keywords [search term] --cov --output json/yaml/csv --wide # prints the keywords of the search term with its study details (title, authors, year, etc.)
def keywords(
    term: Annotated[str, typer.Argument(
        help="Search term")],
    cov: Annotated[str, typer.Option(
        help="Covidence number")],
    output: Annotated[str, typer.Option(
        help="Output format")] = "standard",
    wide: Annotated[bool, typer.Option(
        help="Wide format")] = False,
):
    print(f"Keywords {term}...")
