import requests
from bs4 import BeautifulSoup


class BaseScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Connection": "keep-alive",
                "Referer": "https://www.amazon.in/",
            }

    def fetch(self, url=None, headers=None):
        if headers:
            self.headers.update(headers)
        try:
            url = url if url else self.url
            response = requests.get(url, headers=self.headers)
            # self.check_response(response)  # Validate response
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def get_product_details(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def check_response(self, response):
        import json
        import streamlit as st

        st.text(response.url[:150])
        st.text(response.status_code)
        st.json(json.dumps(dict(response.request.headers)))