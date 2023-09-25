import sqlite3 as sql
from sqlalchemy import create_engine

from slh.utils.config import load_config

config_data = load_config()


def get_db():
    """Gets the database session

    Returns:
        session (any): the database session
    """
    # create sqlalchemy engine and session
    engine = create_engine(f"sqlite:///{config_data['sqlite_db']}")
    db = engine.connect()
    return db


def get_db_cursor():  # DEPRECATED
    """Gets the database cursor and connection

    Returns:
        conn (any), curr (any): the database connection and cursor
    """
    conn: sql.connect = sql.connect(config_data["sqlite_db"])
    curr: sql.Cursor = conn.cursor()
    return conn, curr


def table_exists(table_name: str) -> bool:  # DEPRECATED
    curr = get_db_cursor()
    curr.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    db_res: str = curr.fetchone()
    if db_res == None:
        return False
    else:
        return True


def column_exists(table_name: str, column_name: str) -> bool:  # DEPRECATED
    curr = get_db_cursor()
    curr.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    db_res: str = curr.fetchone()
    if db_res == None:
        return False
    else:
        curr.execute(f"PRAGMA table_info({table_name})")
        db_res: str = curr.fetchall()
        for col in db_res:
            if col[1] == column_name:
                return True
        return False


def create_db():  # DEPRECATED
    """Creates the database and tables if they don't exist"""
    conn, curr = get_db_cursor()
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
            text TEXT NOT NULL,
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
