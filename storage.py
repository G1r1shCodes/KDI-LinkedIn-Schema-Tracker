import pandas as pd
import os
import logging
from datetime import datetime
from formatter import format_excel

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, excel_path: str = "Master_Tracker.xlsx", summaries_dir: str = "summaries"):
        self.excel_path = excel_path
        self.summaries_dir = summaries_dir
        
        # Ensure summaries directory exists
        os.makedirs(self.summaries_dir, exist_ok=True)
        
        # Define Excel columns per PRD
        self.columns = [
            "Sr. No.",
            "Date Collected",
            "Post Date",
            "Author",
            "Post Text",
            "Post URL",
            "Category",
            "Summary",
            "Summary File",
            "Status",
            "Remarks"
        ]
        
    def check_lock(self):
        """Checks if the Excel file is open/locked by another application by trying to open it for appending."""
        if os.path.exists(self.excel_path):
            try:
                # On Windows, opening a file currently open in MS Excel in append mode throws PermissionError
                with open(self.excel_path, 'a'):
                    pass
            except PermissionError:
                logger.critical(f"Excel file '{self.excel_path}' is open in another program and is locked.")
                raise PermissionError(
                    f"The Excel file '{os.path.abspath(self.excel_path)}' is currently open/locked. "
                    "Please close MS Excel and run the script again."
                )
            except Exception as e:
                logger.error(f"Error checking Excel file lock: {e}")
                raise e
        
    def _load_existing_data(self) -> pd.DataFrame:
        if os.path.exists(self.excel_path):
            try:
                return pd.read_excel(self.excel_path)
            except Exception as e:
                logger.error(f"Failed to read existing Excel file: {e}")
                
        # Return empty DataFrame with correct columns if file doesn't exist
        return pd.DataFrame(columns=self.columns)
        
    def save_posts(self, posts: list) -> int:
        """
        Saves posts to Excel. Deduplicates based on Post URL.
        Returns the number of new posts added.
        """
        if not posts:
            return 0
            
        df_existing = self._load_existing_data()
        
        # Get set of existing URLs for deduplication
        existing_urls = set(df_existing['Post URL'].dropna())
        
        new_rows = []
        for post in posts:
            if post['url'] and post['url'] in existing_urls:
                # Skip duplicate
                continue
                
            # Generate detailed summary file
            summary_filename = f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(post['author']) % 10000}.txt"
            summary_path = os.path.join(self.summaries_dir, summary_filename)
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Author: {post['author']}\n")
                f.write(f"Date: {post['date_raw']}\n")
                f.write(f"URL: {post['url']}\n")
                f.write(f"Category: {post.get('category', '')}\n")
                f.write("-" * 40 + "\n")
                f.write(post['text'] + "\n")
                f.write("-" * 40 + "\n")
                f.write("Generated Summary:\n")
                f.write(post.get('summary', ''))
                
            # Determine next Sr. No.
            next_sr = len(df_existing) + len(new_rows) + 1
            
            new_rows.append({
                "Sr. No.": next_sr,
                "Date Collected": post['scraped_at'],
                "Post Date": post['date_raw'],
                "Author": post['author'],
                "Post Text": post['text'],
                "Post URL": post['url'],
                "Category": post.get('category', ''),
                "Summary": post.get('summary', ''),
                "Summary File": os.path.abspath(summary_path),
                "Status": "",
                "Remarks": ""
            })
            
        if new_rows:
            df_new = pd.DataFrame(new_rows)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            try:
                # Use openpyxl engine explicitly for modern Excel
                df_combined.to_excel(self.excel_path, index=False, engine='openpyxl')
                # Apply rich formatting (header colours, column widths, row shading, freeze pane)
                format_excel(self.excel_path)
                logger.info(f"Successfully added {len(new_rows)} new posts to Excel.")
                return len(new_rows)
            except PermissionError:
                logger.error("Permission denied to write Excel file. Is it open in another program?")
                raise
            except Exception as e:
                logger.error(f"Error saving to Excel: {e}")
                raise
                
        return 0
