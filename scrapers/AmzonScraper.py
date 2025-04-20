import re
import json
import traceback

from urllib.parse import urljoin

from services.save_product_price import save_price_history
from scrapers.BaseScraper import BaseScraper

class AmazonScraper(BaseScraper):
    def get_product_details(self):
        soup = self.fetch()
        title_tag = soup.select_one("#productTitle")
        price_tag = soup.select_one("#corePriceDisplay_desktop_feature_div .a-price-whole")

        if not title_tag or not price_tag:
            raise Exception("Unable to find product title or price")

        full_title = title_tag.text.strip()
        title = re.sub(r"\(.*\)", "", full_title)
        price = price_tag.text.strip()
        mrp_price_tag = soup.find(lambda x: x.name == "span" and x.text and re.search(r"^M.R.P.:\s*₹\s*([\d\s,.]+)", x.text.strip()))
        mrp_price = re.search(r"^M.R.P.:\s*₹\s*([\d\s,.]+)", mrp_price_tag.text.strip()).group(1).strip()
        asin = soup.find("th", string=re.compile("ASIN")).find_next_sibling().text.strip()
        img = soup.select_one("#main-image-container li.image img")["src"]
        bullets = [li.text.strip() for li in soup.select("#feature-bullets li")]
        in_box = [li.text.strip() for li in soup.select("#whatsInTheBoxDeck li")]

        product_colors = {img["alt"].strip() for img in soup.select("#twister_feature_div img")}

        feature_imgs = [img["src"] for img in soup.select("div.aplus-v2 img[src*='.jpg']")]
        save_price_history(asin, title, price, mrp_price)
        offer_data = None
        try:
            side_sheet = soup.select_one("#itembox-InstantBankDiscount span[data-action]")
            offer_data_obj = json.loads(side_sheet["data-side-sheet"])
            offer_url = f"https://www.amazon.in/gp/product/ajax?asin={asin}&deviceType=web&offerType={offer_data_obj['contentId']}&buyingOptionIndex=0&additionalParams=merchantId:{offer_data_obj['encryptedMerchantId']}smid={offer_data_obj['smid']}&encryptedMerchantId={offer_data_obj['encryptedMerchantId']}&sr={offer_data_obj['sr']}&experienceId=vsxOffersSecondaryView&showFeatures=vsxoffers&featureParams=OfferType:{offer_data_obj['contentId']},DeviceType:web"
            offer_soup = self.fetch(offer_url)
            offer_data = [i.p.text.strip() for i in offer_soup.select(".vsx-offers-desktop-lv__item")]
        except Exception:
            traceback.print_exc()
            offer_data = []

        return {
            "soup": str(soup),
            "title": title,
            "price": price,
            "mrp": mrp_price,
            "full_title": full_title,
            "asin": asin,
            "image": img,
            "bullets": bullets,
            "box_contents": in_box,
            "features": feature_imgs,
            "offers": offer_data,
            "product_colors": product_colors,
            "technical_details_html": self._extract_details_table(soup)
        }

    def _extract_details_table(self, soup):
        table_html_blocks = []
        for table in soup.select("#prodDetails table"):
            h1 = table.find_previous("h1")
            if not h1 or h1.text.lower().strip() not in ["technical details", "additional information"]:
                continue

            for a in table.select("a"):
                if a.has_attr("class") and "a-popover-trigger" in a.attrs["class"]:
                    a.decompose()
                elif not a.has_attr("href") or a["href"].strip().startswith(("#", "javascript")):
                    a.name = "span"
                else:
                    a["href"] = urljoin(self.url, a["href"])
            table_html_blocks.append((h1.text.strip(), str(table)))
        return table_html_blocks
