# teststuff/temp_fetch.py
import requests
import time
from bs4 import BeautifulSoup
import os

BASE_URL = "https://opinion.lawmaking.go.kr"
url = f"{BASE_URL}/gcom/nsmLmSts/out" # Main listing page

try:
    response = requests.get(url)
    time.sleep(1) # Be polite
    response.raise_for_status()
    
    os.makedirs('teststuff', exist_ok=True)
    with open("teststuff/actual_main_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Actual main page HTML saved to teststuff/actual_main_page.html")
    
except requests.exceptions.RequestException as e:
    print(f"Error fetching main listing page: {e}")