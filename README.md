SpaceX Launch Data Engineering & Analytics Project

This project demonstrates an end-to-end data engineering workflow using public SpaceX launch data, including:

Ingestion from a public API

Normalization + transformation

Relational modeling in SQLite (PK/FK, indexes)

Analytical queries (SQL + Python)

Visualization

Packaging for full reproducibility

The project is built to satisfy the requirements of a data engineering assessment emphasizing ingestion, schema design, SQL analytics, Python craftsmanship, and clear communication.

1. Prerequisites

Install Python 3.9+ and the required packages:

pip install -r requirements.txt


Dependencies include:

requests
pandas
matplotlib

2. Project Structure
.
├── main_spacex.py            # Full end-to-end pipeline
├── requirements.txt
├── spacex.db                 # Created automatically (not committed)
└── outputs/
    ├── spacex_analytics_YYYYMMDD_HHMM.xlsx
    └── spacex_monthly_trend.png

3. Dataset: SpaceX REST API

Source:
https://github.com/r-spacex/SpaceX-API

This API provides rich, machine-readable JSON for launches, rockets, payloads, and launchpads.

Why this dataset?

Fully public, no auth required

Real operational and engineering data

Naturally relational: launches ↔ rockets ↔ payloads ↔ launchpads

Large enough for meaningful analytics (~10–20 MB normalized)

High-quality metadata enables business-style questions

4. Schema Design (SQLite)

This project uses a normalized schema optimized for analytical queries:

Dimension Tables

DimRocket — Rocket metadata

DimPayload — Payload characteristics

DimLaunchpad — Location and site performance

Fact Table

FactLaunch — One row per launch (grain)

Keys & Constraints

Natural SpaceX API IDs serve as primary keys.

Fact table contains foreign keys to rocket, payload, and launchpad.

Indexes were added to accelerate common analytical patterns (date, orbit, rocket, launchpad).

Why this schema?

Mirrors modern ELT warehouse design principles

Separates entities and events

Fast filtering and join performance

Idempotent upserts maintain correctness over time

5. End-to-End Pipeline

Run everything with:

python main_spacex.py


The pipeline:

Step A — Fetch

Downloads data from 4 SpaceX endpoints:

/launches

/rockets

/payloads

/launchpads

Step B — Normalize

pandas.json_normalize() flattens nested structures.

Step C — Load Into SQLite

Schema is created if not already present

Records are merged via SQLite-compatible upsert logic

PK/FK relationships remain intact

Indexes accelerate analytical queries

Step D — Analytics

Runs 10 SQL queries covering:

Aggregations

Joins

Filtering

Window-like patterns

Data quality checks

Step E — Export

Excel workbook (all query results)

Monthly trend visualization (PNG)

6. Analytical Questions & Rationale

Below are the questions answered by the pipeline, with a brief explanation of why each is analytically interesting:

1. Launches per Year with Success Rate

Reveals SpaceX's operational maturity and reliability trends over time. Useful for historical performance and capacity planning.

2. Top Rockets by Launch Count & Success Rate

Shows which vehicles are most relied upon and which are most reliable, informing fleet strategy.

3. Payload Mass by Rocket (Avg/Max)

Tracks capability growth and identifies which rocket classes handle heavier missions.

4. Orbit Mix & Success Rate

Determines how mission type (LEO, GTO, SSO, etc.) correlates with success and frequency.

5. Top Launchpads by Success Rate

Evaluates infrastructure performance and identifies top-performing launch facilities.

6. Monthly Launch Trend

Provides a time-series view of cadence and reliability, useful for forecasting or anomaly detection.

7. Most Recent Failed Launches

Aids in operational review and identifying root-cause patterns.

8. Heaviest Payload Launches

Highlights technological milestones and key achievements.

9. Average Payload Mass by Year

Shows whether SpaceX is trending toward heavier missions or more frequent smaller launches.

10. Data Quality Check

Ensures referential integrity and validates ingestion correctness (or API completeness).

📁 7. Outputs

After running the pipeline:

/outputs/spacex_analytics_YYYYMMDD_HHMM.xlsx

Contains one sheet per query.
Good for reviewers to scan your analytics quickly.

/outputs/spacex_monthly_trend.png

Line chart showing monthly launch counts and successes.

8. How to Reproduce Everything

Clone the repo:

git clone <your-public-github-url>
cd <repo>


Install dependencies:

pip install -r requirements.txt


Run the entire ingestion + analysis workflow:

python main_spacex.py


View outputs in the /outputs folder.

9. Optional Enhancements (for extra credit)

These are not required but demonstrate polish:

Add GitHub Actions CI to run python main_spacex.py

Add type hints (-> pd.DataFrame)

Add lightweight logging

Add CLI flags (e.g., --no-chart, --db custom.db)

Add unit tests for normalization functions

10. Assessment Checklist
Requirement	Status
Public dataset ≥10MB	 SpaceX API
Clear schema, PK/FK, indexing	 Implemented
Idempotent ingestion	 Upsert logic
Two SQL questions	 Ten provided
One Python (pandas/matplotlib)	 Monthly trend chart
End-to-end single command	 python main_spacex.py
README with rationale	 (this file)
requirements.txt	 Provided
No raw data in repo	 API-based
Author & Thanks

Author: Travis Christensen
This project is created exclusively for a data engineering skills assessment.
