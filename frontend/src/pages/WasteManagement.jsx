import React, { useState } from 'react';
import '../styles/WasteManagement.css';

const WasteManagement = () => {
  const [activeTab, setActiveTab] = useState('expired');
  
  return (
    <div className="waste-management-page">
      <h1>Waste Management & Return Planning</h1>
      <p>Track expired items and plan for waste disposal during undocking operations.</p>
      
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
          Waste Tracking
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
            <div className="items-list">
              <div className="item-row header">
                <div className="item-col">Item Name</div>
                <div className="item-col">Location</div>
                <div className="item-col">Expired On</div>
                <div className="item-col">Actions</div>
              </div>
              <div className="item-row">
                <div className="item-col">Medical Supplies Kit A</div>
                <div className="item-col">Module 2, Shelf 3</div>
                <div className="item-col">March 15, 2024</div>
                <div className="item-col">
                  <button className="action-btn">Mark as Waste</button>
                </div>
              </div>
              <div className="item-row">
                <div className="item-col">Food Ration Pack C-12</div>
                <div className="item-col">Module 1, Container 7</div>
                <div className="item-col">April 1, 2024</div>
                <div className="item-col">
                  <button className="action-btn">Mark as Waste</button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'waste' && (
          <div className="waste-tracking-tab">
            <h2>Waste Tracking</h2>
            <div className="waste-summary">
              <div className="summary-card">
                <h3>Total Waste</h3>
                <p className="summary-value">24.5 kg</p>
              </div>
              <div className="summary-card">
                <h3>Waste by Type</h3>
                <div className="waste-chart">
                  <div className="chart-bar food" style={{ width: '45%' }}>Food: 45%</div>
                  <div className="chart-bar medical" style={{ width: '25%' }}>Medical: 25%</div>
                  <div className="chart-bar packaging" style={{ width: '30%' }}>Packaging: 30%</div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'undocking' && (
          <div className="undocking-tab">
            <h2>Undocking Preparation</h2>
            <div className="undocking-plan">
              <h3>Next Undocking: May 15, 2024</h3>
              <div className="plan-steps">
                <div className="step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Consolidate Waste</h4>
                    <p>Move all waste items to the return module (Module 6)</p>
                  </div>
                </div>
                <div className="step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>Generate Manifest</h4>
                    <p>Create detailed inventory of return items</p>
                    <button className="generate-btn">Generate Manifest</button>
                  </div>
                </div>
                <div className="step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Prepare Return Vehicle</h4>
                    <p>Ensure weight distribution is within parameters</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="feature-cards">
        <div className="feature-card">
          <h3>Automatic Tracking</h3>
          <p>Track items that become waste (expired or finished) and mark them for disposal.</p>
        </div>
        <div className="feature-card">
          <h3>Undocking Preparation</h3>
          <p>Suggest moving all waste to the undocking module while ensuring weight limits are followed.</p>
        </div>
        <div className="feature-card">
          <h3>Manifest Generation</h3>
          <p>Generate detailed manifests for cargo return during undocking operations.</p>
        </div>
      </div>
    </div>
  );
};

export default WasteManagement; 