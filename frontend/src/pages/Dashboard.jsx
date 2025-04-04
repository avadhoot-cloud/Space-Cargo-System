import React, { useState, useEffect } from 'react';
import ContainerGrid from '../components/ContainerGrid';
import SearchBar from '../components/SearchBar';
import { fetchContainers, fetchItems } from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [containers, setContainers] = useState([]);
  const [items, setItems] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [selectedContainerItems, setSelectedContainerItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState('');
  const [stats, setStats] = useState({
    totalContainers: 0,
    totalItems: 0,
    availableSpace: 0,
    placedItems: 0,
    zoneDistribution: {}
  });

  useEffect(() => {
    // Initial data fetch
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch containers
      const containersData = await fetchContainers();
      setContainers(containersData);
      
      // Fetch all items
      const itemsData = await fetchItems();
      setItems(itemsData);
      
      // Determine data source
      if (containersData.length > 0 || itemsData.length > 0) {
        setDataSource('Data loaded from database and data folder.');
      } else {
        setDataSource('No data available. Please upload CSV files.');
      }
      
      // Set selected container if available
      if (containersData.length > 0) {
        setSelectedContainer(containersData[0]);
        // Get items for this container
        const containerItems = itemsData.filter(item => 
          item.container_id === containersData[0].id
        );
        setSelectedContainerItems(containerItems);
      } else {
        setSelectedContainer(null);
        setSelectedContainerItems([]);
      }
      
      // Calculate stats
      calculateStats(containersData, itemsData);
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data. Please try again.');
      setLoading(false);
    }
  };
  
  const calculateStats = (containersData, itemsData) => {
    const totalContainers = containersData.length;
    const totalItems = itemsData.length;
    const placedItems = itemsData.filter(item => item.container_id !== null).length;
    
    // Calculate zone distribution
    const zoneDistribution = {};
    containersData.forEach(container => {
      const zone = container.zone || 'Unassigned';
      zoneDistribution[zone] = (zoneDistribution[zone] || 0) + 1;
    });
    
    // Calculate available space as percentage
    let totalSpace = 0;
    let usedSpace = 0;
    
    containersData.forEach(container => {
      const containerVolume = container.width * container.height * container.depth;
      totalSpace += containerVolume;
      
      // Calculate space used by items in this container
      const containerItems = itemsData.filter(item => item.container_id === container.id);
      const itemsVolume = containerItems.reduce((sum, item) => sum + (item.volume || 0), 0);
      usedSpace += itemsVolume;
    });
    
    const availableSpace = totalSpace > 0 
      ? Math.round((1 - usedSpace / totalSpace) * 100) 
      : 100;
    
    setStats({
      totalContainers,
      totalItems,
      availableSpace,
      placedItems,
      zoneDistribution
    });
  };

  const handleSearch = (searchParams) => {
    setLoading(true);
    
    if (searchParams.type === 'containers') {
      fetchContainers({
        name: searchParams.query,
        zone: searchParams.zone,
        is_active: searchParams.isActive
      })
      .then(data => {
        setContainers(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to search containers');
        setLoading(false);
        console.error(err);
      });
    } else {
      fetchItems({
        name: searchParams.query,
        container_id: searchParams.containerId || undefined,
        is_placed: searchParams.isPlaced,
        priority_min: searchParams.priorityMin,
        priority_max: searchParams.priorityMax,
        preferred_zone: searchParams.preferredZone
      })
      .then(data => {
        setItems(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to search items');
        setLoading(false);
        console.error(err);
      });
    }
  };

  const handleContainerSelect = (container) => {
    setSelectedContainer(container);
    
    // Filter items for this container
    const containerItems = items.filter(item => item.container_id === container.id);
    setSelectedContainerItems(containerItems);
  };

  if (loading && containers.length === 0) {
    return <div className="dashboard loading">Loading...</div>;
  }

  if (error) {
    return (
      <div className="dashboard error">
        <p>{error}</p>
        <button onClick={loadData} className="reload-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <div className="refresh-button" onClick={loadData}>
          Refresh
        </div>
      </div>
      
      {dataSource && (
        <div className="data-source-info">
          {dataSource}
        </div>
      )}
      
      <div className="dashboard-stats">
        <div className="stat-card">
          <p className="stat-title">Total Containers</p>
          <p className="stat-value">{stats.totalContainers}</p>
        </div>
        <div className="stat-card">
          <p className="stat-title">Total Items</p>
          <p className="stat-value">{stats.totalItems}</p>
        </div>
        <div className="stat-card">
          <p className="stat-title">Available Space</p>
          <p className="stat-value">{stats.availableSpace}%</p>
        </div>
        <div className="stat-card">
          <p className="stat-title">Placed Items</p>
          <p className="stat-value">{stats.placedItems}/{stats.totalItems}</p>
        </div>
      </div>
      
      {/* Zone Distribution */}
      {Object.keys(stats.zoneDistribution).length > 0 && (
        <div className="zone-distribution">
          <h2>Zone Distribution</h2>
          <div className="zone-cards">
            {Object.entries(stats.zoneDistribution).map(([zone, count]) => (
              <div key={zone} className="zone-card">
                <p className="zone-name">{zone}</p>
                <p className="zone-count">{count} containers</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="search-container">
        <h2>Search</h2>
        <SearchBar onSearch={handleSearch} />
      </div>
      
      <div className="dashboard-grid">
        <div className="containers-section">
          <h2>Containers</h2>
          {containers.length === 0 ? (
            <div className="no-data-message">
              <p>No containers found</p>
              <p className="suggestion">Upload container data from the Upload page</p>
            </div>
          ) : (
            <div className="container-cards">
              {containers.map(container => (
                <div 
                  key={container.id} 
                  className={`container-list-item ${selectedContainer && container.id === selectedContainer.id ? 'selected' : ''}`}
                  onClick={() => handleContainerSelect(container)}
                >
                  <div className="container-list-header">
                    <h3>{container.name}</h3>
                    {container.zone && (
                      <span className="container-zone">Zone: {container.zone}</span>
                    )}
                  </div>
                  <div className="container-list-details">
                    <p>ID: {container.id}</p>
                    <p>Dimensions: {container.width} × {container.height} × {container.depth} cm</p>
                    <p>Weight: {container.current_weight || 0}/{container.max_weight} kg</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="visualization-section">
          {selectedContainer ? (
            <ContainerGrid 
              container={selectedContainer} 
              items={selectedContainerItems} 
            />
          ) : (
            <div className="no-container-selected">
              <p>No container selected</p>
            </div>
          )}
        </div>
        
        <div className="items-section">
          <h2>Items</h2>
          {items.length === 0 ? (
            <div className="no-data-message">
              <p>No items found</p>
              <p className="suggestion">Upload item data from the Upload page</p>
            </div>
          ) : (
            <div className="items-table-container">
              <table className="items-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Dimensions (cm)</th>
                    <th>Mass (kg)</th>
                    <th>Priority</th>
                    <th>Preferred Zone</th>
                    <th>Container</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(item => (
                    <tr key={item.id}>
                      <td>{item.id}</td>
                      <td>{item.name}</td>
                      <td>
                        {item.width && item.height && item.depth 
                          ? `${item.width}×${item.height}×${item.depth}`
                          : 'N/A'}
                      </td>
                      <td>{item.weight} kg</td>
                      <td>
                        <span className={`priority priority-${item.priority}`}>
                          {item.priority}
                        </span>
                      </td>
                      <td>{item.preferred_zone || 'Any'}</td>
                      <td>{item.container_id || 'Unplaced'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 