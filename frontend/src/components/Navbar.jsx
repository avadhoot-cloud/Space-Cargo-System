import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';
import { ThemeContext } from '../context/ThemeContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const location = useLocation();
  const { theme } = useContext(ThemeContext);
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🚀</span>
          <span className="logo-text">Space Cargo System</span>
        </Link>
        
        <div className="navbar-menu">
          <Link 
            to="/" 
            className={`navbar-item ${location.pathname === '/' ? 'active' : ''}`}
          >
            <span className="navbar-item-icon">📊</span>
            <span className="navbar-item-text">Dashboard</span>
          </Link>
          <Link 
            to="/upload" 
            className={`navbar-item ${location.pathname === '/upload' ? 'active' : ''}`}
          >
            <span className="navbar-item-icon">📤</span>
            <span className="navbar-item-text">Upload</span>
          </Link>
        </div>
        
        <div className="navbar-actions">
          <div className="theme-toggle-wrapper">
            <span className="theme-label">{theme === 'light' ? 'Light' : 'Dark'} Mode</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 