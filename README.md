# SLRs Little Helper

```
# slh --help
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
