import json
import traceback

import pandas as pd
import streamlit as st
from datetime import datetime

def render_amazon_product(data):
    st.markdown(f"## 🛍️ {data['title']}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"""<div style="font-size: 2rem; color: green;">
                ₹ {data['price']}&nbsp;
                <span style="font-size: 1rem; color: grey;">
                MRP: ₹ {data['mrp']}
               </span>
               </div>
                """,
            unsafe_allow_html=True
        )
        st.caption(f"🆔 **ASIN:** {data['asin']}")
        with st.expander("📋 Price History"):
            show_price_graph_and_table(data['asin'])
        with st.expander("📋 Full Product Title"):
            st.write(data["full_title"])
            if data.get("product_colors"):
                st.markdown("##### 🎨 Available Colors")

                colors_html = "".join([
                    f"""<span style="
                        background-color: #f5f5f5;
                        border: 1px solid #ccc;
                        border-radius: 12px;
                        padding: 6px 14px;
                        margin: 4px;
                        display: inline-block;
                        font-size: 14px;
                    ">{color}</span>""" for color in sorted(data["product_colors"])
                ])

                st.markdown(colors_html, unsafe_allow_html=True)
    with col2:
        st.image(data["image"], use_container_width=True)

    with st.expander("📋 See Product Detail"):

        # 📝 About This Item
        if data["bullets"]:
            st.markdown("### 📝 About This Item")
            for idx, bullet in enumerate(data["bullets"]):
                st.markdown(f"- {bullet}")

        # 🛠️ Technical Details
        if data["technical_details_html"]:
            for section, table_html in data["technical_details_html"]:
                st.markdown(f"### 🛠️ {section}")
                st.markdown(table_html, unsafe_allow_html=True)

        # 📦 What's in the Box
        if data["box_contents"]:
            st.markdown("### 📦 What's in the Box")
            for item in data["box_contents"]:
                st.markdown(f"- {item}")

    # 🖼️ Product Features (Images)
    if data["features"]:
        st.markdown("### 🖼️ Product Features")
        for i in range(0, len(data["features"]), 4):
            cols = st.columns(4)
            for j, img_url in enumerate(data["features"][i:i + 4]):
                with cols[j]:
                    st.image(img_url, use_container_width=True)

    # 💰 Offers
    if data["offers"]:
        st.markdown("### 💰 Instant Cashback Offers")
        with st.expander("🔥 These are the currently available offers"):

            # st.success("🔥 These are the currently available offers:")

            credit_offers = []
            debit_offers = []
            emi_offers = []
            others = []

            for offer in data["offers"]:
                offer_lower = offer.lower()
                if ("emi" in offer_lower and "non-emi" not in offer_lower) or "no cost emi" in offer_lower:
                    emi_offers.append(offer)
                elif "credit card" in offer_lower:
                    credit_offers.append(offer)
                elif "debit card" in offer_lower:
                    debit_offers.append(offer)
                else:
                    others.append(offer)

            def show_offer_section(title, offers_list, emoji):
                if offers_list:
                    st.markdown(f"#### {emoji} {title}")
                    for idx, offer in enumerate(offers_list):
                        st.markdown(f"- **{offer}**")

            show_offer_section("Debit Card Offers", debit_offers, "🏦")
            show_offer_section("Credit Card Offers", credit_offers, "💳")
            show_offer_section("EMI Offers", emi_offers, "📆")
            show_offer_section("Other Offers", others, "🎁")


def show_price_graph_and_table(asin):
    with open("db.json") as f:
        data = json.load(f)

    if asin in data:
        st.markdown(f"### 📈 Price History")

        # Convert price history to a DataFrame
        df = pd.DataFrame(data[asin]["price_history"])
        df["mrp"].fillna(0, inplace=True)
        df["price"] = df["price"].astype(int)  # Convert price to integer
        df["mrp"] = df["mrp"].astype(float)  # Convert price to integer
        df["date"] = pd.to_datetime(df["date"], format="%d %B %Y %H:%M")

        # Plot line chart with date-time on x-axis
        st.line_chart(df.set_index("date")["price"])

        # Show the time-stamped prices in a table
        st.markdown("### 📊 Detailed Price History (Date & Time)")
        st.write(df[["date", "mrp", "price"]].sort_values("date", ascending=False))

    else:
        st.warning("No history found for this product.")

