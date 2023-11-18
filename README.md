# tl;dr

slh-sh - [slh.sh](http://slh.sh)

SRL's Little Helper (SLH) is an unopinionated CLI tool in Python that improves workflow efficiency by automating repetitive chores for Systematic Literature Review projects.

```bash
pip install slh-sh
slh-sh self init
slh-sh --help
```

## Features

**Extraction**
- Import CSV files of studies to SQLite database and export to the Google SHeets (exported from, e.g. Covidence, Zotero, etc).
- Extract PDF links from html files and download them.
- Rename PDF files with provided format.
- Extract text from PDF files (based on searched term, based on Highlights) including the citation at the end of the paragraph.
- Extract Citations with provided format (e.g APA) from PDF files.
- Extract Bibliography with provided format (e.g APA) from PDF files.
- Extract Keywords from PDF files.
- Extract distribution number of keywords in a study.
- Save Extracted data to local SQLite Database.

**Sync**
- Update the data in Google Sheets on spesific Row, Column, Cell from database or complete sync to new Worksheet.
- Fetch and sync data from Google Sheets to new database table.

**Review**
- Open PDF files with default PDF viewer from CLI with its ID number - `slh-sh go pdf 436`
- Highlight PDF files with defined "Theme" in Config file with specific color.

**Get info**
- Compile and format the data from database to a paper with citation.

**Manage**
- One project folder for config files, database, and PDF files.
- Create new project folder with provided structure.
- Backup and restore project folder. (Under Development)


## Rationale

There are at least 17 steps to do a Systematic Literature Review (SLR) with a Google Sheets.

slh-sh would automate all the repetitive tasks.

The only manual steps (12, 16, 17) with slh-sh would be:

- Writing a minimal one line command, e.g. `slh-sh go pdf 120`
- Reading the article and highlighting the texts based on provided Theme Color in Config File.
- Writing your paper.

Manual SLR steps with Google Sheets without using slh-sh:

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


## Preperations

**Google Project and Google Sheets API**

1. Create a Google Project and enable Google Drive and Google Sheets API. [create-project](https://developers.google.com/workspace/guides/create-project)
2. Create a Google Service Account and download the credentials file. [create-credentials](https://developers.google.com/workspace/guides/create-credentials)
3. Create a Google Sheet and share it with the Service Account email.

**Installation**

1. Python 3.8 or higher.
2. Favorite PDF viewer. (e.g [Foxit Reader](https://www.foxit.com/pdf-reader/))
3. SQLite database viewer. (e.g [sqlitebrowser](https://sqlitebrowser.org/dl/))
4. Install slh-sh with pip.

```bash
pip install slh-sh
```

**Run**

1. Create a folder and copy default config file from below OR use `slh-sh self init` to create a new project folder from default template or a questionaire.
2. `slh-sh [Command] --help` - to see the help for a command.
3. `slh-sh self list` - to see the available commands.


## Folder structure

```bash
- slr-project-2023-09-19 (project folder)
  - config.yaml
  - slh.db
  - credentials.json
  - studies.csv
  - export.html
  - pdf_files (folder)
    - Study_1.pdf
    - Study_2.pdf
    - Study_3.pdf
    - ...
```


## Example Config File - config.yaml

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
project_name: slr-thesis-2023-09-19
gs_url: ''
gd_url: ''
csv_export: studies.csv
html_export: export.html
html_id_element: study-header
html_dl_class: 'action-link download'
google_credentials: credentials.json
sqlite_db: slh.db
pdf_path: ''G:\Other computers\My MacBook Pro\Thesis\SLR_Lib'
gs_header_row_number: '3'
gs_studies_sheet_name: Studies
gs_studies_id_column_name: Covidence
themes:
    purple:
        hex: '#c785da'
        term: theme1
    pink:
        hex: '#fc5b89'
        term: theme2
    blue:
        hex: '#69aff1'
        term: theme3
    green:
        hex: '#7bc768'
        term: theme4
    yellow:
        hex: '#fbcd5a'
        term: theme5
searches:
    search_1: term1
    search_2: term2
sources:
    source_1: University Library
    source_2: Scopus
    source_3: Web of Science
    source_4: source4
```

## Data Gathering

### studies.csv

1. Exported from Covidence (Export > REFERENCES > Options [Full text review] > Format [CSV] ), Zotero, etc.
2. The Columns of the Studies table will be created based on this file.
3. Set `gs_studies_id_column_name` in confit.yaml (e.g. Covidence Number), it will be used as the ID of the study in google sheets.

### export.html file containing PDF URLs

1. Using Chrome browser, open the Covidence page with the list of studies.
2. Right click on the page and choose "Save as" and choose "Webpage, HTML Only".
3. The HTML file will be saved in the project folder.

## Examples

```bash
# Initialize a new project folder
slh-sh self init

# Learn about slh-sh commands
slh-sh --help

# See the help for a command
slh-sh [Command] --help

# See the list of available commands
slh-sh self list

# Import studies from CSV file to database
slh-sh add csv studies.csv

# Download PDF files
slh-sh extract dl

# Generate filename based on the provided format, save in database, and rename PDF files
slh-sh extract filename --rename --db

# Extract Keywords from PDF files to Studies table in the database
slh-sh extract keywords --cov [Covidence Number]
slh-sh extract keywords --all --db

# Extract Citations from PDF files to Studies table in the database
slh-sh extract cit --db

# Extract Bibliography from PDF files to Studies table in the  database
slh-sh extract bib --db

# Extract Distribution of a specific research keyword to Distribution table in database
slh-sh extract dist [Term] --cov [Covidence Number]
slh-sh extract dist [Term] --all --db

# Sync Distribution table from database to Google Sheets Worksheet
slh-sh extract dist [Term] --cov [Covidence Number] --wsdsheet

# Sync the config file to database
slh-sh sync config

# Sync Studies table from database to Google Sheets Worksheet
slh-sh sync update --allsheet --apply

# Sync specific data from database to Google Sheets Worksheet's Cell or Row
slh-sh sync update --col "Keywords" --cov [Covidence Number] --apply

# Sync specific Google Sheet to new database table
slh-sh sync fetch 'Stage 1' Stage_1_Table

# Get info about a study and its Citation and Bibliography from a database table by ID.
slh-sh get info 5 --table Stage_1 --idcol Covidence --copy

# Open Google Drive folder in browser
slh-sh go gd

# Open Google Sheets in browser
slh-sh go gs

# Open SQLite database wit default SQLite viewer
slh-sh go db

# Open PDF file with default PDF viewer
slh-sh go pdf [ID e.g. Covidence Number]

# Open DOI in browser
slh-sh go doi [ID e.g. Covidence Number]

```

## Example of SLR's workflow with slh-sh

TODO

## Tips and Tricks

- Pause syncing on Google Drive while editing a PDF file.


### Google APP Script

Adds Google Drive PDF links to the filename column of Google Sheets

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
