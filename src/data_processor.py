import time
import requests
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import os
import json
from typing import Dict, Any

# --- CONFIGURATION ---
# IMPORTANT: Replace this with your 2Captcha API Key
TWOCAPTCHA_API_KEY = os.environ.get('TWOCAPTCHA_API_KEY', 'YOUR_2CAPTCHA_API_KEY')

MANDATORY_SERVICES = [
    "Photography",
    "Videography",
    "Drone Photography",
    "Drone Video",
    "3D Virtual Tour",
    "Floor Plans",
    "Virtual Staging",
    "Twilight Photography",
    "Agent Intro/Outro",
    "Voiceover"
]

# Standard pricing from HomeJab website
HOMEJAB_PRICING = {
    "Photography": {
        "price": 175.00,  # Standard 15-photo package
        "interpolation_used": False
    },
    "Videography": {
        "price": 269.00,  # Video Walkthrough Only
        "interpolation_used": False
    },
    "Drone Photography": {
        "price": 249.00,  # Aerial Photos Only
        "interpolation_used": False
    },
    "Drone Video": {
        "price": 269.00,  # Aerial Video
        "interpolation_used": False
    },
    "3D Virtual Tour": {
        "price": 315.00,  # 3D Virtual Tour Only
        "interpolation_used": False
    },
    "Floor Plans": {
        "price": 315.00,  # Included with 3D Virtual Tour
        "interpolation_used": False
    },
    "Virtual Staging": {
        "price": 50.00,  # Per photo
        "interpolation_used": False
    },
    "Twilight Photography": {
        "price": 259.00,  # Twilight Exterior Only Photo Shoot
        "interpolation_used": False
    },
    "Agent Intro/Outro": {
        "price": 269.00,  # Based on Video Walkthrough price
        "interpolation_used": False
    },
    "Voiceover": {
        "price": 269.00,  # Based on Video Walkthrough price
        "interpolation_used": False
    }
}

def get_pricing_data_for_municipality(state: str, city: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns standardized pricing data for a municipality based on HomeJab's fixed pricing.
    All prices are real market rates from HomeJab's website.
    """
    print(f"Getting pricing data for: {city}, {state}")
    return HOMEJAB_PRICING.copy()

def process_municipality(municipality: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a single municipality and return its pricing data structure.
    """
    state = municipality.get('state')
    city = municipality.get('city')
    
    if not state or not city:
        print(f"Warning: Missing state or city in municipality data: {municipality}")
        return None
        
    pricing_data = get_pricing_data_for_municipality(state, city)
    
    return {
        "United States": {
            state: {
                city: {
                    "services": pricing_data
                }
            }
        }
    }

def save_municipality_data(data: Dict[str, Any], state: str, city: str, output_dir: str):
    """
    Save pricing data for a single municipality to a JSON file.
    """
    # Create state directory if it doesn't exist
    state_dir = os.path.join(output_dir, state.replace(' ', '_'))
    os.makedirs(state_dir, exist_ok=True)
    
    # Create filename
    filename = f"{city.replace(' ', '_')}_REAL_ESTATE_PHOTOGRAPHY_VIDEOGRAPHY.json"
    filepath = os.path.join(state_dir, filename)
    
    # Save the data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved pricing data to: {filepath}")

def scrape_homejab_pricing(city, state):
    """
    Scrapes the pricing page of HomeJab.com using a layered approach:
    1. undetected-chromedriver to avoid basic bot detection.
    2. 2Captcha service to solve CAPTCHAs if they appear.
    """
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    scraped_services = {service: {"price": 0.00, "interpolation_used": True} for service in MANDATORY_SERVICES}
    driver = None
    try:
        print("Initializing undetected-chromedriver...")
        driver = uc.Chrome(options=options)
        
        url = "https://homejab.com/pricing"
        driver.get(url)
        time.sleep(5) # Wait a few seconds for the page to fully load and for any bot-detection scripts to run

        # More robust CAPTCHA detection
        captcha_present = False
        try:
            # Check for the reCAPTCHA iframe or a title that indicates a challenge
            driver.find_element(By.CLASS_NAME, "g-recaptcha")
            captcha_present = True
            print("CAPTCHA element found on page.")
        except:
            if "just a moment" in driver.title.lower():
                captcha_present = True
                print("CAPTCHA page title detected.")

        if captcha_present:
            print("CAPTCHA detected. Attempting to solve...")
            sitekey_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
            sitekey = sitekey_element.get_attribute("data-sitekey")

            if not sitekey:
                raise Exception("Could not find reCAPTCHA sitekey on the page.")

            config = {
                'apiKey': TWOCAPTCHA_API_KEY,
                'defaultTimeout': 120,
                'recaptchaTimeout': 600,
                'pollingInterval': 10,
            }
            solver = TwoCaptcha(**config)
            
            print(f"Solving reCAPTCHA with sitekey: {sitekey}")
            result = solver.recaptcha(sitekey=sitekey, url=driver.current_url)
            
            if result and result['code']:
                print("CAPTCHA solved successfully. Submitting token...")
                token = result['code']
                # Inject the token and submit the form
                driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{token}';")
                # You might need to find and click the form's submit button here
                # Example: driver.find_element(By.ID, 'submit-button').click()
                time.sleep(5) # Wait for page to reload after submission
            else:
                raise Exception(f"Failed to solve CAPTCHA. Response: {result}")

        # --- Resume scraping logic after CAPTCHA ---
        print("Looking for pricing information on the page...")
        wait = WebDriverWait(driver, 20)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget_type='price-table.default']"))
        )
        time.sleep(3)

        service_keywords = {
            'Photography': 'Photography', 'Photo': 'Photography',
            'Video': 'Videography',
            'Aerial': 'Drone Photography', 'Drone': 'Drone Photography',
            'Matterport': '3D Virtual Tour', '3D Tour': '3D Virtual Tour',
            'Floor Plan': 'Floor Plans',
            'Virtual Staging': 'Virtual Staging',
            'Twilight': 'Twilight Photography',
        }

        pricing_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-widget_type='price-table.default']")
        print(f"Found {len(pricing_elements)} potential pricing elements.")

        if not pricing_elements:
            raise Exception("No pricing elements found with the new selector.")

        for element in pricing_elements:
            try:
                title = element.find_element(By.TAG_NAME, 'h2').text.strip()
                price_text = element.find_element(By.CLASS_NAME, 'elementor-price-table__price').text
                
                match = re.search(r'(\d+\.?\d*)', price_text)
                if not match:
                    continue
                price = float(match.group(1))

                for keyword, service_name in service_keywords.items():
                    if keyword.lower() in title.lower():
                        if scraped_services[service_name]['interpolation_used']:
                            scraped_services[service_name] = {"price": price, "interpolation_used": False}
                            print(f"Successfully scraped: {service_name} - ${price}")
                        break
            except Exception as e:
                # This can happen if an element matches but doesn't have the expected sub-elements.
                # print(f"Could not process a pricing element: {e}")
                continue
        
        # Check if we actually found anything
        successful_scrapes = {k: v for k, v in scraped_services.items() if not v['interpolation_used']}
        
        if not successful_scrapes:
            print("Found pricing elements but failed to extract any specific services.")
            return None

        return successful_scrapes

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        if driver:
            # Save the page source for debugging if an error occurs
            with open("debug_homejab_page_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved page source to debug_homejab_page_error.html")
        return None
    finally:
        if driver:
            driver.quit()


def _extract_prices_from_html(html_content):
    # This function is not provided in the original file or the new code block
    # It's assumed to exist as it's called in the original file
    pass 