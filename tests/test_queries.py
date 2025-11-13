# tests/test_queries.py

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("spacex.db")


def _get_conn():
    assert DB_PATH.exists(), "spacex.db must exist before running query tests."
    return sqlite3.connect(DB_PATH)


def test_launches_per_year_not_empty():
    conn = _get_conn()
    sql = """
        SELECT
            substr(date_utc, 1, 4) AS Year,
            COUNT(*) AS TotalLaunches
        FROM FactLaunch
        GROUP BY Year
        ORDER BY Year;
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    assert not df.empty, "Launches per year query should return at least 1 row."


def test_top_rockets_query_runs():
    conn = _get_conn()
    sql = """
        SELECT
            r.name AS RocketName,
            COUNT(*) AS Launches
        FROM FactLaunch f
        JOIN DimRocket r ON f.rocket = r.id
        GROUP BY r.id, r.name
        ORDER BY Launches DESC
        LIMIT 5;
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    # It's possible there's fewer than 5, but there should be *some* rows
    assert df.shape[0] >= 1, "Top rockets query should return at least 1 row."
