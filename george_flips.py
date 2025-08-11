import requests
import pandas as pd
from datetime import datetime

# ---- George prices (replace with updated ones from Hypixel Wiki) ----
GEORGE_PRICES = {
    "Golem": {"EPIC": 200000, "LEGENDARY": 400000},
    "Enderman": {"EPIC": 500000, "LEGENDARY": 1200000},
    "Griffin": {"EPIC": 1500000, "LEGENDARY": 2500000}
    # Add more pets and rarities here
}

# ---- Get current auctions from Coflnet ----
def get_auctions():
    url = "https://api.coflnet.com/auctions/pet"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

# ---- Find profitable flips ----
def find_flips():
    auctions = get_auctions()
    flips = []

    for auc in auctions:
        pet_name = auc.get("name")
        rarity = auc.get("tier")
        price = auc.get("startingBid")

        if pet_name in GEORGE_PRICES and rarity in GEORGE_PRICES[pet_name]:
            george_price = GEORGE_PRICES[pet_name][rarity]
            profit = george_price - price
            if profit > 0:
                flips.append({
                    "pet": pet_name,
                    "rarity": rarity,
                    "auction_price": price,
                    "george_price": george_price,
                    "profit": profit,
                    "time_found": datetime.utcnow().isoformat()
                })
    return flips

# ---- Save flips to CSV ----
def save_flips(flips):
    df = pd.DataFrame(flips)
    df.to_csv("flips.csv", index=False)
    print(f"Saved {len(flips)} profitable flips to flips.csv")

if __name__ == "__main__":
    flips = find_flips()
    save_flips(flips)
import csv
import os
from datetime import datetime

def save_flips_csv(flips):
    if not flips:
        return
    file_exists = os.path.isfile("flips.csv")
    with open("flips.csv", mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Pet", "Rarity", "Auction Price", "George Price", "Profit"])
        for fdata in flips:
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fdata["pet"],
                fdata["rarity"],
                fdata["auction_price"],
                fdata["george_price"],
                fdata["profit"]
            ])

# After you compute `flips`:
save_flips_csv(flips)
