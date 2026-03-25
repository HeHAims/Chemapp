from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "inventory.json"
REQUEST_TIMEOUT = 20

app = Flask(__name__, static_folder="static", static_url_path="/static")


def _default_inventory() -> dict[str, list[dict[str, str]]]:
    return {
        "barstools": [],
        "chairs": [],
        "sofas": [],
        "ottomans": [],
    }


def load_inventory() -> dict[str, list[dict[str, str]]]:
    if not DATA_FILE.exists():
        return _default_inventory()

    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return _default_inventory()

    for category in ["barstools", "chairs", "sofas", "ottomans"]:
        data.setdefault(category, [])
    return data


def save_inventory(data: dict[str, list[dict[str, str]]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_name(raw_text: str) -> str:
    text = re.sub(r"\s+", " ", raw_text).strip()
    parts = text.split(" ")

    # Listing links often repeat labels like "Aliza Aliza".
    if len(parts) >= 2 and len(parts) % 2 == 0:
        first_half = " ".join(parts[: len(parts) // 2]).lower()
        second_half = " ".join(parts[len(parts) // 2 :]).lower()
        if first_half == second_half:
            text = " ".join(parts[: len(parts) // 2])

    text = re.sub(r"\bNEW\b", "", text, flags=re.IGNORECASE).strip()
    return text


def extract_image_from_product(url: str) -> str:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"].strip()

    selectors = [
        "img.wp-post-image",
        ".woocommerce-product-gallery__image img",
        "img.attachment-woocommerce_single",
        "img",
    ]

    for selector in selectors:
        img = soup.select_one(selector)
        if not img:
            continue
        src = img.get("src") or img.get("data-src") or ""
        if src:
            return src.strip()

    return ""


def scrape_category_page(page_url: str) -> list[dict[str, str]]:
    response = requests.get(page_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    seen: set[str] = set()
    items: list[dict[str, str]] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if "/product/" not in href:
            continue

        product_url = urljoin(page_url, href)
        if product_url in seen:
            continue

        name = normalize_name(anchor.get_text(" ", strip=True))
        if not name:
            continue

        seen.add(product_url)
        image = extract_image_from_product(product_url)
        items.append({"name": name, "url": product_url, "image": image})

    return items


def merge_items(existing: list[dict[str, str]], incoming: list[dict[str, str]]) -> list[dict[str, str]]:
    by_url: dict[str, dict[str, str]] = {item.get("url", ""): item for item in existing if item.get("url")}

    for item in incoming:
        url = item.get("url", "").strip()
        if not url:
            continue

        current = by_url.get(url, {})
        by_url[url] = {
            "name": item.get("name") or current.get("name", ""),
            "url": url,
            "image": item.get("image") or current.get("image", ""),
        }

    merged = list(by_url.values())
    merged.sort(key=lambda x: x.get("name", "").lower())
    return merged


@app.get("/")
def index() -> Any:
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/inventory")
def get_inventory() -> Any:
    return jsonify(load_inventory())


@app.post("/api/import-json")
def import_json() -> Any:
    payload = request.get_json(silent=True) or {}
    category = (payload.get("category") or "").strip().lower()
    items = payload.get("items")

    if category not in {"barstools", "chairs", "sofas", "ottomans"}:
        return jsonify({"error": "Invalid category."}), 400

    if not isinstance(items, list):
        return jsonify({"error": "items must be an array."}), 400

    cleaned: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        url = str(item.get("url", "")).strip()
        image = str(item.get("image", "")).strip()
        if not name or not url:
            continue
        cleaned.append({"name": name, "url": url, "image": image})

    inventory = load_inventory()
    inventory[category] = merge_items(inventory.get(category, []), cleaned)
    save_inventory(inventory)

    return jsonify({"category": category, "imported": len(cleaned), "total": len(inventory[category])})


@app.post("/api/scrape-category")
def scrape_category() -> Any:
    payload = request.get_json(silent=True) or {}
    category = (payload.get("category") or "").strip().lower()
    page_url = (payload.get("url") or "").strip()
    save_results = bool(payload.get("save", True))

    if category not in {"barstools", "chairs", "sofas", "ottomans"}:
        return jsonify({"error": "Invalid category."}), 400
    if not page_url:
        return jsonify({"error": "url is required."}), 400

    try:
        scraped = scrape_category_page(page_url)
    except requests.RequestException as exc:
        return jsonify({"error": f"Failed to scrape page: {exc}"}), 400

    if not save_results:
        return jsonify({"category": category, "count": len(scraped), "items": scraped})

    inventory = load_inventory()
    inventory[category] = merge_items(inventory.get(category, []), scraped)
    save_inventory(inventory)

    return jsonify(
        {
            "category": category,
            "scraped": len(scraped),
            "total": len(inventory[category]),
            "saved": True,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
