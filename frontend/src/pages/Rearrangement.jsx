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
      
      // Fetch placement results and statistics
      const [resultsResponse, statsResponse] = await Promise.all([
        apiService.placement.getResults(),
        apiService.placement.getStatistics()
      ]);
      
      setPlacementResults(resultsResponse.data);
      setSpaceUtilization(statsResponse.data.space_utilization);
      
      // Generate rearrangement recommendations
      generateRecommendations(resultsResponse.data);
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load rearrangement data');
      setLoading(false);
    }
  };

  const generateRecommendations = (data) => {
    if (!data || !data.containers || !data.placed_items) return;
    
    const recommendations = [];
    
    // Calculate container utilization
    const containerUtilization = {};
    data.containers.forEach(container => {
      const containerItems = data.placed_items.filter(item => item.container_id === container.container_id);
      const usedVolume = containerItems.reduce((total, item) => {
        return total + (item.width_cm * item.height_cm * item.depth_cm);
      }, 0);
      const totalVolume = container.width_cm * container.height_cm * container.depth_cm;
      const utilization = (usedVolume / totalVolume) * 100;
      
      containerUtilization[container.container_id] = {
        container,
        utilization,
        usedVolume,
        totalVolume
      };
    });
    
    // Find containers with utilization < 50%
    const lowUtilizationContainers = Object.values(containerUtilization)
      .filter(cont => cont.utilization < 50)
      .sort((a, b) => a.utilization - b.utilization);
      
    // Find containers with utilization > 80%
    const highUtilizationContainers = Object.values(containerUtilization)
      .filter(cont => cont.utilization > 80)
      .sort((a, b) => b.utilization - a.utilization);
    
    // Generate recommendations for consolidation
    if (lowUtilizationContainers.length > 0) {
      recommendations.push({
        type: 'consolidation',
        title: `Consolidate ${lowUtilizationContainers[0].container.container_id}`,
        description: `Container ${lowUtilizationContainers[0].container.container_id} is at ${lowUtilizationContainers[0].utilization.toFixed(1)}% capacity. Consider consolidating items to free up space.`,
        container: lowUtilizationContainers[0].container,
        utilization: lowUtilizationContainers[0].utilization
      });
    }
    
    // Generate recommendations for load balancing
    if (highUtilizationContainers.length > 0 && lowUtilizationContainers.length > 0) {
      recommendations.push({
        type: 'balancing',
        title: 'Balance Container Load',
        description: `Move items from ${highUtilizationContainers[0].container.container_id} (${highUtilizationContainers[0].utilization.toFixed(1)}% full) to ${lowUtilizationContainers[0].container.container_id} (${lowUtilizationContainers[0].utilization.toFixed(1)}% full) to balance the load.`,
        sourceContainer: highUtilizationContainers[0].container,
        targetContainer: lowUtilizationContainers[0].container,
        sourceUtilization: highUtilizationContainers[0].utilization,
        targetUtilization: lowUtilizationContainers[0].utilization
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

  const generateRearrangementPlan = (recommendation) => {
    const plan = [];
    
    if (recommendation.type === 'consolidation') {
      const container = recommendation.container;
      const containerItems = placementResults.placed_items.filter(
        item => item.container_id === container.container_id
      );
      
      // Find target containers
      const otherContainers = placementResults.containers.filter(
        c => c.container_id !== container.container_id
      );
      
      if (otherContainers.length > 0) {
        // Pick the first container as target for simplicity
        const targetContainer = otherContainers[0];
        
        // Generate plan to move items
        containerItems.forEach((item, index) => {
          plan.push({
            step: index + 1,
            action: 'move',
            itemId: item.item_id,
            itemName: (placementResults.items.find(i => i.item_id === item.item_id) || {}).name || `Item ${item.item_id}`,
            fromContainer: container.container_id,
            toContainer: targetContainer.container_id
          });
        });
      }
    } else if (recommendation.type === 'balancing') {
      const sourceContainer = recommendation.sourceContainer;
      const targetContainer = recommendation.targetContainer;
      
      // Get items from source container
      const sourceItems = placementResults.placed_items.filter(
        item => item.container_id === sourceContainer.container_id
      );
      
      // Move half of the items to target container
      const itemsToMove = sourceItems.slice(0, Math.ceil(sourceItems.length / 2));
      
      itemsToMove.forEach((item, index) => {
        plan.push({
          step: index + 1,
          action: 'move',
          itemId: item.item_id,
          itemName: (placementResults.items.find(i => i.item_id === item.item_id) || {}).name || `Item ${item.item_id}`,
          fromContainer: sourceContainer.container_id,
          toContainer: targetContainer.container_id
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
        
        plan.push({
          step: index + 1,
          action: 'move',
          itemId: item.item_id,
          itemName: itemData.name || `Item ${item.item_id}`,
          fromContainer: item.container_id,
          toContainer: targetContainer.container_id
        });
      });
    }
    
    return plan;
  };

  const handleViewPlan = (recommendation) => {
    const plan = generateRearrangementPlan(recommendation);
    setRearrangementPlan(plan);
    setShowRearrangementModal(true);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loader"></div>
        <p>Loading rearrangement data...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p>{error}</p>
        <button onClick={fetchData} className="retry-button">Retry</button>
      </div>
    );
  }
  
  return (
    <div className="rearrangement-page">
      <h1>Rearrangement Recommendations</h1>
      <p>Get smart suggestions for reorganizing cargo to maximize space efficiency.</p>
      
      <div className="rearrangement-dashboard">
        <div className="space-utilization">
          <h2>Space Utilization</h2>
          <div className="utilization-chart">
            <div className="chart-bg">
              <div 
                className={`chart-bar ${spaceUtilization > 80 ? 'high' : spaceUtilization > 50 ? 'medium' : 'low'}`} 
                style={{ width: `${spaceUtilization}%` }}
              >
                {spaceUtilization.toFixed(1)}%
              </div>
            </div>
          </div>
          <p>Current space utilization across all modules</p>
        </div>
        
        <div className="recommendations-section">
          <h2>Recommended Actions</h2>
          
          {recommendations.length > 0 ? (
            <div className="action-cards">
              {recommendations.map((recommendation, index) => (
                <div className="action-card" key={index}>
                  <h3>{recommendation.title}</h3>
                  <p>{recommendation.description}</p>
                  <button 
                    className="action-button"
                    onClick={() => handleViewPlan(recommendation)}
                  >
                    View Plan
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-recommendations">
              <p>No rearrangement recommendations at this time. Current arrangement is optimal.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Rearrangement Plan Modal */}
      {showRearrangementModal && (
        <div className="modal-overlay">
          <div className="rearrangement-modal">
            <div className="modal-header">
              <h3>Rearrangement Plan</h3>
              <button 
                className="close-modal-button"
                onClick={() => setShowRearrangementModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-content">
              {rearrangementPlan.length > 0 ? (
                <>
                  <p>Follow these steps to rearrange items:</p>
                  <ol className="rearrangement-steps">
                    {rearrangementPlan.map((step, index) => (
                      <li key={index}>
                        {step.action === 'move' ? (
                          <span>
                            Move {step.itemName} from Container {step.fromContainer} to Container {step.toContainer}
                          </span>
                        ) : (
                          <span>{step.action} {step.itemName}</span>
                        )}
                      </li>
                    ))}
                  </ol>
                </>
              ) : (
                <p>No rearrangement steps needed.</p>
              )}
            </div>
            
            <div className="modal-footer">
              <button 
                className="modal-button"
                onClick={() => setShowRearrangementModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Rearrangement;