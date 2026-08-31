import os
import requests
import pandas as pd

# Define paths relative to this file
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(DATA_DIR, "raw")
CSV_PATH = os.path.join(RAW_DIR, "online_retail.csv")
URL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"

def download_dataset():
    os.makedirs(RAW_DIR, exist_ok=True)
    print("Starting download of Online Retail dataset...")
    try:
        response = requests.get(URL, stream=True)
        response.raise_for_status()
        
        with open(CSV_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"Dataset saved to: {CSV_PATH}")
        
        # Verify
        df = pd.read_csv(CSV_PATH)
        print(f"Verified dataset: {df.shape[0]:,} rows loaded.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    download_dataset()
