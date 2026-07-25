import csv
import os
import pandas as pd

FILE_PATH = "hongkong_schools.csv"

def sanitize_csv():
    if not os.path.exists(FILE_PATH):
        print(f"❌ File '{FILE_PATH}' not found!")
        return

    print(f"🛠️ Sanitizing and fixing '{FILE_PATH}'...")
    try:
        # Load CSV with Pandas (automatically handles RFC-4180 escaping)
        df = pd.read_csv(FILE_PATH)
        
        # Clean column headers (strip accidental spaces or hidden BOM characters)
        df.columns = df.columns.astype(str).str.strip()
        
        # Flatten internal multi-line linebreaks inside text cells
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("\r\n", " | ")
                    .str.replace("\n", " | ")
                    .str.replace("\r", " | ")
                )
        
        # Overwrite hongkong_schools.csv with clean, perfectly aligned formatting
        df.to_csv(FILE_PATH, index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"✨ Successfully sanitized '{FILE_PATH}' in-place!")

    except Exception as e:
        print(f"❌ Error fixing CSV: {e}")

if __name__ == "__main__":
    sanitize_csv()
