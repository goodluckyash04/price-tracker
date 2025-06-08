import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import newton
import datetime

from services.auth import guard

guard()

st.set_page_config(page_title="XIRR Calculator", layout="wide", page_icon="📈")

st.title("📈 XIRR Calculator")

# Sample CSV content
sample_data = pd.DataFrame({
    "Date": ["01 Jan 2022", "15 Mar 2022", "10 Oct 2023"],
    "Amount": ["10000", "15000", "5000"],
    "Transaction Type": ["PURCHASE", "PURCHASE", "REDEEM"]
})

# Option to choose input method
st.subheader("📥 Enter Transaction Data")

csv_bytes = sample_data.to_csv(index=False).encode("utf-8")
st.download_button("Download Sample CSV", csv_bytes, file_name="sample_xirr_template.csv", mime="text/csv")

input_method = st.radio("Select input method", ["Upload CSV", "Manual Entry"])

# Initialize dataframe
df = None

if input_method == "Upload CSV":
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
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
        submit = st.form_submit_button("Add Transaction")

        if submit:
            st.session_state.setdefault("manual_entries", [])
            st.session_state.manual_entries.append({
                "Date": date.strftime("%d-%b-%y"),
                "Amount": amount,
                "Transaction Type": txn_type
            })

    if "manual_entries" in st.session_state:
        df = pd.DataFrame(st.session_state["manual_entries"])
        st.write("### 🧾 Your Entries")
        st.dataframe(df)

# Common XIRR logic
def calculate_xirr(amounts, dates, current_value_input):
    dates = pd.to_datetime(dates, format="%d-%b-%y", errors='coerce')
    if dates.isnull().any():
        st.error("Date conversion failed for some entries.")
        return None

    dates = list(dates)
    amounts = list(amounts)

    if current_value_input:
        try:
            current_val = float(current_value_input)
            dates.append(pd.Timestamp.now().normalize())
            amounts.append(current_val)
        except ValueError:
            st.error("Invalid current value. Please enter a numeric amount.")
            return None

    d0 = min(dates)

    def xnpv(rate):
        return sum(cf / (1 + rate) ** ((d - d0).days / 365) for cf, d in zip(amounts, dates))

    try:
        return newton(xnpv, 0.1, tol=1e-8, maxiter=100)
    except Exception as e:
        st.error(f"XIRR calculation failed: {e}")
        return None

# Process and calculate XIRR if df is ready
if df is not None:
    required_cols = {"Amount", "Transaction Type", "Date"}
    if not required_cols.issubset(df.columns):
        st.error("CSV must contain 'Amount', 'Transaction Type', and 'Date' columns.")
        st.stop()

    df["Amount"] = df["Amount"].astype(str).str.replace(",", "")
    try:
        df["Amount"] = df["Amount"].astype(float)
    except ValueError:
        st.error("Invalid amount format.")
        st.stop()

    sign_map = {"REDEEM": 1, "PURCHASE": -1}
    if not df["Transaction Type"].isin(sign_map).all():
        st.error("Transaction Type must be 'PURCHASE' or 'REDEEM'.")
        st.stop()

    df["Signed Amount"] = df["Amount"] * df["Transaction Type"].map(sign_map)

    st.subheader("💰 Enter Current Value")
    current_status = st.text_input("Current investment value")
    if current_status:
        xirr_result = calculate_xirr(df["Signed Amount"], df["Date"], current_status)
        if xirr_result is not None:
            st.success(f"📊 Your XIRR is: **{xirr_result * 100:.2f}% annually**")
        else:
            st.error("XIRR could not be calculated.")

    st.subheader("📋 Data Used")
    st.dataframe(df)

else:
    st.info("Upload a CSV or manually add transactions to calculate XIRR.")
