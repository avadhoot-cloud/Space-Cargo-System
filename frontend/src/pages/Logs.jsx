import React, { useState, useEffect, useRef } from 'react';
import apiService from '../services/api';
import '../styles/Logs.css';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    itemId: '',
    userId: '',
    actionType: ''
  });
  
  // Timeout reference
  const timeoutRef = useRef(null);

  useEffect(() => {
    fetchLogs();
    
    // Cleanup timeout on component unmount
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Set timeout for 15 seconds
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        setLoading(false);
        setLogs([]);
        setError('Failed to load data. Please try again later.');
      }, 15000); // 15 seconds timeout
      
      const { startDate, endDate, itemId, userId, actionType } = filters;

      const response = await apiService.logs.getLogs(
        startDate || undefined,
        endDate || undefined,
        itemId || undefined,
        userId || undefined,
        actionType || undefined
      );

      // Clear timeout since data loaded successfully
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      
      setLogs(response.data.logs || []);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to load logs');
      setLoading(false);
      
      // Clear timeout
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleFilter = (e) => {
    e.preventDefault();
    fetchLogs();
  };

  const handleClear = () => {
    setFilters({
      startDate: '',
      endDate: '',
      itemId: '',
      userId: '',
      actionType: ''
    });
    // Fetch logs after clearing filters with a small delay to allow state update
    setTimeout(fetchLogs, 0);
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  const InputField = ({ label, name, type = 'text', placeholder }) => (
    <div className="input-field">
      <label>{label}</label>
      <input
        type={type}
        name={name}
        value={filters[name]}
        onChange={handleChange}
        placeholder={placeholder}
        className="form-control"
      />
    </div>
  );

  return (
    <div className="logs-page">
      <div className="logs-header">
        <h1>System Activity Logs</h1>
        <p>View and filter system operations and user activities</p>
      </div>

      <div className="logs-content">
        <div className="filter-panel">
          <h3>Filter Options</h3>
          <form className="filter-form" onSubmit={handleFilter}>
            <div className="filter-row">
              <InputField label="Start Date" name="startDate" type="date" />
              <InputField label="End Date" name="endDate" type="date" />
            </div>
            
            <div className="filter-row">
              <InputField label="Item ID" name="itemId" placeholder="Enter Item ID" />
              <InputField label="User ID" name="userId" placeholder="Enter User ID" />
            </div>
            
            <div className="filter-row">
              <div className="input-field">
                <label>Action Type</label>
                <select 
                  name="actionType" 
                  value={filters.actionType} 
                  onChange={handleChange}
                  className="form-control"
                >
                  <option value="">All Actions</option>
                  <option value="placement">Placement</option>
                  <option value="retrieval">Retrieval</option>
                  <option value="disposal">Disposal</option>
                  <option value="rearrangement">Rearrangement</option>
                </select>
              </div>
            </div>

            <div className="filter-actions">
              <button type="submit" className="btn apply-btn">
                <i className="filter-icon"></i>Apply Filters
              </button>
              <button type="button" className="btn clear-btn" onClick={handleClear}>
                <i className="clear-icon"></i>Clear All
              </button>
            </div>
          </form>
        </div>

        <div className="logs-table-section">
          {error ? (
            <div className="error-message">
              <i className="error-icon"></i>
              <p>{error}</p>
              <button onClick={fetchLogs} className="btn retry-btn">Try Again</button>
            </div>
          ) : loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading logs data...</p>
            </div>
          ) : (
            <div className="table-container">
              <div className="table-header">
                <h3>Log Entries {logs.length > 0 && `(${logs.length})`}</h3>
                <span className="last-updated">Last updated: {new Date().toLocaleTimeString()}</span>
              </div>
              
              {logs.length > 0 ? (
                <table className="logs-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>User</th>
                      <th>Action</th>
                      <th>Item ID</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log, index) => (
                      <tr key={index} className={`log-row ${log.action_type}`}>
                        <td className="timestamp">{formatDate(log.timestamp)}</td>
                        <td className="user-id">{log.user_id || 'System'}</td>
                        <td className="action-type">
                          <span className={`action-badge ${log.action_type}`}>
                            {log.action_type}
                          </span>
                        </td>
                        <td className="item-id">{log.item_id || '-'}</td>
                        <td className="details">{log.details || 'No details available'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-logs-message">
                  <i className="empty-icon"></i>
                  <p>No logs found matching the selected filters.</p>
                  <p className="suggestion">Try clearing filters or adjusting your search criteria.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Logs;
