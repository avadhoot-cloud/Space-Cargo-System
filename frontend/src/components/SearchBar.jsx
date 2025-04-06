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
  
  // Search results state
  const [quickResults, setQuickResults] = useState([]);
  const [showQuickResults, setShowQuickResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
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
        
        // Show initial quick results
        if (searchType === 'items') {
          setQuickResults(items.slice(0, 5));
        } else {
          setQuickResults(containers.slice(0, 5));
        }
        setShowQuickResults(true);
        
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
  
  // Update type of quick results when search type changes
  useEffect(() => {
    if (searchType === 'items') {
      setQuickResults(allItems.slice(0, 5));
    } else {
      setQuickResults(allContainers.slice(0, 5));
    }
  }, [searchType, allItems, allContainers]);
  
  // Update suggestions when search query changes
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      // Show quick results when search query is empty
      setShowQuickResults(true);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    let filteredResults = [];
    
    if (searchType === 'items') {
      filteredResults = allItems
        .filter(item => item.name?.toLowerCase().includes(query) || 
                        (item.description && item.description.toLowerCase().includes(query)))
        .slice(0, 5); // Limit to 5 suggestions
    } else {
      filteredResults = allContainers
        .filter(container => container.name?.toLowerCase().includes(query) ||
                             (container.zone && container.zone.toLowerCase().includes(query)))
        .slice(0, 5); // Limit to 5 suggestions
    }
    
    setSuggestions(filteredResults);
    setShowSuggestions(true);
    setShowQuickResults(false);
  }, [searchQuery, searchType, allContainers, allItems]);

  const handleSearch = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    setShowQuickResults(false);
    setIsSearching(true);
    
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
    
    // Show quick results again
    if (searchType === 'items') {
      setQuickResults(allItems.slice(0, 5));
    } else {
      setQuickResults(allContainers.slice(0, 5));
    }
    setShowQuickResults(true);
    setShowSuggestions(false);
    setIsSearching(false);
    
    if (onClear) {
      onClear();
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.name || '');
    setShowSuggestions(false);
    setShowQuickResults(false);
    
    // Trigger search with the selected suggestion
    const searchParams = {
      type: searchType,
      query: suggestion.name || '',
      directSearch: true,
      exactMatch: true,
      selectedId: suggestion.id
    };
    
    onSearch(searchParams);
  };
  
  const handleResultsClick = (result) => {
    handleSuggestionClick(result);
  };
  
  const handleSearchTypeChange = (type) => {
    setSearchType(type);
    // Reset filters when changing search type
    if (type === 'items') {
      setContainerStatus('all');
      setContainerZone('');
    } else {
      setWeightValue('');
      setPriorityValue('');
      setExpiryDate('');
      setUsageLimit('');
      setPreferredZone('');
    }
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
            onClick={() => handleSearchTypeChange('items')}
          >
            Search Items
          </button>
          <button
            type="button"
            className={`toggle-btn ${searchType === 'containers' ? 'active' : ''}`}
            onClick={() => handleSearchTypeChange('containers')}
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
          
          <div className="search-buttons">
            <button type="submit" className="search-btn">
              Search
            </button>
            <button type="button" className="clear-btn" onClick={handleClear}>
              Clear
            </button>
          </div>
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
              
              <div className="filter-group">
                <label>Preferred Zone:</label>
                <select 
                  value={preferredZone}
                  onChange={(e) => setPreferredZone(e.target.value)}
                >
                  <option value="">Any Zone</option>
                  {preferredZones.map(zone => (
                    <option key={zone} value={zone}>{zone}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
        
        {/* Container Filters */}
        {searchType === 'containers' && (
          <div className="search-filters">
            <div className="filter-row">
              <div className="filter-group">
                <label>Status:</label>
                <select 
                  value={containerStatus}
                  onChange={(e) => setContainerStatus(e.target.value)}
                >
                  <option value="all">All Containers</option>
                  <option value="empty">Empty</option>
                  <option value="partial">Partially Filled</option>
                  <option value="full">Full</option>
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
      </form>
      
      {/* Quick results section - shown when no search is performed or on initial load */}
      {!isSearching && showQuickResults && quickResults.length > 0 && (
        <div className="quick-results">
          <div className="quick-results-header">
            <h3>{searchQuery ? 'Search Results' : 'Recent Items'}</h3>
          </div>
          <div className="quick-results-list">
            {quickResults.map(result => (
              <div 
                key={result.id} 
                className="quick-result-item"
                onClick={() => handleResultsClick(result)}
              >
                <div className="quick-result-icon">
                  {searchType === 'items' ? '📦' : '🗄️'}
                </div>
                <div className="quick-result-content">
                  <div className="quick-result-name">{result.name}</div>
                  {searchType === 'containers' && result.zone && (
                    <div className="quick-result-detail">Zone: {result.zone}</div>
                  )}
                  {searchType === 'items' && (
                    <div className="quick-result-detail">
                      Mass: {result.weight || 0} kg, Priority: {result.priority || 'N/A'}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar; 