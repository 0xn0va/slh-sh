[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# SLRsLittleHelper

```
# python3.10 ./slh.py extract --metadata "CovidenceNumber,Authors,Year,Title,DOI,Abstract"
```

```
# python3.10 ./slh.py extract --filename "#CovidenceNumber_LastName_LastName2[et_al]_Year"
```

```
# python3.10 ./slh.py extract --citation "apa7"
```

```
# python3.10 ./slh.py rename
```

## Google APP Script to add links to drive files

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

## Tips
1. Pause syncing on Google Drive while editing a PDF file.
