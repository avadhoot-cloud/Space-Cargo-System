import React, { useState, useEffect } from 'react';
import ContainerGrid from '../components/ContainerGrid';
import SearchBar from '../components/SearchBar';
import '../styles/Dashboard.css';
import { fetchContainers, fetchItems } from '../services/api';

const Dashboard = () => {
  const [containers, setContainers] = useState([]);
  const [items, setItems] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [selectedContainerItems, setSelectedContainerItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch containers on component mount
    fetchContainers()
      .then(data => {
        setContainers(data);
        if (data.length > 0) {
          setSelectedContainer(data[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch containers');
        setLoading(false);
        console.error(err);
      });
  }, []);

  useEffect(() => {
    // When selected container changes, fetch its items
    if (selectedContainer) {
      fetchItems({ container_id: selectedContainer.id })
        .then(data => {
          setSelectedContainerItems(data);
        })
        .catch(err => {
          console.error('Error fetching container items:', err);
        });
    }
  }, [selectedContainer]);

  const handleSearch = (searchParams) => {
    setLoading(true);
    
    if (searchParams.type === 'containers') {
      fetchContainers({
        name: searchParams.query,
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
        is_placed: searchParams.isPlaced
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
  };

  if (loading) {
    return <div className="dashboard loading">Loading...</div>;
  }

  if (error) {
    return <div className="dashboard error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <section className="search-section">
        <h2>Search</h2>
        <SearchBar onSearch={handleSearch} />
      </section>
      
      <section className="container-section">
        <h2>Containers</h2>
        <div className="container-list">
          {containers.length === 0 ? (
            <p>No containers found</p>
          ) : (
            containers.map(container => (
              <div 
                key={container.id} 
                className={`container-item ${selectedContainer && container.id === selectedContainer.id ? 'selected' : ''}`}
                onClick={() => handleContainerSelect(container)}
              >
                <h3>{container.name}</h3>
                <p>Space: {Math.round((1 - container.current_weight / container.max_weight) * 100)}% free</p>
                <p>Items: {container.items ? container.items.length : '0'}</p>
              </div>
            ))
          )}
        </div>
      </section>
      
      <section className="visualization-section">
        <ContainerGrid 
          container={selectedContainer} 
          items={selectedContainerItems} 
        />
      </section>
      
      <section className="items-section">
        <h2>Items</h2>
        <div className="items-list">
          {items.length === 0 ? (
            <p>No items found. Use the search to find items.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Priority</th>
                  <th>Weight</th>
                  <th>Volume</th>
                  <th>Container</th>
                  <th>Position</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.name}</td>
                    <td>{item.priority}</td>
                    <td>{item.weight} kg</td>
                    <td>{item.volume} m³</td>
                    <td>{item.container_id || 'Unplaced'}</td>
                    <td>
                      {item.position_x !== null 
                        ? `(${item.position_x}, ${item.position_y}, ${item.position_z})`
                        : '-'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
};

export default Dashboard; 