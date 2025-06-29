import pandas as pd
import requests
from zipfile import ZipFile
from io import BytesIO
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_municipalities_csv():
    url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2022_Gazetteer/2022_Gaz_place_national.zip"
    print("Downloading Gazetteer file...")
    response = requests.get(url, verify=False)  # <--- disable SSL verification
    with ZipFile(BytesIO(response.content)) as zipfile:
        zipfile.extractall("gazetteer_data")

    df = pd.read_csv("gazetteer_data/2022_Gaz_place_national.txt", delimiter="\t", dtype=str)
    df_filtered = df[["NAME", "USPS"]].copy()
    df_filtered.columns = ["municipality", "state"]
    df_filtered["city"] = df_filtered["municipality"].str.extract(r"^(.*?)(?:\s+(city|town|village|borough|CDP|municipality))?$")[0]
    df_filtered.to_csv("us_municipalities.csv", index=False)
    print(f"Saved {len(df_filtered)} municipalities to us_municipalities.csv")

if __name__ == "__main__":
    generate_municipalities_csv()
