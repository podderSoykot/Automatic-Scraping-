import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
from config import SERVICES, SCRAPEOPS_API_KEY
from utils import clean_price
import urllib3
import json
import time
import random
import re

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_scrapeops_url(url, extra_params=None):
    """Generates a ScrapeOps proxy URL for the given target URL."""
    if not SCRAPEOPS_API_KEY or SCRAPEOPS_API_KEY == "YOUR_API_KEY_HERE":
        raise ValueError("ScrapeOps API key is not set in config.py. Get a free key from https://scrapeops.io/")
    
    payload = {
        'api_key': SCRAPEOPS_API_KEY,
        'url': url,
        'country': 'us',
        'premium_proxy': 'true',
        'render_js': 'false',  # Changed to false as we're scraping static content
        'residential_proxy': 'true',
    }
    
    # Add any extra parameters
    if extra_params:
        payload.update(extra_params)
        
    return 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)

def extract_price_from_text(text, service):
    """Extract price from text for a specific service."""
    # Convert text and service to lowercase for case-insensitive matching
    text = text.lower()
    service_lower = service.lower()
    
    # Different variations of service names
    service_variations = {
        'photography': ['photo', 'photography', 'pictures', 'photos'],
        'videography': ['video', 'videography', 'film', 'filming'],
        'drone photography': ['drone photo', 'aerial photo', 'drone photography'],
        'drone video': ['drone video', 'aerial video', 'drone film'],
        '3d virtual tour': ['3d tour', 'virtual tour', 'matterport', '3d walkthrough'],
        'floor plans': ['floor plan', 'floorplan', 'floor maps'],
        'virtual staging': ['virtual staging', 'digital staging'],
        'twilight photography': ['twilight', 'sunset photo', 'dusk photo'],
        'agent intro/outro': ['agent intro', 'agent video', 'realtor intro'],
        'voiceover': ['voice over', 'voiceover', 'narration']
    }
    
    # Get variations for the current service
    variations = service_variations.get(service_lower, [service_lower])
    
    # Look for prices near service mentions
    for variation in variations:
        # Look for price within 100 characters of service mention
        for match in re.finditer(variation, text):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            # Look for price patterns
            price_patterns = [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Standard price format
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars',  # Price with "dollars"
                r'starting at\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # "Starting at" prices
                r'from\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # "From" prices
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\$',  # Price with $ after number
            ]
            
            for pattern in price_patterns:
                prices = re.findall(pattern, context)
                if prices:
                    # Clean and validate prices
                    cleaned_prices = []
                    for price in prices:
                        price = clean_price(price)
                        if price and 50 <= price <= 5000:  # Reasonable price range
                            cleaned_prices.append(price)
                    
                    if cleaned_prices:
                        return cleaned_prices[0]  # Return the first valid price found
    
    return None

def fetch_from_google_business(city, state):
    """
    Scrapes Google search results via the ScrapeOps API to find business websites
    and then scrapes those websites for pricing information.
    """
    results = {svc: [] for svc in SERVICES}
    
    # Construct search queries for different variations
    queries = [
        f"real estate photography videography pricing packages {city} {state}",
        f"real estate photographer rates pricing packages {city} {state}",
        f"real estate video production cost pricing {city} {state}",
        f"3d virtual tour matterport pricing {city} {state}",
        f"drone real estate photography video pricing {city}"
    ]
    
    all_website_urls = set()
    
    for query in queries:
        encoded_query = quote_plus(query)
        
        # Use different Google domains and parameters
        google_urls = [
            f'https://www.google.com/search?q={encoded_query}&num=100&hl=en&gl=us',
            f'https://google.com/search?q={encoded_query}&num=100&hl=en&gl=us',
        ]
        
        for google_url in google_urls:
            logging.info(f"Requesting Google search for: {query}")
            
            try:
                # Add random delay between requests
                time.sleep(random.uniform(2, 4))
                
                response = requests.get(
                    get_scrapeops_url(google_url),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    },
                    verify=False,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logging.error(f"Failed to get search results: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selectors for Google search results
                for selector in [
                    'div.g div.yuRUbf > a[href]',  # Modern format
                    'div.g > div > div > div > a[href]',  # Alternative format
                    'div.g a[href]',  # Basic format
                    'a[href^="http"]'  # Any external link
                ]:
                    links = soup.select(selector)
                    if links:
                        logging.info(f"Found {len(links)} links with selector: {selector}")
                        for link in links:
                            url = link.get('href', '')
                            if (url.startswith('http') and 
                                not any(x in url.lower() for x in [
                                    'google.com', 'youtube.com', 'facebook.com', 
                                    'instagram.com', 'linkedin.com', 'twitter.com',
                                    'pinterest.com', 'yelp.com', 'amazon.com'
                                ])):
                                all_website_urls.add(url)
                                logging.info(f"Added URL: {url}")
                
            except Exception as e:
                logging.error(f"Error during search for {query}: {str(e)}")
                continue
    
    logging.info(f"Found {len(all_website_urls)} unique websites to scrape")
    
    # Scrape each individual website found
    for url in list(all_website_urls)[:5]:  # Limit to first 5 for efficiency
        try:
            logging.info(f"Scraping website: {url}")
            
            # Add random delay between requests
            time.sleep(random.uniform(1, 2))
            
            site_response = requests.get(
                get_scrapeops_url(url),
                verify=False,
                timeout=30
            )
            
            if site_response.status_code != 200:
                logging.warning(f"Failed to scrape {url}: {site_response.status_code}")
                continue
            
            site_soup = BeautifulSoup(site_response.text, "html.parser")
            
            # Get all text content
            text_elements = site_soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            page_text = ' '.join(element.get_text(' ', strip=True) for element in text_elements)
            
            # Look for pricing information for each service
            for svc in SERVICES:
                price = extract_price_from_text(page_text, svc)
                if price:
                    logging.info(f"Found price for {svc}: ${price}")
                    results[svc].append(price)
            
        except Exception as e:
            logging.warning(f"Failed to scrape website {url}: {str(e)}")
            continue

    # Aggregate the results
    aggregated = {}
    for svc, vals in results.items():
        if vals:
            # Remove outliers (prices outside 2 standard deviations)
            if len(vals) > 2:
                mean = sum(vals) / len(vals)
                std = (sum((x - mean) ** 2 for x in vals) / len(vals)) ** 0.5
                filtered_vals = [x for x in vals if mean - 2 * std <= x <= mean + 2 * std]
                vals = filtered_vals if filtered_vals else vals
            
            aggregated[svc] = float(sum(vals) / len(vals))
        else:
            aggregated[svc] = None
            
    return aggregated 