
# 🚀 SpaceX Launch Data Engineering & Analytics Project

This project demonstrates an end-to-end data engineering workflow using **public SpaceX launch data**, including:

- Ingestion from a public API  
- Normalization & transformation  
- Relational modeling (SQLite star schema)  
- Analytical SQL queries  
- Python-based visualization  
- Full reproducibility through a single command  

---

## 📦 1. Prerequisites

Install Python dependencies:

```
pip install -r requirements.txt
```

Dependencies include:

```
requests
pandas
matplotlib
```

---

## 🛠️ 2. Project Structure

```
main_spacex.py           # Full ingestion + analysis pipeline
requirements.txt
spacex.db                # SQLite database (auto-generated)
outputs/
    spacex_analytics_YYYYMMDD_HHMM.xlsx
    spacex_monthly_trend.png
```

---

## 🚀 3. Dataset: SpaceX REST API

**Source:** https://github.com/r-spacex/SpaceX-API

**Why this dataset?**

- Rich real-world engineering + launch data  
- Good relational structure (launches → rockets, payloads, launchpads)  
- Public and machine-readable  
- Large enough for real analytics  

---

## 🧩 4. Schema Design (ERD)

A standard star schema:

### **Dimensions**
- **DimRocket**
- **DimPayload**
- **DimLaunchpad**

### **Fact**
- **FactLaunch** (grain: one per launch)

### **Keys**
- FactLaunch.rocket → DimRocket.id  
- FactLaunch.payload_id → DimPayload.id  
- FactLaunch.launchpad → DimLaunchpad.id  

---

## 🔄 5. End-to-End Pipeline

Run everything with:

```
python main_spacex.py
```

The pipeline:

1. Fetches SpaceX API JSON  
2. Normalizes nested data  
3. UPSERTS rows safely into SQLite  
4. Runs 10 SQL analytical queries  
5. Generates:
   - Excel workbook of results  
   - PNG chart of monthly launch trend  

---

## 📊 6. Analytics & Rationale

### Examples:
- **Launches per year** → shows reliability and cadence  
- **Rocket performance** → shows fleet maturity  
- **Payload mass analysis** → measures capability growth  
- **Orbit mix** → reveals mission types  
- **Launchpad performance** → infrastructure reliability  

---

## 📁 7. Outputs

After running:

```
/outputs/spacex_analytics_YYYYMMDD_HHMM.xlsx  
/outputs/spacex_monthly_trend.png  
```

---

## 🧪 8. How to Reproduce

```
git clone <your-repo>
cd <repo>
pip install -r requirements.txt
python main_spacex.py
```

---

## ✔️ 9. Assessment Coverage

| Requirement | Status |
|------------|--------|
| Public dataset (10MB+) | ✅ SpaceX API |
| Normalized schema | ✅ Star schema |
| PK/FK + indexes | ✅ Implemented |
| Idempotent ingestion | ✅ Upsert logic |
| ≥2 SQL queries | ✅ 10 total |
| ≥1 Python analysis | ✅ Trend chart |
| One-command run | ✅ `python main_spacex.py` |
| README included | ✅ This file |

---

This project is designed specifically for a data engineering skills assessment and demonstrates real-world ETL, modeling, and analytical capabilities.
