#!/usr/bin/env python3
"""
george_scanner.py
- Fetches Coflnet lowest BINs for pets (or active BIN listing).
- Uses a local JSON mapping file george_prices.json (pet -> rarity -> price).
- Appends any profitable flips (BIN < George) to flips.csv.
- Designed to run under GitHub Actions and commit flips.csv back to the repo.
"""

import requests, json, csv, os, sys, time
from datetime import datetime

# ---------- CONFIG ----------
COFLNET_LOWEST_BIN_URL = "https://sky.coflnet.com/api/lowestBin?type=pet"  # expected JSON mapping or list
GEORGE_PRICES_FILE = "george_prices.json"  # should be committed in repo with full mapping
OUTPUT_CSV = "flips.csv"
MAX_LOG = 500  # keep last N lines if you want to trim (optional)

# ---------- helpers ----------
def load_george_prices():
    if not os.path.exists(GEORGE_PRICES_FILE):
        print("Missing", GEORGE_PRICES_FILE)
        return {}
    with open(GEORGE_PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_coflnet_lowest_bins():
    r = requests.get(COFLNET_LOWEST_BIN_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    mapping = {}
    # Accept either dict {key: price} or list of entries
    if isinstance(data, dict):
        for k, v in data.items():
            try:
                mapping[k.lower()] = int(v)
            except:
                try:
                    mapping[k.lower()] = int(float(v))
                except:
                    continue
    elif isinstance(data, list):
        for item in data:
            # try common fields
            key = item.get("item") or item.get("name") or item.get("id")
            price = item.get("price") or item.get("lowestBin") or item.get("value")
            if key and price is not None:
                try:
                    mapping[str(key).lower()] = int(price)
                except:
                    pass
    return mapping

def normalize_key(k):
    if not k: return k
    kk = k.lower().strip()
    if kk.startswith("pet_"): kk = kk[4:]
    kk = kk.replace("-", "_")
    kk = kk.replace(" ", "_")
    return kk

def find_opps(coflnet_map, george_map):
    opps = []
    for raw_key, bin_price in coflnet_map.items():
        k = normalize_key(raw_key)
        # attempt many lookup patterns in george_map
        # george_map is expected like {"golem": {"epic": 500000, "legendary": 2500000}, ...}
        parts = k.split("_")
        # find rarity token at end maybe
        rarity = None
        if parts[-1] in ("common","uncommon","rare","epic","legendary","mythic","divine"):
            rarity = parts[-1]
            petname = "_".join(parts[:-1])
        else:
            # try to find any mapping by checking all rarities
            petname = k

        if petname in george_map:
            if rarity:
                gprice = george_map[petname].get(rarity)
                if gprice and bin_price < gprice:
                    opps.append((petname, rarity, bin_price, gprice, gprice - bin_price, raw_key))
            else:
                # check all rarities for potential matches
                for r, gprice in george_map[petname].items():
                    if gprice and bin_price < gprice:
                        opps.append((petname, r, bin_price, gprice, gprice - bin_price, raw_key))
    # sort by profit desc
    opps.sort(key=lambda x: x[4], reverse=True)
    return opps

def append_csv(rows):
    new_file = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp","pet_name","rarity","bin_price","george_price","profit","coflnet_key"])
        for r in rows:
            writer.writerow([
                datetime.utcnow().isoformat(),
                r[0], r[1], int(r[2]), int(r[3]), int(r[4]), r[5]
            ])

def main():
    try:
        george_map = load_george_prices()
        if not george_map:
            print("No george_prices.json found or empty. Create it with pet->rarity->price mapping.")
            return 1
        coflnet_map = fetch_coflnet_lowest_bins()
        opps = find_opps(coflnet_map, george_map)
        if opps:
            print(f"Found {len(opps)} opportunities. Appending to {OUTPUT_CSV}")
            append_csv(opps)
        else:
            print("No profitable flips right now.")
    except Exception as e:
        print("Error:", e)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
