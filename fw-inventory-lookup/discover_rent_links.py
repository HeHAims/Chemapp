from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

seed_urls = [
    "https://fwrental.com/",
    "https://fwrental.com/rentals/",
]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
found = set()
for seed in seed_urls:
    try:
        r = session.get(seed, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print("ERR", seed, e)
        continue
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        full = urljoin(seed, href)
        if full.startswith("https://fwrental.com/") and "/product/" not in full:
            found.add(full.split("#", 1)[0])

for url in sorted(found):
    if any(seg in url for seg in ["/seating/", "/tables/", "/bars/", "/decor/", "/props", "/lighting", "/wall", "/charging", "/shelv", "/carts", "/rental", "/rentals/"]):
        print(url)
