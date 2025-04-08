// frontend/src/pages/Rearrangement.jsx

import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import '../styles/Rearrangement.css';

const Rearrangement = () => {
  const [placementResults, setPlacementResults] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [spaceUtilization, setSpaceUtilization] = useState(0);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [showRearrangementModal, setShowRearrangementModal] = useState(false);
  const [rearrangementPlan, setRearrangementPlan] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch placement results
      const resultsResponse = await apiService.placement.getResults();
      
      if (resultsResponse.data && resultsResponse.data.success) {
        setPlacementResults(resultsResponse.data);
        
        // Calculate overall space utilization
        const totalUtilization = Object.values(resultsResponse.data.container_utilization || {})
          .reduce((sum, cont) => sum + (cont.utilization || 0), 0);
        const avgUtilization = totalUtilization / (Object.keys(resultsResponse.data.container_utilization || {}).length || 1);
        setSpaceUtilization(avgUtilization);
        
        // Generate recommendations
        generateRecommendations(resultsResponse.data);
      } else {
        setError('Failed to load placement data');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load rearrangement data');
      setLoading(false);
    }
  };

  const generateRecommendations = (data) => {
    if (!data || !data.containers || !data.placed_items) {
      setRecommendations([]);
      return;
    }
    
    const recommendations = [];
    const lowUtilization = [];
    const highUtilization = [];
    const zoningIssues = [];

    // Calculate container utilization
    data.containers.forEach(container => {
      const totalVolume = container.width * container.height * container.depth;
      const usedVolume = container.items.reduce((sum, item) => sum + (item.volume || 0), 0);
      const utilization = (usedVolume / totalVolume) * 100;

      if (utilization < 30) {
        lowUtilization.push({
          container_id: container.container_id,
          utilization,
          items: container.items
        });
      } else if (utilization > 90) {
        highUtilization.push({
          container_id: container.container_id,
          utilization,
          items: container.items
        });
      }
    });

    // Generate recommendations based on utilization
    if (lowUtilization.length > 0) {
      recommendations.push({
        type: 'consolidation',
        title: 'Container Consolidation',
        description: 'Consolidate items from low utilization containers',
        containers: lowUtilization
      });
    }

    if (highUtilization.length > 0) {
      recommendations.push({
        type: 'balancing',
        title: 'Load Balancing',
        description: 'Redistribute items from high utilization containers',
        containers: highUtilization
      });
    }

    // Generate zone-based recommendations
    const itemsInWrongZone = data.placed_items.filter(item => {
      const itemData = data.items.find(i => i.item_id === item.item_id);
      const containerData = data.containers.find(c => c.container_id === item.container_id);
      return itemData && containerData && itemData.preferred_zone && itemData.preferred_zone !== containerData.zone;
    });
    
    if (itemsInWrongZone.length > 0) {
      recommendations.push({
        type: 'zoning',
        title: 'Optimize Zone Placement',
        description: `${itemsInWrongZone.length} items are not in their preferred zones. Consider rearranging to improve zone match rate.`,
        itemCount: itemsInWrongZone.length
      });
    }
    
    setRecommendations(recommendations);
  };

  const handleViewPlan = (recommendation) => {
    setSelectedContainer(recommendation);
    setShowRearrangementModal(true);
    generateRearrangementPlan(recommendation);
  };

  const generateRearrangementPlan = (recommendation) => {
    if (!placementResults || !placementResults.containers) {
      console.error('Placement data not loaded');
      setRearrangementPlan([]);
      return;
    }

    const plan = {
      moves: [],
      estimatedTime: 0
    };

    if (recommendation.type === 'consolidation') {
      // Implementation for consolidation
      const sourceContainers = recommendation.containers;
      const targetContainer = placementResults.containers.find(c => 
        !sourceContainers.some(sc => sc.container_id === c.container_id) &&
        c.items.length < c.max_items
      );

      if (targetContainer) {
        sourceContainers.forEach(source => {
          source.items.forEach(item => {
            plan.moves.push({
              item_id: item.item_id,
              from_container: source.container_id,
              to_container: targetContainer.container_id,
              reason: 'Consolidation'
            });
          });
        });
      }
    } else if (recommendation.type === 'balancing') {
      const sourceContainers = recommendation.containers;
      const targetContainers = placementResults.containers.filter(c => 
        !sourceContainers.some(sc => sc.container_id === c.container_id)
      );
      
      sourceContainers.forEach(source => {
        const itemsToMove = source.items.slice(0, Math.ceil(source.items.length / 2));
        itemsToMove.forEach(item => {
          const targetContainer = targetContainers.find(c => c.container_id !== source.container_id);
          if (targetContainer) {
            plan.moves.push({
              item_id: item.item_id,
              from_container: source.container_id,
              to_container: targetContainer.container_id,
              reason: 'Load Balancing'
            });
          }
        });
      });
    } else if (recommendation.type === 'zoning') {
      // Find items in wrong zones
      const itemsInWrongZone = placementResults.placed_items.filter(item => {
        const itemData = placementResults.items.find(i => i.item_id === item.item_id);
        const containerData = placementResults.containers.find(c => c.container_id === item.container_id);
        return itemData && containerData && itemData.preferred_zone && itemData.preferred_zone !== containerData.zone;
      });
      
      // Find containers in the correct zones
      itemsInWrongZone.forEach((item, index) => {
        const itemData = placementResults.items.find(i => i.item_id === item.item_id);
        if (!itemData || !itemData.preferred_zone) return;
        
        // Find a container in the preferred zone
        const targetContainer = placementResults.containers.find(c => c.zone === itemData.preferred_zone);
        if (!targetContainer) return;
        
        plan.moves.push({
          item_id: item.item_id,
          from_container: item.container_id,
          to_container: targetContainer.container_id,
          reason: 'Zoning'
        });
      });
    }
    
    setRearrangementPlan(plan);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="rearrangement-container">
      <h1>Container Rearrangement</h1>
      
      <div className="stats-container">
        <div className="stat-card">
          <h3>Space Utilization</h3>
          <p>{spaceUtilization.toFixed(1)}%</p>
        </div>
        <div className="stat-card">
          <h3>Items Placed</h3>
          <p>{placementResults?.placed_items?.length || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Unplaced Items</h3>
          <p>{placementResults?.unplaced_items?.length || 0}</p>
        </div>
      </div>
      
      <div className="recommendations-container">
        <h2>Recommendations</h2>
        {recommendations.length > 0 ? (
          <div className="recommendations-list">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-card">
                <h3>{rec.title}</h3>
                <p>{rec.description}</p>
                <button onClick={() => handleViewPlan(rec)}>View Plan</button>
              </div>
            ))}
          </div>
        ) : (
          <p>No recommendations available</p>
        )}
      </div>
      
      {showRearrangementModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>Rearrangement Plan</h2>
            <h3>{selectedContainer?.title}</h3>
            <div className="plan-steps">
              {rearrangementPlan.moves.map((move, index) => (
                <div key={index} className="plan-step">
                  <span className="step-number">Step {index + 1}:</span>
                  <span className="step-action">
                    Move {move.item_id} from Container {move.from_container} to Container {move.to_container}
                  </span>
                </div>
              ))}
            </div>
            <button onClick={() => setShowRearrangementModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Rearrangement;