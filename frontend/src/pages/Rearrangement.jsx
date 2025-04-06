import React from 'react';
import '../styles/Rearrangement.css';

const Rearrangement = () => {
  return (
    <div className="rearrangement-page">
      <h1>Rearrangement Recommendations</h1>
      <p>Get smart suggestions for reorganizing cargo to maximize space efficiency.</p>
      
      <div className="rearrangement-dashboard">
        <div className="space-utilization">
          <h2>Space Utilization</h2>
          <div className="utilization-chart">
            {/* Placeholder for space utilization visualization */}
            <div className="chart-placeholder">
              <div className="chart-bar" style={{ width: '75%' }}>75%</div>
            </div>
          </div>
          <p>Current space utilization across all modules</p>
        </div>
        
        <div className="recommendations-section">
          <h2>Recommended Actions</h2>
          <div className="action-cards">
            <div className="action-card">
              <h3>Consolidate Module 3</h3>
              <p>Module 3 is at 45% capacity. Consider moving items from Module 5 to consolidate space.</p>
              <button className="action-button">View Plan</button>
            </div>
            <div className="action-card">
              <h3>Reorganize by Priority</h3>
              <p>High-priority items in Module 2 are difficult to access. Consider rearranging for better access.</p>
              <button className="action-button">View Plan</button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="feature-cards">
        <div className="feature-card">
          <h3>Relocation Suggestions</h3>
          <p>Automatically suggest which low-priority items can be relocated when space is insufficient.</p>
        </div>
        <div className="feature-card">
          <h3>Time Optimization</h3>
          <p>Minimize time spent moving items with efficient rearrangement plans.</p>
        </div>
        <div className="feature-card">
          <h3>Step-by-Step Plans</h3>
          <p>Show detailed movement plans when rearrangement is necessary.</p>
        </div>
      </div>
    </div>
  );
};

export default Rearrangement; 