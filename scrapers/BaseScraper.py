import requests
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

    def fetch(self, url=None):
        try:
            url = url if url else self.url
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def get_product_details(self):
        raise NotImplementedError("This method should be implemented by subclasses")