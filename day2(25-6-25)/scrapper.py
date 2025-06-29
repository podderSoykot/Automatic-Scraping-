import requests
from bs4 import BeautifulSoup
from config import SERVICES, SCRAPE_TIMEOUT, RETRY_COUNT, USER_AGENT
from utils import clean_price
import logging
import time

HEADERS = {"User-Agent": USER_AGENT}

def fetch_business_pricing(city, state):
    """
    Attempt to fetch service pricing per municipality via directory or aggregated search.
    Returns dict: service -> avg price or None.
    """
    results = {svc: [] for svc in SERVICES}
    # Example: directory listing with known pattern:
    query_url = f"https://www.google.com/search?q=real+estate+photography+pricing+{city}+{state}"
    for attempt in range(RETRY_COUNT):
        try:
            r = requests.get(query_url, headers=HEADERS, timeout=SCRAPE_TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")
            # Example select: <div class="price">Photography: $300</div>
            for div in soup.select("div.price"):
                text = div.get_text()
                for svc in SERVICES:
                    if svc.lower() in text.lower():
                        price = clean_price(text)
                        if price:
                            results[svc].append(price)
            break
        except Exception as e:
            logging.warning(f"Fetch failure [{attempt+1}/{RETRY_COUNT}] for {city}, {state}: {e}")
            time.sleep(1)
    # derive median or mean
    aggregated = {}
    for svc, vals in results.items():
        aggregated[svc] = float(sum(vals) / len(vals)) if vals else None
    return aggregated
