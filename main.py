import asyncio
import json
import logging
import os
import datetime
from dotenv import load_dotenv

from scraper import LinkedInScraper
from processor import DataProcessor
from storage import StorageManager

# Configure basic logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting LinkedIn Tender & Scheme Tracker...")
    
    # Load Environment variables
    load_dotenv()
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_model = os.getenv("MISTRAL_MODEL")
    
    if not user_data_dir:
        logger.error("CHROME_USER_DATA_DIR is missing from .env file.")
        return
        
    # Load Config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found.")
        return
        
    target_profiles = config.get("target_profiles", [])
    keywords = config.get("keywords", [])
    exclude_keywords = config.get("exclude_keywords", [])
    
    if not target_profiles or not keywords:
        logger.error("Profiles or keywords missing in config.json.")
        return
        
    # Load last scraped dates for round-robin sorting
    last_scraped_file = "last_scraped.json"
    last_scraped = {}
    if os.path.exists(last_scraped_file):
        try:
            with open(last_scraped_file, "r") as f:
                last_scraped = json.load(f)
        except Exception:
            pass

    # Sort target profiles: never scraped (empty string) or oldest scraped first
    target_profiles.sort(key=lambda url: last_scraped.get(url, ""))
        
    # Initialize components
    scraper = LinkedInScraper(user_data_dir=user_data_dir)
    processor = DataProcessor(
        keywords=keywords,
        exclude_keywords=exclude_keywords,
        api_key=mistral_api_key,
        model=mistral_model
    )
    storage = StorageManager()
    
    # Check Excel file lock before starting the long scraper process
    try:
        storage.check_lock()
    except PermissionError as e:
        logger.critical(str(e))
        return
    except Exception as e:
        logger.error(f"Excel check failed: {e}")
        return
        
    # Enforce once-per-day limit
    today_str = datetime.date.today().isoformat()
    last_run_file = "last_run.txt"
    if os.path.exists(last_run_file):
        with open(last_run_file, "r") as f:
            last_run = f.read().strip()
        if last_run == today_str:
            logger.warning("Scraper already ran today. As per safety guidelines, it can only run once per day to protect your account.")
            return
            
    # Record today as run
    with open(last_run_file, "w") as f:
        f.write(today_str)
        
    # 1. Scrape
    logger.info("Phase 1: Scraping...")
    try:
        scraped_posts = await scraper.scrape_profiles(target_profiles)
        logger.info(f"Scraping completed. Found {len(scraped_posts)} total posts.")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return
        
    if not scraped_posts:
        logger.critical(
            "CRITICAL: No posts were collected from any target profiles. "
            "This may indicate that the target profiles have no activity in the last 48h, "
            "or LinkedIn has updated its layout (invalidating the HTML selectors in scraper.py). "
            "Aborting execution to prevent empty/corrupted data entry."
        )
        return
        
    # 2. Process / Filter / Summarize
    logger.info("Phase 2: Processing and Filtering...")
    matched_posts = processor.filter_posts(scraped_posts)
    
    for post in matched_posts:
        # Generate summary
        summary = processor.generate_summary(post['text'])
        post['summary'] = summary
        
    # 3. Store
    logger.info("Phase 3: Saving to Excel...")
    try:
        added_count = storage.save_posts(matched_posts)
    except Exception as e:
        logger.error("Failed to save posts to Excel.")
        return
        
    # 4. Report
    logger.info("================ RUN REPORT ================")
    logger.info(f"Target Profiles Scanned: {len(target_profiles)}")
    logger.info(f"Total Posts Scraped:     {len(scraped_posts)}")
    logger.info(f"Posts Matched Keywords:  {len(matched_posts)}")
    logger.info(f"New Posts Added:         {added_count}")
    logger.info("============================================")
    
if __name__ == "__main__":
    # Workaround for Windows async event loop issues
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
