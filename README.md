# tl;dr

Name: slh-sh (slh.sh)

SLH: SLRs Little Helper

SLR: Systematic Literature Review

A Cross Platform CLI tool in Python to help with the Systematic Literature Review process.

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

1. slh-sh with `slh-sh [Command] --help` to see the help for a command.
2. `slh-sh self list` to see the available commands.
3. `slh-sh init` to create a new project folder.


## Synopsis

```bash



```


## Tips and Tricks
- Pause syncing on Google Drive while editing a PDF file.


### Google APP Script to add links to drive files

```
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