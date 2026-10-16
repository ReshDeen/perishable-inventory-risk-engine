"""
P.I.R.E. — Perishable Inventory Risk Evaluation System
Main Streamlit Application
Interactive Multilingual Web Dashboard for Retail Inventory Risk Assessment and Clearance Decision Support
"""

import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    CATEGORY_STORAGE_TEMPS,
    DATA_DIR,
    DEFAULT_LANGUAGE,
    DISCOUNT_CONFIG,
    MODELS_DIR,
    REPORTS_DIR,
    RISK_LEVELS,
    SUPPORTED_LANGUAGES,
)
from src.data_loader import DataLoader
from src.data_validation import DataValidator
from src.database import DatabaseManager
from src.discount_engine import DiscountEngine
from src.model_training import ModelTrainer
from src.prediction import RiskPredictor
from src.report_generator import ReportGenerator
from src.risk_engine import RiskEngine
from src.simulation import StorageSimulator
from src.translations import t


# -----------------------------------------------------------------------------
# Streamlit Application Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="P.I.R.E. — Inventory Risk Evaluation",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished dashboard typography and cards
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        margin-top: 0.25rem;
        color: #0F172A;
    }
    .kpi-value-danger { color: #DC2626 !important; }
    .kpi-value-warning { color: #D97706 !important; }
    .kpi-value-success { color: #059669 !important; }
    .kpi-value-primary { color: #2563EB !important; }

    .food-safety-banner {
        background-color: #FEF2F2;
        border-left: 6px solid #DC2626;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #991B1B;
        font-weight: 600;
    }
    .status-badge-mongodb {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #A7F3D0;
    }
    .status-badge-fallback {
        background-color: #FFFBEB;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #FDE68A;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE

if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if "predictor" not in st.session_state:
    st.session_state.predictor = RiskPredictor()

if "assessed_df" not in st.session_state:
    st.session_state.assessed_df = None

if "validation_summary" not in st.session_state:
    st.session_state.validation_summary = None

if "dataset_source_label" not in st.session_state:
    st.session_state.dataset_source_label = "None"

lang = st.session_state.language


def load_dataset_pipeline(file_source, filename="uploaded_file"):
    """Core pipeline function: load, validate, predict, risk assessment, and discount generation."""
    with st.spinner("Processing dataset through P.I.R.E. evaluation pipeline..."):
        raw_df, std_df, meta = DataLoader.load_file(file_source, filename=filename)
        if raw_df is None or meta.get("error"):
            st.error(f"Error loading file: {meta.get('error')}")
            return False

        # Validate
        is_operable, annotated_df, val_summary = DataValidator.validate_dataset(std_df)
        st.session_state.validation_summary = val_summary

        if not is_operable:
            st.error(f"Dataset invalid: {val_summary['critical_errors']}")
            return False

        # Run XGBoost Inference
        predictor = st.session_state.predictor
        if not predictor.is_loaded:
            # Train model if not present
            trainer = ModelTrainer()
            success, train_res = trainer.train_model(annotated_df)
            if success:
                predictor._try_load()

        if predictor.is_loaded:
            p_success, pred_df, p_err = predictor.predict(annotated_df)
            if not p_success:
                st.warning(f"ML prediction note: {p_err}. Falling back to business rule assessment.")
                pred_df = annotated_df
        else:
            pred_df = annotated_df

        # Evaluate Risk Engine Rules + Food Safety Override
        assessed_df = RiskEngine.evaluate_dataframe(pred_df)

        # Generate Safe Discount Recommendations
        disc_engine = DiscountEngine()
        final_df = disc_engine.generate_recommendations(assessed_df)

        st.session_state.assessed_df = final_df
        st.session_state.dataset_source_label = filename

        # Log audit
        st.session_state.db_manager.log_audit(
            "DATASET_EVALUATION",
            f"Successfully processed {len(final_df)} records from '{filename}'."
        )
        return True


# Auto-load sample dataset if state is empty on startup
if st.session_state.assessed_df is None:
    sample_path = DATA_DIR / "sample_inventory.csv"
    if sample_path.exists():
        load_dataset_pipeline(sample_path, filename="Built-in Sample Demonstration Dataset")


# -----------------------------------------------------------------------------
# Sidebar Configuration & Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/snowflake.png", width=64)
    st.markdown("### **P.I.R.E. Console**")
    st.caption("Perishable Inventory Risk Evaluation")

    # Language Selector
    st.markdown("---")
    selected_lang_name = st.selectbox(
        t("select_language", lang),
        options=list(SUPPORTED_LANGUAGES.values()),
        index=list(SUPPORTED_LANGUAGES.keys()).index(lang)
    )
    # Find matching lang code
    for code, name in SUPPORTED_LANGUAGES.items():
        if name == selected_lang_name:
            if st.session_state.language != code:
                st.session_state.language = code
                st.rerun()

    lang = st.session_state.language

    # Database Status Indicator
    st.markdown("---")
    st.markdown("**Database Persistence:**")
    db_stat = st.session_state.db_manager.get_status()
    if db_stat["is_connected"]:
        db_type = "Cloud Atlas" if "mongodb+srv" in str(db_stat.get("target_uri", "")) else "Community Server"
        st.markdown(
            f"<div class='status-badge-mongodb'>🟢 MongoDB {db_type} (Connected)</div>",
            unsafe_allow_html=True
        )
        st.caption(f"DB: `{db_stat['database_name']}`")
    else:
        st.markdown(
            f"<div class='status-badge-fallback'>🟡 Local File Fallback Active</div>",
            unsafe_allow_html=True
        )
        st.caption("MongoDB Community service offline. Data persists locally.")

    # Dataset Ingestion Controls
    st.markdown("---")
    st.markdown(f"**{t('upload_header', lang)}**")
    uploaded_file = st.file_uploader(
        t("upload_button_label", lang),
        type=["csv", "xlsx", "xls"],
        help="Upload CSV or Excel inventory files. Aliases like product_id, price, exp_date are automatically mapped."
    )

    if uploaded_file is not None:
        if st.button("📥 Process Uploaded File", use_container_width=True, type="primary"):
            success = load_dataset_pipeline(uploaded_file, filename=uploaded_file.name)
            if success:
                st.success("File processed successfully!")
                st.rerun()

    if st.button(f"🔄 {t('btn_load_sample', lang)}", use_container_width=True):
        sample_path = DATA_DIR / "sample_inventory.csv"
        if sample_path.exists():
            load_dataset_pipeline(sample_path, filename="Built-in Sample Demonstration Dataset")
            st.rerun()

    # Model Quick Status
    st.markdown("---")
    st.markdown("**XGBoost Model Status:**")
    if st.session_state.predictor.is_loaded:
        st.success("Model: Active & Ready (XGBoost)")
    else:
        st.warning("Model: Not Loaded (Click below to train)")

    if st.button(f"⚙️ {t('btn_train_model', lang)}", use_container_width=True):
        if st.session_state.assessed_df is not None:
            with st.spinner("Training XGBoost Classifier..."):
                trainer = ModelTrainer()
                success, results = trainer.train_model(st.session_state.assessed_df)
                if success:
                    st.session_state.predictor._try_load()
                    st.session_state.db_manager.save_model_metadata(results)
                    st.success(f"Model trained! Accuracy: {results['metrics']['accuracy']*100:.1f}%")
                    st.rerun()
                else:
                    st.error(f"Training failed: {results.get('error')}")


# -----------------------------------------------------------------------------
# Main Dashboard Header
# -----------------------------------------------------------------------------
st.markdown(f"<div class='main-header'>{t('app_title', lang)}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>{t('app_subtitle', lang)}</div>", unsafe_allow_html=True)

df = st.session_state.assessed_df

# Check if data is available
if df is None or df.empty:
    st.info("👋 Welcome to P.I.R.E. Please load the sample dataset or upload an inventory file from the left sidebar.")
    st.stop()

# Mandatory Food Safety Alert Banner if any expired goods exist
expired_count = int((df["final_risk"] == "EXPIRED").sum())
if expired_count > 0:
    st.markdown(
        f"<div class='food-safety-banner'>⚠️ {t('safety_alert_expired', lang)} ({expired_count} items identified)</div>",
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# Main Navigation Tabs (Phase 9 Structure)
# -----------------------------------------------------------------------------
tab_overview, tab_inventory, tab_prediction, tab_discounts, tab_simulation, tab_model, tab_reports, tab_database = st.tabs([
    t("nav_overview", lang),
    t("nav_inventory", lang),
    t("nav_prediction", lang),
    t("nav_discounts", lang),
    t("nav_simulation", lang),
    t("nav_model_performance", lang),
    t("nav_reports", lang),
    t("nav_database", lang)
])


# =============================================================================
# TAB 1: OVERVIEW DASHBOARD
# =============================================================================
with tab_overview:
    disc_engine = DiscountEngine()
    fin_summary = disc_engine.calculate_financial_summary(df)

    # Top KPI Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_total_products', lang)}</div>
            <div class='kpi-value kpi-value-primary'>{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_expired_products', lang)}</div>
            <div class='kpi-value kpi-value-danger'>{expired_count}</div>
        </div>
        """, unsafe_allow_html=True)

    crit_count = int((df["final_risk"] == "CRITICAL").sum())
    high_count = int((df["final_risk"] == "HIGH").sum())

    with c3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_critical_risk', lang)}</div>
            <div class='kpi-value kpi-value-danger'>{crit_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        expiring_soon_count = int((df["days_remaining"] <= 3).sum())
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_expiring_soon', lang)}</div>
            <div class='kpi-value kpi-value-warning'>{expiring_soon_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_value_at_risk', lang)}</div>
            <div class='kpi-value kpi-value-warning'>₹{fin_summary['total_value_at_risk']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{t('kpi_potential_recovery', lang)}</div>
            <div class='kpi-value kpi-value-success'>₹{fin_summary['total_potential_recovery']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1: Risk Distribution & Risk by Category
    chart_col1, chart_col2 = st.columns(2)

    risk_colors = {
        "LOW": "#10B981",
        "MEDIUM": "#F59E0B",
        "HIGH": "#F97316",
        "CRITICAL": "#EF4444",
        "EXPIRED": "#991B1B"
    }

    with chart_col1:
        st.markdown("##### **Portfolio Risk Category Breakdown**")
        risk_counts = df["final_risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk_Level", "Count"]

        fig_pie = px.pie(
            risk_counts,
            names="Risk_Level",
            values="Count",
            color="Risk_Level",
            color_discrete_map=risk_colors,
            hole=0.45,
        )
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown("##### **Risk Levels Distributed by Food Category**")
        cat_risk = df.groupby(["category", "final_risk"]).size().reset_index(name="Count")
        fig_cat = px.bar(
            cat_risk,
            x="category",
            y="Count",
            color="final_risk",
            color_discrete_map=risk_colors,
            barmode="stack"
        )
        fig_cat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, xaxis_title="", yaxis_title="Number of SKUs")
        st.plotly_chart(fig_cat, use_container_width=True)

    # Charts Row 2: Expiry Timeline & Financial Exposure by Category
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("##### **Expiry Timeline (Days Remaining Distribution)**")
        fig_hist = px.histogram(
            df,
            x="days_remaining",
            color="final_risk",
            color_discrete_map=risk_colors,
            nbins=30,
            labels={"days_remaining": "Days Remaining until Expiry"}
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="#DC2626", annotation_text="Expiry Threshold")
        fig_hist.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, yaxis_title="SKU Count")
        st.plotly_chart(fig_hist, use_container_width=True)

    with chart_col4:
        st.markdown("##### **Inventory Financial Value at Risk by Category**")
        cat_val = df.groupby("category")["inventory_value_at_risk"].sum().reset_index()
        fig_val = px.bar(
            cat_val,
            x="category",
            y="inventory_value_at_risk",
            text_auto=".2s",
            color="category",
            labels={"inventory_value_at_risk": "Value at Risk (₹)"}
        )
        fig_val.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, xaxis_title="", showlegend=False)
        st.plotly_chart(fig_val, use_container_width=True)


# =============================================================================
# TAB 2: INVENTORY MANAGEMENT
# =============================================================================
with tab_inventory:
    st.markdown("### 📦 Inventory Catalog & Data Quality")

    # Data Validation summary expander
    val_sum = st.session_state.validation_summary
    if val_sum:
        with st.expander("🔍 Ingestion Validation Summary", expanded=False):
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("Total Rows Evaluated", val_sum["total_rows"])
            v2.metric("Valid Rows", val_sum["valid_rows"])
            v3.metric("Warning Rows", val_sum["warning_rows"])
            v4.metric("Invalid Rows", val_sum["invalid_rows"])

            if val_sum.get("row_issues"):
                st.markdown("**Row-level issues detected:**")
                st.dataframe(pd.DataFrame(val_sum["row_issues"]), use_container_width=True)

    # Filters
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

    with f_col1:
        search_query = st.text_input("🔎 Search by Product Name or Product ID", "")

    with f_col2:
        all_categories = sorted(list(df["category"].dropna().unique()))
        selected_categories = st.multiselect("Filter Category", all_categories, default=all_categories)

    with f_col3:
        all_risks = [lvl for lvl in RISK_LEVELS if lvl in df["final_risk"].values]
        selected_risks = st.multiselect("Filter Risk Tier", all_risks, default=all_risks)

    # Filter dataframe
    filtered_df = df.copy()

    if search_query:
        sq = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["prod_name"].astype(str).str.lower().str.contains(sq) |
            filtered_df["prod_id"].astype(str).str.lower().str.contains(sq)
        ]

    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

    if selected_risks:
        filtered_df = filtered_df[filtered_df["final_risk"].isin(selected_risks)]

    st.markdown(f"**Displaying {len(filtered_df)} of {len(df)} records:**")

    # Display columns
    cols_to_show = [
        "prod_id", "prod_name", "category", "quantity", "prod_price",
        "temp", "mf_date", "exp_date", "days_remaining", "final_risk",
        "recommended_discount_pct", "recommended_selling_price"
    ]
    present_show_cols = [c for c in cols_to_show if c in filtered_df.columns]

    st.dataframe(
        filtered_df[present_show_cols],
        use_container_width=True,
        column_config={
            "prod_price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
            "recommended_selling_price": st.column_config.NumberColumn("Clearance Price (₹)", format="₹%.2f"),
            "recommended_discount_pct": st.column_config.NumberColumn("Discount", format="%.1f%%"),
            "days_remaining": st.column_config.NumberColumn("Days Left", format="%.1f"),
            "temp": st.column_config.NumberColumn("Storage Temp", format="%.1f°C"),
        }
    )


# =============================================================================
# TAB 3: ML RISK PREDICTION
# =============================================================================
with tab_prediction:
    st.markdown("### 🤖 XGBoost Multi-Class Risk Inference")
    st.caption("Inspect machine-learning predictive scores, probabilities, and evidentiary risk reasons.")

    pred_cols = [
        "prod_id", "prod_name", "category", "days_remaining", "shelf_life_ratio",
        "temp", "temp_deviation", "ml_predicted_risk", "ml_confidence",
        "rule_urgency", "final_risk", "recommended_action"
    ]
    present_pred_cols = [c for c in pred_cols if c in df.columns]

    st.dataframe(
        df[present_pred_cols],
        use_container_width=True,
        column_config={
            "ml_confidence": st.column_config.ProgressColumn("ML Confidence", min_value=0.0, max_value=1.0, format="%.2f"),
            "shelf_life_ratio": st.column_config.NumberColumn("Life Ratio", format="%.2f"),
            "temp_deviation": st.column_config.NumberColumn("Temp Anomaly", format="%.1f°C"),
        }
    )

    # Drill-down into individual SKU explanation
    st.markdown("---")
    st.markdown("##### **Inspect Individual SKU Risk & Feature Evidence**")
    sku_options = df["prod_id"].astype(str) + " — " + df["prod_name"].astype(str)
    selected_sku_str = st.selectbox("Select SKU to view detailed diagnostic reasoning:", sku_options)

    if selected_sku_str:
        sel_id = selected_sku_str.split(" — ")[0]
        item_row = df[df["prod_id"] == sel_id].iloc[0]

        d1, d2 = st.columns([1, 1])

        with d1:
            st.markdown(f"**Product:** `{item_row['prod_name']}` ({item_row['prod_id']})")
            st.markdown(f"**Category:** `{item_row.get('category')}` | **Stock:** `{item_row.get('quantity')}` units")
            st.markdown(f"**Manufacturing Date:** `{item_row.get('mf_date')}`")
            st.markdown(f"**Expiry Date:** `{item_row.get('exp_date')}`")
            st.markdown(f"**Days Remaining:** `{item_row.get('days_remaining')} days`")
            st.markdown(f"**Storage Temperature:** `{item_row.get('temp')}°C` (Deviation: `{item_row.get('temp_deviation', 0):.1f}°C`)")

        with d2:
            st.markdown(f"**ML Predicted Risk:** `{item_row.get('ml_predicted_risk', 'N/A')}` (Confidence: `{item_row.get('ml_confidence', 'N/A')}`)")
            st.markdown(f"**Deterministic Rule Urgency:** `{item_row.get('rule_urgency', 'N/A')}`")
            st.markdown(f"**Final Consolidated Risk:** `{item_row.get('final_risk')}`")
            st.markdown(f"**Action Directive:** `{item_row.get('recommended_action')}`")

            reasons_list = item_row.get("flag_reasons", [])
            if reasons_list:
                st.markdown("**Evidentiary Explanations:**")
                for r in reasons_list:
                    st.markdown(f"- {r}")


# =============================================================================
# TAB 4: DISCOUNT RECOMMENDATIONS
# =============================================================================
with tab_discounts:
    st.markdown("### 🏷️ Transparent Clearance Discount Recommendations")
    st.caption("Configurable, category-capped clearance pricing ensuring safe inventory monetization.")

    disc_summary = DiscountEngine.calculate_financial_summary(df)

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    d_col1.metric("Discount-Eligible SKUs", disc_summary["discount_eligible_items_count"])
    d_col2.metric("Total Value at Risk", f"₹{disc_summary['total_value_at_risk']:,.2f}")
    d_col3.metric("Est. Recoverable Value", f"₹{disc_summary['total_potential_recovery']:,.2f}")
    d_col4.metric("Expired Loss (0% Sale)", f"₹{disc_summary['expired_writeoff_loss']:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Clearance Table
    disc_cols = [
        "prod_id", "prod_name", "category", "days_remaining", "quantity",
        "original_price", "recommended_discount_pct", "discount_amount",
        "recommended_selling_price", "inventory_value_at_risk",
        "estimated_recoverable_value", "discount_explanation"
    ]
    present_disc_cols = [c for c in disc_cols if c in df.columns]

    st.dataframe(
        df[present_disc_cols],
        use_container_width=True,
        column_config={
            "original_price": st.column_config.NumberColumn("Original Price (₹)", format="₹%.2f"),
            "discount_amount": st.column_config.NumberColumn("Markdown (₹)", format="₹%.2f"),
            "recommended_selling_price": st.column_config.NumberColumn("Clearance Price (₹)", format="₹%.2f"),
            "recommended_discount_pct": st.column_config.NumberColumn("Discount", format="%.1f%%"),
            "inventory_value_at_risk": st.column_config.NumberColumn("At Risk (₹)", format="₹%.2f"),
            "estimated_recoverable_value": st.column_config.NumberColumn("Est. Recovery (₹)", format="₹%.2f"),
        }
    )


# =============================================================================
# TAB 5: WHAT-IF STORAGE SIMULATION
# =============================================================================
with tab_simulation:
    st.markdown(f"### {t('sim_title', lang)}")
    st.caption(t("sim_desc", lang))

    s_c1, s_c2 = st.columns([1, 1])

    with s_c1:
        sim_delta = st.slider(
            t("sim_temp_slider", lang),
            min_value=-5.0,
            max_value=15.0,
            value=4.0,
            step=0.5,
            help="Positive values simulate cooling failure / temperature abuse. Negative values simulate cold-chain reinforcement."
        )

    with s_c2:
        categories_available = ["All"] + sorted(list(df["category"].dropna().unique()))
        sim_target_cat = st.selectbox(
            t("sim_category_select", lang),
            options=categories_available
        )

    # Run Simulation
    sim_df, sim_meta = StorageSimulator.simulate_temperature_change(
        baseline_df=df,
        temp_delta=sim_delta,
        target_category=sim_target_cat,
        predictor=st.session_state.predictor
    )

    # Metrics Delta Comparison Cards
    st.markdown("#### **Simulation Impact Assessment**")
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Temperature Shift", f"{sim_delta:+.1f}°C")
    m2.metric(
        "Risk Escalated SKUs",
        sim_meta["escalated_items_count"],
        delta=f"+{sim_meta['escalated_items_count']}" if sim_meta['escalated_items_count'] > 0 else "0",
        delta_color="inverse"
    )
    m3.metric(
        "Value at Risk Shift",
        f"₹{sim_meta['simulated_financials']['total_value_at_risk']:,.0f}",
        delta=f"₹{sim_meta['value_at_risk_delta']:+,.0f}",
        delta_color="inverse"
    )
    m4.metric(
        "Potential Recovery Shift",
        f"₹{sim_meta['simulated_financials']['total_potential_recovery']:,.0f}",
        delta=f"₹{sim_meta['potential_recovery_delta']:+,.0f}",
        delta_color="normal"
    )

    # Side-by-side comparison charts
    sim_chart_col1, sim_chart_col2 = st.columns(2)

    with sim_chart_col1:
        st.markdown("##### **Baseline vs. Simulated Risk Profile**")
        base_s = pd.Series(sim_meta["baseline_distribution"], name="Baseline")
        sim_s = pd.Series(sim_meta["simulated_distribution"], name="Simulated")
        comp_df = pd.concat([base_s, sim_s], axis=1).fillna(0).reset_index()
        comp_df.columns = ["Risk_Level", "Baseline", "Simulated"]

        fig_comp = go.Figure(data=[
            go.Bar(name="Baseline", x=comp_df["Risk_Level"], y=comp_df["Baseline"], marker_color="#3B82F6"),
            go.Bar(name="Simulated", x=comp_df["Risk_Level"], y=comp_df["Simulated"], marker_color="#EF4444")
        ])
        fig_comp.update_layout(barmode="group", height=320, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_comp, use_container_width=True)

    with sim_chart_col2:
        st.markdown("##### **Simulated Temperature Anomaly Distribution**")
        fig_sim_temp = px.histogram(
            sim_df,
            x="temp",
            color="final_risk",
            color_discrete_map=risk_colors,
            nbins=25,
            labels={"temp": "Simulated Storage Temp (°C)"}
        )
        fig_sim_temp.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sim_temp, use_container_width=True)


# =============================================================================
# TAB 6: MODEL PERFORMANCE
# =============================================================================
with tab_model:
    st.markdown("### 📈 XGBoost Classifier Performance Metrics")
    st.caption("Honest, un-fabricated test-split evaluation results and confusion matrix.")

    meta = st.session_state.predictor.metadata

    if meta and "metrics" in meta:
        m = meta["metrics"]
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Accuracy Score", f"{m.get('accuracy', 0)*100:.1f}%")
        p2.metric("Weighted Precision", f"{m.get('precision', 0)*100:.1f}%")
        p3.metric("Weighted Recall", f"{m.get('recall', 0)*100:.1f}%")
        p4.metric("Weighted F1-Score", f"{m.get('f1_score', 0)*100:.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        mod_col1, mod_col2 = st.columns([1, 1])

        with mod_col1:
            st.markdown("##### **Confusion Matrix**")
            cm = meta.get("confusion_matrix")
            classes = meta.get("classes_present", RISK_LEVELS)
            if cm:
                fig_cm = px.imshow(
                    cm,
                    text_auto=True,
                    labels=dict(x="Predicted Risk Level", y="Actual / Proxy Ground Truth", color="Count"),
                    x=classes[:len(cm[0])],
                    y=classes[:len(cm)],
                    color_continuous_scale="Blues"
                )
                fig_cm.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_cm, use_container_width=True)

        with mod_col2:
            st.markdown("##### **Training Metadata & Data Split**")
            st.markdown(f"- **Trained At:** `{meta.get('trained_at', 'N/A')}`")
            st.markdown(f"- **Target Source:** `{meta.get('target_source', 'N/A')}`")
            st.markdown(f"- **Training Samples:** `{meta.get('train_samples', 'N/A')}`")
            st.markdown(f"- **Test Validation Samples:** `{meta.get('test_samples', 'N/A')}`")
            st.markdown(f"- **Model Path:** `{meta.get('model_path', 'N/A')}`")

            warnings = meta.get("warnings", [])
            if warnings:
                st.markdown("**Methodological Notices:**")
                for w in warnings:
                    st.info(f"ℹ️ {w}")

    else:
        st.warning("No model metadata found. Please train the model using the sidebar button.")


# =============================================================================
# TAB 7: REPORTS & EXPORTS
# =============================================================================
with tab_reports:
    st.markdown("### 📄 Audit Report & Export Center")
    st.caption("Generate formal audit documentation in PDF and structured CSV formats.")

    r_col1, r_col2, r_col3 = st.columns(3)

    disc_engine = DiscountEngine()
    current_fin_summary = disc_engine.calculate_financial_summary(df)

    with r_col1:
        st.markdown("#### **Official PDF Audit Report**")
        st.write("Generates an executive PDF inventory audit report via ReportLab.")

        pdf_bytes = ReportGenerator.generate_pdf_report(
            df=df,
            financial_summary=current_fin_summary,
            model_metrics=st.session_state.predictor.metadata,
            dataset_origin=st.session_state.dataset_source_label
        )

        st.download_button(
            label="📥 Download Official PDF Report",
            data=pdf_bytes,
            file_name=f"PIRE_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    with r_col2:
        st.markdown("#### **Inventory & Predictions CSV**")
        st.write("Export full inventory with ML probabilities and risk categories.")

        csv_bytes = ReportGenerator.generate_csv_bytes(df)
        st.download_button(
            label="📥 Download Risk Assessment CSV",
            data=csv_bytes,
            file_name=f"PIRE_Risk_Predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with r_col3:
        st.markdown("#### **Discount Strategy CSV**")
        st.write("Export markdown pricing schedules and financial exposure.")

        disc_sub_df = df[[c for c in [
            "prod_id", "prod_name", "category", "quantity", "prod_price",
            "recommended_discount_pct", "discount_amount", "recommended_selling_price",
            "inventory_value_at_risk", "estimated_recoverable_value", "is_eligible_for_sale"
        ] if c in df.columns]]

        st.download_button(
            label="📥 Download Discount Schedule CSV",
            data=ReportGenerator.generate_csv_bytes(disc_sub_df),
            file_name=f"PIRE_Discount_Schedules_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# =============================================================================
# TAB 8: DATABASE STATUS & AUDIT LOGS
# =============================================================================
with tab_database:
    st.markdown("### 🗄️ Database Connectivity & Audit Logs")

    db_mgr = st.session_state.db_manager
    status = db_mgr.get_status()

    st.markdown(f"**Storage Engine Status:** `{status['storage_mode']}`")

    if status["is_connected"]:
        st.success(t("db_connected", lang))
    else:
        st.warning(t("db_fallback", lang))
        with st.expander("🛠️ How to Enable MongoDB Community Server on Windows", expanded=False):
            st.markdown("""
            1. **Download & Install:** Download [MongoDB Community Server](https://www.mongodb.com/try/download/community) for Windows.
            2. **Start Service:** Open Windows PowerShell as Administrator and run:
               ```powershell
               net start MongoDB
               ```
            3. **Verify:** Check that port 27017 is listening:
               ```powershell
               Test-NetConnection -ComputerName localhost -Port 27017
               ```
            4. Refresh this page to enable automatic MongoDB persistence!
            """)

    st.markdown("---")
    st.markdown("##### **Database Synchronization**")
    sync_col1, sync_col2 = st.columns([1, 2])

    with sync_col1:
        if st.button("💾 Persist Current Assessment to Storage", use_container_width=True):
            records = df.to_dict(orient="records")
            success, msg, count = db_mgr.save_predictions(records)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    # Audit Trail
    st.markdown("---")
    st.markdown("##### **System Audit Trail**")
    logs = db_mgr.get_audit_logs(limit=25)
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.write("No audit records recorded yet.")
