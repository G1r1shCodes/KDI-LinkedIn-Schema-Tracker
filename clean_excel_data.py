import pandas as pd
import re
import textwrap
import unicodedata
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
        def sanitize_text(x):
            if pd.notnull(x):
                x = str(x)
                # Normalize unicode to convert weird LinkedIn bold/italic characters to standard text
                x = unicodedata.normalize('NFKD', x)
                x = re.sub(r'[\u200b\u200e\u200f\ufeff]', '', x)
                x = re.sub(r'[ \t\r\f\v\xa0]+', ' ', x)
                x = re.sub(r'\n ', '\n', x)
                x = re.sub(r' \n', '\n', x)
                x = re.sub(r'\n{2,}', '\n\n', x).strip()
                # Force wrap long lines so Excel calculates row height properly
                x = '\n'.join([textwrap.fill(p, width=100) for p in x.split('\n')])
            return x
        df['Post Text'] = df['Post Text'].apply(sanitize_text)

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
