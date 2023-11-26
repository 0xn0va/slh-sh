# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.11] - 2023-11-26

### Added
- `slh-sh check` command to check if all required tables are present in the database.

### Fixed
- Logger
- Cleanup

## [0.1.10] - 2023-11-24

### Changed
- Refactored command schemas, see `slh-sh --help` and `slh-sh list` for more information.

## [0.1.9] - 2023-11-24

### Added
- `slh-sh query [query]` Multipart with one or more arguments, first argument one or more Author or ID separated by colon, second ThemeName, third SubThemeName
e.g. slh-sh query themes John,120,192 Stage_1 Derogation  or a direct SQL query with -s/--sqlquery

## [0.1.8] - 2023-11-18
- `slh-sh go doi [id]` command to open doi in browser, example: `slh-sh go doi 91`

## [0.1.7] - 2023-11-18

### Added
- `slh-sh get info` command to get information from database table and copy to clipboard, example: `slh-sh get info 5 --table Stage_1 --idcol Covidence --copy`

## [0.1.6] - 2023-11-18

### Added
- `slh-sh sync fetch` command to fetch and save data from Google Sheet to a new database table, example: `slh-sh sync fetch 'Stage 1' Stage_1_Table`

### Changed
- Code cleanup

## [0.1.5] - 2023-11-05

### Changed
- README.md fixes

## [0.1.4] - 2023-11-05

### Changed
- README.md

## [0.1.3] - 2023-11-05

### Changed
- Cleanup.

## [0.1.2]  - 2023-11-05

### Changed
- README.md

## [0.1.1] - 2023-11-04

### Added

- `self list` command. List all available commands and their descriptions.
- Github Actions to deploy on pypi.

### Fixed

- Cleanup.
- Added test/pdf_test.py.
- Added Github actions to deploy on pypi.


## [0.1.0] - 2023-10-05

- Initial release