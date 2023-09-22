import typer
import time
import random
import string
import sys
import sqlite3 as sql

from typing_extensions import Annotated
from rich import print

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from slh.config import load_config

# import pandas as pd
# import requests
# from gspread_dataframe import get_as_dataframe, set_with_dataframe

app = typer.Typer()
configData = load_config()


def gs_auth():
    try:
        # Authorization
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            configData["google_credentials"], scope
        )
        gc = gspread.authorize(credentials)
        return gc
    except gspread.SpreadsheetNotFound:
        print(f"Spreadsheet authentication failed!")
        sys.exit()


def get_spreadsheet_by_url(gs):
    try:
        auth = gs_auth()
        spreadSheet = auth.open_by_url(gs)
        return spreadSheet
    except gspread.SpreadsheetNotFound:
        print(f"Spreadsheet {gs} not found!")
        sys.exit()


def get_worksheet_by_name(gs, sheet):
    try:
        spreadSheet = get_spreadsheet_by_url(gs)
        return spreadSheet.worksheet(sheet)
    except gspread.WorksheetNotFound:
        print(f"Worksheet {sheet} not found in Google Sheet!")
        sys.exit()


def update_sheet_cell(
    ws, id_col_values, id_col_value, updating_col_index_header, dbRes
):
    ws.update_cell(
        id_col_values.index(id_col_value) + 1, updating_col_index_header + 1, dbRes
    )
    print(f"Updated {id_col_value} with '{dbRes}'")


