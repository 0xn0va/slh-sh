import typer
import os
import json
import sqlite3 as sql
import pyperclip

from rich import print
from typing_extensions import Annotated

from slh_sh.utils.file import get_conf

app = typer.Typer()


@app.command()
def query(
    terms: Annotated[
        list[str],
        typer.Argument(
            help="""Multipart with one or more arguments,
first argument one or more Author or ID separated by colon, second ThemeName, third SubThemeName
e.g. slh-sh query themes John,120,192 Stage_1 Derogation"""
        ),
    ],
    studytable: Annotated[
        str, typer.Option("-st", "--studytable", help="Study table name")
    ] = get_conf("default_studies"),
    idname: Annotated[
        str, typer.Option("-id", "--idname", help="ID column name")
    ] = get_conf("default_id"),
    copy: Annotated[
        bool, typer.Option("-c", "--copy", help="Copy to clipboard")
    ] = False,
):
    """Get themes about a study from a database table by ID."""

    authors = terms[0].split(",")
    theme = ""
    subtheme = ""
    if len(terms) == 2:
        theme = terms[1]
    if len(terms) == 3:
        subtheme = terms[2]
    if len(terms) > 3:
        print("Too many arguments!")
        exit()

    results = {}

    conn = sql.connect(get_conf("sqlite_db"))
    curr = conn.cursor()

    for author in authors:
        if author.isnumeric():
            curr.execute(f"SELECT * FROM {studytable} WHERE {idname} = {author}")
            db_res = curr.fetchone()
            if db_res == "None":
                print(
                    f"Study with the ID: {author} not found in database table: {studytable}!"
                )
            else:
                curr.execute(
                    f"SELECT citation, bibliography FROM studies WHERE {get_conf('default_id')} = {author}"
                )
                db_citbib = curr.fetchone()
                res = {
                    "ID": author,
                    "Authors": db_res[2],
                    "Title": db_res[1],
                    "Theme": theme,
                    "Subtheme": subtheme,
                    "Citation": db_citbib[0],
                    "Bibliography": db_citbib[1],
                }
                results[author] = res
        else:
            curr.execute(f"SELECT * FROM {studytable} WHERE authors LIKE '%{author}%'")
            db_res = curr.fetchone()
            if db_res == "None":
                print(
                    f"Study with the Author: {author} not found in database table: {studytable}!"
                )
            else:
                id_index = [
                    i for i, col in enumerate(curr.description) if col[0] == idname
                ][0]
                curr.execute(
                    f"SELECT citation, bibliography FROM studies WHERE {get_conf('default_id')} = {db_res[id_index]}"
                )
                db_citbib = curr.fetchone()
                res = {
                    "ID": db_res[id_index],
                    "Authors": db_res[2],
                    "Title": db_res[1],
                    "Theme": theme,
                    "Subtheme": subtheme,
                    "Citation": db_citbib[0],
                    "Bibliography": db_citbib[1],
                }
                results[author] = res
    if theme != "":
        for key, value in results.items():
            if subtheme == "":
                curr.execute(f"SELECT * FROM {theme} WHERE {idname} = {value['ID']}")
                db_res = curr.fetchone()
                if db_res[0] == "None":
                    print(
                        f"Theme for Study with the ID: {value['ID']} not found in database table: {theme}!"
                    )
                else:
                    # remove ID column and None values
                    db_res = [x for x in db_res if x != "None"]
                    db_res = [x for x in db_res if x != value["ID"]]
                    # add column names
                    db_res = dict(zip(curr.description[1:], db_res))
                    # remove empty columns
                    db_res = {k: v for k, v in db_res.items() if v != ""}
                    value["Theme_Text"] = db_res
            else:
                curr.execute(
                    f"SELECT {subtheme} FROM {theme} WHERE {idname} = {value['ID']}"
                )
                db_res = curr.fetchone()
                if db_res[0] == "None":
                    print(
                        f"Subtheme for Study with the ID: {value['ID']} not found in database table: {theme}!"
                    )
                else:
                    value["Subtheme_Text"] = db_res[0]

    conn.close()
    print(results)
