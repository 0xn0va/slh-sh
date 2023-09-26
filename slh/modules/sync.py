import sys
import gspread


from oauth2client.service_account import ServiceAccountCredentials

from slh.utils.file import get_conf


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
