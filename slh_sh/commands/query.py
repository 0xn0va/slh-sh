import typer
import os
import json
import sqlite3 as sql
import pyperclip

from rich import print
from typing_extensions import Annotated

# from scholarly import scholarly
from slh_sh.utils.file import get_conf

app = typer.Typer()


@app.command()
def themes(
    terms: Annotated[
        list[str],
        typer.Argument(
            help="""Multipart with one or more arguments,
first argument one or more Author or ID separated by colon, second ThemeName, third SubThemeName
e.g. slh-sh query themes John,120,192 Stage_1 Derogation"""
        ),
    ],
    studytable: Annotated[str, typer.Option("-st", "--studytable", help="Study table name")] = get_conf("default_studies"),
    idname: Annotated[str, typer.Option("-id", "--idname", help="ID column name")] = get_conf("default_id"),
    copy: Annotated[
        bool, typer.Option("-c", "--copy", help="Copy to clipboard")
    ] = False,
):
    """Get themes about a study from a database table by ID."""

    print(terms)
