// frontend/src/pages/ItemSearch.jsx

import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import '../styles/ItemSearch.css';

const ItemSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retrieving, setRetrieving] = useState(false);
  const [items, setItems] = useState([]);

  useEffect(() => {
    // Load all items on component mount
    const fetchItems = async () => {
      try {
        console.log("DEBUG: Fetching all items");
        const response = await apiService.data.getItems();
        console.log("DEBUG: Items fetched:", response.data);
        setItems(response.data);
      } catch (err) {
        console.error('DEBUG: Error loading items:', err);
      }
    };
    
    fetchItems();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    try {
      console.log("DEBUG: Searching for:", searchTerm);
      setLoading(true);
      setError(null);
      
      // Try to find by ID first, then by name
      const itemId = searchTerm.includes('-') ? searchTerm : null;
      const itemName = !searchTerm.includes('-') ? searchTerm : null;
      console.log("DEBUG: Search params - itemId:", itemId, "itemName:", itemName);
      
      const response = await apiService.search.findItem(itemId, itemName);
      console.log("DEBUG: Search results:", response.data);
      
      setSearchResults(response.data);
      setLoading(false);
    } catch (err) {
      console.error('DEBUG: Error searching items:', err);
      setError('Failed to search for items');
      setLoading(false);
    }
  };

  const handleRetrieve = async (itemId) => {
    try {
      console.log("DEBUG: Retrieving item:", itemId);
      setRetrieving(true);
      await apiService.search.retrieveItem(itemId);
      alert(`Item ${itemId} has been retrieved successfully`);
      
      // Refresh search results
      console.log("DEBUG: Refreshing search results for item:", itemId);
      const response = await apiService.search.findItem(
        itemId,
        null
      );
      console.log("DEBUG: Updated search results:", response.data);
      
      setSearchResults(response.data);
      setRetrieving(false);
    } catch (err) {
      console.error('DEBUG: Error retrieving item:', err);
      setError('Failed to retrieve item');
      setRetrieving(false);
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
              placeholder="Search for items by ID or name..."
              className="search-input"
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {searchResults && searchResults.found ? (
          <div className="search-results">
            <h2>Search Results</h2>
            <div className="item-details-card">
              <h3>{searchResults.item.name} ({searchResults.item.itemId})</h3>
              
              <div className="item-location-info">
                {searchResults.item.containerId ? (
                  <>
                    <p><strong>Location:</strong> Container {searchResults.item.containerId}</p>
                    <p><strong>Position:</strong> ({searchResults.item.position.startCoordinates.width}, {searchResults.item.position.startCoordinates.depth}, {searchResults.item.position.startCoordinates.height})</p>
                    <div className="retrieval-button-container">
                      <button 
                        className="retrieve-button"
                        onClick={() => handleRetrieve(searchResults.item.itemId)}
                        disabled={retrieving}
                      >
                        {retrieving ? 'Retrieving...' : 'Retrieve Item'}
                      </button>
                    </div>
                  </>
                ) : (
                  <p><strong>Status:</strong> Item not currently placed in any container</p>
                )}
              </div>
              
              {searchResults.retrievalSteps && searchResults.retrievalSteps.length > 0 && (
                <div className="retrieval-steps">
                  <h4>Retrieval Steps:</h4>
                  <ol>
                    {searchResults.retrievalSteps.map((step, index) => (
                      <li key={index}>
                        {step.action === 'retrieve' ? 'Retrieve item directly' : step.action} {step.itemName}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          </div>
        ) : (
          searchResults && !searchResults.found && (
            <p className="no-results">No items found matching your search.</p>
          )
        )}
        
        {!searchResults && !loading && (
          <div className="browse-items">
            <h3>Browse All Items</h3>
            <div className="items-grid">
              {items.slice(0, 10).map(item => (
                <div key={item.item_id} className="item-card" onClick={() => setSearchTerm(item.item_id)}>
                  <h4>{item.name}</h4>
                  <p>ID: {item.item_id}</p>
                  {item.preferred_zone && <p>Zone: {item.preferred_zone}</p>}
                </div>
              ))}
              {items.length > 10 && (
                <div className="more-items">
                  + {items.length - 10} more items
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ItemSearch;