# P.I.R.E. — Technical & Academic Project Documentation

## An XGBoost-Based Multilingual Expiry Risk Prediction and Decision Support System for Perishable Retail Inventory

---

## Abstract

Perishable inventory management represents one of the most critical operational challenges in the global retail grocery sector. Millions of tons of food are discarded annually due to inadequate monitoring, delayed clearance markdowns, and cold-chain compliance failures. This project introduces **P.I.R.E. (Perishable Inventory Risk Evaluation)**, an end-to-end decision-support and predictive analytics platform. P.I.R.E. couples an authentic **XGBoost multi-class classifier** with deterministic retail business logic and strict food safety compliance rules. 

The system processes real-world inventory attributes (such as shelf-life ratios, stock quantities, retail prices, and cold-chain temperatures), categorizing stock into five distinct risk levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, and `EXPIRED`. Crucially, the system enforces a non-negotiable food safety guardrail: items that have passed their expiration date are condemned for disposal and cannot be discounted or sold. For sellable goods facing expiry threats, an automated, category-capped markdown engine computes recommended clearance prices, inventory value-at-risk, and estimated recoverable revenue. An environmental simulation engine models the shelf-life consequences of refrigeration temperature shifts without altering pristine baseline data. The user interface features full localization in **English**, **Tamil (தமிழ்)**, and **Hindi (हिन्दी)**, robust **MongoDB** persistence with local fallback, and automated executive PDF audit reports generated via **ReportLab**.

---

## 1. Introduction & Background

### 1.1 Context
In retail grocery operations, perishable goods (comprising fresh dairy, meats, baked goods, poultry, and farm produce) account for up to 40% of overall supermarket revenue but represent more than 70% of total retail inventory shrinkage. Conventional retail inventory management systems rely on periodic manual shelf inspections or basic FIFO (First-In, First-Out) rotation. These manual methods suffer from high human error rates, delayed identification of at-risk products, and arbitrary markdowns.

### 1.2 The Role of Machine Learning
Machine learning offers predictive capacity by mapping complex non-linear interactions among multiple features:
- Elapsed product age vs. total shelf life
- Stock volume pressure vs. velocity of sales
- Environmental storage temperatures vs. manufacturer specifications

By implementing an **Extreme Gradient Boosting (XGBoost)** multi-class model, P.I.R.E. provides calibrated predictive probabilities for inventory risk tiers days in advance of product expiration.

---

## 2. Mathematical Modeling & Algorithmic Formulation

### 2.1 Feature Engineering Equations

1. **Days Remaining until Expiry (\(D_{\text{rem}}\)):**
   \[
   D_{\text{rem}} = \frac{T_{\text{exp}} - T_{\text{ref}}}{86400}
   \]
   Where \(T_{\text{exp}}\) is the unix timestamp of the expiration date and \(T_{\text{ref}}\) is the reference evaluation timestamp.

2. **Total Lifespan Duration (\(L_{\text{total}}\)):**
   \[
   L_{\text{total}} = \max\left(1.0, \frac{T_{\text{exp}} - T_{\text{mf}}}{86400}\right)
   \]

3. **Shelf-Life Consumption Ratio (\(R_{\text{life}}\)):**
   \[
   R_{\text{life}} = \text{clip}\left(\frac{D_{\text{rem}}}{L_{\text{total}}}, -1.0, 2.0\right)
   \]

4. **Temperature Abuse Anomaly (\(\Delta T_{\text{abuse}}\)):**
   \[
   \Delta T_{\text{abuse}} = 
   \begin{cases}
   T_{\text{actual}} - T_{\text{max\_allowed}} & \text{if } T_{\text{actual}} > T_{\text{max\_allowed}} \\
   T_{\text{min\_allowed}} - T_{\text{actual}} & \text{if } T_{\text{actual}} < T_{\text{min\_allowed}} \\
   0 & \text{otherwise}
   \end{cases}
   \]

