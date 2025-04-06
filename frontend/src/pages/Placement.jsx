import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Placement.css';

const Placement = () => {
  const [placementStats, setPlacementStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('statistics');

  useEffect(() => {
    const fetchPlacementStats = async () => {
      try {
        setLoading(true);
        // Log the API URL for debugging
        const apiUrl = `${process.env.REACT_APP_API_URL}/placement/statistics`;
        console.log('Fetching placement statistics from:', apiUrl);
        
        const response = await axios.get(apiUrl);
        console.log('Received placement statistics:', response.data);
        setPlacementStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching placement statistics:', err);
        setError(`Failed to load placement statistics: ${err.message}`);
        setLoading(false);
      }
    };

    fetchPlacementStats();
  }, []);

  if (loading) return (
    <div className="loading-container">
      <div className="loader"></div>
      <p>Loading placement statistics...</p>
    </div>
  );
  
  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p>{error}</p>
      <button onClick={() => window.location.reload()} className="retry-button">Retry</button>
    </div>
  );

  return (
    <div className="placement-page">
      <div className="placement-header">
        <h1>Placement Recommendations</h1>
        <p>This page provides automatic suggestions for where to place items based on available space and priority.</p>
        
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'statistics' ? 'active' : ''}`}
            onClick={() => setActiveTab('statistics')}
          >
            Statistics
          </button>
          <button 
            className={`tab-button ${activeTab === 'visualize' ? 'active' : ''}`}
            onClick={() => setActiveTab('visualize')}
          >
            3D Visualization
          </button>
          <button 
            className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            Recommendations
          </button>
        </div>
      </div>
      
      {activeTab === 'statistics' && placementStats && (
        <div className="stats-container">
          <h2>Placement Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📦</div>
              <h3>Total Items Placed</h3>
              <p className="stat-value">{placementStats.totalItemsPlaced || 0}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <h3>Space Utilization</h3>
              <p className="stat-value">{placementStats.spaceUtilization || 0}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${placementStats.spaceUtilization || 0}%` }}
                ></div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <h3>Successful Placements</h3>
              <p className="stat-value">{placementStats.successRate || 0}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill success" 
                  style={{ width: `${placementStats.successRate || 0}%` }}
                ></div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚡</div>
              <h3>Placement Efficiency</h3>
              <p className="stat-value">{placementStats.efficiency || 0}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill efficiency" 
                  style={{ width: `${placementStats.efficiency || 0}%` }}
                ></div>
              </div>
            </div>
            {placementStats.prioritySatisfaction && (
              <div className="stat-card">
                <div className="stat-icon">🔝</div>
                <h3>Priority Satisfaction</h3>
                <p className="stat-value">{placementStats.prioritySatisfaction}%</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill priority" 
                    style={{ width: `${placementStats.prioritySatisfaction}%` }}
                  ></div>
                </div>
              </div>
            )}
            {placementStats.zoneMatchRate && (
              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <h3>Zone Match Rate</h3>
                <p className="stat-value">{placementStats.zoneMatchRate}%</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill zone" 
                    style={{ width: `${placementStats.zoneMatchRate}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
          
          {/* Container Utilization Section */}
          {placementStats.containerUtilization && placementStats.containerUtilization.length > 0 && (
            <div className="container-utilization">
              <h2>Container Utilization</h2>
              <div className="container-grid">
                {placementStats.containerUtilization.map((container) => (
                  <div className="container-card" key={container.id}>
                    <h3>{container.name}</h3>
                    <div className="utilization-bar-container">
                      <div 
                        className="utilization-bar" 
                        style={{ height: `${container.utilizationPercentage}%` }}
                      >
                        <span className="utilization-text">{container.utilizationPercentage}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'visualize' && (
        <div className="visualization-container">
          <div className="visualization-placeholder">
            <h3>3D Container Visualization</h3>
            <p>Interactive visualization of container utilization and item placement</p>
            <div className="visualization-box">
              <div className="placeholder-text">3D Visualization coming soon</div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'recommendations' && (
        <div className="recommendations-container">
          <h3>Placement Recommendations</h3>
          <p>Optimized recommendations for placing new items</p>
          
          <div className="recommendation-list">
            <div className="recommendation-item">
              <div className="recommendation-icon">📦</div>
              <div className="recommendation-content">
                <h4>Item: Science Equipment Box</h4>
                <p>Suggested container: <strong>Storage Module Alpha, Section B-2</strong></p>
                <p>Reasoning: Best space utilization and priority matching</p>
                <div className="recommendation-actions">
                  <button className="accept-btn">Accept</button>
                  <button className="reject-btn">Reject</button>
                </div>
              </div>
            </div>
            
            <div className="recommendation-item">
              <div className="recommendation-icon">🧪</div>
              <div className="recommendation-content">
                <h4>Item: Lab Supplies</h4>
                <p>Suggested container: <strong>Lab Module, Section L-5</strong></p>
                <p>Reasoning: Zone matching and accessibility optimization</p>
                <div className="recommendation-actions">
                  <button className="accept-btn">Accept</button>
                  <button className="reject-btn">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="feature-cards">
        <div className="feature-card">
          <div className="feature-icon">🏆</div>
          <h3>Priority-Based Placement</h3>
          <p>Automatically suggest optimal placement locations based on item priority and available space.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🧩</div>
          <h3>Space Optimization</h3>
          <p>If space is insufficient, recommend rearranging existing items to make room.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Accessibility Focus</h3>
          <p>Ensure high-priority items remain easily accessible and in preferred zones.</p>
        </div>
      </div>
    </div>
  );
};

export default Placement; 