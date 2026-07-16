import sys
import os

# Adjust sys.path to import workspace files from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from processor import DataProcessor
from storage import StorageManager

def test_full_pipeline():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    load_dotenv(dotenv_path=os.path.join(root_dir, ".env"))
    
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_model = os.getenv("MISTRAL_MODEL")
    
    print("Initializing test pipeline...")
    print(f"Model: {mistral_model}")
    print(f"API Key Provided: {'Yes' if mistral_api_key else 'No'}")
    
    # 1. Mock Scraped Posts
    mock_scraped_posts = [
        {
            "author": "Bill Gates",
            "text": "We are proud to announce a new tender bid for a green energy yojana project contract in India.",
            "date_raw": "1d",
            "url": "https://www.linkedin.com/feed/update/urn:li:activity:123456/",
            "scraped_at": "2026-07-16 19:15:00"
        },
        {
            "author": "Satya Nadella",
            "text": "Attending a wonderful developer event in Seattle. The community is thriving!",
            "date_raw": "2h",
            "url": "https://www.linkedin.com/feed/update/urn:li:activity:789012/",
            "scraped_at": "2026-07-16 19:15:00"
        }
    ]
    
    print(f"Scraped {len(mock_scraped_posts)} mock posts.")
    
    # 2. Filter / Process
    keywords = ["tender", "yojana", "project", "contract", "bid"]
    processor = DataProcessor(keywords=keywords, api_key=mistral_api_key, model=mistral_model)
    
    print("\n--- Filtering Posts ---")
    matched_posts = processor.filter_posts(mock_scraped_posts)
    print(f"Matched {len(matched_posts)} posts.")
    
    # 3. Summarize
    print("\n--- Generating Summaries via Mistral ---")
    for post in matched_posts:
        print(f"Summarizing post by {post['author']}...")
        summary = processor.generate_summary(post['text'])
        post['summary'] = summary
        print(f"Summary: {summary}")
        
    # 4. Store
    excel_file = os.path.join(root_dir, "Test_Tracker.xlsx")
    summaries_dir = os.path.join(root_dir, "summaries")
    storage = StorageManager(excel_path=excel_file, summaries_dir=summaries_dir)
    
    # Clean up old test file if it exists to make test repeatable
    if os.path.exists(excel_file):
        os.remove(excel_file)
        
    print("\n--- Saving to Excel ---")
    added_count = storage.save_posts(matched_posts)
    print(f"Successfully added {added_count} new posts to {excel_file}.")
    print("\nPipeline Test SUCCESS!")

if __name__ == "__main__":
    test_full_pipeline()
