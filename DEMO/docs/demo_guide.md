# P.I.R.E. — Live College Demonstration Guide & Viva Defense

This guide provides a step-by-step presentation script and anticipated examiner questions with accurate technical answers for your final year project viva demonstration.

---

## 1. Quick Launch Checklist (Before the Presentation)

1. Open **Windows PowerShell**.
2. Navigate to the project root:
   ```powershell
   cd c:\Users\deenr\Desktop\FinalYearProject\DEMO
   ```
3. Run the automated test suite to confirm 100% test pass status:
   ```powershell
   python -m pytest tests -v
   ```
4. Start the application:
   ```powershell
   python -m streamlit run app.py
   ```
5. The application will open at `http://localhost:8501`. Have it open in full-screen browser mode.

---

## 2. Step-by-Step 5-Minute Live Demo Script

### Step 1: Introduction & Title (30 Seconds)
- **What to say:**  
  *"Good morning respected evaluators. Today I am presenting **P.I.R.E. — Perishable Inventory Risk Evaluation**, an XGBoost-based multilingual expiry risk prediction and decision support system for retail inventory. Our system tackles two massive retail problems: food waste and food safety compliance."*

### Step 2: Ingestion & Automatic Demonstration (45 Seconds)
- **What to show:**  
  Point to the sidebar. Show that `sample_inventory.csv` is loaded automatically.
- **What to say:**  
  *"The system automatically ingests inventory datasets in CSV or Excel format. Our flexible data loader handles real-world column aliases like `mrp`, `price`, `stock`, and `expiration_date`. It runs sanity validation checks, identifying inverted dates, negative prices, or duplicate SKUs without crashing."*

### Step 3: Multilingual Interface (30 Seconds)
- **What to show:**  
  In the sidebar, switch the language dropdown from **English** to **தமிழ் (Tamil)**, then to **हिन्दी (Hindi)**.
- **What to say:**  
  *"To support diverse retail workforce environments across India, P.I.R.E. features a native translation engine supporting English, Tamil, and Hindi. Notice how all KPI cards, navigation tabs, buttons, and safety alerts dynamically update."*  
  *(Switch back to English for the rest of the demonstration).*

### Step 4: Food Safety Override & Overview Dashboard (1 Minute)
- **What to show:**  
  Tab 1 (Overview Dashboard). Point to the red food safety alert banner and KPI cards:
  - Total Products: `134`
  - Expired: `33`
  - Critical: `8`
  - Inventory Value at Risk: `~₹1,035,000`
  - Potential Recoverable Value: `~₹498,000`
- **What to say:**  
  *"Here is our most critical engineering principle: **Food safety is non-negotiable**. If a product has passed its expiration date, P.I.R.E. strictly classifies it as EXPIRED. It is locked out from clearance discounts, cannot be sold, and is flagged for quarantine disposal. Low model risk is never allowed to override food safety laws."*

### Step 5: XGBoost Risk Prediction & Diagnosis (1 Minute)
- **What to show:**  
  Click **Tab 3: 🤖 ML Risk Prediction**. Scroll to the individual SKU inspector. Select a product.
- **What to say:**  
  *"In Tab 3, we see the output of our trained XGBoost multi-class classifier. The model calculates probability confidence scores across 5 risk tiers based on derived features: shelf-life ratio, days to expiry, product age, and temperature deviations. Every recommendation is accompanied by human-readable explanations based on empirical data."*

### Step 6: What-If Cold-Chain Simulation (1 Minute)
- **What to show:**  
  Click **Tab 5: 🌡️ What-If Storage Simulation**. Slide the temperature slider from `0°C` to `+6°C`.
- **What to say:**  
  *"Supermarket chillers often experience mechanical faults. In Tab 5, store managers can simulate temperature fluctuations without altering the pristine raw data. Notice how elevating the temperature triggers thermal abuse flags, escalates risk categories, and re-calculates the increased inventory value at risk in real time."*

### Step 7: Clearance Discounts & PDF Audit Report (45 Seconds)
- **What to show:**  
  Click **Tab 4: 🏷️ Discount Recommendations** and then **Tab 7: 📄 Reports & Exports**. Click **"Download Official PDF Report"** and open the generated PDF.
- **What to say:**  
  *"Finally, the system calculates transparent, category-capped clearance markdowns to liquidate near-expiry stock before it spoils. Management can download an official publication-quality executive audit PDF report generated directly via ReportLab."*

---

## 3. Frequently Asked Examiner Questions & Model Answers

### Q1: "Why did you choose XGBoost instead of a Deep Learning neural network or standard Logistic Regression?"
> **Answer:**  
> *"Tabular inventory data exhibits complex non-linear feature interactions (such as temperature deviation combined with shelf-life ratios) where tree-based ensemble methods consistently outperform neural networks. XGBoost provides superior gradient-boosting regularization (\(L_1\) and \(L_2\)), handles missing values inherently, resists overfitting on medium-sized retail datasets, and produces calibrated multi-class probability distributions with microsecond inference times."*

### Q2: "What prevents your machine-learning model from recommending discounts on expired food to maximize sales?"
> **Answer:**  
> *"We maintain a strict separation between machine-learning prediction and deterministic food safety business rules. While XGBoost predicts risk probabilities, the **RiskEngine** enforces a hard deterministic override: if `days_remaining <= 0`, the product is permanently classified as `EXPIRED`. The **DiscountEngine** then enforces a hard zero-discount rule (`recommended_discount_pct = 0.0`) and marks `is_eligible_for_sale = False`. Machine learning provides decision support, but food safety laws have absolute priority."*

### Q3: "How does the system handle MongoDB failure or a system without MongoDB installed?"
> **Answer:**  
> *"P.I.R.E. implements an enterprise-grade connection fallback pattern. On initialization, `DatabaseManager` pings MongoDB with a 1.5-second timeout. If the service is unreachable or uninstalled, the application automatically transitions into `LOCAL_FALLBACK` mode. All predictions, model metadata, and audit logs are persisted to structured local JSON stores in `local_fallback_db/`. The application never crashes and transparently indicates fallback status to the user."*

### Q4: "Where did you get your dataset? Is it real retailer data?"
> **Answer:**  
> *"To protect commercial confidentiality and ensure reproducibility, we developed a synthetic demonstration generator that produces realistic perishable inventory modeled after Indian retail chains (Amul, Mother Dairy, Licious, Harvest Gold). The dataset contains 134 records across 6 food categories with authentic shelf-life durations, storage temperatures, and edge cases to showcase data validation."*

### Q5: "What are the limitations of this project and what would you build next?"
> **Answer:**  
> *"Currently, our temperature simulation uses rule-governed thermal thresholds rather than microbiological kinetic growth models (e.g., the Arrhenius equation). In future work, we plan to connect real-time IoT RFID temperature sensors in cold-storage units and integrate with electronic shelf labels (ESLs) for automatic dynamic repricing."*
