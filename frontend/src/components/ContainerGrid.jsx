import React from 'react';
import '../styles/ContainerGrid.css';

// Enhanced placeholder component with more visual information
const ContainerVisualizationPlaceholder = ({ container, items }) => {
  // Calculate container usage percentage
  const usedVolume = items.reduce((total, item) => total + (item.volume || 0), 0);
  const containerVolume = container.width * container.height * container.depth;
  const usagePercentage = Math.min(Math.round((usedVolume / containerVolume) * 100), 100) || 0;
  
  return (
    <div className="visualization-placeholder">
      <div className="placeholder-info">
        <h3>{container.name} - Space Usage</h3>
        <div className="usage-bar">
          <div className="usage-fill" style={{ width: `${usagePercentage}%` }}></div>
          <span className="usage-text">{usagePercentage}%</span>
        </div>
        <div className="container-details">
          <p><strong>Items:</strong> {items.length}</p>
          <p><strong>Dimensions:</strong> {container.width}×{container.height}×{container.depth} units</p>
          <p><strong>Space used:</strong> {usedVolume.toFixed(2)} of {containerVolume.toFixed(2)} cubic units</p>
        </div>
      </div>
    </div>
  );
};

const ContainerGrid = ({ container, items = [] }) => {
  if (!container) {
    return (
      <div className="empty-message">
        <h3>No Container Selected</h3>
        <p>Please select a container to view its details</p>
      </div>
    );
  }
  
  // Calculate weight information
  const currentWeight = container.current_weight || 0;
  const maxWeight = container.max_weight || 100;
  const weightPercentage = Math.min(Math.round((currentWeight / maxWeight) * 100), 100);
  
  // Group items by priority
  const itemsByPriority = items.reduce((acc, item) => {
    const priority = item.priority || 1;
    if (!acc[priority]) acc[priority] = [];
    acc[priority].push(item);
    return acc;
  }, {});
  
  return (
    <div className="container-card">
      <div className="container-header">
        <h2 className="container-title">{container.name}</h2>
        <span className="container-id">ID: {container.id || 'N/A'}</span>
      </div>
      
      <div className="container-visualization">
        <ContainerVisualizationPlaceholder container={container} items={items} />
      </div>
      
      <div className="container-stats">
        <div className="stat">
          <span className="stat-value">{items.length}</span>
          <span className="stat-label">Items</span>
        </div>
        <div className="stat">
          <span className="stat-value">{weightPercentage}%</span>
          <span className="stat-label">Weight Capacity</span>
        </div>
        <div className="stat">
          <span className="stat-value">{Object.keys(itemsByPriority).length}</span>
          <span className="stat-label">Priority Groups</span>
        </div>
      </div>
      
      <div className="container-info">
        <p>
          <span>Dimensions</span>
          <strong>{container.width} × {container.height} × {container.depth}</strong>
        </p>
        <p>
          <span>Weight</span>
          <strong>{currentWeight} / {maxWeight} kg</strong>
        </p>
        <p>
          <span>Location</span>
          <strong>{container.location || 'Unspecified'}</strong>
        </p>
      </div>
      
      <div className="container-actions">
        <button className="action-button">View Items</button>
        <button className="action-button primary">Manage</button>
      </div>
    </div>
  );
};

export default ContainerGrid; 