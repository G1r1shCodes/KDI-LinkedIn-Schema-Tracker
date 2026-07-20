import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
    print(f"Launching Chrome with profile: {user_data_dir}")
    print("Please log into LinkedIn in the browser window that opens.")
    print("This window will stay open for 3 minutes for you to complete the login.")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/login")
        
        print("Waiting for you to log in... (waiting 3 minutes max)")
        await asyncio.sleep(180)  # Wait for 3 minutes to allow user to log in
        
        print("Closing browser...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
