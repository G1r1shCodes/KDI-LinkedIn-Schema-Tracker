import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def test():
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
    test_url = "https://www.linkedin.com/company/polycabindia/recent-activity/all/"
    print(f"Testing URL: {test_url}")
    print(f"User Data Dir: {user_data_dir}")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(test_url, wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(5)
        
        current_url = page.url
        title = await page.title()
        print(f"Current Page URL: {current_url}")
        print(f"Page Title: {title}")
        
        # Check selectors
        selectors = [
            ".feed-shared-update-v2",
            ".occludable-update",
            ".update-components-update-v2",
            "div[data-urn*='urn:li:activity']",
            "main",
            "article",
            ".org-view-page"
        ]
        for sel in selectors:
            count = len(await page.query_selector_all(sel))
            print(f"Selector '{sel}': {count} elements")

        await context.close()

if __name__ == "__main__":
    asyncio.run(test())
