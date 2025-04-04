import React, { useState } from 'react';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [searchType, setSearchType] = useState('items');
  const [searchQuery, setSearchQuery] = useState('');
  const [containerFilter, setContainerFilter] = useState('all');
  const [priorityMin, setPriorityMin] = useState(1);
  const [priorityMax, setPriorityMax] = useState(5);
  const [containerStatus, setContainerStatus] = useState('all');
  const [preferredZone, setPreferredZone] = useState('');
  const [zone, setZone] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    
    const searchParams = {
      type: searchType,
      query: searchQuery,
    };
    
    if (searchType === 'items') {
      searchParams.containerId = containerFilter !== 'all' ? 
        (containerFilter === 'placed' ? 'any' : null) : undefined;
      
      searchParams.isPlaced = containerFilter === 'placed';
      searchParams.priorityMin = priorityMin;
      searchParams.priorityMax = priorityMax;
      searchParams.preferredZone = preferredZone || undefined;
    } else {
      searchParams.isActive = containerStatus !== 'inactive';
      searchParams.zone = zone || undefined;
    }
    
    onSearch(searchParams);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch}>
        <div className="search-type-toggle">
          <button
            type="button"
            className={`toggle-btn ${searchType === 'items' ? 'active' : ''}`}
            onClick={() => setSearchType('items')}
          >
            Search Items
          </button>
          <button
            type="button"
            className={`toggle-btn ${searchType === 'containers' ? 'active' : ''}`}
            onClick={() => setSearchType('containers')}
          >
            Search Containers
          </button>
        </div>
        
        <div className="search-input-group">
          <input
            type="text"
            placeholder={`Search ${searchType} by name...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          
          {searchType === 'items' && (
            <div className="search-filters">
              <div className="filter-row">
                <div className="filter-group">
                  <label>Container Status:</label>
                  <select 
                    value={containerFilter}
                    onChange={(e) => setContainerFilter(e.target.value)}
                  >
                    <option value="all">All Items</option>
                    <option value="placed">Placed in Containers</option>
                    <option value="unplaced">Not Placed</option>
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>Priority Range:</label>
                  <div className="range-inputs">
                    <input 
                      type="number" 
                      min="1" 
                      max="5" 
                      value={priorityMin}
                      onChange={(e) => setPriorityMin(Number(e.target.value))}
                    />
                    <span>to</span>
                    <input 
                      type="number" 
                      min="1" 
                      max="5" 
                      value={priorityMax}
                      onChange={(e) => setPriorityMax(Number(e.target.value))}
                    />
                  </div>
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group">
                  <label>Preferred Zone:</label>
                  <input
                    type="text"
                    placeholder="Filter by zone (A, B, C...)"
                    value={preferredZone}
                    onChange={(e) => setPreferredZone(e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}
          
          {searchType === 'containers' && (
            <div className="search-filters">
              <div className="filter-row">
                <div className="filter-group">
                  <label>Container Status:</label>
                  <select 
                    value={containerStatus}
                    onChange={(e) => setContainerStatus(e.target.value)}
                  >
                    <option value="all">All Containers</option>
                    <option value="active">Active Only</option>
                    <option value="inactive">Inactive Only</option>
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>Zone:</label>
                  <input
                    type="text"
                    placeholder="Filter by zone (A, B, C...)"
                    value={zone}
                    onChange={(e) => setZone(e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
        
        <button type="submit" className="search-button">
          Search
        </button>
      </form>
    </div>
  );
};

export default SearchBar; 