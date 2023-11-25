import typer
import sqlite3 as sql
import pyperclip
import json

from rich import print
from typing_extensions import Annotated

from slh_sh.utils.file import get_conf
from slh_sh.utils.log import logger

app = typer.Typer()


@app.command()
def query(
    terms: Annotated[
        list[str],
        typer.Argument(
            help="""Multipart with one or more arguments,
first argument one or more Author or ID separated by colon, second ThemeName, third SubThemeName
e.g. slh-sh query themes John,120,192 Stage_1 Derogation or a direct SQL query with -s/--sqlquery"""
        ),
    ],
    studytable: Annotated[
        str, typer.Option("-st", "--studytable", help="Study table name")
    ] = get_conf("default_studies"),
    idcol: Annotated[
        str, typer.Option(help="ID column name")
    ] = get_conf("default_id"),
    sqlquery: Annotated[
        bool, typer.Option("-s", "--sqlquery", help="SQL query")
    ] = False,
    copy: Annotated[
        bool, typer.Option("-c", "--copy", help="Copy to clipboard")
    ] = False,
):
    """Get themes about a study from a database table by ID."""

    if sqlquery != False:
        conn = sql.connect(get_conf("sqlite_db"))
        curr = conn.cursor()
        print(terms[0])
        curr.execute(terms[0])
        db_res = curr.fetchall()
        if db_res == None:
            print(
                f"""
Nothing Found!
sqlquery: {sqlquery}
result: {db_res}
"""
            )
        else:
            db_res = [
                dict(zip([col[0] for col in curr.description], row)) for row in db_res
            ]
            json_data = json.dumps(db_res, indent=4)
            print(json_data)
            if copy:
                pyperclip.copy(json_data)
                print("Copied to clipboard!")
        conn.close()
        logger().info(f"SQL query executed: {terms[0]}")
        exit()

    authors = terms[0].split(",")
    theme = ""
    subtheme = ""
    if len(terms) == 1:
        input = terms[0].lower()
        if input and " " in input:
            print(
                """
SQL query detected!
to query sql database directly use -s/--sqlquery option, e.g.:
slh-sh query -s "SELECT * FROM studies WHERE authors LIKE '%John%'"
"""
            )
            exit()
        else:
            pass
    if len(terms) == 2:
        theme = terms[1]
    if len(terms) == 3:
        theme = terms[1]
        subtheme = terms[2]
    if len(terms) > 3:
        print("Too many arguments!")
        exit()

    results = {}

    conn = sql.connect(get_conf("sqlite_db"))
    curr = conn.cursor()

    for author in authors:
        if author.isnumeric():
            curr.execute(f"SELECT * FROM {studytable} WHERE {idcol} = {author}")
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
                    i for i, col in enumerate(curr.description) if col[0] == idcol
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
                curr.execute(f"SELECT * FROM {theme} WHERE {idcol} = {value['ID']}")
                db_res = curr.fetchone()
                if db_res == None:
                    print(
                        f"Theme for Study with the ID: {value['ID']} not found in database table: {theme}!"
                    )
                else:
                    # add column names to result
                    for i, col in enumerate(db_res):
                        value[curr.description[i][0]] = col
            else:
                curr.execute(
                    f"SELECT {theme},{subtheme} FROM {theme} WHERE {idcol} = {value['ID']}"
                )
                db_res = curr.fetchone()
                if db_res == None:
                    print(
                        f"Subtheme for Study with the ID: {value['ID']} not found in database table: {theme}!"
                    )
                else:
                    value["Theme_Text"] = db_res[0]
                    value["Subtheme_Text"] = db_res[1]
    else:
        print("No theme specified!")

    conn.close()
    print(results)

    if copy:
        text = ""
        if subtheme != "":
            text = value["Subtheme_Text"] + " " + value["Citation"]
        elif theme != "":
            text = value[theme] + " " + value["Citation"]
        else:
            # add citation from results
            for key, value in results.items():
                text += value["Citation"] + "\n"
        pyperclip.copy(text)
        print(
            """

The following copied to clipboard!
Note: If query was for multiple studies, only the last result was copied.

"""
        )
        print(text + "\n")
    logger().info(f"Query executed: {terms}")
