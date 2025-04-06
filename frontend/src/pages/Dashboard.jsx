import React, { useState, useEffect } from 'react';
import { fetchContainers, fetchItems } from '../services/api';
import SearchBar from '../components/SearchBar';
import StatsCard from '../components/StatsCard';
import ISSModel from '../components/ISSModel';
import '../styles/Dashboard.css';
import '../styles/ISSModel.css';

// Zone visualization component
const ZoneVisualization = ({ zoneDistribution }) => {
  return (
    <div className="zone-visualization">
      <h2>🗺️ Zones Distribution</h2>
      <div className="zone-summary">
        <div className="zone-count-badge">
          <span className="zone-count-number">{zoneDistribution.length}</span>
          <span className="zone-count-label">Unique Zones</span>
        </div>
        <div className="zone-list">
          {zoneDistribution.map(zone => (
            <div key={zone.zone} className="zone-item">
              <span className="zone-name">{zone.zone}</span>
              <span className="zone-container-count">{zone.count} containers</span>
              <div className="zone-percentage-bar">
                <div 
                  className="zone-percentage-fill" 
                  style={{ width: `${zone.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [containers, setContainers] = useState([]);
  const [items, setItems] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalContainers: 0,
    totalItems: 0,
    availableSpace: 0,
    zoneDistribution: []
  });
  
  // New state variables for search results
  const [searchResults, setSearchResults] = useState(null);
  const [relatedResults, setRelatedResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [availableZones, setAvailableZones] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const fetchedContainers = await fetchContainers();
      const fetchedItems = await fetchItems();
      
      setContainers(fetchedContainers);
      setItems(fetchedItems);
      calculateStats(fetchedContainers, fetchedItems);
      
      // Extract unique zones for filter dropdowns
      const uniqueZones = [...new Set(fetchedContainers
        .map(container => container.zone)
        .filter(zone => zone !== null && zone !== undefined))];
      setAvailableZones(uniqueZones);
      
      // Reset search results when fresh data is loaded
      setSearchResults(null);
      setRelatedResults(null);
      setIsSearching(false);
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (containers, items) => {
    // Calculate total containers
    const totalContainers = containers.length;
    
    // Calculate total items
    const totalItems = items.length;
    
    // Calculate available space (sum of container volumes minus sum of item volumes)
    const totalContainerVolume = containers.reduce((sum, container) => {
      const volume = (container.width * container.height * container.depth) / 1000000; // Convert cm³ to m³
      return sum + volume;
    }, 0);
    
    const totalItemVolume = items.reduce((sum, item) => sum + item.volume, 0);
    const availableSpace = Math.max(0, totalContainerVolume - totalItemVolume);
    
    // Calculate zone distribution
    const zones = {};
    containers.forEach(container => {
      const zone = container.zone || 'Unassigned';
      if (!zones[zone]) {
        zones[zone] = 0;
      }
      zones[zone]++;
    });
    
    const zoneDistribution = Object.entries(zones).map(([zone, count]) => ({
      zone,
      count,
      percentage: (count / totalContainers) * 100
    }));
    
    setStats({
      totalContainers,
      totalItems,
      availableSpace,
      zoneDistribution
    });
  };

  const handleContainerClick = (container) => {
    if (selectedContainer && selectedContainer.id === container.id) {
      setSelectedContainer(null);
    } else {
      setSelectedContainer(container);
    }
    
    // Reset search results when container is selected
    setSearchResults(null);
    setRelatedResults(null);
    setIsSearching(false);
  };

  const handleSearch = async (searchParams) => {
    setIsSearching(true);
    setLoading(true);
    setError(null);
    
    try {
      if (searchParams.type === 'containers') {
        // Search for containers with new status options
        const containerParams = {
          name: searchParams.query
        };
        
        if (searchParams.zone) {
          containerParams.zone = searchParams.zone;
        }
        
        // Handle new container status filters
        if (searchParams.status) {
          // Set fillStatus based on the selected option
          containerParams.fillStatus = searchParams.status;
        }
        
        const results = await fetchContainers(containerParams);
        
        // Direct results (exact matches)
        const directResults = results.filter(container => 
          container.name.toLowerCase().includes(searchParams.query.toLowerCase()) ||
          (container.zone && container.zone.toLowerCase().includes(searchParams.query.toLowerCase()))
        );
        
        // Related results (partial matches or related properties)
        const relatedResults = results.filter(container => 
          !directResults.some(dr => dr.id === container.id)
        );
        
        setSearchResults(directResults);
        setRelatedResults(relatedResults);
        setSelectedContainer(null);
        setContainers(results);
      } else {
        // Search for items with new single value filters
        const itemParams = {
          name: searchParams.query
        };
        
        // Add the new single value filters
        if (searchParams.weight) {
          itemParams.weight = searchParams.weight;
        }
        
        if (searchParams.priority) {
          itemParams.priority = searchParams.priority;
        }
        
        if (searchParams.expiryDate) {
          itemParams.expiryDate = searchParams.expiryDate;
        }
        
        if (searchParams.usageLimit) {
          itemParams.usageLimit = searchParams.usageLimit;
        }
        
        if (searchParams.preferredZone) {
          itemParams.preferredZone = searchParams.preferredZone;
        }
        
        const results = await fetchItems(itemParams);
        
        // Direct results (exact matches)
        const directResults = results.filter(item => 
          item.name.toLowerCase().includes(searchParams.query.toLowerCase()) ||
          (item.description && item.description.toLowerCase().includes(searchParams.query.toLowerCase()))
        );
        
        // Related results (partial matches or related properties)
        const relatedResults = results.filter(item => 
          !directResults.some(dr => dr.id === item.id)
        );
        
        setSearchResults(directResults);
        setRelatedResults(relatedResults);
        setItems(results);
      }
    } catch (err) {
      setError('Failed to perform search. Please try again.');
      console.error('Error searching:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchResults(null);
    setRelatedResults(null);
    setIsSearching(false);
    loadData();
  };

  // Get items for the selected container
  const getContainerItems = () => {
    if (!selectedContainer) return [];
    return items.filter(item => item.container_id === selectedContainer.id);
  };

  // Format volume for display
  const formatVolume = (volume) => {
    return volume.toFixed(4) + ' m³';
  };

  // Calculate container volume
  const calculateContainerVolume = (container) => {
    return (container.width * container.height * container.depth) / 1000000; // Convert cm³ to m³
  };

  const renderContainerCard = (container) => (
    <div 
      key={container.id}
      className={`container-card ${selectedContainer && selectedContainer.id === container.id ? 'selected' : ''}`}
      onClick={() => handleContainerClick(container)}
    >
      <h3>
        {container.name}
        {container.zone && (
          <span className="container-zone-badge">{container.zone}</span>
        )}
      </h3>
      <div className="container-details">
        <p>
          <span className="label">ID:</span> 
          <span className="value">{container.id}</span>
        </p>
        <p>
          <span className="label">Dimensions:</span>
          <span className="value">{container.width}×{container.height}×{container.depth} cm</span>
        </p>
        <p>
          <span className="label">Volume:</span>
          <span className="value">{formatVolume(calculateContainerVolume(container))}</span>
        </p>
        <p>
          <span className="label">Weight Capacity:</span>
          <span className="value">{container.max_weight} kg</span>
        </p>
        <p>
          <span className="label">Current Weight:</span>
          <span className="value">{container.current_weight || 0} kg</span>
        </p>
        <p>
          <span className="label">Status:</span>
          <span className="value">{container.is_active ? 'Active' : 'Inactive'}</span>
        </p>
      </div>
      <button className="container-view-3d-btn" onClick={(e) => {
        e.stopPropagation();
        // Handle 3D view functionality
        alert(`3D view for container #${container.id} will be implemented soon`);
      }}>
        <span>📊</span> 3D View
      </button>
    </div>
  );

  if (loading && !isSearching) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error && !isSearching) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Space Cargo System Dashboard</h1>
        <button onClick={loadData} className="refresh-button">
          🔄 Refresh Data
        </button>
      </div>

      {/* Replace 3D Architecture Visualization with ISSModel */}
      {!loading && !error && (
        <div className="model-section">
          <h2>International Space Station Model</h2>
          <ISSModel modelUrl="/models/iss.glb" />
          <div className="model-instructions">
            <p>Drag to rotate • Scroll to zoom • Shift+drag to pan</p>
            <p>Note: Upload your ISS GLB model to the public/models directory to view it</p>
          </div>
        </div>
      )}

      {/* Statistics Overview */}
      <div className="stats-container">
        <StatsCard 
          title="Total Containers" 
          value={stats.totalContainers} 
          icon="📦" 
        />
        <StatsCard 
          title="Total Items" 
          value={stats.totalItems} 
          icon="🏷️" 
        />
        <StatsCard 
          title="Available Space" 
          value={formatVolume(stats.availableSpace)} 
          icon="📏" 
        />
        <StatsCard 
          title="Zones" 
          value={stats.zoneDistribution.length} 
          icon="🗺️" 
        />
      </div>

      {/* Zone Visualization */}
      {!loading && !error && (
        <ZoneVisualization zoneDistribution={stats.zoneDistribution} />
      )}

      {/* Enhanced Search Bar */}
      <div className="search-container">
        <SearchBar 
          onSearch={handleSearch} 
          onClear={handleClearSearch}
          availableZones={availableZones}
        />
        
        {isSearching && (
          <div className="search-controls">
            <button className="clear-search-button" onClick={handleClearSearch}>
              Clear Search Results
            </button>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && !isSearching && (
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isSearching && (
        <div className="dashboard-error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadData} className="retry-button">
            Retry
          </button>
        </div>
      )}

      {/* Container and Items Display */}
      {!loading && !error && (
        <div className="dashboard-content">
          <div className="containers-section">
            <h2 className="section-title">Containers</h2>
            <div className="container-cards">
              {containers.length > 0 ? (
                containers.map(container => renderContainerCard(container))
              ) : (
                <div className="no-data-message">
                  <p>No containers available. Add containers or adjust your search criteria.</p>
                </div>
              )}
            </div>
          </div>

          <div className="items-section">
            <h2 className="section-title">Items</h2>
            <div className="items-table-container">
              {items.length > 0 ? (
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Weight (kg)</th>
                      <th>Volume (m³)</th>
                      <th>Container</th>
                      <th>Priority</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(item => (
                      <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>{item.name}</td>
                        <td>{item.weight} kg</td>
                        <td>{formatVolume(item.volume)}</td>
                        <td>{item.container_id || 'Not placed'}</td>
                        <td>
                          <span className={`priority priority-${item.priority}`}>
                            {item.priority}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-data-message">
                  <p>No items available. Add items or adjust your search criteria.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 