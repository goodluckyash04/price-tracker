import json, os
import traceback
from datetime import datetime

from services.firebase_service import db


def save_price_history(asin, title, price, mrp, domain=""):
    print(domain)
    try:
        # Prepare entry
        entry = {
            "price": price.replace(",", ""),  # clean price
            "date": datetime.now().strftime("%d %B %Y %H:%M"),
            "mrp": mrp.replace(",", "")
        }

        product_ref = db.collection('products').document(asin)
        product_doc = product_ref.get()

        if product_doc.exists:
            # If product exists, append to price history
            product_data = product_doc.to_dict()
            price_history = product_data.get("price_history", [])

            last = price_history[-1] if price_history else None
            if not last or last["price"] != entry["price"] or last["date"] != entry["date"]:
                price_history.append(entry)

            product_ref.update({
                "price_history": price_history,
                "latest_captured_at": datetime.now().strftime("%d %B %Y %H:%M"),
            })
        else:
            product_ref.set({
                "title": title,
                "asin": asin,
                "price_history": [entry],
                "domain": domain.title(),
                "latest_captured_at": datetime.now().strftime("%d %B %Y %H:%M")
            })

    except Exception as e:
        traceback.print_exc()
        print(f"Error saving price history: {e}")
