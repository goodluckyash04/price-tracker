import streamlit as st
import pandas as pd

from scrapers.AmzonScraper import AmazonScraper
from services.firebase_service import db
from services.auth import guard
from assets.theme import inject_global_css, page_hero, section_header

st.set_page_config(page_title="My Products", layout="wide", page_icon="🗂️")
inject_global_css()
guard()

page_hero("🗂️", "My Products", "All tracked products with price history and refresh controls.")

# ── Load from Firebase ────────────────────────────────────────────────────
product_collection = db.collection("products")
docs = product_collection.stream()

doc_list = []
for doc in docs:
    data = doc.to_dict()
    data["id"] = doc.id
    doc_list.append(data)

df = pd.DataFrame(doc_list)

if df.empty:
    st.info("📭 No products tracked yet. Go to **Product Tracker** to add your first product.")
    st.stop()

df = df.rename(columns={
    "asin": "ASIN",
    "title": "Title",
    "latest_captured_at": "Latest Captured",
    "domain": "Domain",
})

# ── Search ────────────────────────────────────────────────────────────────
search_col, _ = st.columns([3, 5])
with search_col:
    search_asin = st.text_input("🔎 Search by ASIN or keyword", placeholder="e.g. B0XXXXXXX")

filtered_df = df.copy()
filtered_df["Latest Captured"] = pd.to_datetime(filtered_df["Latest Captured"], errors="coerce")
filtered_df = filtered_df.sort_values(by="Latest Captured", ascending=False)

if search_asin:
    mask = (
        filtered_df["ASIN"].str.contains(search_asin.strip(), case=False, na=False) |
        filtered_df["Title"].str.contains(search_asin.strip(), case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if filtered_df.empty:
    st.warning("⚠️ No products match your search.")
    st.stop()

# ── Build display table ───────────────────────────────────────────────────
display_df = pd.DataFrame({
    "ASIN": filtered_df["ASIN"],
    "Title": filtered_df["Title"],
    "Latest Captured": filtered_df["Latest Captured"].dt.strftime("%d %b %Y %H:%M"),
    "Domain": filtered_df["Domain"],
    "Lowest Price": None,
    "Highest Price": None,
    "Latest Price": None,
})

for idx, row in filtered_df.iterrows():
    price_history = row.get("price_history", [])
    if price_history:
        history_df = pd.DataFrame(price_history)
        history_df["date"] = pd.to_datetime(history_df["date"], errors="coerce")
        display_df.at[idx, "Lowest Price"]  = f"₹{history_df['price'].min()}"
        display_df.at[idx, "Highest Price"] = f"₹{history_df['price'].max()}"
        display_df.at[idx, "Latest Price"]  = f"₹{history_df.sort_values('date', ascending=False).iloc[0]['price']}"
    else:
        display_df.at[idx, "Lowest Price"]  = "—"
        display_df.at[idx, "Highest Price"] = "—"
        display_df.at[idx, "Latest Price"]  = "—"

section_header(f"{len(display_df)} products")
st.dataframe(display_df.reset_index(drop=True), use_container_width=True, hide_index=True)

# ── Refresh section ───────────────────────────────────────────────────────
section_header("Refresh a Product")

options = [f"{row['ASIN']}  —  {row['Title'][:60]}" for _, row in filtered_df.iterrows()]
asin_mapping = {f"{row['ASIN']}  —  {row['Title'][:60]}": row["ASIN"] for _, row in filtered_df.iterrows()}

refresh_col, btn_col = st.columns([5, 1])
with refresh_col:
    selected_option = st.selectbox("Select product", options, label_visibility="collapsed")
with btn_col:
    do_refresh = st.button("🔄 Refresh", type="primary", use_container_width=True)

if do_refresh:
    selected_asin = asin_mapping[selected_option]
    selected_row = filtered_df[filtered_df["ASIN"] == selected_asin].iloc[0]
    if selected_row["Domain"] == "Amazon":
        with st.spinner("Fetching latest data from Amazon…"):
            AmazonScraper(f"https://www.amazon.in/dp/{selected_row['ASIN']}").get_product_details()
        st.success(f"✅ Refreshed **{selected_row['ASIN']}** successfully!")
        st.rerun()
    else:
        st.warning("Refresh is only supported for Amazon products right now.")
