import json
import os
from config import OUTPUT_FOLDER

def write_json(data, by_state=False):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    if by_state:
        for state, cities in data["United States"].items():
            # Create a folder for each state
            state_folder = os.path.join(OUTPUT_FOLDER, state.replace(" ", "_"))
            os.makedirs(state_folder, exist_ok=True)
            fname = os.path.join(state_folder, f"US_{state.replace(' ', '_')}_REAL_ESTATE_PHOTOGRAPHY_VIDEOGRAPHY.json")
            with open(fname, "w") as f:
                json.dump({"United States": {state: cities}}, f, indent=2)
    else:
        fname = os.path.join(OUTPUT_FOLDER, "US_REAL_ESTATE_PHOTOGRAPHY_VIDEOGRAPHY_COMPLETE.json")
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
