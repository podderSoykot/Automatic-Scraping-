import pandas as pd
import requests
import io
import urllib3

# Disable SSL warnings about unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2022_Gazetteer/2022_Gaz_place_national.txt"

print("Downloading Gazetteer data with SSL verification disabled...")
response = requests.get(url, verify=False)  # <-- Disable SSL verification here
response.raise_for_status()

data = response.content.decode('utf-8')

df = pd.read_csv(io.StringIO(data), delimiter='\t', dtype=str)

print(f"Total rows: {len(df)}")
print(df.head())

# Prepare City and State columns
df['City'] = df['NAME'].str.strip()
df['State'] = df['USPS']

# Drop duplicates if any
df = df.drop_duplicates(subset=['City', 'State'])

print(f"Unique municipalities (City, State): {len(df)}")

# Save to CSV
df[['City', 'State']].to_csv("us_municipalities_2022.csv", index=False)

print("Saved municipalities list to us_municipalities_2022.csv")
