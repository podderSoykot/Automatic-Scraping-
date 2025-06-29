import json
import sys
import os
from pymongo import MongoClient

# Usage: python push_to_mongo.py <directory_with_json_files>

MONGO_URI = "mongodb+srv://soykotpodderwaywise:IN0JNIBAtwXucbdS@cluster0.w8271th.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "real_estate"
COLLECTION_NAME = "services"

def push_json_to_mongo(json_path, collection):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        result = collection.insert_one(data)
        print(f"Inserted {json_path} as document with _id: {result.inserted_id}")
    elif isinstance(data, list):
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents from {json_path}.")
    else:
        print(f"Unsupported JSON structure in {json_path}.")

def push_all_json_in_dir(root_dir):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(subdir, file)
                try:
                    push_json_to_mongo(json_path, collection)
                except Exception as e:
                    print(f"Failed to insert {json_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python push_to_mongo.py <directory_with_json_files>")
        sys.exit(1)
    root_dir = sys.argv[1]
    push_all_json_in_dir(root_dir) 