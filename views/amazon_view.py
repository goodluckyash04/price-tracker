import pandas as pd
import streamlit as st

from services.firebase_service import db


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
        st.caption(f"**ASIN:** {data['asin']}")

        with st.expander("🕰️ Price History"):
            show_price_graph_and_table(data['asin'])

        with st.expander("📋 Product Description"):
            st.write(data["full_title"])

            s_feature = "".join([
                f"""<span style="
                    color: green;
                    border: 1px solid #ccc;
                    border-radius: 12px;
                    padding: 6px 14px;
                    margin: 4px;
                    display: inline-block;
                    font-size: 14px;
                ">{color}</span>""" for color in sorted(data["site_features"])
            ])
            st.markdown(s_feature, unsafe_allow_html=True)

            if data.get("product_colors"):
                st.markdown("##### 🎨 Available Colors")

                colors_html = "".join([
                    f"""<span style="
                        border: 1px solid #ccc;
                        border-radius: 12px;
                        padding: 6px 14px;
                        margin: 4px;
                        display: inline-block;
                        font-size: 14px;
                    ">{color}</span>""" for color in sorted(data["product_colors"])
                ])

                st.markdown(colors_html, unsafe_allow_html=True)

        with st.expander("🛠️ See Product Detail"):

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

        # 💰 Offers
        if data["offers"]:
            with st.expander("💰 Instant Cashback Offers"):
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

        # 🖼️ Product Features (Images)
        product_images = data["product_images"][1:] + data["features"]
        if product_images:
            with st.expander("### 📷 Product Features"):
                for i in range(0, len(product_images), 4):
                    cols = st.columns(4)
                    for j, img_url in enumerate(product_images[i:i + 4]):
                        with cols[j]:
                            st.image(img_url, use_container_width=True)

    with col2:
        st.image(data["product_images"][0], use_container_width=True)


def show_price_graph_and_table(asin):
    try:
        product_ref = db.collection('products').document(asin)
        product_doc = product_ref.get()

        if product_doc.exists:
            st.markdown(f"### 📈 Price History")

            # Extract price history
            product_data = product_doc.to_dict()
            price_history = product_data.get("price_history", [])

            # Convert price history to a DataFrame
            df = pd.DataFrame(price_history, index=None)
            df["mrp"].fillna(0, inplace=True)
            df["Price"] = df["price"].astype(int)  # Convert price to integer
            df["MRP"] = df["mrp"].astype(float)  # Convert price to integer
            df["Date"] = pd.to_datetime(df["date"], format="%d %B %Y %H:%M")
            df["OnlyDate"] = pd.to_datetime(df["Date"]).dt.date

            # Drop duplicate entries based on Date, MRP, and Price
            unique_df = df.drop_duplicates(subset=["OnlyDate", "MRP", "Price"])
            unique_df = unique_df[["Date", "MRP", "Price"]].sort_values("Date", ascending=False)

            # Plot line chart with date-time on x-axis
            st.line_chart(df.set_index("Date")["Price"])

            # Show the time-stamped prices in a table
            st.markdown("### 📊 Detailed Price History (Date & Time)")
            st.dataframe(unique_df, hide_index=True)
        else:
            st.warning("No history found for this product.")

    except Exception as e:
        st.error(f"Error fetching price history: {e}")

