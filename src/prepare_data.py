import csv
import json

def create_municipalities_json(csv_filepath, json_filepath):
    """
    Reads a CSV file of US cities and creates a JSON file
    with state and city information.
    """
    municipalities = []
    try:
        with open(csv_filepath, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                municipalities.append({
                    "state": row["state_name"],
                    "city": row["city"]
                })
    except FileNotFoundError:
        print(f"Error: The file at {csv_filepath} was not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    with open(json_filepath, 'w') as json_file:
        json.dump(municipalities, json_file, indent=4)
    
    print(f"Successfully created {json_filepath} with {len(municipalities)} entries.")

if __name__ == '__main__':
    csv_path = 'data/uscities.csv'
    json_path = 'data/municipalities.json'
    create_municipalities_json(csv_path, json_path) 