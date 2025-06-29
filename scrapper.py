import re
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Cities to scrape
CITIES = [
    {"state": "California", "city": "Los Angeles"},
    {"state": "Texas", "city": "Austin"},
    {"state": "Florida", "city": "Orlando"},
    # Add more cities...
]

SERVICES = [
    "Photography", "Videography", "Drone Photography", "Drone Video",
    "3D Virtual Tour", "Floor Plans", "Virtual Staging", "Twilight Photography",
    "Agent Intro/Outro", "Voiceover"
]

# Output path
OUTPUT_PATH = Path("data/yelp_full_html_prices.json")
OUTPUT_PATH.parent.mkdir(exist_ok=True)

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def fetch_yelp_html(city: str, state: str) -> str:
    driver = create_driver()
    url = f"https://www.yelp.com/search?find_desc=real+estate+photography&find_loc={city.replace(' ', '+')}%2C+{state}"
    print(f"Fetching Yelp page for {city}, {state}: {url}")
    driver.get(url)
    time.sleep(5)  # wait for page load
    html = driver.page_source
    driver.quit()
    # Save debug HTML
    debug_file = f"debug_yelp_full_{city}_{state}.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved debug HTML: {debug_file}")
    return html

def extract_prices_from_full_html(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=" ").lower()
    
    # Find all price-like patterns anywhere: $xx, $xxx, $xx.xx
    price_patterns = re.findall(r"\$\d+(?:\.\d{1,2})?", text)
    print(f"All prices found: {price_patterns}")

    # We'll try to associate prices with services by proximity of keywords + price in text

    # Lowercase text for searching
    lower_text = text

    found_prices = {}
    for service in SERVICES:
        service_lc = service.lower()
        # Find occurrences of service keywords
        pattern = re.compile(rf"{service_lc}.{{0,50}}\$\d+(?:\.\d{{1,2}})?")
        matches = pattern.findall(lower_text)
        if matches:
            # Extract price from first match
            price_match = re.search(r"\$\d+(?:\.\d{1,2})?", matches[0])
            if price_match:
                price_val = float(price_match.group().replace("$", ""))
                found_prices[service] = price_val
                print(f"Found price for {service}: {price_val}")
        else:
            # Try reversed order: price then keyword within 50 chars
            pattern_rev = re.compile(rf"\$\d+(?:\.\d{{1,2}})?.{{0,50}}{service_lc}")
            matches_rev = pattern_rev.findall(lower_text)
            if matches_rev:
                price_match = re.search(r"\$\d+(?:\.\d{1,2})?", matches_rev[0])
                if price_match:
                    price_val = float(price_match.group().replace("$", ""))
                    found_prices[service] = price_val
                    print(f"Found price for {service} (rev): {price_val}")

    return found_prices

def interpolate_price(service: str) -> float:
    defaults = {
        "Photography": 275.0,
        "Videography": 450.0,
        "Drone Photography": 180.0,
        "Drone Video": 290.0,
        "3D Virtual Tour": 210.0,
        "Floor Plans": 130.0,
        "Virtual Staging": 90.0,
        "Twilight Photography": 155.0,
        "Agent Intro/Outro": 220.0,
        "Voiceover": 100.0,
    }
    return defaults.get(service, 0.0)

def process_city(city_info: dict) -> dict:
    city, state = city_info["city"], city_info["state"]
    html = fetch_yelp_html(city, state)
    prices = extract_prices_from_full_html(html)

    services_output = {}
    for service in SERVICES:
        if service in prices:
            services_output[service] = {
                "price": prices[service],
                "interpolation_used": False
            }
        else:
            services_output[service] = {
                "price": interpolate_price(service),
                "interpolation_used": True
            }
    return {state: {city: {"services": services_output}}}

def main():
    final_result = {"United States": {}}
    for city_info in CITIES:
        city_data = process_city(city_info)
        state = list(city_data.keys())[0]
        city = list(city_data[state].keys())[0]
        if state not in final_result["United States"]:
            final_result["United States"][state] = {}
        final_result["United States"][state][city] = city_data[state][city]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(final_result, f, indent=2)
    print(f"Output saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
