import requests
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("spacex.db")
API_BASE = "https://api.spacexdata.com/v4"
ENDPOINTS = ["launches", "rockets", "payloads", "launchpads"]

def create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create tables with primary/foreign keys and analytic indexes."""
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS DimRocket (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            stages INTEGER,
            boosters INTEGER,
            cost_per_launch INTEGER,
            success_rate_pct INTEGER,
            first_flight TEXT,
            country TEXT,
            company TEXT
        );

        CREATE TABLE IF NOT EXISTS DimPayload (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            mass_kg REAL,
            orbit TEXT,
            reference_system TEXT,
            customer TEXT
        );

        CREATE TABLE IF NOT EXISTS DimLaunchpad (
            id TEXT PRIMARY KEY,
            name TEXT,
            region TEXT,
            locality TEXT,
            latitude REAL,
            longitude REAL,
            launch_attempts INTEGER,
            launch_successes INTEGER
        );

        CREATE TABLE IF NOT EXISTS FactLaunch (
            id TEXT PRIMARY KEY,
            name TEXT,
            date_utc TEXT,
            success INTEGER,               -- 1 true, 0 false, NULL unknown
            rocket TEXT,
            payload_id TEXT,
            launchpad TEXT,
            details TEXT,
            flight_number INTEGER,
            FOREIGN KEY (rocket)     REFERENCES DimRocket(id),
            FOREIGN KEY (payload_id) REFERENCES DimPayload(id),
            FOREIGN KEY (launchpad)  REFERENCES DimLaunchpad(id)
        );

        -- Helpful indexes (kept across runs)
        CREATE INDEX IF NOT EXISTS idx_dimrocket_name         ON DimRocket(name);
        CREATE INDEX IF NOT EXISTS idx_dimpayload_orbit       ON DimPayload(orbit);
        CREATE INDEX IF NOT EXISTS idx_dimpayload_mass        ON DimPayload(mass_kg);
        CREATE INDEX IF NOT EXISTS idx_dimlaunchpad_name      ON DimLaunchpad(name);
        CREATE INDEX IF NOT EXISTS idx_dimlaunchpad_region    ON DimLaunchpad(region);

        CREATE INDEX IF NOT EXISTS idx_factlaunch_date        ON FactLaunch(date_utc);
        CREATE INDEX IF NOT EXISTS idx_factlaunch_rocket      ON FactLaunch(rocket);
        CREATE INDEX IF NOT EXISTS idx_factlaunch_payload     ON FactLaunch(payload_id);
        CREATE INDEX IF NOT EXISTS idx_factlaunch_launchpad   ON FactLaunch(launchpad);
        CREATE INDEX IF NOT EXISTS idx_factlaunch_success     ON FactLaunch(success);
        """
    )
    print("Schema created/verified.")


def upsert_dataframe(df: pd.DataFrame, table: str, conn: sqlite3.Connection) -> None:
    """
    SQLite-compatible UPSERT without 'ON CONFLICT ... DO UPDATE' (works on older SQLite).
    Strategy:
      1) Write df to a temp table.
      2) UPDATE existing rows by PK ('id') from temp.
      3) INSERT rows that don't exist.
      4) Drop temp table.
    """
    if df.empty:
        print(f"Skipping {table}: DataFrame is empty.")
        return

    cols = list(df.columns)
    if "id" not in cols:
        raise ValueError(f"Expected primary key column 'id' in {table}. Got: {cols}")

    tmp = f"tmp_{table}"
    df.to_sql(tmp, conn, if_exists="replace", index=False)

    non_pk_cols = [c for c in cols if c != "id"]
    col_list = ", ".join(cols)

    # UPDATE existing rows
    if non_pk_cols:
        set_clause = ", ".join(
            [f"{c} = (SELECT {tmp}.{c} FROM {tmp} WHERE {tmp}.id = {table}.id)" for c in non_pk_cols]
        )
        update_sql = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE id IN (SELECT id FROM {tmp});
        """
        conn.execute(update_sql)

    # INSERT new rows
    insert_sql = f"""
    INSERT INTO {table} ({col_list})
    SELECT {col_list} FROM {tmp}
    WHERE NOT EXISTS (SELECT 1 FROM {table} t WHERE t.id = {tmp}.id);
    """
    conn.execute(insert_sql)

    # Cleanup
    conn.execute(f"DROP TABLE {tmp};")
    conn.commit()
    print(f"Upserted {len(df)} rows into {table}.")

def fetch_data(endpoint: str):
    url = f"{API_BASE}/{endpoint}"
    print(f"Fetching {endpoint} ... {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def normalize_all(endpoints_json: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Normalize launches, rockets, payloads, launchpads into DataFrames."""
    # Launches
    launches = pd.json_normalize(endpoints_json["launches"], sep="_")[
        [
            "id",
            "name",
            "date_utc",
            "success",
            "rocket",
            "payloads",
            "launchpad",
            "details",
            "flight_number",
        ]
    ]
    # single payload_id for flat model (first payload if multiple)
    launches["payload_id"] = launches["payloads"].apply(
        lambda x: x[0] if isinstance(x, list) and x else None
    )
    launches.drop(columns=["payloads"], inplace=True)

    # Rockets
    rockets = pd.json_normalize(endpoints_json["rockets"], sep="_")[
        [
            "id",
            "name",
            "type",
            "stages",
            "boosters",
            "cost_per_launch",
            "success_rate_pct",
            "first_flight",
            "country",
            "company",
        ]
    ]

    # Payloads
    payloads = pd.json_normalize(endpoints_json["payloads"], sep="_")[
        ["id", "name", "type", "mass_kg", "orbit", "reference_system", "customers"]
    ]
    payloads["customer"] = payloads["customers"].apply(
        lambda x: x[0] if isinstance(x, list) and x else None
    )
    payloads.drop(columns=["customers"], inplace=True)

    # Launchpads
    launchpads = pd.json_normalize(endpoints_json["launchpads"], sep="_")[
        [
            "id",
            "name",
            "region",
            "locality",
            "latitude",
            "longitude",
            "launch_attempts",
            "launch_successes",
        ]
    ]

    return launches, rockets, payloads, launchpads

def main():
    # (optional) print sqlite versions for debugging
    print("sqlite runtime:", sqlite3.sqlite_version, "| module:", sqlite3.version)

    conn = create_connection()
    create_schema(conn)

    # Fetch JSON from all endpoints
    data = {ep: fetch_data(ep) for ep in ENDPOINTS}

    # Normalize JSON -> DataFrames
    launches, rockets, payloads, launchpads = normalize_all(data)

    # UPSERT into target tables
    upsert_dataframe(rockets, "DimRocket", conn)
    upsert_dataframe(payloads, "DimPayload", conn)
    upsert_dataframe(launchpads, "DimLaunchpad", conn)
    upsert_dataframe(launches, "FactLaunch", conn)

    # Verify
    print("\nTable row counts:")
    for t in ["DimRocket", "DimPayload", "DimLaunchpad", "FactLaunch"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:14s} : {n:,}")

    conn.close()
    print(f"\nIngestion complete. Database: {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()
