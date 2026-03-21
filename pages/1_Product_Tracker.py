import re

import streamlit as st
from urllib.parse import urlparse
from scrapers.AmzonScraper import AmazonScraper
from views.amazon_view import render_amazon_product
from services.auth import guard
from assets.theme import inject_global_css, page_hero

st.set_page_config(page_title="Product Tracker", layout="wide", page_icon="📦")
inject_global_css()
guard()

page_hero("📦", "Product Tracker", "Enter an Amazon product URL or ASIN to start tracking prices.")

SUPPORTED_DOMAINS = {
    "www.amazon.in": {
        "scrapers": AmazonScraper,
        "view": render_amazon_product,
    },
}

st.markdown("<br>", unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    url = st.text_input(
        "Product URL or ASIN",
        placeholder="e.g. https://www.amazon.in/dp/B0C... or B0XXXXXXXXX",
        label_visibility="collapsed",
    )
with col_btn:
    submit = st.button("🔍 Track", type="primary", use_container_width=True)

if url and submit:
    is_asin = bool(re.search(r"^[A-Z0-9]{10}$", url))
    if is_asin:
        domain = "www.amazon.in"
        url = f"https://www.amazon.in/dp/{url}"
    else:
        domain = urlparse(url).netloc
        if domain not in SUPPORTED_DOMAINS:
            st.error(f"❌ Tracking for **{domain}** is not supported yet. Only Amazon India is supported.")
            st.stop()

    domain_config = SUPPORTED_DOMAINS[domain]
    ScraperClass = domain_config["scrapers"]
    render_func = domain_config["view"]
    scraper = ScraperClass(url)

    with st.spinner("Fetching product info from Amazon…"):
        try:
            data = scraper.get_product_details()
            render_func(data)
        except Exception as e:
            st.error(f"❌ {str(e)}")
