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
        
        # Add a short delay to avoid hitting Mistral API rate limits (HTTP 429)
        time.sleep(1.5)
        
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
        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error calling Mistral API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Mistral API Response: {e.response.text}")
            return "Error generating summary. Check logs for details."
