# P.I.R.E. — Perishable Inventory Risk Evaluation

> **An XGBoost-Based Multilingual Expiry Risk Prediction and Decision Support System for Perishable Retail Inventory**

---

## 1. Project Overview

**P.I.R.E. (Perishable Inventory Risk Evaluation)** is an intelligent retail decision-support system designed to mitigate post-harvest food waste, optimize clearance pricing, and enforce strict food safety compliance across perishable retail grocery supply chains. 

Built using **Python**, **XGBoost**, and **Streamlit**, P.I.R.E. bridges the gap between machine-learning risk forecasting and deterministic retail compliance rules.

### Key Highlights
- **Authentic XGBoost Multi-Class Classification:** Evaluates perishable stock across 5 calibrated risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, and `EXPIRED`).
- **Strict Food Safety Guardrail:** Physically expired goods are strictly flagged for immediate removal and quarantined with **0% clearance discount**—food safety regulations cannot be bypassed.
- **Dynamic Clearance Pricing Engine:** Calculates category-governed discount markdowns, total inventory value-at-risk, and estimated recoverable revenue.
- **What-If Cold-Chain Simulation:** Tests the downstream shelf-life impact of ambient temperature fluctuations without altering pristine inventory datasets.
- **Centralized Multilingual Interface:** Complete, native localized UI in **English**, **Tamil (தமிழ்)**, and **Hindi (हिन्दी)**.
- **Enterprise-Grade Database Resilience:** Native **MongoDB Community Server** persistence with automatic, zero-crash fallback to local JSON storage.
- **Executive Audit Reports:** On-demand generation of publication-grade PDF audit reports via **ReportLab** and CSV data exports.

---

## 2. Problem Statement & Objectives

### Problem Statement
Retail supermarkets and grocery chains face massive operational and financial losses due to perishable inventory expiration:
1. **Unsalable Inventory Write-offs:** Perishable categories (Dairy, Meat, Bakery, Produce) have narrow shelf-life windows. Without early warning systems, stock expires un-monitored.
2. **Food Safety Violations:** Selling expired or temperature-compromised food incurs severe legal liabilities and health hazards.
3. **Inefficient Markdowns:** Manual markdowns are often applied too late or too aggressively, eroding gross retail margins.

### Project Aim & Objectives
- **Predictive Expiry Modeling:** Train an XGBoost classifier on temporal, volume, and cold-chain features to identify imminent risk days before expiration.
- **Automated Decision Support:** Formulate transparent, category-capped clearance discount schedules to accelerate sell-through while goods remain fresh and safe.
- **Food Safety Compliance:** Guarantee that expired items are condemned and removed from sale.
- **Environmental Simulation:** Assess cold-chain resilience by simulating refrigeration temperature anomalies.
- **Accessibility:** Deliver a localized interface in English, Tamil, and Hindi for regional retail staff.

---

## 3. System Architecture

```
                       +-----------------------------------+
                       |    Retail Ingestion (CSV / XLS)   |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       | Data Loader & Column Mapping Engine|
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |    Data Validation & Anomaly Check|
                       +-----------------+-----------------+
                                         |
                       +-----------------+-----------------+
                       |    Feature Engineering Pipeline   |
                       |  - Days to Expiry  - Shelf Ratio  |
                       |  - Age in Days     - Temp Delta   |
                       +--------+-----------------+--------+
                                |                 |
                                v                 v
             +------------------+---+         +---+------------------+
             | XGBoost Risk Model   |         | Deterministic Rules  |
             | Multi-Class ML Tier  |         | Food Safety Guardrail|
             +------------------+---+         +---+------------------+
                                \                 /
                                 \               /
                                  v             v
                       +----------+-------------+----------+
                       |    Consolidated Risk Assessment   |
                       |  - LOW | MEDIUM | HIGH | CRITICAL  |
                       |  - EXPIRED (Zero-Sale Override)   |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       | Dynamic Clearance Discount Engine |
                       |  - Category Caps   - Markdowns    |
                       |  - Value-at-Risk   - Est Recovery |
                       +--------+-----------------+--------+
                                |                 |
          +---------------------+                 +--------------------+
          |                                                            |
          v                                                            v
+---------+--------------------+                     +-----------------+--------------------+
|  Streamlit 8-Tab Dashboard   |                     |     Persistence & Reporting Layer    |
| - Multilingual (EN, TA, HI)  |                     | - MongoDB / Local JSON Fallback      |
| - Interactive Plotly Charts  |                     | - ReportLab PDF Audit Reports        |
| - What-If Storage Simulation |                     | - Clean CSV Streaming Exports        |
+------------------------------+                     +--------------------------------------+
```

---

## 4. Technologies Used

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10 – 3.13 | Core programming language |
| **Web Interface** | Streamlit 1.39+ | Interactive reactive web application |
| **Machine Learning**| XGBoost 2.1+ | Multi-class gradient-boosted decision trees |
| **Data Processing** | pandas, NumPy, scikit-learn | Feature engineering, preprocessing & metrics |
| **Data Visualization**| Plotly 5.24+ | Interactive responsive charts & distribution graphs |
| **PDF Generation** | ReportLab 5.0+ | Executive audit PDF document compiler |
| **File Formats** | openpyxl, csv | Excel and CSV workbook support |
| **Persistence** | PyMongo 4.9+ | MongoDB Community Server database connectivity |
| **Fallback DB** | Local JSON Store | Resilient zero-downtime offline storage |
| **Testing** | pytest 8.3+ | Automated test suite (17 comprehensive test cases) |

---

## 5. Dataset Specification

### Supported Fields & Aliases
P.I.R.E. includes an intelligent column-mapping engine that automatically resolves common naming variations:

