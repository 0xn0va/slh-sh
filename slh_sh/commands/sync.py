import typer
import sys
import sqlite3 as sql

# import sqlalchemy as sa

# from sqlalchemy.inspection import inspect

from rich import print
from typing_extensions import Annotated

from slh_sh.utils.log import logger
from slh_sh.utils.file import get_conf
from slh_sh.modules.sync import (
    get_worksheet_by_name,
    update_sheet_cell,
    sync_studies_sheet,
    sync_studies_column_sheet,
    get_worksheet_id_col_index_values,
    get_worksheet_updating_col_index_header,
    get_worksheet_headers_row_values,
)
from slh_sh.utils.db import get_db
from slh_sh.data.models import (
    Study,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def update(
    sheetcol: Annotated[str, typer.Option(help="Column name in Google Sheet")] = "",
    # TODO: handle range when passed by user as id, Use a number, a range e.g. 1-20 or multiple numbers e.g 1,30,2
    id: Annotated[str, typer.Option(help="ID, e.g. Covidence number")] = "",
    sheet: Annotated[str, typer.Option(help="Name of the Sheet")] = get_conf(
        "default_studies"
    ),
    gs: Annotated[str, typer.Option(help="Google Sheet URL")] = get_conf("gs_url"),
    idcol: Annotated[
        str,
        typer.Option(help="Column name that considered as ID e.g 'Covidence Number'"),
    ] = get_conf("default_id"),
    apply: Annotated[bool, typer.Option(help="Apply changes to Google Sheet")] = False,
    allcol: Annotated[bool, typer.Option(help="Update all data in column")] = False,
    alltable: Annotated[
        str, typer.Option(help="Add all data of a Table to a new Worksheet")
    ] = "",
):
    """
    Update Google Sheet with data from Database.

    --id <default_id> --gs <sheet_name> --col <column_name>
    """
    if alltable == "" and apply:
        ws = get_worksheet_by_name(gs, sheet)
    if id != "" and sheetcol != "" and "," not in id and "-" not in id:
        # get Google Sheet's Worksheet's id column index values
        headers_row_values = get_worksheet_headers_row_values(ws)
        id_col_values = get_worksheet_id_col_index_values(ws, idcol)
        updating_col_index_header = get_worksheet_updating_col_index_header(
            headers_row_values, sheetcol
        )
        # curr.execute(f"SELECT {sheetcol} FROM studies WHERE Covidence = '{id}'")
        # db_res: str = curr.fetchone()
        dbs = get_db()
        # select [idcol = covidence] from database where idcol is id_col_value
        db_res = dbs.query(Study).filter_by(idcol=id_col_values).first()
        if db_res == None:
            print(f"Study {id} not found in database!")
            sys.exit()
        elif db_res[0] != None:
            if apply:
                update_sheet_cell(
                    ws, id_col_values, id, updating_col_index_header, db_res[0]
                )
                print(
                    """
            :tada: Sync finished successfully from database to Google Sheet:
            Column: {col}
            Sheet: {sheet}
            Study: {id}
            Google Sheet {gs}...
                    """
                )
            else:
                print(f"Would update {id} with '{db_res[0]}'")
        else:
            print(f"Empty {sheetcol} for {id}, skipping...")
    elif allcol and sheetcol != "":
        res = sync_studies_column_sheet(gs, idcol, sheetcol)
        print(
            f"""
            :tada: Sync finished successfully from database to Google Sheet:
            Column: {sheetcol}
            Sheet: {sheet}
            Google Sheet {gs}...
            """
        )
    elif alltable != "":
        if apply:
            print(f"Appending all data in the {alltable} to a new Worksheet...")
            print(gs)
            new_worksheet_title = sync_studies_sheet(gs)
            print(
                f"""
            :tada: Sync finished successfully from database to Google Sheet:
            New Worksheet: {new_worksheet_title}
            Table: {alltable}
            Google Sheet {gs}...
            """
            )
        else:
            print(
                f"""
                By adding --apply the following will happen:
                1. Would create a new Worksheet at Google Sheet from database...
                2. Would add all data from {alltable} table of sqlite dababase to the new Worksheet
                """
            )
    else:
        print(f"Invalid covidence id {id}, {sheetcol} or table name {alltable}!")
        # if id contains , or - then it's a range
        # if "," in id:
        #     print("Multiple detected!")
        #     id = id.split(",")
        #     print(id)
        #     # check if any value in id exists in id_col_values
        #     if apply:
        #         for id_col_value in id_col_values[3:]:
        #             if id in id_col_value:
        #                 print(id)
        #                 update_sheet_cell(
        #                     ws, id_col_values, id_col_value, updating_col_index_header, db_res[0])
        #                 # sleep for 3 seconds to avoid Google API rate limit
        #                 time.sleep(3)
        #             else:
        #                 print(f"Study {id_col_value} not found in database!")
        #                 continue
        #     sys.exit()
        # elif "-" in id:
        #     print("Range detected!")
        #     id = id.split("-")
        #     print(id)
        #     sys.exit()
    logger().info(f"Sync finished successfully from database to Google Sheet!")


@app.command()
def config():
    """
    Iterate over Themes, Searches, and Sources in config.yaml and insert into database.

    Creates the needed tables if not exists.
    """
    print(f"Syncing config.yaml to database: {get_conf('sqlite_db')}...")

    conn: sql.connect = sql.connect(get_conf("sqlite_db"))
    curr: sql.Cursor = conn.cursor()

    # iterate over Themes in config_data and insert into database
    for theme in get_conf("themes"):
        # check if theme exists in database
        curr.execute(f"SELECT id FROM themes WHERE color = '{theme}'")
        db_res: str = curr.fetchone()
        if db_res == None:
            # insert theme into database
            hex = get_conf("themes")[theme]["hex"]
            term = get_conf("themes")[theme]["term"]
            # TODO: add study (id) and totalCount columns
            curr.execute(
                f"INSERT INTO themes (color, hex, term) VALUES ('{theme}', '{hex}', '{term}');"
            )
            conn.commit()
            print(f"Theme {theme} inserted in database!")
        else:
            print(f"Theme {theme} already exists in database!")

    # iterate over Searches in config_data and insert into database
    for search in get_conf("searches"):
        # check if search exists in database
        curr.execute(f"SELECT id FROM searches WHERE name = '{search}'")
        db_res: str = curr.fetchone()
        if db_res == None:
            # insert search into database
            description = get_conf("searches")[search]
            curr.execute(
                f"INSERT INTO searches (name, description) VALUES ('{search}', '{description}');"
            )
            conn.commit()
            print(f"Search {search} inserted in database!")
        else:
            print(f"Search {search} already exists in database!")

    # iterate over Sources in config_data and insert into database
    for source in get_conf("sources"):
        # check if source exists in database
        curr.execute(f"SELECT id FROM sources WHERE name = '{source}'")
        db_res: str = curr.fetchone()
        if db_res == None:
            # insert source into database
            description = get_conf("sources")[source]
            curr.execute(
                f"INSERT INTO sources (name, description) VALUES ('{source}', '{description}');"
            )
            conn.commit()
            print(f"Source {source} inserted in database!")
        else:
            print(f"Source {source} already exists in database!")

    conn.close()
    logger().info(f"Sync finished successfully from config.yaml to database!")


@app.command()
def fetch(
    sheet: Annotated[
        str, typer.Argument(help="Name of the Sheet e.g. 'Stage 1' or Stage_1")
    ],
    dbtable: Annotated[
        str,
        typer.Argument(
            help="Name of the Database Table, if empty the name will be used e.g Stage_One_Sheet"
        ),
    ] = "",
    gs: Annotated[str, typer.Option(help="Google Sheet URL")] = get_conf("gs_url"),
):
    """Fetch data from Google Sheet to a new database table."""

    print(f"Fetching Google Sheet to database...")

    ws = get_worksheet_by_name(gs, sheet)
    ws_data = ws.get_values()
    ws_headers = ws_data[2]
    ws_data = ws_data[3:]

    if dbtable == "":
        dbtable = sheet
        sheet = sheet.replace(" ", "_")
    elif dbtable != "":
        dbtable = dbtable.replace(" ", "_")

    ws_headers = [header.replace(" ", "_") for header in ws_headers]
    ws_headers = [header.replace("/", "_") for header in ws_headers]

    # replace empty string with None in ws_data
    ws_data = [["None" if cell == "" else cell for cell in row] for row in ws_data]

    conn = sql.connect(get_conf("sqlite_db"))
    curr = conn.cursor()

    curr.execute(
        f""" CREATE TABLE IF NOT EXISTS {dbtable} ({', '.join([f'{header} TEXT' for header in ws_headers])});"""
    )
    conn.commit()

    for row in ws_data:
        print(row)
        curr.execute(
            f"INSERT INTO {dbtable} ({', '.join(ws_headers)}) VALUES ({', '.join([f'?' for i in range(len(ws_headers))])})",
            row,
        )
        conn.commit()

    conn.close()

    print(f"Data from {dbtable} added to corresponding database table!")
    logger().info(f"Data from {dbtable} added to corresponding database table!")
