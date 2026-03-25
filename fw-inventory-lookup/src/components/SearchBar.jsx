import React from "react";

function SearchBar({ query, onChange }) {
  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search inventory..."
        value={query}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

export default SearchBar;
