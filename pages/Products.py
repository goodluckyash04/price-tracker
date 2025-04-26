import streamlit as st
import pandas as pd

from scrapers.AmzonScraper import AmazonScraper
from services.firebase_service import db

# --- Page Setup ---
st.set_page_config(page_title="Product List", layout="wide")

# --- Load Products from Firebase ---
product_collection = db.collection("products")
docs = product_collection.stream()

# --- Process Documents ---
doc_list = []
for doc in docs:
    data = doc.to_dict()
    data["id"] = doc.id
    doc_list.append(data)

# --- Create initial DataFrame ---
df = pd.DataFrame(doc_list)

# Rename columns
df = df.rename(columns={
    "asin": "ASIN",
    "title": "Title",
    "latest_captured_at": "Latest Captured",
    "domain": "Domain",
})

# --- Display Title ---
st.title("📦 Product List with Price Info")

# --- Search Bar ---
search_asin = st.text_input("🔎 Search by ASIN")

# --- Filter Data based on Search ---
filtered_df = df.copy()

# Make sure "Latest Captured" is datetime
filtered_df["Latest Captured"] = pd.to_datetime(filtered_df["Latest Captured"], errors="coerce")

# Sort by Latest Captured (newest first)
filtered_df = filtered_df.sort_values(by="Latest Captured", ascending=False)
if search_asin:
    filtered_df = filtered_df[filtered_df["ASIN"].str.contains(search_asin.strip(), case=False, na=False)]

# --- If no products after search ---
if filtered_df.empty:
    st.warning("⚠️ No products found for your search.")
else:
    # --- Table Header ---
    header_cols = st.columns([3, 6, 3, 2, 2, 2, 2, 2])
    header_cols[0].markdown("**ASIN**")
    header_cols[1].markdown("**Title**")
    header_cols[2].markdown("**Latest Captured**")
    header_cols[3].markdown("**Domain**")
    header_cols[4].markdown("**Lowest**")
    header_cols[5].markdown("**Highest**")
    header_cols[6].markdown("**Latest**")
    header_cols[7].markdown("**Action**")

    # --- Table Body ---
    for index, row in filtered_df.iterrows():
        cols = st.columns([3, 6, 3, 2, 2, 2, 2, 2])

        cols[0].write(f"[{row['ASIN']}](https://www.amazon.in/dp/{row['ASIN']})")
        cols[1].write(row["Title"])
        cols[2].write(str(row["Latest Captured"]))
        cols[3].write(row["Domain"])

        # --- Price Stats ---
        price_history = row.get("price_history", [])
        if price_history:
            history_df = pd.DataFrame(price_history)
            history_df['date'] = pd.to_datetime(history_df['date'], errors="coerce")

            lowest_price = history_df['price'].min()
            highest_price = history_df['price'].max()
            latest_price = history_df.sort_values('date', ascending=False).iloc[0]['price']
        else:
            lowest_price = highest_price = latest_price = "N/A"

        cols[4].write(f"₹{lowest_price}" if lowest_price != "N/A" else "-")
        cols[5].write(f"₹{highest_price}" if highest_price != "N/A" else "-")
        cols[6].write(f"₹{latest_price}" if latest_price != "N/A" else "-")

        # --- Action Button ---
        if cols[7].button("🔄", key=f"refresh_{index}"):
            if row["Domain"] == "Amazon":
                with st.spinner("🔄 Fetching latest data..."):
                    scraper = AmazonScraper(f"https://www.amazon.in/dp/{row['ASIN']}").get_product_details()
                    st.success(f"✅ Successfully fetched product: {row['ASIN']}")
                st.rerun()
