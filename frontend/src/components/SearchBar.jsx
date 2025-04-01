import React, { useState } from 'react';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('items');
  const [filters, setFilters] = useState({
    isPlaced: null,
    priorityMin: '',
    priorityMax: '',
    containerId: ''
  });

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value === '' ? '' : (name === 'containerId' ? parseInt(value) : value)
    });
  };

  const handleSelectChange = (e) => {
    setSearchType(e.target.value);
    // Reset filters when changing search type
    setFilters({
      isPlaced: null,
      priorityMin: '',
      priorityMax: '',
      containerId: ''
    });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    
    // Construct search parameters
    const searchParams = {
      type: searchType,
      query: query,
      ...filters
    };
    
    // Pass search parameters to parent component
    onSearch(searchParams);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch}>
        <div className="search-row">
          <select 
            value={searchType} 
            onChange={handleSelectChange}
            className="search-type"
          >
            <option value="items">Items</option>
            <option value="containers">Containers</option>
          </select>
          
          <input
            type="text"
            placeholder={`Search ${searchType}...`}
            value={query}
            onChange={handleInputChange}
            className="search-input"
          />
          
          <button type="submit" className="search-button">
            Search
          </button>
        </div>
        
        <div className="filters">
          {searchType === 'items' && (
            <>
              <div className="filter-group">
                <label>Status:</label>
                <select 
                  name="isPlaced"
                  value={filters.isPlaced === null ? '' : filters.isPlaced.toString()}
                  onChange={(e) => setFilters({
                    ...filters,
                    isPlaced: e.target.value === '' ? null : e.target.value === 'true'
                  })}
                >
                  <option value="">All</option>
                  <option value="true">Placed</option>
                  <option value="false">Unplaced</option>
                </select>
              </div>
              
              <div className="filter-group">
                <label>Priority:</label>
                <input
                  type="number"
                  name="priorityMin"
                  placeholder="Min"
                  min="1"
                  max="5"
                  value={filters.priorityMin}
                  onChange={handleFilterChange}
                  className="small-input"
                />
                <span>-</span>
                <input
                  type="number"
                  name="priorityMax"
                  placeholder="Max"
                  min="1"
                  max="5"
                  value={filters.priorityMax}
                  onChange={handleFilterChange}
                  className="small-input"
                />
              </div>
              
              <div className="filter-group">
                <label>Container ID:</label>
                <input
                  type="number"
                  name="containerId"
                  placeholder="ID"
                  value={filters.containerId}
                  onChange={handleFilterChange}
                  className="small-input"
                />
              </div>
            </>
          )}
          
          {searchType === 'containers' && (
            <div className="filter-group">
              <label>Status:</label>
              <select 
                name="isActive"
                value={filters.isActive === null ? '' : filters.isActive.toString()}
                onChange={(e) => setFilters({
                  ...filters,
                  isActive: e.target.value === '' ? null : e.target.value === 'true'
                })}
              >
                <option value="">All</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar; 