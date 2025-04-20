import json, os
import traceback
from datetime import datetime

from services.firebase_service import db


def save_price_history(asin, title, price, mrp):
    try:
        # Prepare entry
        entry = {
            "price": price.replace(",", ""),  # clean price
            "date": datetime.now().strftime("%d %B %Y %H:%M"),
            "mrp": mrp.replace(",", "")
        }

        # Reference to the product in Firestore (use ASIN as the document ID)
        product_ref = db.collection('products').document(asin)

        # Get current data from Firestore (if exists)
        product_doc = product_ref.get()

        if product_doc.exists:
            # If product exists, append to price history
            product_data = product_doc.to_dict()
            price_history = product_data.get("price_history", [])

            # Avoid duplicate entry if already added today
            last = price_history[-1] if price_history else None
            if not last or last["price"] != entry["price"] or last["date"] != entry["date"]:
                price_history.append(entry)

            # Update Firestore document with the new price history
            product_ref.update({
                "price_history": price_history
            })
        else:
            # If product does not exist, create new entry
            product_ref.set({
                "title": title,
                "asin": asin,
                "price_history": [entry]
            })

    except Exception as e:
        traceback.print_exc()
        print(f"Error saving price history: {e}")
