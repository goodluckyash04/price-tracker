import streamlit as st
from urllib.parse import urlparse
from scrapers.AmzonScraper import AmazonScraper
from views.amazon_view import render_amazon_product

SUPPORTED_DOMAINS = {
    "www.amazon.in": {
        "scrapers": AmazonScraper,
        "view": render_amazon_product
    },
    # Add other domains like "www.flipkart.com": { "scrapers": ..., "view": ... }
}

st.set_page_config(page_title="Track Product", layout="wide")
st.title("🛒 Product Tracker")

url = st.text_input("Product URL", placeholder="Enter product url to track")
submit = st.button("Start tracking", type="primary")

if url and submit:
    domain = urlparse(url).netloc
    if domain not in SUPPORTED_DOMAINS:
        st.error(f"Tracking for {domain} is not supported yet.")
        st.stop()

    domain_config = SUPPORTED_DOMAINS[domain]
    ScraperClass = domain_config["scrapers"]
    render_func = domain_config["view"]

    scraper = ScraperClass(url)

    with st.spinner("Fetching product info..."):
        try:
            data = scraper.get_product_details()
            render_func(data)
        except Exception as e:
            st.error(str(e))
