import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://fwrental.com"
CATEGORY_SOURCES = {
    "barstools": ["https://fwrental.com/seating/barstools/"],
    "chairs": ["https://fwrental.com/seating/chairs/"],
    "sofas": ["https://fwrental.com/seating/sofas/"],
    "cafe_console_dining": ["https://fwrental.com/tables-bars/cafe-console-dining/"],
    "coffee_tables": ["https://fwrental.com/product-category/tables-and-bars/coffee-tables/"],
    "side_tables": ["https://fwrental.com/tables-bars/side-tables/"],
    "highboys": ["https://fwrental.com/tables-bars/highboys/"],
    "carts": ["https://fwrental.com/decor-display/carts/"],
    "lighting": ["https://fwrental.com/decor-display/lighting/"],
    "shelving": ["https://fwrental.com/decor-display/shelving/"],
    "walls": ["https://fwrental.com/decor-display/walls/"],
    "charging": ["https://fwrental.com/tech/charging/"],
    "props_misc": ["https://fwrental.com/misc/", "https://fwrental.com/misc-2/"],
}

FW_DATA = Path(__file__).resolve().parent / "data"
LEGACY = Path(r"C:\Users\hilar\CHEMAPP\data\inventory.json")
OUT = Path(__file__).resolve().parent / "audit_rent_sync_report.json"


def norm(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        url = urljoin(BASE_URL, url)
    p = urlparse(url)
    out = f"{p.scheme}://{p.netloc}{p.path}"
    if not out.endswith("/"):
        out += "/"
    return out.lower()


def scrape_product_urls(start_url: str) -> set[str]:
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    seen = set()
    q = [norm(start_url)]
    urls = set()
    while q and len(seen) < 40:
        u = q.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            r = s.get(u, timeout=10)
            if r.status_code != 200:
                continue
        except Exception:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href*='/product/']"):
            pu = norm(a.get("href", ""))
            if pu:
                urls.add(pu)
        nxt = soup.select_one("a.next.page-numbers")
        if nxt and nxt.get("href"):
            nu = norm(nxt.get("href"))
            if nu.startswith(norm(start_url)) and nu not in seen:
                q.append(nu)
    return urls


def load_local(category: str) -> set[str]:
    data = json.loads((FW_DATA / f"{category}.json").read_text(encoding="utf-8-sig"))
    return {norm(x.get("url", "")) for x in data if x.get("url")}


report = {"localCounts": {}, "coverage": {}, "legacySeating": {}, "localTotal": 0}
for cat in CATEGORY_SOURCES:
    local = load_local(cat)
    report["localCounts"][cat] = len(local)
    report["localTotal"] += len(local)

for cat, sources in CATEGORY_SOURCES.items():
    website = set()
    for src in sources:
        website |= scrape_product_urls(src)
    local = load_local(cat)
    report["coverage"][cat] = {
        "site": len(website),
        "local": len(local),
        "match": len(website & local),
        "missing": len(website - local),
    }

legacy = json.loads(LEGACY.read_text(encoding="utf-8-sig"))
report["legacySeating"] = {
    "barstools": len(legacy.get("barstools", [])),
    "chairs": len(legacy.get("chairs", [])),
    "sofas": len(legacy.get("sofas", [])),
}

OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(str(OUT))