@app.command()
def update(
    col: Annotated[str, typer.Option(help="Column name in Google Sheet")] = "",
    # TODO: handle range when passed by user as cov, Use a number, a range e.g. 1-20 or multiple numbers e.g 1,30,2
    cov: Annotated[str, typer.Option(help="Covidence number as ID")] = "",
    sheet: Annotated[str, typer.Option(help="Name of the Sheet")] = configData[
        "gs_studies_sheet_name"
    ],
    gs: Annotated[str, typer.Option(help="Google Sheet URL")] = configData["gs_url"],
    idcol: Annotated[
        str, typer.Option(help="Column name that considered as ID e.g 'Covidence #'")
    ] = configData["gs_studies_id_column_name"],
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

        header_row: int = int(configData["gs_header_row_number"])
        header_row_values = ws.row_values(header_row)
        # get index number of provided Column e.g "Keywords" in header_values
        updating_col_index_header = header_row_values.index(col)
        id_col_index = header_row_values.index(idcol)
        # get all values of id_col_index from header_row to the last row
        id_col_values = ws.col_values(id_col_index + 1)

    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()

    if cov != "" and col != "" and "," not in cov and "-" not in cov:
        if apply:
            print(
                f"Updating Covidence id {cov} on column {col} of Sheet {sheet} in Google Sheet..."
            )
        else:
            print(
                f"Would update Covidence id {cov} on column {col} of Sheet {sheet} in Google Sheet..."
            )

        curr.execute(f"SELECT {col} FROM studies WHERE Covidence = '{cov}'")
        dbRes: str = curr.fetchone()

        if dbRes == None:
            print(f"Study {cov} not found in database!")
            sys.exit()
        elif dbRes[0] != None:
            if apply:
                update_sheet_cell(
                    ws, id_col_values, cov, updating_col_index_header, dbRes[0]
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
                print(f"Would update {cov} with '{dbRes[0]}'")
        else:
            print(f"Empty {col} for {cov}, skipping...")

    elif allcol and col != "":
        if apply:
            print(f"Updating all data in column {col} of {sheet} of Google Sheet...")
        else:
            print(
                f"Would update all data in column {col} of {sheet} of Google Sheet..."
            )

        # select all Keywords from database where Covidence is id_col_values
        for id_col_value in id_col_values[3:]:
            curr.execute(
                f"SELECT {col} FROM studies WHERE Covidence = '{id_col_value}'"
            )
            dbRes: str = curr.fetchone()
            # check if SELECT found any value
            if dbRes == None:
                print(f"Study {id_col_value} not found in database!")
                continue
            elif dbRes[0] != None:
                if apply:
                    update_sheet_cell(
                        ws,
                        id_col_values,
                        id_col_value,
                        updating_col_index_header,
                        dbRes[0],
                    )
                    # sleep for 3 seconds to avoid Google API rate limit
                    time.sleep(3)
                else:
                    print(f"Would update {id_col_value} with '{dbRes[0]}'")
            else:
                print(f"Empty {col} for {id_col_value}, skipping...")

        print(
            f"""

            :tada: Sync finished successfully from database to Google Sheet:
            Column: {col}
            Sheet: {sheet}
            Google Sheet {gs}...

            """
        )
    elif alltable != "":
        if apply:
            print(f"Appending all data in the {alltable} to a new Worksheet...")
            print(gs)
            sheet = get_spreadsheet_by_url(gs)
            randomString = "".join(random.choices(string.ascii_lowercase, k=4))
            # create a new worksheet
            new_ws = sheet.add_worksheet(
                title=f"slh-{randomString}", rows="1000", cols="200"
            )
            print(f"New Worksheet created: slh-{randomString}")

            # get column from studies table from sqlite db
            curr.execute(f"PRAGMA table_info({alltable})")
            colNames = curr.fetchall()
            colNames = [tup[1] for tup in colNames]
            new_ws.append_row(colNames)
            time.sleep(3)

            # get all rows in studies table from sqlite db
            curr.execute(f"SELECT * FROM {alltable}")
            dbRes: str = curr.fetchall()
            # add all data from studies table of sqlite dababase to the new Worksheet
            for row in dbRes:
                row = list(row)
                new_ws.append_row(row)
                print(f":white_check_mark: {row[0]}")
                # sleep for 3 seconds to avoid Google API rate limit
                time.sleep(3)

            print(
                f"""

            :tada: Sync finished successfully from database to Google Sheet:

            New Worksheet: {new_ws.title}
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
        print(f"Invalid covidence id {cov}, {col} or table name {alltable}!")
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
        #                     ws, id_col_values, id_col_value, updating_col_index_header, dbRes[0])
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

    conn.close()


@app.command()
# shows differencess and missing fields
# https://www.geeksforgeeks.org/pandas-find-the-difference-between-two-dataframes/
# https://datascientyst.com/compare-two-pandas-dataframes-get-differences/
def diff(data: str):
    """ """
    print(f"Diff DB with Google Sheet: {data}...")


@app.command()
def config():
    """
    Iterate over Themes, Searches, and Sources in config.yaml and insert into database.

    Creates the needed tables if not exists.
    """
    print(f"Syncing config.yaml to database: {configData['sqlite_db']}...")

    conn: sql.connect = sql.connect(configData["sqlite_db"])
    curr: sql.Cursor = conn.cursor()

    # check if Themes table exists
    curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='themes'")
    dbRes: str = curr.fetchone()
    if dbRes == None:
        print(f"Themes table not found in database!")
        # create Themes table
        curr.execute(
            """CREATE TABLE themes
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT NOT NULL,
            hex TEXT NOT NULL,
            term TEXT NOT NULL);"""
        )
        conn.commit()
        print(f"Themes table created in database!")

    # check if Searches table exists
    curr.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='searches'"
    )
    dbRes: str = curr.fetchone()
    if dbRes == None:
        print(f"Searches table not found in database!")
        # create Searches table
        curr.execute(
            """CREATE TABLE searches
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL);"""
        )
        conn.commit()
        print(f"Searches table created in database!")

    # check if Sources table exists
    curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sources'")
    dbRes: str = curr.fetchone()
    if dbRes == None:
        print(f"Sources table not found in database!")
        # create Sources table
        curr.execute(
            """CREATE TABLE sources
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL);"""
        )
        conn.commit()
        print(f"Sources table created in database!")

    # annotations table: studiesID, themeID, annotation, pageNumber, pageImage
    # check if Annotations table exists
    curr.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'"
    )
    dbRes: str = curr.fetchone()
    if dbRes == None:
        print(f"Annotations table not found in database!")
        # create Annotations table
        curr.execute(
            """CREATE TABLE annotations
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            studiesID INTEGER NOT NULL,
            themeID INTEGER NOT NULL,
            annotation TEXT NOT NULL,
            pageNumber INTEGER NOT NULL,
            pageImage TEXT NOT NULL,
            FOREIGN KEY(studiesID) REFERENCES studies(id),
            FOREIGN KEY(themeID) REFERENCES themes(id));"""
        )
        conn.commit()
        print(f"Annotations table created in database!")

    # distribution table: id, studiesID, term, count, description (majority amount of the term under study headings), automatically calculated from themes table
    # check if Distribution table exists
    curr.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='distribution'"
    )
    dbRes: str = curr.fetchone()
    if dbRes == None:
        print(f"Distribution table not found in database!")
        # create Distribution table
        curr.execute(
            """CREATE TABLE distribution
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            studiesID INTEGER NOT NULL,
            term TEXT NOT NULL,
            count INTEGER NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY(studiesID) REFERENCES studies(id));"""
        )
        conn.commit()
        print(f"Distribution table created in database!")

    # iterate over Themes in configData and insert into database
    for theme in configData["themes"]:
        # check if theme exists in database
        curr.execute(f"SELECT id FROM themes WHERE color = '{theme}'")
        dbRes: str = curr.fetchone()
        if dbRes == None:
            # insert theme into database
            hex = configData["themes"][theme]["hex"]
            term = configData["themes"][theme]["term"]
            curr.execute(
                f"INSERT INTO themes (color, hex, term) VALUES ('{theme}', '{hex}', '{term}');"
            )
            conn.commit()
            print(f"Theme {theme} inserted in database!")
        else:
            print(f"Theme {theme} already exists in database!")

    # iterate over Searches in configData and insert into database
    for search in configData["searches"]:
        # check if search exists in database
        curr.execute(f"SELECT id FROM searches WHERE name = '{search}'")
        dbRes: str = curr.fetchone()
        if dbRes == None:
            # insert search into database
            description = configData["searches"][search]
            curr.execute(
                f"INSERT INTO searches (name, description) VALUES ('{search}', '{description}');"
            )
            conn.commit()
            print(f"Search {search} inserted in database!")
        else:
            print(f"Search {search} already exists in database!")

    # iterate over Sources in configData and insert into database
    for source in configData["sources"]:
        # check if source exists in database
        curr.execute(f"SELECT id FROM sources WHERE name = '{source}'")
        dbRes: str = curr.fetchone()
        if dbRes == None:
            # insert source into database
            description = configData["sources"][source]
            curr.execute(
                f"INSERT INTO sources (name, description) VALUES ('{source}', '{description}');"
            )
            conn.commit()
            print(f"Source {source} inserted in database!")
        else:
            print(f"Source {source} already exists in database!")

    conn.close()
