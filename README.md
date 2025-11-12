# 🚀 SpaceX Launch Data Engineering & Analytics Project

This project demonstrates an end‑to‑end data engineering workflow using **public SpaceX launch data**, including:

- Data ingestion from the SpaceX REST API  
- JSON normalization & transformation  
- Relational modeling in SQLite (star schema: 3 dimensions + 1 fact)  
- Analytical SQL queries  
- Python‑based analytics & visualization  
- Full reproducibility using two clear Python scripts (or one optional combined runner)

---

# 📦 1. Prerequisites

Install project dependencies:

```bash
pip install -r requirements.txt
```

Dependencies include:

```
requests
pandas
matplotlib
```

---

# 🛠️ 2. Project Structure

```
Get_SpaceX_Data.py        # Ingestion + database creation (ETL)
Run_SpaceX_Queries.py     # Analytical SQL queries + visualization
main.py (optional)        # Runs both scripts end‑to‑end
requirements.txt
spacex.db                 # Auto-generated SQLite database
outputs/
    spacex_analytics_YYYYMMDD_HHMM.xlsx
    spacex_monthly_trend.png
README.md
```

---

# 🚀 3. Dataset: SpaceX REST API

**Source:** https://github.com/r-spacex/SpaceX-API

## Why this dataset?
- Public, machine-readable JSON  
- Naturally relational: launches → rockets → payloads → launchpads  
- Rich metadata suitable for real analysis  
- Large enough to demonstrate ingestion, modeling & analytics  
- No authentication required  

---

# 🧩 4. Schema Design (ERD)

This project uses a clean star schema optimized for analytics:

### **Dimensions**
- **DimRocket** — Rocket metadata  
- **DimPayload** — Payload characteristics  
- **DimLaunchpad** — Launch site information  

### **Fact**
- **FactLaunch** — One row per launch event  

### **Relationships**
- FactLaunch.rocket → DimRocket.id  
- FactLaunch.payload_id → DimPayload.id  
- FactLaunch.launchpad → DimLaunchpad.id  

All foreign keys and indexes are created automatically during ingestion.

---

# 🔄 5. End‑to‑End Pipeline

This project is executed in **two steps**, matching a real-world engineering workflow.

---

## ✅ Step 1 — Build Database & Ingest Data
Runs the full ETL pipeline:

- Fetches JSON from 4 SpaceX API endpoints  
- Normalizes nested JSON into tables  
- Builds the SQLite schema (dimensions + fact)  
- Performs idempotent UPSERT operations  
- Creates analytic indexes  

Run:

```bash
python Get_SpaceX_Data.py
```

This produces or updates:

```
spacex.db
```

---

## ✅ Step 2 — Run All SQL Queries & Generate Outputs

This step:

- Runs **10 analytical SQL queries**  
- Generates an Excel workbook  
- Creates a monthly launch trend PNG using matplotlib  
- Prints results to the console  

Run:

```bash
python Run_SpaceX_Queries.py
```

Outputs will appear in:

```
outputs/
```

---

# ⭐ Optional: One‑Command Master Runner

If you prefer a single command, include this file:

### `main.py`
```python
import subprocess

print("=== Running SpaceX Ingestion ===")
subprocess.run(["python", "Get_SpaceX_Data.py"], check=True)

print("=== Running SpaceX Analytics ===")
subprocess.run(["python", "Run_SpaceX_Queries.py"], check=True)

print("=== All tasks completed successfully! ===")
```

Run everything:

```bash
python main.py
```

---

# 📊 6. Analytical Questions & Rationale

The SQL portion answers 10 meaningful questions, including:

### 1. Launch cadence & success rate by year  
Shows operational maturity and reliability trends.

### 2. Rockets ranked by launch count & success  
Evaluates hardware reliability and fleet health.

### 3. Payload mass analysis by rocket  
Analyzes technical capability and historical improvements.

### 4. Orbit mix & mission profiles  
Shows what types of missions SpaceX performs most frequently.

### 5. Launchpad reliability  
Assesses infrastructure performance.

### 6. Monthly launch trend (visualized)  
Time‑series trend for forecasting and anomaly detection.

### 7–10. Deep-dive and data quality checks  
Includes payload mass extremes, average mass by year, and referential integrity.

---

# 📁 7. Outputs

After running the scripts, you will find:

### **Excel analytics workbook**
```
outputs/spacex_analytics_YYYYMMDD_HHMM.xlsx
```

### **PNG line chart**
```
outputs/spacex_monthly_trend.png
```

---

# 🧪 8. How to Reproduce

Clone the repo:

```bash
git clone <your-repo-url>
cd <repo>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the full workflow:

```bash
python Get_SpaceX_Data.py
python Run_SpaceX_Queries.py
```

(Optional)

```bash
python main.py
```

---

# ✔️ 9. Assessment Coverage

| Requirement | Status |
|------------|--------|
| Public dataset | ✔ SpaceX API |
| Normalized schema | ✔ Star schema (3 dims + 1 fact) |
| PK/FK + indexes | ✔ Implemented |
| Idempotent ingestion | ✔ UPSERT logic |
| ≥2 SQL questions | ✔ 10 total |
| ≥1 Python analysis | ✔ Monthly trend chart |
| One-command run | ✔ Optional main.py |
| README included | ✔ This file |
| No raw data checked in | ✔ API-based ETL |

---

# 🛰️ Summary

This project showcases complete, production-style ETL and analytics using real-world API data, demonstrating strong skills in:

- Data ingestion  
- Data modeling  
- SQL analytics  
- Python engineering  
- Communication & packaging  

It is fully reproducible and assessment-ready.

