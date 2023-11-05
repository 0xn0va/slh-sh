# tl;dr

Name: slh-sh (slh.sh)

SLH: SLRs Little Helper

SLR: Systematic Literature Review

A Cross Platform CLI tool in Python to automated repetitive tasks of a Systematic Literature Review project.

```bash
pip install slh-sh
slh-sh --help
```

## Features

Extraction:
- Import CSV files of studies to SQLite database and export to the Google SHeets (exported from, e.g. Covidence, Zotero, etc).
- Extract PDF links from html files and download them.
- Rename PDF files with predefined format.
- Extract text from PDF files (based on searched term, based on Highlights) including the citation at the end of the paragraph.
- Extract Citations with predefined format (e.g APA) from PDF files.
- Extract Bibliography with predefined format (e.g APA) from PDF files.
- Extract Keywords from PDF files.
- Extract distribution number of keywords in a study.
- Save Extracted data to local SQLite Database.

Sync:
 - Update the data in Google Sheets on spesific Row, Column, Cell from database or complete sync to new Worksheet.

Review:
- Open PDF files with default PDF viewer from CLI with its ID number - `slh-sh go pdf 436`
- Highlight PDF files with defined "Theme" in Config file with specific color.

Fetch: (Under Development)
- Fetch and format all related Highlighted text based on the Theme color.

Manage:
- One project folder for config files, database, and PDF files.
- Create new project folder with predefined structure.
- Backup and restore project folder. (Under Development)


## Rationale

There are at least 17 steps to do a Systematic Literature Review (SLR) with a Google Sheets.

slh-sh would automate the all the repetitive tasks.

The only manual steps (12, 16, 17) would be:
- Writing a minimal one line command
- Reading the article and highlighting the texts based on predefined Theme Color in Config File.
- Writing your paper.

1. Find the next study in the list on Covidence.
2. Add new row to Google Sheet.
3. Download the PDF file.
4. Take the names and format the File with the naming format e.g. #100_NAME_NAME2[et_al]_YEAR.pdf
5. Put the file name on Google Sheets.
6. Format the authors to the naming style.
7. Put the formatted author's name on Google Sheets.
8. Find and copy the abstract to Google Sheets.
9. Find and copy keywords to Google Sheets.
10. Copy the year to Google Sheets.
11. Find and copy APA and DOI to Google Sheets.
12. **Open, scan, and read the article; find and highlight by colors based on the themes.**
13. Find and transfer highlighted texts to Google Sheets based on the themes (colors/fields).
14. Copy the PDF file to the Google Drive folder.
15. Make the Filename column on Google Sheets link to Google Drive.
16. **Mark or color the Inclusion column as included, excluded, or unknown.**
17. **Write your Own thought column.**
18. Take a breath.
19. Repeat.


## Installation

Install:

