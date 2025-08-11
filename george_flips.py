import requests
import pandas as pd
from datetime import datetime

# ---- George prices (replace with updated ones from Hypixel Wiki) ----
GEORGE_PRICES = {
    
  "blue_whale": {
    "legendary": 5000000,
    "epic": 500000
  },
  "lion": {
    "legendary": 5000000,
    "epic": 500000
  },
  "monkey": {
    "legendary": 5000000,
    "epic": 500000
  },
  "giraffe": {
    "legendary": 5000000,
    "epic": 500000
  },
  "tiger": {
    "legendary": 5000000,
    "epic": 500000
  },
  "elephant": {
    "legendary": 5000000,
    "epic": 500000
  },
  "bat": {
    "mythic": 10000,
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "blaze": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "chicken": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "endermite": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "horse": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "jerry": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "mooshroom_cow": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "pig": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "rabbit": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "sheep": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "silverfish": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "skeleton": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "wolf": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "zombie": {
    "legendary": 5000,
    "epic": 2000,
    "rare": 1000,
    "uncommon": 500,
    "common": 100
  },
  "baby_yeti": {
    "legendary": 1000000,
    "epic": 10000,
    "rare": 2000,
    "uncommon": 500,
    "common": 100
  },
  "ender_dragon": {
    "legendary": 100000000,
    "epic": 5000000
  },
  "magma_cube": {
    "legendary": 100000,
    "epic": 2000
  },
  "ghoul": {
    "epic": 2000
  },
  "hound": {
    "legendary": 100000,
    "epic": 2000
  },
  "slug": {
    "legendary": 5000000,
    "epic": 500000
  },
  "tarantula": {
    "mythic": 150000,
    "legendary": 100000,
    "epic": 2000
  },
  "phoenix": {
    "legendary": 5000000,
    "epic": 500000
  },
  "dolphin": {
    "legendary": 10000000,
    "epic": 2500000,
    "rare": 500000,
    "uncommon": 50000,
    "common": 10000
  },
  "apal": {
    "legendary": 5000000,
    "epic": 5000
  },
  "rock_turtle": {
    "legendary": 5000000,
    "epic": 500000
  },
  "parrot": {
    "legendary": 5000,
    "epic": 2000
  },
  "ammonite": {
    "legendary": 5000
  },
  "armadillo": {
    "legendary": 5000,
    "epic": 2000
  },
  "bal": {
    "legendary": 5000,
    "epic": 2000
  },
  "bee": {
    "legendary": 325000,
    "epic": 100000,
    "rare": 25000,
    "uncommon": 5000,
    "common": 2500
  },
  "bingo": {
    "legendary": 5000000,
    "mythic": 10000000
  },
  "black_cat": {
    "legendary": 5000000,
    "mythic": 10000000
  }
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
