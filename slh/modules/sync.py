import sys
import random
import string
import time
import gspread


from oauth2client.service_account import ServiceAccountCredentials

from slh.utils.file import get_conf
from slh.utils.log import logger
from slh.utils.db import get_db

from slh.data.models import (
    Study,
    Theme,
    Annotation,
    Distribution,
)


def gs_auth():
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
    ws, id_col_values, id_col_value, updating_col_index_header, db_res
):
    ws.update_cell(
        id_col_values.index(id_col_value) + 1, updating_col_index_header + 1, db_res
    )
    print(f"Updated {id_col_value} with '{db_res}'")


def sync_studies_sheet(gs):
    """Sync studies table of sqlite database to Google Sheet

    Args:
        gs (str): Google Sheet URL

    Returns:
        str: New Worksheet title
    """
    sheet = get_spreadsheet_by_url(gs)
    randomString = "".join(random.choices(string.ascii_lowercase, k=4))
    new_ws = sheet.add_worksheet(title=f"slh-{randomString}", rows="1000", cols="200")
    print(f"New Worksheet created: slh-{randomString}")

    dbs = get_db()
    rows = dbs.query(Study).all()
    col_names = Study.__table__.columns.keys()
    new_ws.append_row(col_names)
    time.sleep(3)

    # add all data from studies table of sqlite dababase to the new Worksheet
    for row in rows:
        row = list(row)
        new_ws.append_row(row)
        print(f":white_check_mark: {row[0]}")
        # sleep for 3 seconds to avoid Google API rate limit
        time.sleep(3)

    return new_ws.title


def sync_studies_column_sheet(gs):
    pass
