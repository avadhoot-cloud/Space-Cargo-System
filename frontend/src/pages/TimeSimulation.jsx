import React, { useState } from 'react';
import axios from 'axios';
import '../styles/TimeSimulation.css';

const TimeSimulation = () => {
  const [simulationDays, setSimulationDays] = useState(1);
  const [simulating, setSimulating] = useState(false);
  const [simulationResults, setSimulationResults] = useState(null);
  const [error, setError] = useState(null);

  const simulateNextDay = async () => {
    try {
      setSimulating(true);
      setError(null);
      // Debug API URL
      const apiUrl = `${process.env.REACT_APP_API_URL}/simulation/day`;
      console.log('Simulation API URL:', apiUrl);
      
      const response = await axios.post(apiUrl);
      setSimulationResults(response.data);
      setSimulating(false);
    } catch (err) {
      console.error('Error simulating next day:', err);
      setError('Failed to simulate next day');
      setSimulating(false);
    }
  };

  const fastForwardDays = async () => {
    try {
      setSimulating(true);
      setError(null);
      // Debug API URL
      const apiUrl = `${process.env.REACT_APP_API_URL}/simulation/days`;
      console.log('Fast Forward API URL:', apiUrl);
      
      const response = await axios.post(
        apiUrl, 
        { days: simulationDays }
      );
      setSimulationResults(response.data);
      setSimulating(false);
    } catch (err) {
      console.error('Error fast forwarding days:', err);
      setError('Failed to fast forward days');
      setSimulating(false);
    }
  };

  return (
    <div className="time-simulation-page">
      <h1>Time Simulation</h1>
      <p>Simulate the passage of time to forecast inventory status and plan missions.</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="simulation-controls">
        <div className="control-card">
          <h3>Next Day Simulation</h3>
          <p>Simulate one day of operations with configurable item usage.</p>
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
      </div>
      
      {simulationResults && (
        <div className="simulation-results">
          <h2>Simulation Results</h2>
          <div className="results-grid">
            <div className="result-card">
              <h3>Items Consumed</h3>
              <p className="result-value">{simulationResults.itemsConsumed}</p>
            </div>
            <div className="result-card">
              <h3>New Expired Items</h3>
              <p className="result-value">{simulationResults.newExpiredItems}</p>
            </div>
            <div className="result-card">
              <h3>Days Simulated</h3>
              <p className="result-value">{simulationResults.daysSimulated}</p>
            </div>
            <div className="result-card">
              <h3>Current Date</h3>
              <p className="result-value">{new Date(simulationResults.currentDate).toLocaleDateString()}</p>
            </div>
          </div>
          
          {simulationResults.alerts && simulationResults.alerts.length > 0 && (
            <div className="simulation-alerts">
              <h3>Alerts</h3>
              <ul className="alerts-list">
                {simulationResults.alerts.map((alert, index) => (
                  <li key={index} className={`alert-item alert-${alert.severity}`}>
                    <span className="alert-severity">{alert.severity.toUpperCase()}</span>
                    <span className="alert-message">{alert.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      <div className="feature-cards">
        <div className="feature-card">
          <h3>Next Day Simulation</h3>
          <p>Simulate one day of operations with configurable item usage.</p>
        </div>
        <div className="feature-card">
          <h3>Fast Forward</h3>
          <p>Simulate multiple days at once to see longer-term effects.</p>
        </div>
        <div className="feature-card">
          <h3>Mission Planning</h3>
          <p>Use time simulation to help with future mission planning and resource allocation.</p>
        </div>
      </div>
    </div>
  );
};

export default TimeSimulation; 