const categoryTree = document.getElementById("categoryTree");
const listTitle = document.getElementById("listTitle");
const listMeta = document.getElementById("listMeta");
const itemList = document.getElementById("itemList");
const previewName = document.getElementById("previewName");
const previewImage = document.getElementById("previewImage");
const previewEmpty = document.getElementById("previewEmpty");
const previewLink = document.getElementById("previewLink");

let inventoryData = null;
let selectedCategoryIndex = null;
let selectedSubcategoryIndex = null;
let selectedItemIndex = null;

function setPreview(item) {
  if (!item) {
    previewName.textContent = "No item selected";
    previewImage.style.display = "none";
    previewEmpty.style.display = "block";
    previewLink.classList.add("hidden");
    previewLink.removeAttribute("href");
    return;
  }

  previewName.textContent = item.name;

  if (item.image) {
    previewImage.src = item.image;
    previewImage.alt = item.name;
    previewImage.style.display = "block";
    previewEmpty.style.display = "none";
  } else {
    previewImage.style.display = "none";
    previewEmpty.style.display = "block";
  }

  if (item.url) {
    previewLink.href = item.url;
    previewLink.classList.remove("hidden");
  } else {
    previewLink.classList.add("hidden");
  }
}

function renderItems() {
  itemList.innerHTML = "";
  setPreview(null);

  if (selectedCategoryIndex === null || selectedSubcategoryIndex === null) {
    listTitle.textContent = "Select a subcategory";
    listMeta.textContent = "No items loaded";
    return;
  }

  const subcategory =
    inventoryData.categories[selectedCategoryIndex].subcategories[selectedSubcategoryIndex];

  listTitle.textContent = `${subcategory.name}`;
  listMeta.textContent = `${subcategory.items.length} items`;

  subcategory.items.forEach((item, itemIndex) => {
    const li = document.createElement("li");
    li.textContent = item.name;

    li.addEventListener("click", () => {
      selectedItemIndex = itemIndex;
      const allRows = itemList.querySelectorAll("li");
      allRows.forEach((row) => row.classList.remove("active"));
      li.classList.add("active");
      setPreview(item);
    });

    itemList.appendChild(li);
  });
}

function renderCategoryTree() {
  categoryTree.innerHTML = "";

  inventoryData.categories.forEach((category, categoryIndex) => {
    const categoryWrap = document.createElement("div");
    categoryWrap.className = "category";

    const categoryButton = document.createElement("button");
    categoryButton.type = "button";
    categoryButton.textContent = category.name;

    const subcategoryList = document.createElement("div");
    subcategoryList.className = "subcategory-list";

    category.subcategories.forEach((subcat, subcatIndex) => {
      const subcategory = document.createElement("div");
      subcategory.className = "subcategory";
      subcategory.textContent = subcat.name;

      subcategory.addEventListener("click", () => {
        selectedCategoryIndex = categoryIndex;
        selectedSubcategoryIndex = subcatIndex;
        selectedItemIndex = null;

        document
          .querySelectorAll(".subcategory")
          .forEach((node) => node.classList.remove("active"));
        subcategory.classList.add("active");

        document
          .querySelectorAll(".category")
          .forEach((node, idx) => node.classList.toggle("expanded", idx === categoryIndex));

        renderItems();
      });

      subcategoryList.appendChild(subcategory);
    });

    categoryButton.addEventListener("click", () => {
      const isExpanded = categoryWrap.classList.contains("expanded");
      document
        .querySelectorAll(".category")
        .forEach((node) => node.classList.remove("expanded"));
      if (!isExpanded) {
        categoryWrap.classList.add("expanded");
      }
    });

    categoryWrap.appendChild(categoryButton);
    categoryWrap.appendChild(subcategoryList);
    categoryTree.appendChild(categoryWrap);
  });
}

async function loadInventory() {
  try {
    const response = await fetch("./data.json");
    if (!response.ok) {
      throw new Error(`Failed to load data.json (${response.status})`);
    }
    inventoryData = await response.json();
  } catch (error) {
    listTitle.textContent = "Failed to load inventory";
    listMeta.textContent = String(error.message || error);
    return;
  }

  renderCategoryTree();
}

loadInventory();
