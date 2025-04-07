// frontend/src/pages/Placement.jsx

import React, { useState, useEffect, Suspense } from 'react';
import apiService from '../services/api';
import Container3D from '../components/Container3D';
import '../styles/Placement.css';

const Placement = () => {
  const [placementStats, setPlacementStats] = useState(null);
  const [placementResults, setPlacementResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('statistics');
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [containers, setContainers] = useState([]);
  const [showPlacementModal, setShowPlacementModal] = useState(false);
  const [placementProcessing, setPlacementProcessing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsResponse, resultsResponse] = await Promise.all([
          apiService.placement.getStatistics(),
          apiService.placement.getResults()
        ]);

        setPlacementStats(statsResponse.data);
        setPlacementResults(resultsResponse.data);
        
        if (resultsResponse.data?.containers) {
          setContainers(resultsResponse.data.containers);
          if (resultsResponse.data.containers.length > 0 && !selectedContainer) {
            setSelectedContainer(resultsResponse.data.containers[0]);
          }
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(`Failed to load data: ${err.message}`);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoadingRecommendations(true);
      const response = await apiService.placement.getRecommendations();
      setRecommendations(response.data);
      setLoadingRecommendations(false);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(`Failed to load recommendations: ${err.message}`);
      setLoadingRecommendations(false);
    }
  };

  const handlePlacementAction = async (itemId, containerId) => {
    try {
      const response = await apiService.placement.placeItem(itemId, containerId);

      if (response.data.success) {
        // Refresh recommendations after successful placement
        fetchRecommendations();
        // Refresh statistics and results
        const [statsResponse, resultsResponse] = await Promise.all([
          apiService.placement.getStatistics(),
          apiService.placement.getResults()
        ]);
        setPlacementStats(statsResponse.data);
        setPlacementResults(resultsResponse.data);
      } else {
        setError(`Failed to place item: ${response.data.message}`);
      }
    } catch (err) {
      console.error(`Error placing item:`, err);
      setError(`Failed to place item: ${err.message}`);
    }
  };

  useEffect(() => {
    if (activeTab === 'recommendations') {
      fetchRecommendations();
    }
  }, [activeTab]);

  // Get items for a specific container
  const getContainerItems = (containerId) => {
    if (!placementResults?.placed_items) return [];
    return placementResults.placed_items.filter(item => item.container_id === containerId);
  };

  // Get a specific container by ID
  const getContainerById = (containerId) => {
    if (!placementResults?.containers) return null;
    return placementResults.containers.find(c => c.container_id === containerId);
  };

  const processPlacement = async () => {
    try {
      setPlacementProcessing(true);
      const response = await apiService.placement.processData();
      
      if (response.data.success) {
        // Refresh data after successful processing
        const [statsResponse, resultsResponse] = await Promise.all([
          apiService.placement.getStatistics(),
          apiService.placement.getResults()
        ]);
        
        setPlacementStats(statsResponse.data);
        setPlacementResults(resultsResponse.data);
        
        if (resultsResponse.data?.containers) {
          setContainers(resultsResponse.data.containers);
          if (resultsResponse.data.containers.length > 0) {
            setSelectedContainer(resultsResponse.data.containers[0]);
          }
        }
        
        // Show success message
        alert("Placement processing completed successfully!");
      } else {
        setError(`Failed to process placement: ${response.data.message}`);
      }
    } catch (err) {
      console.error('Error processing placement:', err);
      setError(`Failed to process placement: ${err.message}`);
    } finally {
      setPlacementProcessing(false);
    }
  };

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
        
        <button 
          className="process-button"
          onClick={processPlacement}
          disabled={placementProcessing}
        >
          {placementProcessing ? 'Processing...' : 'Process Placement Data'}
        </button>
      </div>
      
      {activeTab === 'statistics' && placementStats && (
        <div className="stats-container">
          <h2>Placement Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📦</div>
              <h3>Total Items Placed</h3>
              <p className="stat-value">{placementResults?.placed_items?.length || 0}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <h3>Space Utilization</h3>
              <p className="stat-value">{placementStats.space_utilization.toFixed(1)}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${placementStats.space_utilization}%` }}
                ></div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <h3>Success Rate</h3>
              <p className="stat-value">{placementStats.success_rate.toFixed(1)}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill success" 
                  style={{ width: `${placementStats.success_rate}%` }}
                ></div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚡</div>
              <h3>Overall Efficiency</h3>
              <p className="stat-value">{placementStats.efficiency.toFixed(1)}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill efficiency" 
                  style={{ width: `${placementStats.efficiency}%` }}
                ></div>
              </div>
            </div>
            {placementStats.priority_satisfaction && (
              <div className="stat-card">
                <div className="stat-icon">🔝</div>
                <h3>Priority Satisfaction</h3>
                <p className="stat-value">{placementStats.priority_satisfaction.toFixed(1)}%</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill priority" 
                    style={{ width: `${placementStats.priority_satisfaction}%` }}
                  ></div>
                </div>
              </div>
            )}
            {placementStats.zone_match_rate && (
              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <h3>Zone Match Rate</h3>
                <p className="stat-value">{placementStats.zone_match_rate.toFixed(1)}%</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill zone" 
                    style={{ width: `${placementStats.zone_match_rate}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
          
          {placementStats.container_utilization && placementStats.container_utilization.length > 0 && (
            <div className="container-utilization">
              <h2>Container Utilization</h2>
              <div className="container-grid">
                {placementStats.container_utilization.map((container) => (
                  <div className="container-card" key={container.id}>
                    <h3>{container.name || `Container ${container.id}`}</h3>
                    <div className="utilization-bar-container">
                      <div 
                        className="utilization-bar" 
                        style={{ height: `${container.utilization_percentage}%` }}
                      >
                        <span className="utilization-text">{Math.round(container.utilization_percentage)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'visualize' && placementResults && (
        <div className="visualization-container">
          <div className="container-selector">
            <h3>Select Container</h3>
            <select 
              value={selectedContainer?.container_id || ''}
              onChange={(e) => {
                const containerId = e.target.value;
                const container = getContainerById(containerId);
                setSelectedContainer(container);
              }}
            >
              {containers.map(container => (
                <option key={container.container_id} value={container.container_id}>
                  {container.name || `Container ${container.container_id}`} ({container.zone})
                </option>
              ))}
            </select>
          </div>
          
          {selectedContainer ? (
            <div className="container-visualization">
              <Suspense fallback={<div>Loading 3D view...</div>}>
                <Container3D 
                  containerData={selectedContainer}
                  placedItems={getContainerItems(selectedContainer.container_id)}
                />
              </Suspense>
              
              <div className="container-info">
                <h4>Container {selectedContainer.container_id} Contents</h4>
                <div className="items-list">
                  {getContainerItems(selectedContainer.container_id).map((item) => (
                    <div key={item.item_id} className="item-entry">
                      <span>Item {item.item_id}</span>
                      <span>Position: ({item.x_cm}, {item.y_cm}, {item.z_cm})</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="visualization-placeholder">
              <p>No container selected or no containers available.</p>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'recommendations' && (
        <div className="recommendations-container">
          <h3>Placement Recommendations</h3>
          <p>Optimized recommendations for placing new items</p>
          
          {loadingRecommendations ? (
            <div className="loading-container">
              <div className="loader"></div>
              <p>Loading recommendations...</p>
            </div>
          ) : (
            <div className="recommendation-list">
              {recommendations.map((recommendation) => (
                <div className="recommendation-item" key={recommendation.item_id}>
                  <div className="recommendation-icon">📦</div>
                  <div className="recommendation-content">
                    <h4>Item: {recommendation.item_name}</h4>
                    <p>Suggested container: <strong>{recommendation.container_name}</strong></p>
                    <p>Reasoning: {recommendation.reasoning}</p>
                    <div className="recommendation-actions">
                      <button 
                        className="accept-btn"
                        onClick={() => handlePlacementAction(recommendation.item_id, recommendation.container_id)}
                      >
                        Accept
                      </button>
                      <button 
                        className="reject-btn"
                        onClick={() => {
                          // Remove this recommendation
                          setRecommendations(recommendations.filter(r => r.item_id !== recommendation.item_id));
                        }}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {recommendations.length === 0 && (
                <div className="no-recommendations">
                  <p>No placement recommendations available at this time.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Placement;