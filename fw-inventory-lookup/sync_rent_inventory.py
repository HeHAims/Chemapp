import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://fwrental.com"

# Target categories used by fw-inventory-lookup/data/*.json
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

ROOT = Path(__file__).resolve().parents[1]  # C:/Users/hilar/CHEMAPP
FW_ROOT = Path(__file__).resolve().parent
FW_DATA = FW_ROOT / "data"
FW_SRC_MASTER = FW_ROOT / "src" / "data" / "master.json"
LEGACY_INVENTORY = ROOT / "data" / "inventory.json"


def norm_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        url = urljoin(BASE_URL, url)
    parsed = urlparse(url)
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if not clean.endswith("/"):
        clean += "/"
    return clean.lower()


def is_same_domain(url: str) -> bool:
    try:
        return urlparse(url).netloc.endswith("fwrental.com")
    except Exception:
        return False


def extract_name(anchor) -> str:
    text = anchor.get_text(" ", strip=True)
    if text:
        return " ".join(text.split())
    img = anchor.select_one("img")
    if img:
        alt = (img.get("alt") or "").strip()
        if alt:
            return " ".join(alt.split())
    return ""


def scrape_category(session: requests.Session, start_urls: list[str]) -> list[dict]:
    queue = [norm_url(u) for u in start_urls]
    seen_pages = set()
    products = {}
    max_pages = 40

    while queue and len(seen_pages) < max_pages:
        page = queue.pop(0)
        if not page or page in seen_pages:
            continue
        seen_pages.add(page)

        try:
            resp = session.get(page, timeout=10)
            if resp.status_code != 200:
                continue
        except Exception:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a[href*='/product/']"):
            href = norm_url(a.get("href", ""))
            if not href or "/product/" not in href:
                continue
            name = extract_name(a)
            if href not in products:
                products[href] = name

        # Follow pagination only within the same category branch.
        for a in soup.select("a.next.page-numbers"):
            href = norm_url(a.get("href", ""))
            if not href:
                continue
            if not is_same_domain(href):
                continue
            if "/product/" in href:
                continue
            # Keep crawling inside the same first source path.
            seed = norm_url(start_urls[0])
            if href.startswith(seed) and href not in seen_pages and href not in queue:
                queue.append(href)

    result = []
    for url, name in sorted(products.items(), key=lambda kv: (kv[1].lower() if kv[1] else "", kv[0])):
        result.append({
            "name": name or url.rstrip("/").split("/")[-1].replace("-", " ").title(),
            "url": url,
            "images": [],
        })
    return result


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    scraped_counts = {}
    for category, urls in CATEGORY_SOURCES.items():
        print(f"Scraping {category}...", flush=True)
        items = scrape_category(session, urls)
        scraped_counts[category] = len(items)
        if items:
            write_json(FW_DATA / f"{category}.json", items)

    master = {}
    for file in sorted(FW_DATA.glob("*.json")):
        if file.name == "master.json":
            continue
        master[file.stem] = json.loads(file.read_text(encoding="utf-8-sig"))

    write_json(FW_DATA / "master.json", master)
    write_json(FW_SRC_MASTER, master)

    # Keep legacy inventory seating aligned with live rent pages.
    if LEGACY_INVENTORY.exists():
        legacy = json.loads(LEGACY_INVENTORY.read_text(encoding="utf-8-sig"))
        for k in ["barstools", "chairs", "sofas"]:
            legacy[k] = [
                {
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "image": "",
                }
                for item in master.get(k, [])
            ]
        if "ottomans" not in legacy:
            legacy["ottomans"] = []
        write_json(LEGACY_INVENTORY, legacy)

    print("SCRAPED_COUNTS")
    for k in CATEGORY_SOURCES:
        print(k, scraped_counts.get(k, 0))
    print("TOTAL", sum(scraped_counts.values()))


if __name__ == "__main__":
    main()
