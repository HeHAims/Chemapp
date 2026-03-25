import React from "react";

function HomeScreen({ groups, onOpenCategory }) {
  return (
    <div className="home-screen">
      <h2>Categories</h2>
      <div className="group-grid">
        {Object.entries(groups).map(([groupName, subcategories]) => (
          <div className="group-card" key={groupName}>
            <h3>{groupName}</h3>
            <ul>
              {subcategories.map((subcategory) => (
                <li key={subcategory}>
                  <button type="button" onClick={() => onOpenCategory(subcategory)}>
                    {subcategory.replace(/_/g, " ")}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomeScreen;
