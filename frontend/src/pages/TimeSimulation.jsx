// frontend/src/pages/TimeSimulation.jsx

import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import '../styles/TimeSimulation.css';

const TimeSimulation = () => {
  const [simulationDays, setSimulationDays] = useState(1);
  const [targetDate, setTargetDate] = useState('');
  const [simulating, setSimulating] = useState(false);
  const [simulationResults, setSimulationResults] = useState(null);
  const [error, setError] = useState(null);
  const [items, setItems] = useState([]);
  const [itemsToUse, setItemsToUse] = useState([]);
  const [selectedItem, setSelectedItem] = useState('');

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await apiService.data.getItems();
        setItems(response.data);
      } catch (err) {
        console.error('Error fetching items:', err);
        setError('Failed to load items');
      }
    };
    
    fetchItems();
  }, []);

  const addItemToUse = () => {
    if (!selectedItem) return;
    
    const item = items.find(i => i.item_id === selectedItem);
    if (item) {
      setItemsToUse([...itemsToUse, {
        itemId: item.item_id,
        name: item.name
      }]);
      setSelectedItem('');
    }
  };

  const removeItemToUse = (itemId) => {
    setItemsToUse(itemsToUse.filter(item => item.itemId !== itemId));
  };

  const simulateNextDay = async () => {
    try {
      setSimulating(true);
      setError(null);
      
      const response = await apiService.simulation.simulateDays(1, itemsToUse);
      setSimulationResults(response.data);
      
      // Reset items to use
      setItemsToUse([]);
      
      // Update items list with new data
      const itemsResponse = await apiService.data.getItems();
      setItems(itemsResponse.data);
      
      setSimulating(false);
    } catch (err) {
      console.error('Error simulating next day:', err);
      setError('Failed to simulate next day');
      setSimulating(false);
    }
  };

  const fastForwardDays = async () => {
    try {
      if (simulationDays <= 0) {
        setError('Number of days must be positive');
        return;
      }
      
      setSimulating(true);
      setError(null);
      
      const response = await apiService.simulation.simulateDays(simulationDays, itemsToUse);
      setSimulationResults(response.data);
      
      // Reset items to use
      setItemsToUse([]);
      
      // Update items list with new data
      const itemsResponse = await apiService.data.getItems();
      setItems(itemsResponse.data);
      
      setSimulating(false);
    } catch (err) {
      console.error('Error fast forwarding days:', err);
      setError('Failed to fast forward days');
      setSimulating(false);
    }
  };

  const simulateToDate = async () => {
    try {
      if (!targetDate) {
        setError('Please select a target date');
        return;
      }
      
      const targetTimestamp = new Date(targetDate).toISOString();
      
      setSimulating(true);
      setError(null);
      
      const response = await apiService.simulation.simulateToDate(targetTimestamp, itemsToUse);
      setSimulationResults(response.data);
      
      // Reset items to use
      setItemsToUse([]);
      
      // Update items list with new data
      const itemsResponse = await apiService.data.getItems();
      setItems(itemsResponse.data);
      
      setSimulating(false);
    } catch (err) {
      console.error('Error simulating to date:', err);
      setError('Failed to simulate to date');
      setSimulating(false);
    }
  };

  return (
    <div className="time-simulation-page">
      <h1>Time Simulation</h1>
      <p>Simulate the passage of time to forecast inventory status and plan missions.</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="items-to-use-section">
        <h2>Items to Use</h2>
        <div className="item-selection">
          <select 
            value={selectedItem}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            <option value="">Select an item to use</option>
            {items.map(item => (
              <option key={item.item_id} value={item.item_id}>
                {item.name} (ID: {item.item_id})
              </option>
            ))}
          </select>
          <button 
            className="add-item-btn"
            onClick={addItemToUse}
            disabled={!selectedItem}
          >
            Add Item
          </button>
        </div>
        
        {itemsToUse.length > 0 && (
          <div className="items-to-use-list">
            <h3>Selected Items:</h3>
            <ul>
              {itemsToUse.map((item, index) => (
                <li key={index}>
                  {item.name}
                  <button 
                    className="remove-item-btn"
                    onClick={() => removeItemToUse(item.itemId)}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div className="simulation-controls">
        <div className="control-card">
          <h3>Next Day Simulation</h3>
          <p>Simulate one day of operations with selected items.</p>
          <button 
            className="sim-button" 
            onClick={simulateNextDay} 
            disabled={simulating}
          >
            {simulating ? 'Simulating...' : 'Simulate Next Day'}
          </button>
        </div>
        
        <div className="control-card">
          <h3>Fast Forward</h3>
          <p>Simulate multiple days at once to see longer-term effects.</p>
          <div className="sim-control">
            <input 
              type="number" 
              min="1" 
              max="90" 
              value={simulationDays}
              onChange={(e) => setSimulationDays(parseInt(e.target.value))}
              className="sim-input" 
            />
            <button 
              className="sim-button" 
              onClick={fastForwardDays} 
              disabled={simulating}
            >
              {simulating ? 'Simulating...' : 'Fast Forward'}
            </button>
          </div>
        </div>
        
        <div className="control-card">
          <h3>Simulate to Date</h3>
          <p>Simulate time passage until a specific calendar date.</p>
          <div className="sim-control">
            <input 
              type="date" 
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="sim-input date-input" 
            />
            <button 
              className="sim-button" 
              onClick={simulateToDate} 
              disabled={simulating}
            >
              {simulating ? 'Simulating...' : 'Simulate to Date'}
            </button>
          </div>
        </div>
      </div>
      
      {simulationResults && (
        <div className="simulation-results">
          <h2>Simulation Results</h2>
          <div className="results-grid">
            <div className="result-card">
              <h3>New Date</h3>
              <p className="result-value">{new Date(simulationResults.newDate).toLocaleDateString()}</p>
            </div>
            <div className="result-card">
              <h3>Items Used</h3>
              <p className="result-value">{simulationResults.changes.itemsUsed.length}</p>
            </div>
            <div className="result-card">
              <h3>New Expired Items</h3>
              <p className="result-value">{simulationResults.changes.itemsExpired.length}</p>
            </div>
            <div className="result-card">
              <h3>Items Depleted</h3>
              <p className="result-value">{simulationResults.changes.itemsDepletedToday.length}</p>
            </div>
          </div>
          
          {simulationResults.changes.itemsExpired.length > 0 && (
            <div className="expiry-alerts">
              <h3>Expired Items:</h3>
              <ul className="alerts-list">
                {simulationResults.changes.itemsExpired.map((item, index) => (
                  <li key={index} className="alert-item alert-critical">
                    <span className="alert-message">Item {item.name} (ID: {item.item_id}) has expired</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {simulationResults.changes.itemsDepletedToday.length > 0 && (
            <div className="depletion-alerts">
              <h3>Depleted Items:</h3>
              <ul className="alerts-list">
                {simulationResults.changes.itemsDepletedToday.map((item, index) => (
                  <li key={index} className="alert-item alert-warning">
                    <span className="alert-message">Item {item.name} (ID: {item.item_id}) is out of uses</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TimeSimulation;