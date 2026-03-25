const cardsEl = document.getElementById("cards");
const template = document.getElementById("cardTemplate");
const categoryFilterEl = document.getElementById("categoryFilter");
const searchInputEl = document.getElementById("searchInput");
const statsTextEl = document.getElementById("statsText");
const scrapeCategoryEl = document.getElementById("scrapeCategory");
const scrapeUrlEl = document.getElementById("scrapeUrl");
const scrapeButtonEl = document.getElementById("scrapeButton");
const refreshButtonEl = document.getElementById("refreshButton");
const scrapeStatusEl = document.getElementById("scrapeStatus");

let allItems = [];

function flattenInventory(inventory) {
  return Object.entries(inventory).flatMap(([category, items]) => {
    return items.map((item) => ({ ...item, category }));
  });
}

function render() {
  const category = categoryFilterEl.value;
  const query = searchInputEl.value.trim().toLowerCase();

  const filtered = allItems.filter((item) => {
    const categoryOk = category === "all" || item.category === category;
    const queryOk = !query || item.name.toLowerCase().includes(query);
    return categoryOk && queryOk;
  });

  cardsEl.innerHTML = "";

  for (const item of filtered) {
    const fragment = template.content.cloneNode(true);
    const img = fragment.querySelector(".thumb");
    const name = fragment.querySelector(".item-name");
    const cat = fragment.querySelector(".item-category");
    const link = fragment.querySelector(".item-link");

    name.textContent = item.name;
    cat.textContent = item.category;
    link.href = item.url;

    if (item.image) {
      img.src = item.image;
      img.alt = item.name;
    } else {
      img.alt = "No image yet";
      img.src =
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='500'%3E%3Crect width='100%25' height='100%25' fill='%23dfe3dd'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%235a6460' font-family='sans-serif' font-size='28'%3ENo image saved%3C/text%3E%3C/svg%3E";
    }

    cardsEl.appendChild(fragment);
  }

  statsTextEl.textContent = `${filtered.length} items shown`;
}

async function loadInventory() {
  const response = await fetch("/api/inventory");
  const inventory = await response.json();
  allItems = flattenInventory(inventory);
  render();
}

async function scrapeAndSave() {
  const category = scrapeCategoryEl.value;
  const url = scrapeUrlEl.value.trim();

  if (!url) {
    scrapeStatusEl.textContent = "Please enter a category URL.";
    return;
  }

  scrapeStatusEl.textContent = "Scraping products and images...";
  scrapeButtonEl.disabled = true;

  try {
    const response = await fetch("/api/scrape-category", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, url, save: true }),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Scrape failed.");
    }

    scrapeStatusEl.textContent = `Saved ${result.scraped} products to ${category}. Total: ${result.total}.`;
    await loadInventory();
  } catch (error) {
    scrapeStatusEl.textContent = error.message;
  } finally {
    scrapeButtonEl.disabled = false;
  }
}

categoryFilterEl.addEventListener("change", render);
searchInputEl.addEventListener("input", render);
scrapeButtonEl.addEventListener("click", scrapeAndSave);
refreshButtonEl.addEventListener("click", loadInventory);

loadInventory();
