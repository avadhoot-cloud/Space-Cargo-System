import React, { useState } from 'react';
import axios from 'axios';
import '../styles/ItemSearch.css';

const ItemSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    try {
      setLoading(true);
      setError(null);
      // Debug API URL
      const apiUrl = `${process.env.REACT_APP_API_URL}/search/items?query=${searchTerm}`;
      console.log('Search API URL:', apiUrl);
      
      const response = await axios.get(apiUrl);
      setSearchResults(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error searching items:', err);
      setError('Failed to search for items');
      setLoading(false);
    }
  };

  return (
    <div className="item-search-page">
      <h1>Item Search & Retrieval</h1>
      <p>Find items quickly and get optimized retrieval instructions.</p>
      
      <div className="search-container">
        <form onSubmit={handleSearch}>
          <div className="search-input-group">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for items..."
              className="search-input"
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {searchResults.length > 0 ? (
          <div className="search-results">
            <h2>Search Results</h2>
            <div className="results-list">
              {searchResults.map((item) => (
                <div key={item.id} className="result-item">
                  <h3>{item.name}</h3>
                  <div className="item-details">
                    <p><strong>Location:</strong> Module {item.container.module}, Position ({item.position_x}, {item.position_y}, {item.position_z})</p>
                    <p><strong>Priority:</strong> {item.priority}</p>
                    <p><strong>Weight:</strong> {item.weight} kg</p>
                    {item.expiry_date && <p><strong>Expires:</strong> {new Date(item.expiry_date).toLocaleDateString()}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          !loading && searchTerm && <p className="no-results">No items found matching your search.</p>
        )}
      </div>

      <div className="feature-cards">
        <div className="feature-card">
          <h3>Precise Location</h3>
          <p>Suggest the exact module and position of the requested item.</p>
        </div>
        <div className="feature-card">
          <h3>Smart Selection</h3>
          <p>Choose items based on ease of retrieval and closeness to expiry date.</p>
        </div>
        <div className="feature-card">
          <h3>Retrieval Logging</h3>
          <p>Log retrieval actions including who retrieved the item, when, and from where.</p>
        </div>
      </div>
    </div>
  );
};

export default ItemSearch; 