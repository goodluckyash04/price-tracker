import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import newton
import datetime

from services.auth import guard
from assets.theme import inject_global_css, page_hero, section_header

st.set_page_config(page_title="XIRR Calculator", layout="wide", page_icon="📈")
inject_global_css()
guard()

page_hero("📈", "XIRR Return Calculator", "Upload a transaction CSV or enter data manually to calculate annualised returns.")

# ── XIRR logic ─────────────────────────────────────────────────────────────
def calculate_xirr(amounts, dates, current_value_input):
    dates = pd.to_datetime(dates, format="%d-%b-%y", errors="coerce")
    if dates.isnull().any():
        st.error("Date conversion failed. Use format like '01 Jan 2022'.")
        return None
    dates = list(dates)
    amounts = list(amounts)
    if current_value_input:
        try:
            current_val = float(current_value_input)
            dates.append(pd.Timestamp.now().normalize())
            amounts.append(current_val)
        except ValueError:
            st.error("Invalid current value. Enter a numeric amount.")
            return None
    d0 = min(dates)

    def xnpv(rate):
        return sum(cf / (1 + rate) ** ((d - d0).days / 365) for cf, d in zip(amounts, dates))

    try:
        return newton(xnpv, 0.1, tol=1e-8, maxiter=100)
    except Exception as e:
        st.error(f"XIRR calculation failed: {e}")
        return None

# ── Sample download ─────────────────────────────────────────────────────────
sample_data = pd.DataFrame({
    "Date": ["01 Jan 2022", "15 Mar 2022", "10 Oct 2023"],
    "Amount": ["10000", "15000", "5000"],
    "Transaction Type": ["PURCHASE", "PURCHASE", "REDEEM"],
})

left, right = st.columns([3, 2])

with left:
    section_header("Transaction Data")
    csv_bytes = sample_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Sample CSV Template",
        csv_bytes,
        file_name="xirr_template.csv",
        mime="text/csv",
    )

    input_method = st.radio("Input method", ["Upload CSV", "Manual Entry"], horizontal=True)
    df = None

    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                st.stop()
    else:
        with st.form("manual_input_form"):
            date = st.date_input("Date", value=datetime.date.today())
            amount = st.text_input("Amount", value="10000")
            txn_type = st.selectbox("Transaction Type", ["PURCHASE", "REDEEM"])
            if st.form_submit_button("➕ Add Transaction", type="primary"):
                st.session_state.setdefault("manual_entries", [])
                st.session_state.manual_entries.append({
                    "Date": date.strftime("%d-%b-%y"),
                    "Amount": amount,
                    "Transaction Type": txn_type,
                })
        if "manual_entries" in st.session_state and st.session_state.manual_entries:
            df = pd.DataFrame(st.session_state.manual_entries)
            section_header("Your Entries")
            st.dataframe(df, use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear All"):
                st.session_state.manual_entries = []
                st.rerun()

with right:
    section_header("Calculate XIRR")

    if df is not None:
        required_cols = {"Amount", "Transaction Type", "Date"}
        if not required_cols.issubset(df.columns):
            st.error("CSV must contain 'Amount', 'Transaction Type', and 'Date' columns.")
            st.stop()

        df["Amount"] = df["Amount"].astype(str).str.replace(",", "")
        try:
            df["Amount"] = df["Amount"].astype(float)
        except ValueError:
            st.error("Invalid amount format in CSV.")
            st.stop()

        sign_map = {"REDEEM": 1, "PURCHASE": -1}
        if not df["Transaction Type"].isin(sign_map).all():
            st.error("Transaction Type must be 'PURCHASE' or 'REDEEM'.")
            st.stop()

        df["Signed Amount"] = df["Amount"] * df["Transaction Type"].map(sign_map)
        current_status = st.text_input("Current investment value (₹)", placeholder="e.g. 30000")

        if current_status:
            xirr_result = calculate_xirr(df["Signed Amount"], df["Date"], current_status)
            if xirr_result is not None:
                pct = xirr_result * 100
                colour = "#22c55e" if pct >= 0 else "#ef4444"
                arrow = "▲" if pct >= 0 else "▼"
                st.markdown(f"""
                <div class="card-surface" style="text-align:center; margin-top:16px;">
                    <div style="font-size:13px; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Your XIRR</div>
                    <div style="font-size:3rem; font-weight:800; color:{colour};">{arrow} {pct:.2f}%</div>
                    <div style="font-size:13px; color:#64748b; margin-top:4px;">per year (annualised)</div>
                </div>
                """, unsafe_allow_html=True)

        section_header("Data Used")
        st.dataframe(df[["Date", "Amount", "Transaction Type"]], use_container_width=True, hide_index=True)
    else:
        st.info("⬅️ Add transaction data on the left to calculate XIRR.")
