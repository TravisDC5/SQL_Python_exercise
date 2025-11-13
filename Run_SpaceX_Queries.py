import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

# Connect to your existing SQLite DB built by spacex_ingest.py
conn = sqlite3.connect("spacex.db")

# Define SpaceX analytics queries (all-SQL)
queries = {
    "1 Launches per Year with Success Rate": """
        SELECT
            substr(f.date_utc, 1, 4) AS Year,
            COUNT(*) AS TotalLaunches,
            SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) AS Successes,
            ROUND(100.0 * SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS SuccessRatePct
        FROM FactLaunch f
        GROUP BY Year
        ORDER BY Year;
    """,

    "2 Top Rockets by Launch Count & Success Rate": """
        SELECT
            r.name AS RocketName,
            COUNT(*) AS Launches,
            SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) AS Successes,
            ROUND(100.0 * SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS SuccessRatePct
        FROM FactLaunch f
        JOIN DimRocket r ON f.rocket = r.id
        GROUP BY r.id, r.name
        ORDER BY Launches DESC, SuccessRatePct DESC, RocketName
        LIMIT 10;
    """,

    "3 Payload Mass by Rocket (Avg/Max)": """
        SELECT
            r.name AS RocketName,
            COUNT(DISTINCT f.id) AS LaunchesWithPayload,
            ROUND(AVG(p.mass_kg), 2) AS AvgPayloadKg,
            MAX(p.mass_kg) AS MaxPayloadKg
        FROM FactLaunch f
        JOIN DimRocket r ON f.rocket = r.id
        LEFT JOIN DimPayload p ON f.payload_id = p.id
        GROUP BY r.id, r.name
        HAVING LaunchesWithPayload > 0
        ORDER BY MaxPayloadKg DESC NULLS LAST, AvgPayloadKg DESC;
    """,

    "4 Orbit Mix & Success Rate": """
        SELECT
            COALESCE(p.orbit, 'UNKNOWN') AS Orbit,
            COUNT(*) AS Launches,
            SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) AS Successes,
            ROUND(100.0 * SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS SuccessRatePct
        FROM FactLaunch f
        LEFT JOIN DimPayload p ON f.payload_id = p.id
        GROUP BY Orbit
        ORDER BY Launches DESC, SuccessRatePct DESC;
    """,

    "5 Top Launchpads by Success Rate (min 5 launches)": """
        WITH pad AS (
            SELECT
                lpad.name AS Launchpad,
                COUNT(*) AS Launches,
                SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) AS Successes
            FROM FactLaunch f
            JOIN DimLaunchpad lpad ON f.launchpad = lpad.id
            GROUP BY lpad.id, lpad.name
        )
        SELECT
            Launchpad,
            Launches,
            Successes,
            ROUND(100.0 * Successes / Launches, 2) AS SuccessRatePct
        FROM pad
        WHERE Launches >= 5
        ORDER BY SuccessRatePct DESC, Launches DESC;
    """,

    "6 Monthly Launch Trend (Count & Successes)": """
        SELECT
            substr(f.date_utc, 1, 7) AS YearMonth,
            COUNT(*) AS TotalLaunches,
            SUM(CASE WHEN f.success = 1 THEN 1 ELSE 0 END) AS Successes
        FROM FactLaunch f
        GROUP BY YearMonth
        ORDER BY YearMonth;
    """,

    "7 Recent Failed Launches (name/rocket)": """
        SELECT
            f.name AS LaunchName,
            substr(f.date_utc, 1, 10) AS LaunchDate,
            r.name AS RocketName,
            lpad.name AS Launchpad
        FROM FactLaunch f
        JOIN DimRocket r ON f.rocket = r.id
        JOIN DimLaunchpad lpad ON f.launchpad = lpad.id
        WHERE f.success = 0
        ORDER BY f.date_utc DESC
        LIMIT 10;
    """,

    "8 Heaviest Payload Launches": """
        SELECT
            f.name AS LaunchName,
            r.name AS RocketName,
            p.name AS PayloadName,
            p.orbit AS Orbit,
            p.mass_kg AS PayloadKg,
            substr(f.date_utc, 1, 10) AS LaunchDate
        FROM FactLaunch f
        JOIN DimRocket r ON f.rocket = r.id
        LEFT JOIN DimPayload p ON f.payload_id = p.id
        WHERE p.mass_kg IS NOT NULL
        ORDER BY p.mass_kg DESC
        LIMIT 10;
    """,

    "9 Average Payload Mass by Year": """
        SELECT
            substr(f.date_utc, 1, 4) AS Year,
            ROUND(AVG(p.mass_kg), 2) AS AvgPayloadKg,
            COUNT(p.id) AS PayloadCount
        FROM FactLaunch f
        LEFT JOIN DimPayload p ON f.payload_id = p.id
        WHERE p.mass_kg IS NOT NULL
        GROUP BY Year
        ORDER BY Year;
    """,

    "10 Data Quality Check: Orphaned/Null FKs": """
        SELECT
            f.id AS LaunchID,
            f.name AS LaunchName,
            CASE WHEN r.id IS NULL THEN 'Missing Rocket' END AS RocketIssue,
            CASE WHEN p.id IS NULL THEN 'Missing Payload' END AS PayloadIssue,
            CASE WHEN lpad.id IS NULL THEN 'Missing Launchpad' END AS LaunchpadIssue
        FROM FactLaunch f
        LEFT JOIN DimRocket r ON f.rocket = r.id
        LEFT JOIN DimPayload p ON f.payload_id = p.id
        LEFT JOIN DimLaunchpad lpad ON f.launchpad = lpad.id
        WHERE r.id IS NULL OR p.id IS NULL OR lpad.id IS NULL;
    """
}

# Directory for outputs
OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

results = {}

# Run and display each query (pretty print)
for title, sql in queries.items():
    print("\n" + "="*100)
    print(title)
    print("="*100)
    try:
        df = pd.read_sql_query(sql, conn)
        if not df.empty:
            print(df.head(20).to_string(index=False))
            # Save this result in memory so we can export it
            results[title] = df
        else:
            print("No results returned.")
    except Exception as e:
        print(f"Error running query: {e}")

# Export all results to a single Excel workbook (if we have any)
if results:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    xlsx_path = OUTPUTS_DIR / f"spacex_analytics_{timestamp}.xlsx"

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for title, df in results.items():

            # Excel sheet names must be valid and <= 31 characters
            invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
            sheet_name = title
            for ch in invalid_chars:
                sheet_name = sheet_name.replace(ch, " ")
            sheet_name = sheet_name[:31]

            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\n Excel exported: {xlsx_path}")
else:
    print("\n No non-empty query results to export.")


# Close the DB connection
conn.close()
print("\nFinished running SpaceX queries.")

# Auto-open outputs folder (Windows)
try:
    os.startfile(str(OUTPUTS_DIR))
    print(f"\n Opened outputs folder: {OUTPUTS_DIR}")
except Exception as e:
    print(f"\n Could not open folder automatically: {e}")
    print(f"You can open it manually here: {OUTPUTS_DIR}")
