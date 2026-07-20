import pandas as pd
import re
from formatter import format_excel
import sys

def clean_excel(path="Master_Tracker.xlsx"):
    print(f"Loading {path}...")
    try:
        df = pd.read_excel(path)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        sys.exit(1)

    print("Cleaning 'Post Text' (removing excessive newlines/whitespace)...")
    if 'Post Text' in df.columns:
        df['Post Text'] = df['Post Text'].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip() if pd.notnull(x) else x)

    print("Cleaning 'Summary' (removing markdown **)...")
    if 'Summary' in df.columns:
        df['Summary'] = df['Summary'].astype(str).apply(lambda x: x.replace('**', '') if pd.notnull(x) else x)

    print(f"Saving cleaned data to {path}...")
    df.to_excel(path, index=False, engine='openpyxl')

    print("Applying Excel styling...")
    format_excel(path)

    print("Done! Open the file to check.")

if __name__ == "__main__":
    clean_excel()
