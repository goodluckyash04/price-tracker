import pandas as pd
import streamlit as st

from services.firebase_service import db


def render_amazon_product(data):
    # ── Product header ────────────────────────────────────────────────────
    st.markdown(
        f'<h2 style="color:#e2eaff; font-weight:800; margin-bottom:4px;">🛍️ {data["title"]}</h2>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        # Price block
        price_colour = "#22c55e"
        st.markdown(
            f'<div style="margin:12px 0 20px 0;">'
            f'<span style="font-size:2.4rem; font-weight:800; color:{price_colour};">₹{data["price"]}</span>'
            f'&nbsp;&nbsp;<span style="font-size:1rem; color:#64748b; text-decoration:line-through;">MRP ₹{data["mrp"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-size:12px; color:#64748b; margin-bottom:16px;">ASIN: <span style="color:#94a3b8; font-weight:600;">{data["asin"]}</span></div>',
            unsafe_allow_html=True,
        )

        with st.expander("🕰️ Price History"):
            show_price_graph_and_table(data["asin"])

        with st.expander("📋 Product Description"):
            st.write(data["full_title"])

            if data.get("site_features"):
                features_html = "".join(
                    f'<span style="background:#1e2d47;border:1px solid #1f2d44;border-radius:20px;'
                    f'padding:5px 12px;margin:4px;display:inline-block;font-size:13px;color:#94a3b8;">{f}</span>'
                    for f in sorted(data["site_features"])
                )
                st.markdown(features_html, unsafe_allow_html=True)

            if data.get("product_colors"):
                st.markdown("##### 🎨 Available Colors")
                colors_html = "".join(
                    f'<span style="background:#1e2d47;border:1px solid #1f2d44;border-radius:20px;'
                    f'padding:5px 12px;margin:4px;display:inline-block;font-size:13px;color:#94a3b8;">{c}</span>'
                    for c in sorted(data["product_colors"])
                )
                st.markdown(colors_html, unsafe_allow_html=True)

        with st.expander("🛠️ Technical Details"):
            if data["bullets"]:
                st.markdown("### 📝 About This Item")
                for bullet in data["bullets"]:
                    st.markdown(f"- {bullet}")
            if data["technical_details_html"]:
                for section, table_html in data["technical_details_html"]:
                    st.markdown(f"### 🛠️ {section}")
                    st.markdown(table_html, unsafe_allow_html=True)
            if data["box_contents"]:
                st.markdown("### 📦 What's in the Box")
                for item in data["box_contents"]:
                    st.markdown(f"- {item}")

        if data["offers"]:
            with st.expander("💰 Instant Cashback & Card Offers"):
                credit_offers, debit_offers, emi_offers, others = [], [], [], []
                for offer in data["offers"]:
                    ol = offer.lower()
                    if ("emi" in ol and "non-emi" not in ol) or "no cost emi" in ol:
                        emi_offers.append(offer)
                    elif "credit card" in ol:
                        credit_offers.append(offer)
                    elif "debit card" in ol:
                        debit_offers.append(offer)
                    else:
                        others.append(offer)

                def _offer_section(title, lst, emoji):
                    if lst:
                        st.markdown(f"#### {emoji} {title}")
                        for o in lst:
                            st.markdown(f"- **{o}**")

                _offer_section("Debit Card Offers", debit_offers, "🏦")
                _offer_section("Credit Card Offers", credit_offers, "💳")
                _offer_section("EMI Offers", emi_offers, "📆")
                _offer_section("Other Offers", others, "🎁")

        product_images = data["product_images"][1:] + data["features"]
        if product_images:
            with st.expander("📷 Product Feature Images"):
                for i in range(0, len(product_images), 4):
                    cols = st.columns(4)
                    for j, img_url in enumerate(product_images[i:i + 4]):
                        with cols[j]:
                            st.image(img_url, use_container_width=True)

    with col2:
        if data.get("product_images"):
            st.image(data["product_images"][0], use_container_width=True)


def show_price_graph_and_table(asin):
    try:
        product_ref = db.collection("products").document(asin)
        product_doc = product_ref.get()

        if not product_doc.exists:
            st.warning("No price history found for this product.")
            return

        product_data = product_doc.to_dict()
        price_history = product_data.get("price_history", [])
        if not price_history:
            st.info("No price history recorded yet.")
            return

        df = pd.DataFrame(price_history)
        df["mrp"].fillna(0, inplace=True)
        df["Price"] = df["price"].astype(int)
        df["MRP"] = df["mrp"].astype(float)
        df["Date"] = pd.to_datetime(df["date"], format="%d %B %Y %H:%M")
        df["OnlyDate"] = df["Date"].dt.date

        unique_df = df.drop_duplicates(subset=["OnlyDate", "MRP", "Price"])
        unique_df = unique_df[["Date", "MRP", "Price"]].sort_values("Date", ascending=False)

        st.markdown("### 📈 Price Over Time")
        st.line_chart(df.set_index("Date")["Price"])

        st.markdown("### 📊 Detailed Price History")
        st.dataframe(unique_df, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching price history: {e}")
