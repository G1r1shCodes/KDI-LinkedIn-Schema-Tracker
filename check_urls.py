import urllib.request
import urllib.parse
import re
import time

companies = [
    "KEI Industries Limited",
    "Finolex Cables",
    "Havells India",
    "Gupta Power Infrastructure",
    "KEC International",
    "Universal Cables Ltd"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

for company in companies:
    try:
        query = urllib.parse.quote(f'"{company}" site:linkedin.com/company')
        url = f'https://www.google.com/search?q={query}'
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        matches = re.findall(r'https://in\.linkedin\.com/company/([^&"\'<]+)', html)
        if not matches:
             matches = re.findall(r'https://www\.linkedin\.com/company/([^&"\'<]+)', html)
        
        if matches:
            slug = matches[0].split('?')[0].strip('/')
            print(f"{company}: {slug}")
        else:
            print(f"{company}: NOT FOUND")
        time.sleep(2)
    except Exception as e:
        print(f"{company}: ERROR {e}")