### 2.2 XGBoost Objective Formulation
The model optimizes a multi-class softmax loss function over \(K = 5\) classes:
\[
\mathcal{L}(\theta) = -\sum_{i=1}^{N} \sum_{k=1}^{K} y_{i,k} \log\left(\frac{e^{f_k(x_i)}}{\sum_{j=1}^K e^{f_j(x_i)}}\right) + \sum_{m=1}^M \Omega(f_m)
\]
Where \(\Omega(f) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2\) represents the tree complexity regularization term preventing overfitting.

### 2.3 Clearance Markdown Formulation
Let \(P_0\) be unit retail price, \(Q\) be stock quantity, \(R \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{CRITICAL}, \text{EXPIRED}\}\), and \(C_{\text{cap}}\) be the category maximum discount ceiling:

\[
d_{\text{raw}} = 
\begin{cases}
0.0 & \text{if } R = \text{EXPIRED} \quad \text{(Strict Food Safety Constraint)} \\
0.50 & \text{if } R = \text{CRITICAL} \\
0.35 & \text{if } R = \text{HIGH} \\
0.15 & \text{if } R = \text{MEDIUM} \\
0.0 & \text{if } R = \text{LOW}
\end{cases}
\]

The final effective discount percentage \(d^*\) is bounded:
\[
d^* = \min(d_{\text{raw}}, C_{\text{cap}}, d_{\text{global\_max}})
\]

Financial valuations:
- **Selling Price (\(P_{\text{sale}}\)):** \(P_{\text{sale}} = P_0 \times (1 - d^*)\)
- **Inventory Value at Risk (\(V_{\text{risk}}\)):**
  \[
  V_{\text{risk}} = 
  \begin{cases}
  P_0 \times Q & \text{if } R \in \{\text{MEDIUM}, \text{HIGH}, \text{CRITICAL}, \text{EXPIRED}\} \\
  0 & \text{if } R = \text{LOW}
  \end{cases}
  \]
- **Estimated Recoverable Value (\(V_{\text{recov}}\)):**
  \[
  V_{\text{recov}} = 
  \begin{cases}
  P_{\text{sale}} \times Q & \text{if } R \neq \text{EXPIRED} \text{ and } d^* > 0 \\
  0 & \text{otherwise}
  \end{cases}
  \]

---

## 3. Database Schema & Architecture

### MongoDB Collections Design (`pire_inventory` Database)

1. **`products`:** Master catalog storing SKU metadata (`prod_id`, `prod_name`, `category`, `price`, `storage_temp_norm`).
2. **`predictions`:** Historical inference records containing ML probabilities, assigned risk tier, confidence scores, and timestamps.
3. **`discount_recommendations`:** Markdown audit records with recommended clearance prices and potential recovery calculations.
4. **`audit_logs`:** System event log tracking user ingestion, model retraining, and export activities.
5. **`model_metadata`:** Versioned registry storing hyperparameter sets, test evaluation metrics, confusion matrices, and training dataset signatures.

### Local Storage Fallback Mode
When MongoDB Community Server is offline or uninstalled, the system transitions automatically to the `LOCAL_FALLBACK` engine without runtime failure. Data is persisted to synchronized JSON stores in `local_fallback_db/`.

---

## 4. Verification & Testing Results

The automated test suite in `tests/` executes 17 test cases across five test modules:
- `test_data_validation.py`: Verifies column aliasing, inverted date checks, negative price/quantity detection, and missing fields.
- `test_risk_engine.py`: Verifies food safety overrides (expired products never downgraded to safe) and temperature anomaly escalations.
- `test_discount_engine.py`: Asserts 0% discount on expired products, category capping, and financial formulas.
- `test_prediction.py`: Verifies feature engineering outputs, XGBoost training, probability calibrations, and single-class dataset rejection.
- `test_reports.py`: Validates ReportLab PDF generation, CSV byte streams, and offline database fallback resilience.

**Results:** 17 Passed / 0 Failed (100% Pass Rate).

---

## 5. Conclusion

P.I.R.E. successfully demonstrates that predictive machine learning can be combined with deterministic retail business rules to solve complex inventory challenges. By prioritizing food safety, transparent clearance discounts, environmental simulation, and native multilingual support, the application provides a production-ready model for modern perishable retail operations.
