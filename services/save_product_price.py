import json, os
import traceback
from datetime import datetime

def save_price_history(asin, title, price, mrp):
    try:
        file = "db.json"
        data = {}
        if os.path.exists(file):
            with open(file, "r") as f:
                data = json.load(f)

        # Prepare entry
        entry = {
            "price": price.replace(",", ""),  # clean price
            "date": datetime.now().strftime("%d %B %Y %H:%M"),
            "mrp": mrp.replace(",", "")
        }

        # Update or create new record
        if asin not in data:
            data[asin] = {
                "title": title,
                "asin": asin,
                "price_history": [entry]
            }
        else:
            # Avoid duplicate entry if already added today
            last = data[asin]["price_history"][-1]
            if last["price"] != entry["price"] or last["date"] != entry["date"]:
                data[asin]["price_history"].append(entry)
        print(data)
        # Save
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except:
        traceback.print_exc()
