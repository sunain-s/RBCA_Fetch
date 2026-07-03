# RBCA List Webscraping

#-----------------------------------------------------------------------------------------------------------
# Imports

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

#-----------------------------------------------------------------------------------------------------------
# Webscrape

BASE = "https://www.find-a-building-control-approver.service.gov.uk"
LIST_URL = (
    BASE +
    "/public-register-england/results"
    "?building-control-approver=&browse-all=true"
)
HEADERS = {
    "User-Agent":
        "RBCA Register Downloader/1.0"
        "(contact: your.email@example.com)"
}

session = requests.Session()
session.headers.update(HEADERS)

response = session.get(LIST_URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/public-register-england/" in href and "results" not in href:
        links.append(urljoin(BASE, href))

links = sorted(set(links))
print(f"Found {len(links)} companies")

print(soup.prettify()[:5000])
print("ACIVICO" in response.text)