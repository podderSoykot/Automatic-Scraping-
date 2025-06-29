import json



def load_municipalities(filepath):

    """Loads a list of municipalities from a JSON file."""

    try:

        with open(filepath, 'r', encoding='utf-8') as f:

            return json.load(f)

    except FileNotFoundError:

        print(f"Error: The file at {filepath} was not found.")

        return []

    except json.JSONDecodeError:

        print(f"Error: Could not decode JSON from the file at {filepath}.")

        return []



def save_json_output(data, filepath):

    """Saves data to a JSON file."""

    with open(filepath, 'w', encoding='utf-8') as f:

        json.dump(data, f, indent=2)

