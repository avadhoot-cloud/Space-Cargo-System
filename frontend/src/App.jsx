import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './styles/App.css';

// Import pages
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Logs from './pages/Logs';

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>Space Cargo System</h1>
          <nav>
            <ul>
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/upload">Upload</Link></li>
              <li><Link to="/logs">Logs</Link></li>
            </ul>
          </nav>
        </header>
        
        <main className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </main>
        
        <footer className="app-footer">
          <p>Space Cargo System &copy; 2023</p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 