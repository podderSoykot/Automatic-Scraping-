import os
import json
import random
import time
from collections import defaultdict

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Load municipalities CSV
municipality_csv = "us_municipalities.csv"
df = pd.read_csv(municipality_csv)

services = [
    "Photography", "Videography", "Drone Photography", "Drone Video",
    "3D Virtual Tour", "Floor Plans", "Virtual Staging",
    "Twilight Photography", "Agent Intro/Outro", "Voiceover"
]

# Setup Selenium ChromeDriver (headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)

# Scrape prices per municipality and service
scraped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

max_cities = 5  # For demo, scrape first 5 cities only. Remove or increase for full scraping.

print(f"Starting scraping for up to {max_cities} municipalities...")

for idx, row in df.iterrows():
    state = row['state']
    city = row['city']

    print(f"Scraping: {city}, {state} ({idx+1}/{len(df)})")

    for service in services:
        try:
            search_url = f"https://www.thumbtack.com/search?search={service}&location={city}%2C+{state}"
            driver.get(search_url)
            time.sleep(random.uniform(3, 6))  # Random delay to reduce blocking

            cards = driver.find_elements(By.CSS_SELECTOR, "div[data-test=pro-card]")
            prices = []
            for card in cards:
                try:
                    text = card.text
                    if "$" in text:
                        for part in text.split():
                            if part.startswith("$"):
                                val = part.replace("$", "").replace(",", "")
                                if val.replace(".", "").isdigit():
                                    prices.append(float(val))
                except:
                    continue

            scraped_data[state][city][service] = prices

        except Exception as e:
            print(f"Error scraping {service} in {city}, {state}: {e}")
            scraped_data[state][city][service] = []

    if idx + 1 >= max_cities:
        break

driver.quit()

# Compute dynamic fallback prices per service (national average)
service_price_totals = defaultdict(list)
for state_data in scraped_data.values():
    for city_data in state_data.values():
        for service, prices in city_data.items():
            if prices:
                service_price_totals[service].extend(prices)

dynamic_fallback_prices = {}
for service in services:
    prices = service_price_totals.get(service, [])
    if prices:
        dynamic_fallback_prices[service] = round(sum(prices) / len(prices), 2)
    else:
        dynamic_fallback_prices[service] = 100.00  # fallback default if no data

print("Dynamic fallback prices computed:")
for service, price in dynamic_fallback_prices.items():
    print(f"  {service}: ${price}")

# Build final nested JSON output
result_json = {"United States": {}}

for state, cities in scraped_data.items():
    result_json["United States"][state] = {}
    for city, service_prices in cities.items():
        result_json["United States"][state][city] = {"services": {}}
        for service, prices in service_prices.items():
            if prices:
                avg_price = round(sum(prices) / len(prices), 2)
                interpolation_used = False
            else:
                avg_price = dynamic_fallback_prices[service]
                interpolation_used = True
            result_json["United States"][state][city]["services"][service] = {
                "price": avg_price,
                "interpolation_used": interpolation_used
            }

# Save to JSON
os.makedirs("output", exist_ok=True)
with open("output/real_estate_services.json", "w") as f:
    json.dump(result_json, f, indent=2)

print("Scraping complete! Data saved to output/real_estate_services.json")
