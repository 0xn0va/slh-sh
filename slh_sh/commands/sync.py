import typer
import sys
import sqlite3 as sql

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

app = typer.Typer()


@app.command()
def update(
    sheetcol: Annotated[str, typer.Option(help="Column name in Google Sheet")] = "",
    # TODO: handle range when passed by user as cov, Use a number, a range e.g. 1-20 or multiple numbers e.g 1,30,2
    cov: Annotated[str, typer.Option(help="Covidence number as ID")] = "",
    sheet: Annotated[str, typer.Option(help="Name of the Sheet")] = get_conf(
        "gs_studies_sheet_name"
    ),
    gs: Annotated[str, typer.Option(help="Google Sheet URL")] = get_conf("gs_url"),
    idcol: Annotated[
        str,
        typer.Option(help="Column name that considered as ID e.g 'Covidence #'"),
    ] = get_conf("gs_studies_id_column_name"),
    apply: Annotated[bool, typer.Option(help="Apply changes to Google Sheet")] = False,
    allcol: Annotated[bool, typer.Option(help="Update all data in column")] = False,
    alltable: Annotated[
        str, typer.Option(help="Add all data of a Table to a new Worksheet")
    ] = "",
):
    """
    Update Google Sheet with data from Database.

    --cov <covidence_id> --gs <sheet_name> --col <column_name>
    """
    if alltable == "" and apply:
        ws = get_worksheet_by_name(gs, sheet)
    if cov != "" and sheetcol != "" and "," not in cov and "-" not in cov:
        # get Google Sheet's Worksheet's id column index values
        headers_row_values = get_worksheet_headers_row_values(ws)
        id_col_values = get_worksheet_id_col_index_values(ws, idcol)
        updating_col_index_header = get_worksheet_updating_col_index_header(
            headers_row_values, sheetcol
        )
        # curr.execute(f"SELECT {sheetcol} FROM studies WHERE Covidence = '{cov}'")
        # db_res: str = curr.fetchone()
        dbs = get_db()
        # select [idcol = covidence] from database where idcol is id_col_value
        db_res = dbs.query(Study).filter_by(idcol=id_col_values).first()
        if db_res == None:
            print(f"Study {cov} not found in database!")
            sys.exit()
        elif db_res[0] != None:
            if apply:
                update_sheet_cell(
                    ws, id_col_values, cov, updating_col_index_header, db_res[0]
                )
                print(
                    """
            :tada: Sync finished successfully from database to Google Sheet:
            Column: {col}
            Sheet: {sheet}
            Study: {cov}
            Google Sheet {gs}...
                    """
                )
            else:
                print(f"Would update {cov} with '{db_res[0]}'")
        else:
            print(f"Empty {sheetcol} for {cov}, skipping...")
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
        print(f"Invalid covidence id {cov}, {sheetcol} or table name {alltable}!")
        # if cov contains , or - then it's a range
        # if "," in cov:
        #     print("Multiple detected!")
        #     cov = cov.split(",")
        #     print(cov)
        #     # check if any value in cov exists in id_col_values
        #     if apply:
        #         for id_col_value in id_col_values[3:]:
        #             if cov in id_col_value:
        #                 print(cov)
        #                 update_sheet_cell(
        #                     ws, id_col_values, id_col_value, updating_col_index_header, db_res[0])
        #                 # sleep for 3 seconds to avoid Google API rate limit
        #                 time.sleep(3)
        #             else:
        #                 print(f"Study {id_col_value} not found in database!")
        #                 continue
        #     sys.exit()
        # elif "-" in cov:
        #     print("Range detected!")
        #     cov = cov.split("-")
        #     print(cov)
        #     sys.exit()


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
            # TODO: add study (cov) and totalCount columns
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


@app.command()
# shows differencess and missing fields
# https://www.geeksforgeeks.org/pandas-find-the-difference-between-two-dataframes/
# https://datascientyst.com/compare-two-pandas-dataframes-get-differences/
def diff(data: str):
    """ """
    print(f"Diff DB with Google Sheet: {data}...")
