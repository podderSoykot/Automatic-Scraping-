# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_processor import process_municipality, save_municipality_data

def load_municipalities(file_path: str) -> List[Dict[str, str]]:
    """
    Load the municipalities data from the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading municipalities file: {e}")
        return []

def main():
    """
    Main function to process all US municipalities and generate pricing data.
    """
    municipalities_file = os.path.join('data', 'municipalities.json')
    output_dir = 'output2'

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    municipalities = load_municipalities(municipalities_file)
    if not municipalities:
        print("No municipalities to process. Exiting.")
        return

    total_municipalities = len(municipalities)
    print(f"Processing {total_municipalities} municipalities...")
    
    start_time = time.time()
    processed_count = 0
    
    # Process each municipality
    for municipality in municipalities:
        state = municipality.get('state')
        city = municipality.get('city')
        
        if not state or not city:
            continue
            
        print(f"Processing {city}, {state} ({processed_count + 1}/{total_municipalities})")
        
        # Get and save the pricing data
        pricing_data = process_municipality(municipality)
        if pricing_data:
            save_municipality_data(pricing_data, state, city, output_dir)
        
        processed_count += 1
        
        # Print progress every 100 municipalities
        if processed_count % 100 == 0:
            elapsed_time = time.time() - start_time
            avg_time_per_city = elapsed_time / processed_count
            remaining_cities = total_municipalities - processed_count
            estimated_time_remaining = remaining_cities * avg_time_per_city
            
            print(f"\nProgress: {processed_count}/{total_municipalities} municipalities processed")
            print(f"Estimated time remaining: {estimated_time_remaining/60:.1f} minutes\n")
    
    total_time = time.time() - start_time
    print(f"\nProcessing complete!")
    print(f"Processed {processed_count} municipalities in {total_time/60:.1f} minutes")
    print(f"Average time per municipality: {total_time/processed_count:.2f} seconds")

if __name__ == "__main__":
    main()

