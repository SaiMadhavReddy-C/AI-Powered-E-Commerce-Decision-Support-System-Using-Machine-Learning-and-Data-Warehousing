import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSubmit }) => {
  const [query, setQuery] = useState('');
  const [detectedRetailer, setDetectedRetailer] = useState('');

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.includes('amazon.in')) setDetectedRetailer('Amazon India');
    else if (value.includes('flipkart.com')) setDetectedRetailer('Flipkart');
    else if (value.includes('croma.com')) setDetectedRetailer('Croma');
    else if (value.includes('myntra.com')) setDetectedRetailer('Myntra');
    else setDetectedRetailer('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && onSubmit) {
      onSubmit(query.trim());
    }
  };

  return (
    <div className="search-bar-container">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            aria-label="Paste product link or search term"
            placeholder="Paste a product link or search for a product"
            value={query}
            onChange={handleInputChange}
          />
          <button type="submit" className="search-button" aria-label="Check with ShopQ">
            Check with ShopQ
          </button>
        </div>
      </form>
      {detectedRetailer && (
        <div className="detected-retailer fade-in" role="status" aria-live="polite">
          Looking up on {detectedRetailer}...
        </div>
      )}
    </div>
  );
};

export default SearchBar;
