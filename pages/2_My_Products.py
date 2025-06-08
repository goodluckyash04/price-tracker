import streamlit as st
import pandas as pd

from scrapers.AmzonScraper import AmazonScraper
from services.firebase_service import db

from services.auth import guard

guard()

# --- Page Setup ---
st.set_page_config(page_title="Product List", layout="wide", page_icon="📦")

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
    # --- Build a nice display DataFrame ---
    display_df = pd.DataFrame({
        "ASIN": filtered_df["ASIN"],
        "Title": filtered_df["Title"],
        "Latest Captured": filtered_df["Latest Captured"].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Domain": filtered_df["Domain"],
        "Lowest Price": None,
        "Highest Price": None,
        "Latest Price": None,
    })

    # Fill in price stats
    for idx, row in filtered_df.iterrows():
        price_history = row.get("price_history", [])
        if price_history:
            history_df = pd.DataFrame(price_history)
            history_df['date'] = pd.to_datetime(history_df['date'], errors="coerce")

            display_df.at[idx, "Lowest Price"] = f"₹{history_df['price'].min()}"
            display_df.at[idx, "Highest Price"] = f"₹{history_df['price'].max()}"
            display_df.at[idx, "Latest Price"] = f"₹{history_df.sort_values('date', ascending=False).iloc[0]['price']}"
        else:
            display_df.at[idx, "Lowest Price"] = "-"
            display_df.at[idx, "Highest Price"] = "-"
            display_df.at[idx, "Latest Price"] = "-"

    # --- Display the Table ---
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # --- Refresh Section ---
    st.markdown("### 🔄 Refresh Product Info")

    # Create display options with ASIN + Title
    options = [
        f"{row['ASIN']} - {row['Title']}" for idx, row in filtered_df.iterrows()
    ]

    # Create a mapping from "ASIN - Title" back to ASIN
    asin_mapping = {
        f"{row['ASIN']} - {row['Title']}": row['ASIN'] for idx, row in filtered_df.iterrows()
    }

    selected_option = st.selectbox("Select a product to refresh", options)

    # Get ASIN from selection
    selected_asin = asin_mapping[selected_option]

    if st.button("Refresh Selected Product"):
        selected_row = filtered_df[filtered_df["ASIN"] == selected_asin].iloc[0]
        if selected_row["Domain"] == "Amazon":
            with st.spinner("🔄 Fetching latest data..."):
                scraper = AmazonScraper(f"https://www.amazon.in/dp/{selected_row['ASIN']}").get_product_details()
                st.success(f"✅ Successfully fetched product: {selected_row['ASIN']}")
            st.rerun()
