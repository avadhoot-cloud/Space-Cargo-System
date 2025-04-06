import React, { useState, useEffect } from 'react';
import { fetchContainers, fetchItems } from '../services/api';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch, onClear, availableZones = [] }) => {
  const [searchType, setSearchType] = useState('items');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Container filters
  const [containerStatus, setContainerStatus] = useState('all');
  const [containerZone, setContainerZone] = useState('');
  
  // Item filters - changed from ranges to single values
  const [weightValue, setWeightValue] = useState('');
  const [priorityValue, setPriorityValue] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [usageLimit, setUsageLimit] = useState('');
  const [preferredZone, setPreferredZone] = useState('');
  
  // Suggestions state
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [allContainers, setAllContainers] = useState([]);
  const [allItems, setAllItems] = useState([]);
  
  // Items preferred zones from CSV
  const [preferredZones, setPreferredZones] = useState([]);
  
  // Load initial data for suggestions
  useEffect(() => {
    const loadSuggestionData = async () => {
      try {
        const containers = await fetchContainers();
        const items = await fetchItems();
        setAllContainers(containers);
        setAllItems(items);
        
        // Extract unique preferred zones from items
        const uniquePreferredZones = [...new Set(items
          .map(item => item.preferredZone)
          .filter(zone => zone !== null && zone !== undefined && zone !== '')
        )];
        setPreferredZones(uniquePreferredZones);
      } catch (error) {
        console.error('Error loading suggestion data:', error);
      }
    };
    
    loadSuggestionData();
  }, []);
  
  // Update suggestions when search query changes
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    let filteredResults = [];
    
    if (searchType === 'items') {
      filteredResults = allItems
        .filter(item => item.name.toLowerCase().includes(query) || 
                        (item.description && item.description.toLowerCase().includes(query)))
        .slice(0, 5); // Limit to 5 suggestions
    } else {
      filteredResults = allContainers
        .filter(container => container.name.toLowerCase().includes(query) ||
                             (container.zone && container.zone.toLowerCase().includes(query)))
        .slice(0, 5); // Limit to 5 suggestions
    }
    
    setSuggestions(filteredResults);
    setShowSuggestions(true);
  }, [searchQuery, searchType, allContainers, allItems]);

  const handleSearch = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    
    const searchParams = {
      type: searchType,
      query: searchQuery,
    };
    
    if (searchType === 'items') {
      // Updated to use single value filters instead of ranges
      if (weightValue) searchParams.weight = parseFloat(weightValue);
      if (priorityValue) searchParams.priority = parseInt(priorityValue, 10);
      if (expiryDate) searchParams.expiryDate = expiryDate;
      if (usageLimit) searchParams.usageLimit = parseInt(usageLimit, 10);
      if (preferredZone) searchParams.preferredZone = preferredZone;
    } else {
      // Updated container status options
      if (containerStatus !== 'all') searchParams.status = containerStatus;
      if (containerZone) searchParams.zone = containerZone;
    }
    
    onSearch(searchParams);
  };
  
  const handleClear = () => {
    setSearchQuery('');
    
    // Reset container filters
    setContainerStatus('all');
    setContainerZone('');
    
    // Reset item filters
    setWeightValue('');
    setPriorityValue('');
    setExpiryDate('');
    setUsageLimit('');
    setPreferredZone('');
    
    if (onClear) {
      onClear();
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.name);
    setShowSuggestions(false);
    
    // Trigger search with the selected suggestion
    const searchParams = {
      type: searchType,
      query: suggestion.name,
      directSearch: true,
      exactMatch: true,
      selectedId: suggestion.id
    };
    
    onSearch(searchParams);
  };
  
  const handleInputBlur = () => {
    // Delay hiding suggestions to allow for clicks
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
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
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder={`Search ${searchType} by name...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onBlur={handleInputBlur}
              className="search-input"
            />
            
            {showSuggestions && suggestions.length > 0 && (
              <div className="search-suggestions">
                {suggestions.map(suggestion => (
                  <div 
                    key={suggestion.id} 
                    className="suggestion-item"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <div className="suggestion-name">{suggestion.name}</div>
                    {searchType === 'containers' && suggestion.zone && (
                      <div className="suggestion-detail">Zone: {suggestion.zone}</div>
                    )}
                    {searchType === 'items' && (
                      <div className="suggestion-detail">
                        Mass: {suggestion.weight} kg, Priority: {suggestion.priority}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Item Filters - Updated to use single inputs */}
          {searchType === 'items' && (
            <div className="search-filters">
              <div className="filter-row">
                <div className="filter-group">
                  <label>Mass (kg):</label>
                  <input 
                    type="number" 
                    min="0" 
                    value={weightValue}
                    onChange={(e) => setWeightValue(e.target.value)}
                    placeholder="Enter mass value"
                  />
                </div>
                
                <div className="filter-group">
                  <label>Priority (0-100):</label>
                  <input 
                    type="number" 
                    min="0" 
                    max="100" 
                    value={priorityValue}
                    onChange={(e) => setPriorityValue(e.target.value)}
                    placeholder="Enter priority"
                  />
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group">
                  <label>Usage Limit:</label>
                  <input 
                    type="number" 
                    min="0" 
                    value={usageLimit}
                    onChange={(e) => setUsageLimit(e.target.value)}
                    placeholder="Enter usage limit"
                  />
                </div>
                
                <div className="filter-group">
                  <label>Expiry Date:</label>
                  <input 
                    type="date" 
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group">
                  <label>Preferred Zone:</label>
                  <select 
                    value={preferredZone}
                    onChange={(e) => setPreferredZone(e.target.value)}
                  >
                    <option value="">Any Zone</option>
                    {preferredZones.length > 0 ? (
                      preferredZones.map(zone => (
                        <option key={zone} value={zone}>{zone}</option>
                      ))
                    ) : (
                      availableZones.map(zone => (
                        <option key={zone} value={zone}>{zone}</option>
                      ))
                    )}
                  </select>
                </div>
              </div>
            </div>
          )}
          
          {/* Container Filters - Updated status options */}
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
                    <option value="full">Full</option>
                    <option value="partially">Partially Filled</option>
                    <option value="empty">Empty</option>
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>Zone:</label>
                  <select 
                    value={containerZone}
                    onChange={(e) => setContainerZone(e.target.value)}
                  >
                    <option value="">Any Zone</option>
                    {availableZones.map(zone => (
                      <option key={zone} value={zone}>{zone}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
          
          <div className="search-actions">
            <button type="submit" className="search-button">
              Search
            </button>
            <button type="button" onClick={handleClear} className="clear-button">
              Reset Filters
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default SearchBar; 