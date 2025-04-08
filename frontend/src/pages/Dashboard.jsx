// frontend/src/pages/Dashboard.jsx

import React, { useState, useEffect, useRef } from 'react';
import apiService from '../services/api';
import StatsCard from '../components/StatsCard';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [placementStats, setPlacementStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wasteItems, setWasteItems] = useState([]);
  
  // Timeout reference for data loading
  const timeoutRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      // Set timeout for 15 seconds
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      
      timeoutRef.current = setTimeout(() => {
        setLoading(false);
        // Set default values if data loading times out
        setStats({
          totalItems: 0,
          totalContainers: 0,
          totalZones: 0,
          expiringSoon: 0
        });
        
        setPlacementStats({
          volume_utilization_percent: 0,
          placement_rate_percent: 0,
          total_items: 0,
          placed_items: 0,
          unplaced_items: 0,
          container_utilization: []
        });
        
        setWasteItems([]);
        setError('Failed to load data. Please try again.');
      }, 15000); // 15 seconds timeout
      
      try {
        // Fetch data summary
        const [itemsRes, containersRes, placementStatsRes, wasteRes] = await Promise.all([
          apiService.data.getItems(),
          apiService.data.getContainers(),
          apiService.placement.getStatistics(),
          apiService.waste.identify()
        ]);

        // Clear timeout since data loaded successfully
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        // Calculate stats
        const items = itemsRes.data;
        const containers = containersRes.data;
        
        setStats({
          totalItems: items.length,
          totalContainers: containers.length,
          totalZones: new Set(containers.map(c => c.zone)).size,
          expiringSoon: items.filter(item => {
            if (!item.expiry_date) return false;
            const expiry = new Date(item.expiry_date);
            const now = new Date();
            const daysUntilExpiry = Math.floor((expiry - now) / (1000 * 60 * 60 * 24));
            return daysUntilExpiry >= 0 && daysUntilExpiry <= 7;
          }).length
        });
        
        setPlacementStats(placementStatsRes.data);
        setWasteItems(wasteRes.data.wasteItems || []);
        
        setLoading(false);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        
        // Clear timeout since we already have an error
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }
        
        setError('Failed to load dashboard data. Please try again.');
        // Set default values on error
        setStats({
          totalItems: 0,
          totalContainers: 0,
          totalZones: 0,
          expiringSoon: 0
        });
        
        setPlacementStats({
          volume_utilization_percent: 0,
          placement_rate_percent: 0,
          total_items: 0,
          placed_items: 0,
          unplaced_items: 0,
          container_utilization: []
        });
        
        setWasteItems([]);
        setLoading(false);
      }
    };

    fetchData();
    
    // Cleanup timeout on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Format percentages
  const formatPercent = (value) => {
    if (value === undefined || value === null) {
      return "0.0%";
    }
    return `${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Space Cargo System Dashboard</h1>
        <button onClick={() => window.location.reload()} className="refresh-button">
          🔄 Refresh Data
        </button>
      </div>

      {error && (
        <div className="dashboard-error-banner">
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Try Again
          </button>
        </div>
      )}

      {/* Data Summary */}
      <div className="stats-section">
        <h2>Data Summary</h2>
        <div className="stats-grid">
          <StatsCard
            title="Total Items"
            value={stats?.totalItems || 0}
            icon="📦"
          />
          <StatsCard
            title="Total Containers"
            value={stats?.totalContainers || 0}
            icon="🗄️"
          />
          <StatsCard
            title="Total Zones"
            value={stats?.totalZones || 0}
            icon="🏷️"
          />
          <StatsCard
            title="Items Expiring Soon"
            value={stats?.expiringSoon || 0}
            icon="⏱️"
          />
        </div>
      </div>

      {/* Placement Statistics */}
      <div className="stats-section">
        <h2>Placement Performance</h2>
        <div className="stats-grid">
          <StatsCard
            title="Space Utilization"
            value={placementStats ? formatPercent(placementStats.volume_utilization_percent) : "0.0%"}
            icon="📏"
          />
          <StatsCard
            title="Placement Rate"
            value={placementStats ? formatPercent(placementStats.placement_rate_percent) : "0.0%"}
            icon="✅"
          />
          <StatsCard
            title="Items Placed"
            value={placementStats?.placed_items || 0}
            icon="🎯"
          />
          <StatsCard
            title="Unplaced Items"
            value={placementStats?.unplaced_items || 0}
            icon="⚡"
          />
        </div>
      </div>

      {/* Waste Management Summary */}
      <div className="stats-section">
        <h2>Waste Management</h2>
        <div className="waste-summary">
          <div className="waste-count-card">
            <div className="waste-count">{wasteItems.length}</div>
            <div className="waste-label">Items to Dispose</div>
          </div>
          <div className="waste-types">
            {wasteItems.length > 0 ? (
              <div className="waste-types-content">
                <div className="waste-type">
                  <div className="waste-type-label">Expired Items</div>
                  <div className="waste-type-value">
                    {wasteItems.filter(item => item.reason === "Expired").length}
                  </div>
                </div>
                <div className="waste-type">
                  <div className="waste-type-label">Out of Uses</div>
                  <div className="waste-type-value">
                    {wasteItems.filter(item => item.reason === "Out of Uses").length}
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-waste-message">
                No waste items found
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Container Utilization */}
      <div className="stats-section">
        <h2>Container Utilization</h2>
        {placementStats && placementStats.container_utilization && placementStats.container_utilization.length > 0 ? (
          <div className="container-util-grid">
            {placementStats.container_utilization.map((container, index) => (
              <div className="container-util-card" key={index}>
                <div className="container-util-name">{container.name || `Container ${container.id}`}</div>
                <div className="container-util-bar-container">
                  <div 
                    className="container-util-bar" 
                    style={{ width: `${container.utilization_percent || 0}%` }}
                  >
                    {(container.utilization_percent || 0).toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data-message">
            No container utilization data available
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;