| Standard Field | Acceptable Aliases | Type | Description |
| :--- | :--- | :--- | :--- |
| `prod_id` | `product_id`, `item_id`, `sku`, `id` | String | Unique product identifier |
| `prod_name` | `product_name`, `item_name`, `name` | String | Product name |
| `prod_brand` | `brand`, `manufacturer`, `make` | String | Brand / Manufacturer |
| `supplier_location` | `supplier`, `origin`, `location` | String | Distribution / Logistics hub |
| `category` | `product_category`, `cat`, `dept` | String | Product food category |
| `quantity` | `qty`, `stock`, `units`, `inventory_count` | Integer | Units currently in stock |
| `prod_price` | `price`, `unit_price`, `mrp`, `cost` | Float | Unit retail selling price |
| `temp` | `temperature`, `storage_temp` | Float | Measured storage temperature (°C) |
| `mf_date` | `manufacturing_date`, `mfg_date`, `mfg` | Date | Date of packaging / manufacture |
| `exp_date` | `expiry_date`, `expiration_date`, `use_by`| Date | Manufacturer expiration date |

> **Synthetic Demonstration Data Notice:**  
> The included file `data/sample_inventory.csv` contains 134 synthetic records generated dynamically for educational and demonstration purposes. It includes products spanning Dairy, Meat, Bakery, Produce, Beverages, and Packaged Foods across all 5 risk tiers, plus intentional edge cases to demonstrate validation alerts.

---

## 6. Machine Learning Methodology

### Feature Engineering
1. **`days_until_expiry`:** Time-delta in days between expiration date and reference date (`exp_date - reference_date`).
2. **`product_age_days`:** Elapsed days since packaging (`reference_date - mf_date`).
3. **`total_shelf_life`:** Total expected product lifespan (`exp_date - mf_date`).
4. **`shelf_life_ratio`:** Ratio of remaining days to total shelf life (`days_until_expiry / total_shelf_life`).
5. **`temp_deviation`:** Absolute thermal deviation outside the acceptable category storage temperature window.
6. **`quantity` & `prod_price`:** Numerical stock volume and pricing features.
7. **`category`:** One-hot encoded categorical vector.

### Target Classification Strategy
When trained on unlabelled datasets, proxy labels are generated using documented expiry-urgency business rules (0: LOW, 1: MEDIUM, 2: HIGH, 3: CRITICAL, 4: EXPIRED).  
*Notice: These proxy labels serve as an educational training baseline and do not imply biochemical laboratory assay of spoilage.*

### Evaluation Metrics
- Stratified test-split evaluation (80/20 train/test).
- Evaluates **Accuracy**, **Weighted Precision**, **Weighted Recall**, and **Weighted F1-Score**.
- Generates a full multi-class **Confusion Matrix**.

---

## 7. Windows Installation & Launch Guide

### Prerequisites
- Windows 10 or 11 with PowerShell
- Python 3.10+ installed ([python.org](https://www.python.org/downloads/))

### Step 1: Open PowerShell and Navigate to Workspace
```powershell
cd c:\Users\deenr\Desktop\FinalYearProject\DEMO
```

### Step 2: (Optional) Set Execution Policy
If PowerShell restricts running scripts, permit local execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Required Packages
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run Automated Tests
Verify system integrity by running all 17 automated unit tests:
```powershell
python -m pytest tests -v
```

### Step 5: Launch the P.I.R.E. Streamlit Application
```powershell
python -m streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 8. Live Demonstration Walkthrough

1. **Launch App:** Run `python -m streamlit run app.py`.
2. **Observe Auto-Load:** The dashboard immediately presents 134 sample SKUs categorized across all risk tiers with KPI cards and Plotly charts.
3. **Language Selector:** Toggle the language dropdown in the sidebar to **தமிழ் (Tamil)** or **हिन्दी (Hindi)** to demonstrate real-time UI localization.
4. **Inspect Food Safety Override:** Review the top red warning banner showing expired products strictly flagged for removal with 0% discount.
5. **Inspect ML Risk Predictions (Tab 3):** View XGBoost prediction probabilities, confidence scores, and drill into individual SKU diagnostic explanations.
6. **Review Discount Strategies (Tab 4):** Observe category-governed clearance prices and the calculated potential inventory recovery value.
7. **Run What-If Simulation (Tab 5):** Move the temperature slider to `+5°C` to simulate cooling failure. Observe how elevated temperatures escalate shelf-life risk and increase financial value-at-risk.
8. **Inspect Model Metrics (Tab 6):** Review the genuine test-split accuracy, confusion matrix, and training metadata.
9. **Export PDF Audit Report (Tab 7):** Click **"Download Official PDF Report"** to download and review the publication-quality ReportLab executive summary.
10. **Database Status (Tab 8):** Demonstrate persistent storage status (MongoDB or automatic Local File Fallback) and the real-time audit log.

---

## 9. Academic Limitations & Future Enhancements

### Current Limitations
- Temperature simulation is rule-governed and does not model complex microbial kinetic spoilage curves.
- Estimated recovery revenue assumes 100% sell-through of discount-eligible items.
- Model training is anchored to dates relative to ingestion time.

### Future Enhancements
- Integration with real-time IoT RFID temperature and humidity sensors in retail chillers.
- Computer-vision freshness scoring using edge cameras for unlabelled fresh produce.
- Price elasticity optimization using historical point-of-sale (POS) transaction logs.
- Direct ERP integration (SAP S/4HANA, Oracle Retail) for automated electronic shelf label (ESL) updates.

---

## 10. License & Author Information

- **Project:** P.I.R.E. (Perishable Inventory Risk Evaluation)
- **Author:** College Final Year Project
- **Academic Year:** 2026
