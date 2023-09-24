import sqlite3 as sql

from slh.utils.config import load_config

config_data = load_config()

conn: sql.connect = sql.connect(config_data["sqlite_db"])
curr: sql.Cursor = conn.cursor()


def create_db():
    # check if Themes table exists
    curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='themes'")
    db_res: str = curr.fetchone()
    if db_res == None:
        print(f"Themes table not found in database!")
        # create Themes table
        curr.execute(
            """CREATE TABLE themes
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            studiesID INTEGER,
            color TEXT NOT NULL,
            hex TEXT NOT NULL,
            term TEXT NOT NULL,
            totalCount INTEGER,
            FOREIGN KEY(studiesID) REFERENCES studies(id));"""
        )
        conn.commit()
        print(f"Themes table created in database!")

    # check if Searches table exists
    curr.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='searches'"
    )
    db_res: str = curr.fetchone()
    if db_res == None:
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
    db_res: str = curr.fetchone()
    if db_res == None:
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
    db_res: str = curr.fetchone()
    if db_res == None:
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
    db_res: str = curr.fetchone()
    if db_res == None:
        print(f"Distribution table not found in database!")
        # create Distribution table
        curr.execute(
            """CREATE TABLE distribution
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            studiesID INTEGER NOT NULL,
            themeID INTEGER,
            term TEXT NOT NULL,
            pageNumber TEXT NOT NULL,
            count INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY(themeID) REFERENCES themes(id),
            FOREIGN KEY(studiesID) REFERENCES studies(id));"""
        )
        conn.commit()
        print(f"Distribution table created in database!")
