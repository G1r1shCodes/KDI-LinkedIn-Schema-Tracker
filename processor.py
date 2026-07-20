import re
import logging
import os

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, keywords: list, exclude_keywords: list = None, api_key: str = None, model: str = None):
        self.keywords = [k.lower() for k in keywords]
        self.exclude_keywords = [k.lower() for k in (exclude_keywords or [])]
        self.api_key = api_key
        self.model = model or "mistral-small-latest"
        
    def filter_posts(self, posts: list) -> list:
        """Filters posts based on keywords."""
        matched_posts = []
        for post in posts:
            text_lower = post['text'].lower()
            
            # Check for exclude keywords first (e.g. "hiring", "job")
            skip_post = False
            for exclude_kw in self.exclude_keywords:
                if re.search(rf'\b{re.escape(exclude_kw)}\b', text_lower):
                    logger.info(f"Skipping post due to exclude keyword: '{exclude_kw}'")
                    skip_post = True
                    break
                    
            if skip_post:
                continue
            
            # Check for keyword matches
            matched_keyword = None
            for kw in self.keywords:
                # Use regex for whole word match to avoid partial matches like 'tend' in 'attend'
                if re.search(rf'\b{re.escape(kw)}\b', text_lower):
                    matched_keyword = kw
                    break
                    
            if matched_keyword:
                post['category'] = matched_keyword.title()
                matched_posts.append(post)
                
        logger.info(f"Filtered {len(posts)} posts down to {len(matched_posts)} matched posts.")
        return matched_posts

    def generate_summary(self, post_text: str) -> str:
        """
        Calls the Mistral API to generate a 3-5 line summary.
        If no api_key is configured, returns a mock summary.
        Includes exponential backoff retry on rate limit (HTTP 429).
        """
        if not self.api_key:
            # Mock summarizer
            words = post_text.split()
            preview = ' '.join(words[:20]) + "..." if len(words) > 20 else post_text
            return (
                f"1. This is a mock summary because no Mistral API key was configured.\n"
                f"2. The post mentions keywords related to our tracking goals.\n"
                f"3. Preview: {preview}"
            )
            
        import time
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes text. "
                        "You MUST summarize the text in exactly 3 to 5 clear bullet points or lines. "
                        "Do not include any conversational intro/outro text, headers, or greetings."
                    )
                },
                {
                    "role": "user",
                    "content": f"Summarize this text in exactly 3 to 5 clear bullet points/lines:\n\n{post_text}"
                }
            ]
        }
        
        endpoint = "https://api.mistral.ai/v1/chat/completions"
        max_retries = 5
        backoff = 2  # seconds, doubles each retry
        
        for attempt in range(1, max_retries + 1):
            try:
                # Small base delay to be polite to the API
                time.sleep(1.0)
                response = requests.post(endpoint, headers=headers, json=data, timeout=30)
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", backoff))
                    wait = max(retry_after, backoff)
                    logger.warning(f"Mistral rate limit hit (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
                    time.sleep(wait)
                    backoff = min(backoff * 2, 60)  # cap at 60s
                    continue
                    
                response.raise_for_status()
                raw_summary = response.json()['choices'][0]['message']['content'].strip()
                # Remove markdown bold characters because Excel doesn't render them
                return raw_summary.replace('**', '')
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"Mistral HTTP error on attempt {attempt}: {e}")
                if attempt == max_retries:
                    return "Error generating summary (HTTP error after retries)."
            except Exception as e:
                logger.error(f"Error calling Mistral API on attempt {attempt}: {e}")
                if attempt == max_retries:
                    return "Error generating summary. Check logs for details."
                    
        return "Error generating summary after max retries."

