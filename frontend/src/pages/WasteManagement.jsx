// frontend/src/pages/WasteManagement.jsx

import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import '../styles/WasteManagement.css';

const WasteManagement = () => {
  const [activeTab, setActiveTab] = useState('expired');
  const [wasteItems, setWasteItems] = useState([]);
  const [returnPlan, setReturnPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [undockingContainerId, setUndockingContainerId] = useState('');
  const [maxWeight, setMaxWeight] = useState(1000);
  const [undockingDate, setUndockingDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [containers, setContainers] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [wasteResponse, containersResponse] = await Promise.all([
          apiService.waste.identify(),
          apiService.data.getContainers()
        ]);
        
        setWasteItems(wasteResponse.data.waste_items || []);
        setContainers(containersResponse.data.containers || []);
        
        // Set default undocking container if available
        if (containersResponse.data.containers && containersResponse.data.containers.length > 0) {
          setUndockingContainerId(containersResponse.data.containers[0].container_id);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching waste data:', err);
        setError('Failed to load waste data');
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleGenerateReturnPlan = async () => {
    try {
      if (!undockingContainerId) {
        setError('Please select an undocking container');
        return;
      }
      
      setLoading(true);
      const response = await apiService.waste.returnPlan(
        undockingContainerId,
        undockingDate,
        maxWeight
      );
      
      setReturnPlan(response.data);
      setActiveTab('undocking');
      setLoading(false);
    } catch (err) {
      console.error('Error generating return plan:', err);
      setError('Failed to generate return plan');
      setLoading(false);
    }
  };

  const handleCompleteUndocking = async () => {
    try {
      if (!undockingContainerId) {
        setError('Please select an undocking container');
        return;
      }
      
      setLoading(true);
      const response = await apiService.waste.completeUndocking(undockingContainerId);
      
      if (response.data.success) {
        // Refresh waste items
        const wasteResponse = await apiService.waste.identify();
        setWasteItems(wasteResponse.data.waste_items || []);
        
        alert(`Successfully removed ${response.data.itemsRemoved} waste items`);
        setReturnPlan(null);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error completing undocking:', err);
      setError('Failed to complete undocking');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loader"></div>
        <p>Loading waste management data...</p>
      </div>
    );
  }
  
  return (
    <div className="waste-management-page">
      <h1>Waste Management & Return Planning</h1>
      <p>Track expired items and plan for waste disposal during undocking operations.</p>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      <div className="waste-tabs">
        <button 
          className={`tab-button ${activeTab === 'expired' ? 'active' : ''}`} 
          onClick={() => setActiveTab('expired')}
        >
          Expired Items
        </button>
        <button 
          className={`tab-button ${activeTab === 'waste' ? 'active' : ''}`} 
          onClick={() => setActiveTab('waste')}
        >
          Waste Summary
        </button>
        <button 
          className={`tab-button ${activeTab === 'undocking' ? 'active' : ''}`} 
          onClick={() => setActiveTab('undocking')}
        >
          Undocking Plan
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'expired' && (
          <div className="expired-items-tab">
            <h2>Expired Items</h2>
            {wasteItems.length > 0 ? (
              <div className="items-list">
                <div className="item-row header">
                  <div className="item-col">Item Name</div>
                  <div className="item-col">Item ID</div>
                  <div className="item-col">Location</div>
                  <div className="item-col">Reason</div>
                </div>
                {wasteItems.map((item) => (
                  <div className="item-row" key={item.item_id}>
                    <div className="item-col">{item.name}</div>
                    <div className="item-col">{item.item_id}</div>
                    <div className="item-col">Container {item.containerId}</div>
                    <div className="item-col">{item.reason}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-waste-message">
                <p>No expired or used up items found</p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'waste' && (
          <div className="waste-tracking-tab">
            <h2>Waste Tracking</h2>
            {wasteItems.length > 0 ? (
              <div className="waste-summary">
                <div className="summary-card">
                  <h3>Total Waste Items</h3>
                  <p className="summary-value">{wasteItems.length}</p>
                </div>
                <div className="summary-card">
                  <h3>Waste by Type</h3>
                  <div className="waste-chart">
                    {(() => {
                      const expiredCount = wasteItems.filter(item => item.reason === 'Expired').length;
                      const usedUpCount = wasteItems.filter(item => item.reason === 'Out of Uses').length;
                      const expiredPercentage = (expiredCount / wasteItems.length) * 100;
                      const usedUpPercentage = (usedUpCount / wasteItems.length) * 100;
                      
                      return (
                        <>
                          <div className="chart-bar expired" style={{ width: `${expiredPercentage}%` }}>
                            Expired: {expiredCount} ({expiredPercentage.toFixed(0)}%)
                          </div>
                          <div className="chart-bar used-up" style={{ width: `${usedUpPercentage}%` }}>
                            Out of Uses: {usedUpCount} ({usedUpPercentage.toFixed(0)}%)
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-waste-message">
                <p>No waste items found</p>
              </div>
            )}
            
            {wasteItems.length > 0 && (
              <div className="plan-actions">
                <button 
                  className="generate-plan-button"
                  onClick={handleGenerateReturnPlan}
                >
                  Generate Return Plan
                </button>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'undocking' && (
          <div className="undocking-tab">
            <h2>Undocking Preparation</h2>
            
            <div className="undocking-form">
              <div className="form-group">
                <label>Undocking Container:</label>
                <select 
                  value={undockingContainerId} 
                  onChange={(e) => setUndockingContainerId(e.target.value)}
                >
                  <option value="">Select a container</option>
                  {containers.map(container => (
                    <option key={container.container_id} value={container.container_id}>
                      {container.container_id} ({container.zone})
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Undocking Date:</label>
                <input 
                  type="date" 
                  value={undockingDate} 
                  onChange={(e) => setUndockingDate(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label>Max Weight (kg):</label>
                <input 
                  type="number" 
                  value={maxWeight} 
                  onChange={(e) => setMaxWeight(e.target.value)}
                  min="1"
                  step="0.1"
                />
              </div>
              
              <button 
                className="generate-btn"
                onClick={handleGenerateReturnPlan}
              >
                Generate Return Plan
              </button>
            </div>
            
            {returnPlan && (
              <div className="return-plan-results">
                <h3>Return Plan for {returnPlan.returnManifest.undockingDate}</h3>
                
                <div className="return-summary">
                  <div className="summary-item">
                    <span>Total Items:</span>
                    <span>{returnPlan.returnManifest.returnItems.length}</span>
                  </div>
                  <div className="summary-item">
                    <span>Total Weight:</span>
                    <span>{returnPlan.returnManifest.totalWeight.toFixed(2)} kg</span>
                  </div>
                  <div className="summary-item">
                    <span>Total Volume:</span>
                    <span>{returnPlan.returnManifest.totalVolume.toFixed(2)} cm³</span>
                  </div>
                </div>
                
                {returnPlan.returnPlan.length > 0 ? (
                  <div className="return-steps">
                    <h4>Return Plan Steps:</h4>
                    <ol>
                      {returnPlan.returnPlan.map((step, index) => (
                        <li key={index}>
                          Move {step.itemName} from Container {step.fromContainer} to Container {step.toContainer}
                        </li>
                      ))}
                    </ol>
                    
                    <button 
                      className="complete-undocking-btn"
                      onClick={handleCompleteUndocking}
                    >
                      Complete Undocking
                    </button>
                  </div>
                ) : (
                  <div className="no-return-items">
                    <p>No items to return</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WasteManagement;