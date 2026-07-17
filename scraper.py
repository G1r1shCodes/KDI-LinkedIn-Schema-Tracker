import asyncio
import random
import datetime
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logger
logger = logging.getLogger(__name__)

# Centralized selectors - easy to update if LinkedIn changes
SELECTORS = {
    "post_container": ".feed-shared-update-v2, .occludable-update, .update-components-update-v2, div[data-urn*='urn:li:activity']",
    "author_name": ".update-components-actor__name, .update-components-actor__title, .feed-shared-actor__name",
    "post_text": ".update-components-text, .feed-shared-update-v2__description, .break-words",
    "post_date_raw": ".update-components-actor__sub-description, .update-components-actor__sub-description span, .feed-shared-actor__sub-description",
    "post_link_button": "button[aria-label='Copy link to post'], .feed-shared-control-menu__item",
    "dropdown_trigger": ".feed-shared-control-menu__trigger"
}

class LinkedInScraper:
    def __init__(self, user_data_dir: str):
        self.user_data_dir = user_data_dir
        
    async def _random_delay(self, min_sec=2.0, max_sec=5.0):
        """Implement human-like random delays"""
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def scrape_profiles(self, profile_urls: list) -> list:
        all_posts = []
        
        try:
            async with async_playwright() as p:
                logger.info("Connecting to existing Chrome instance on port 9222...")
                try:
                    browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                    context = browser.contexts[0]
                    page = await context.new_page()
                except Exception as e:
                    logger.error("Failed to connect to Chrome. Did you start Chrome with --remote-debugging-port=9222?")
                    raise e
                
                for idx, url in enumerate(profile_urls):
                    # Pause every 20 profiles to avoid triggering LinkedIn's bot detection
                    if idx > 0 and idx % 20 == 0:
                        logger.info(f"Take a break! Pausing for 30 seconds to avoid LinkedIn rate limits...")
                        await asyncio.sleep(30)
                        
                    logger.info(f"[{idx+1}/{len(profile_urls)}] Visiting profile: {url}")
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        await self._random_delay(4, 7)
                        
                        # Scroll slightly to trigger lazy loading of posts
                        await page.evaluate("window.scrollBy(0, 1000);")
                        await self._random_delay(2, 4)
                        
                        # Extract posts
                        post_elements = await page.query_selector_all(SELECTORS["post_container"])
                        logger.info(f"Found {len(post_elements)} posts on {url}")
                        
                        for el in post_elements:
                            post_data = await self._extract_post_data(el, page)
                            if post_data:
                                # Very basic date filtering - only keep posts from last 48h
                                # LinkedIn dates are relative ("1d", "2h", "1w").
                                if self._is_recent(post_data.get('date_raw', '')):
                                    all_posts.append(post_data)
                                else:
                                    logger.info(f"Post skipped (not recent enough): {post_data.get('date_raw', '')}")
                            else:
                                logger.info("Post skipped (empty text or extraction failed)")
                            
                    except PlaywrightTimeoutError:
                        logger.error(f"Timeout while loading {url}")
                    except Exception as e:
                        logger.error(f"Error scraping {url}: {e}")
                        
                await context.close()
                
        except Exception as e:
            logger.critical(f"Failed to launch Chrome. Make sure all other Chrome instances are closed. Error: {e}")
            raise
            
        return all_posts
        
    async def _extract_post_data(self, element, page) -> dict:
        try:
            # Author
            author_el = await element.query_selector(SELECTORS["author_name"])
            author = await author_el.inner_text() if author_el else "Unknown"
            
            # Text
            text_el = await element.query_selector(SELECTORS["post_text"])
            text = await text_el.inner_text() if text_el else ""
            
            # Date (Raw string like "1d", "2h")
            date_el = await element.query_selector(SELECTORS["post_date_raw"])
            date_raw = await date_el.inner_text() if date_el else ""
            
            # URL - This is tricky without clicking. We will try to construct a dummy URL 
            # if we can't easily extract the real one without clicking the dropdown menu.
            # In a real robust scraper, we might use the URN from the data attribute.
            urn = await element.get_attribute("data-urn")
            url = f"https://www.linkedin.com/feed/update/{urn}/" if urn else None
            
            if not text.strip():
                return None
                
            return {
                "author": author.strip().split('\n')[0], # Clean up title
                "text": text.strip(),
                "date_raw": date_raw.strip(),
                "url": url,
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error extracting individual post: {e}")
            return None

    def _is_recent(self, date_str: str) -> bool:
        """
        LinkedIn dates are relative: '1h', '2d', '1w', '1mo'
        We want 24-48 hours, so 'h' (hours) and '1d', '2d' are acceptable.
        """
        if not date_str:
            return True # Include if we can't parse, just in case
            
        date_str = date_str.lower()
        if 'm' in date_str and 'mo' not in date_str: # minutes
            return True
        if 'h' in date_str: # hours
            return True
        if 'd' in date_str: # days
            try:
                days = int(''.join(filter(str.isdigit, date_str)))
                if days <= 7: # Changed from 2 to 7 to be more forgiving
                    return True
            except:
                pass
        return False
