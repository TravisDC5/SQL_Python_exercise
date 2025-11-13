# tests/test_ingestion.py

import sqlite3
from pathlib import Path

DB_PATH = Path("spacex.db")


def test_database_exists():
    assert DB_PATH.exists(), "spacex.db should exist after running Get_SpaceX_Data.py"


def test_core_tables_exist():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    expected_tables = ["DimRocket", "DimPayload", "DimLaunchpad", "FactLaunch"]

    for table in expected_tables:
        cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;",
            (table,),
        )
        count = cur.fetchone()[0]
        assert count == 1, f"Expected table {table} to exist."

    conn.close()


def test_factlaunch_has_rows():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM FactLaunch;")
    count = cur.fetchone()[0]

    conn.close()
    assert count > 0, "FactLaunch should have at least one row after ingestion."
