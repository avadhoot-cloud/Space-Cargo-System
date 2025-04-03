import React, { useState, useEffect } from 'react';
import '../styles/Logs.css';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Mock API call to fetch logs
    setTimeout(() => {
      const mockLogs = [
        { id: 1, action: 'Item placed', timestamp: '2023-04-01T10:30:15', user: 'system', details: 'Item #A123 placed in Container #C001 at position (1,2,3)' },
        { id: 2, action: 'Container added', timestamp: '2023-04-01T09:15:22', user: 'admin', details: 'Container #C001 added to inventory' },
        { id: 3, action: 'Data imported', timestamp: '2023-04-01T09:10:05', user: 'admin', details: 'Imported 15 items from CSV' },
        { id: 4, action: 'Item retrieved', timestamp: '2023-03-31T16:45:30', user: 'system', details: 'Item #B456 retrieved from Container #C002' },
        { id: 5, action: 'System startup', timestamp: '2023-03-31T08:00:00', user: 'system', details: 'System initialized' },
      ];
      
      setLogs(mockLogs);
      setLoading(false);
    }, 1000);
  }, []);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  return (
    <div className="logs-container">
      <h2>System Logs</h2>
      
      {loading ? (
        <div className="loading">Loading logs...</div>
      ) : (
        <div className="logs-table-container">
          <table className="logs-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>User</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{formatDate(log.timestamp)}</td>
                  <td>{log.action}</td>
                  <td>{log.user}</td>
                  <td>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Logs; 