import sys
import random
import string
import time
import gspread

from oauth2client.service_account import ServiceAccountCredentials

from slh.utils.file import get_conf, get_random_string
from slh.utils.log import logger, get_now
from slh.utils.db import get_db
from slh.data.models import (
    Study,
)


def gs_auth():
    """Authenticate to Google Sheet API

    Returns:
        Client: Google Sheet Client
    """
    try:
        # Authorization
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            get_conf("google_credentials"), scope
        )
        gc = gspread.authorize(credentials)
        return gc
    except gspread.SpreadsheetNotFound:
        logger().warning(f"Spreadsheet authentication failed!")
        return False  # TODO: is it best practice to return False?


def get_spreadsheet_by_url(gs):
    """Get Google Sheet by URL

    Args:
        gs (Client): Google Sheet Client

    Returns:
        Spreadsheet: Google Sheet
    """
    try:
        auth = gs_auth()
        spreadSheet = auth.open_by_url(gs)
        return spreadSheet
    except gspread.SpreadsheetNotFound:
        logger().warning(f"Spreadsheet {gs} not found!")
        return False  # TODO: is it best practice to return False?


def get_worksheet_by_name(gs, sheet):
    """Get Google Sheet's WordSheet by name

    Args:
        gs (Client): Google Sheet Client
        sheet (Worksheet): Google Sheet's Worksheet

    Returns:
        Worksheet (ws) or False: Google Sheet's Worksheet
    """
    try:
        spreadSheet = get_spreadsheet_by_url(gs)
        ws = spreadSheet.worksheet(sheet)
        return ws
    except gspread.WorksheetNotFound:
        logger().warning(f"Worksheet {sheet} not found in Google Sheet!")
        return False  # TODO: is it best practice to return False?


def get_worksheet_headers_row_values(ws):
    """Get Google Sheet's Worksheet's header row values

    Args:
        ws (Worksheet): Google Sheet's Worksheet

    Returns:
        Any: Google Sheet's Worksheet's header row values
    """
    header_row: int = int(get_conf("gs_header_row_number"))
    row_values = ws.row_values(header_row)

    return row_values


def get_worksheet_updating_col_index_header(header_row_values, sheetcol):
    """Get Google Sheet's Worksheet's updating column index header

    Args:
        header_row_values (list): Google Sheet's Worksheet's header row values
        sheetcol (str): Google Sheet's Worksheet's column name

    Returns:
        Any: Google Sheet's Worksheet's updating column index header
    """
    header_row_values = header_row_values.index(sheetcol)

    return header_row_values


def get_worksheet_id_col_index_values(ws, idcol):
    """Get Google Sheet's Worksheet's id column index values

    Args:
        ws (Worksheet): Google Sheet's Worksheet
        idcol (str): Google Sheet's Worksheet's id column name

    Returns:
        Any: Google Sheet's Worksheet's id column index values
    """
    header_row_values = get_worksheet_headers_row_values(ws)
    # get all values of id_col_index from header_row to the last row
    id_col_index = header_row_values.index(idcol)
    id_col_values = ws.col_values(id_col_index + 1)

    return id_col_values


def create_new_worksheet(sheet, name):
    """Create new Google Sheet's Worksheet

    Args:
        sheet (Worksheet): Google Sheet's Worksheet
        rows (str): Google Sheet's Worksheet's rows
        cols (str): Google Sheet's Worksheet's columns

    Returns:
        Worksheet: New Google Sheet's Worksheet
    """
    new_ws = sheet.add_worksheet(title=f"{name}", rows="1000", cols="200")
    print(f"New Worksheet created: {name}")

    return new_ws


def update_sheet_cell(
    ws, id_col_values, id_col_value, updating_col_index_header, db_res
):
    """Update Google Sheet's Worksheet's cell

    Args:
        ws (Worksheet): Google Sheet's Worksheet
        id_col_values (Any): Google Sheet's Worksheet's id column values
        id_col_value (Any): Google Sheet's Worksheet's id column value
        updating_col_index_header (Any): Google Sheet's Worksheet's updating column index header
        db_res (Any): Value to be updated from database

    Returns:
        bool: True if updated successfully, False if not
    """
    try:
        ws.update_cell(
            id_col_values.index(id_col_value) + 1, updating_col_index_header + 1, db_res
        )
        print(f"Updated {id_col_value} with '{db_res}'")
        logger().info(f"{get_now()} Updated {id_col_value} with '{db_res}'")
        return True
    except gspread.exceptions.APIError:
        logger().warning(
            f"Google API rate limit reached, or other API error, please try again later!"
        )
        return False


def sync_studies_sheet(gs):
    """Sync studies table of sqlite database to Google Sheet

    Args:
        gs (str): Google Sheet URL

    Returns:
        str: New Worksheet title
    """
    sheet = get_spreadsheet_by_url(gs)
    new_ws_name = f"slh-{get_random_string()}"
    new_ws = sheet.add_worksheet(title=f"{new_ws_name}", rows="1000", cols="200")
    print(f"New Worksheet created: {new_ws_name}")

    dbs = get_db()
    rows = dbs.query(Study).all()
    col_names = Study.__table__.columns.keys()
    try:
        new_ws.append_row(col_names)
    except gspread.exceptions.APIError:
        logger().warning(
            f"Google API rate limit reached, or other API error, please try again later!"
        )
        time.sleep(3)

    # add all data from studies table of sqlite dababase to the new Worksheet
    for row in rows:
        row = list(row)
        try:
            new_ws.append_row(row)
            print(f":white_check_mark: {row[0]}")
        except:
            print(f":x: {row[0]}")
            logger().warning(
                f"Google API rate limit reached, or other API error, please try again later!"
            )

        # sleep for 3 seconds to avoid Google API rate limit
        time.sleep(3)

    return new_ws.title


def sync_studies_column_sheet(ws, idcol, sheetcol, apply=False):
    """Sync studies table of sqlite database to Google Sheet

    Args:
        ws (Worksheet): Google Sheet's Worksheet
        idcol (str): Google Sheet's Worksheet's id column name
        sheetcol (str): Google Sheet's Worksheet's column name
        apply (bool, optional): Defaults to False.

    Returns:
        bool: True if updated successfully, False if not
    """
    # select all Keywords from database where Covidence is id_col_values
    updating_col_index_header = get_worksheet_updating_col_index_header(
        get_worksheet_headers_row_values(ws), sheetcol
    )
    id_col_values = get_worksheet_id_col_index_values(ws, idcol)
    for id_col_value in id_col_values[3:]:
        dbs = get_db()
        # select [idcol = covidence] from database where idcol is id_col_value
        db_res = dbs.query(Study).filter_by(idcol=id_col_value).first()
        # check if SELECT found any value
        if db_res == None:
            print(f"Study {id_col_value} not found in database!")
            continue
        elif db_res[0] != None:
            if apply:
                try:
                    update_sheet_cell(
                        ws,
                        id_col_values,
                        id_col_value,
                        updating_col_index_header,
                        db_res[0],
                    )
                    time.sleep(3)
                except gspread.exceptions.APIError:
                    logger().warning(
                        f"Google API rate limit reached, or other API error, please try again later!"
                    )
                    return False
                # sleep for 3 seconds to avoid Google API rate limit
            else:
                print(f"Would update {id_col_value} with '{db_res[0]}'")
        else:
            print(f"Empty {sheetcol} for {id_col_value}, skipping...")

    return True
