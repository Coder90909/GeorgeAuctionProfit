import requests
import csv
import json
import os
from datetime import datetime

# Load George's buy prices
with open("george_prices.json", "r") as f:
    george_prices = json.load(f)

# Fetch pet auctions from Coflnet
resp = requests.get("https://sky.coflnet.com/api/auctions/active?type=pet")
resp.raise_for_status()
data = resp.json().get("auctions", [])

flips = []
for auc in data:
    pet = auc.get("item", {}).get("petType", "")
    rarity = auc.get("tier", "").lower()
    price = auc.get("startingBid", 0)
    key = f"{pet.lower()}"
    if key in george_prices and rarity in george_prices[key]:
        gprice = george_prices[key][rarity]
        if price < gprice:
            flips.append({
                "pet": pet,
                "rarity": rarity,
                "auction_price": price,
                "george_price": gprice,
                "profit": gprice - price
            })

# Save flips to CSV
csv_file = "flips.csv"
file_exists = os.path.isfile(csv_file)
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["Timestamp","Pet","Rarity","Auction Price","George Price","Profit"])
    for entry in flips:
        writer.writerow([
            datetime.utcnow().isoformat(),
            entry["pet"], entry["rarity"],
            entry["auction_price"], entry["george_price"], entry["profit"]
        ])

print(f"{len(flips)} profitable flips logged.")
