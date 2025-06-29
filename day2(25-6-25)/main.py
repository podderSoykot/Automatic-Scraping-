import logging
import pandas as pd
from us import states
from config import SERVICES
from google_scraper import fetch_from_google_business
from interpolator import interpolate_city
from json_writer import write_json
from utils import setup_logging
import json

def main():
    setup_logging()
    # Load list of cities and states from municipalities.json
    with open("municipalities.json", "r", encoding="utf-8") as f:
        city_records = json.load(f)
    df = pd.DataFrame(city_records) # Process only the first city for testing
    # Scrape data
    prices = []
    for idx, row in df.iterrows():
        city = row.city
        state = row.state
        sp = fetch_from_google_business(city, state)
        prices.append(sp)
    price_df = pd.concat([df, pd.DataFrame(prices)], axis=1)
    # Build final JSON structure
    master = {"United States": {}}
    for state, sub in price_df.groupby("state"):
        master["United States"][state] = {}
        for _, r in sub.iterrows():
            svc_data = {}
            missing = []
            for svc in SERVICES:
                p = r.get(svc)
                used = False
                if p is None:
                    missing.append(True)
                svc_data[svc] = {"price": p, "interpolation_used": False}
            if any(pd.isna(list(r.get(svc) for svc in SERVICES))):
                interp = interpolate_city(r, price_df)
                for svc in SERVICES:
                    if svc_data[svc]["price"] is None and interp.get(svc) is not None:
                        svc_data[svc]["price"] = interp[svc]
                        svc_data[svc]["interpolation_used"] = True
            master["United States"][state][r.city] = {"services": svc_data}
    write_json(master, by_state=True)
    logging.info("JSON generation complete.")

if __name__ == "__main__":
    main()