1. Python 3.8 or higher.
2. Favorite PDF viewer.
3. SQLite database viewer. (e.g https://sqlitebrowser.org/dl/)
4. Install slh-sh with pip.

```bash
pip install slh-sh
```
Run:

1. Create a folder and copy default config file or use `slh-sh init` to create a new project folder from default template or a questionaire.
2. slh-sh with `slh-sh [Command] --help` to see the help for a command.
3. `slh-sh self list` to see the available commands.


## Config File example (config.yaml)

```yaml
#
# Config file for slh
#
# project_name - Name of the project directory
# gs_url - URL to Google Sheet
# gd_url - URL to Google Drive
# csv_export - Name of the default CSV file
# html_export - Name of the default HTML file
# google_credentials - Name of the default Google Credentials file
# sqlite_db - Name of the default SQLite Database file
# studies_pdf - Name of the default PDF folder
# gs_header_row_number - Number of the header row in Google Sheet
# gs_studies_sheet_name - Name of the Studies sheet in Google Sheet
# gs_studies_id_column_name - Name of the ID column in Google Sheet
# themes - Themes (colors) for the annotations
# searches - Searches (keywords) for the studies
# sources - Sources (where the study is found)
#
# Themes, Searches, and Sources will be added to database with sync yaml command
#
# yamllint disable rule:line-length
---
project_name: slr-ai-thesis-2023-09-19
gs_url: 'https://docs.google.com/spreadsheets/d/1npBLSKPhNUHNoDQRWQY9Tf_Np6dzUH0TTamrX01513s'
gd_url: 'https://drive.google.com/drive/folders/11pjqVjFXfsBVjG4CC0mzMSZ2zeLCXNrE'
csv_export: studies.csv
html_export: export.html
html_id_element: study-header
html_dl_class: 'action-link download'
google_credentials: credentials.json
sqlite_db: slh.db
pdf_path: 'G:\Other computers\My MacBook Pro\Thesis\AI_REG_SLR_Lib_Nova'
gs_header_row_number: '3'
gs_studies_sheet_name: Studies
gs_studies_id_column_name: Covidence
themes:
    purple:
        hex: '#c785da'
        term: Sandbox
    pink:
        hex: '#fc5b89'
        term: Challenges and Risks
    blue:
        hex: '#69aff1'
        term: Stage One
    green:
        hex: '#7bc768'
        term: Stage Two
    yellow:
        hex: '#fbcd5a'
        term: Stage Three
searches:
    search_1: regulatory sandbox
    search_2: regulatory AND sandbox
sources:
    source_1: University Library
    source_2: Scopus
    source_3: Web of Science
```

## Data Gathering

### studies.csv


### export.html file containing PDF utls



## Synopsis

```bash
# Install slh-sh

# See the help for a command

# See the available commands

# Initialize a new project folder

# Import studies from CSV file to database

# Download PDF files

# Rename PDF files

# Extract file names to Studies table in the database based on predefined format

# Rename PDF files with the predefined format from database

# Extract Keywords from PDF files to Studies table in the database

# Extract Citations from PDF files to Studies table in the database

# Extract Bibliography from PDF files to Studies table in the  database

# Extract Distribution of a specific research keyword to Distribution table in database

# Extract Annotatoins from PDF files to Annotations table in the database

# Sync Studies table from database to Google Sheets Worksheet

# Sync specific data from database to Google Sheets Worksheet's Cell or Row

# Sync Distribution table from database to Google Sheets Worksheet

# Open Google Drive folder in browser

# Open Google Sheets in browser

# Open SQLite database wit default SQLite viewer

# Open PDF file with default PDF viewer


```


## Tips and Tricks
- Pause syncing on Google Drive while editing a PDF file.


### Google APP Script to add links to drive files

```javascript
function linkToDriveFile() {
  var columnRange = SpreadsheetApp.getActiveSpreadsheet().getRange("G4:G203");
  var files = DriveApp.getFolderById('11pjqVjFXfsBVjG4CC0mzMSZ2zeLCXNrE').getFiles();
    console.log(fileName + ".pdf")
    while (files.hasNext()) {
      var file = files.next();
      console.log(file.getName())
      for (var i = 1; i <= columnRange.getNumRows(); i++) {
        var fileName = columnRange.getCell(i, 1).getValue();
        if (file.getName() === fileName + ".pdf") {
          console.log("added" + file.getName())
          console.log("added" + fileName)
          columnRange.getCell(i, 1).setFormula(`=HYPERLINK("${file.getUrl()}", "${fileName}"`)
        }
      }
    }
}
```


## Thanks
slh-sh would not be possible without these great projects:
- [Python](https://www.python.org/)
- [Typer](https://typer.tiangolo.com/)
- [Pandas](https://pandas.pydata.org/)
- [Pymupdf](https://pymupdf.readthedocs.io/en/latest/)
- [Gspread](https://gspread.readthedocs.io/en/latest/)
- [SqlAlchemy](https://www.sqlalchemy.org/)
- \+ Work of many others.

## License
This project is licensed under the terms of the MIT license.