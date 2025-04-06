import React, { useContext, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';
import { ThemeContext } from '../context/ThemeContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const location = useLocation();
  const { theme } = useContext(ThemeContext);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🚀</span>
          <span className="logo-text">Space Cargo System</span>
        </Link>
        
        <div className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <Link 
            to="/" 
            className={`navbar-item ${location.pathname === '/' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">📊</span>
            <span className="navbar-item-text">Dashboard</span>
          </Link>
          
          <Link 
            to="/placement" 
            className={`navbar-item ${location.pathname === '/placement' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">📍</span>
            <span className="navbar-item-text">Placement</span>
          </Link>
          
          <Link 
            to="/search" 
            className={`navbar-item ${location.pathname === '/search' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">🔍</span>
            <span className="navbar-item-text">Search</span>
          </Link>
          
          <Link 
            to="/upload" 
            className={`navbar-item ${location.pathname === '/upload' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">📤</span>
            <span className="navbar-item-text">Upload</span>
          </Link>
          
          <Link 
            to="/rearrangement" 
            className={`navbar-item ${location.pathname === '/rearrangement' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">🔄</span>
            <span className="navbar-item-text">Rearrangement</span>
          </Link>
          
          <Link 
            to="/waste" 
            className={`navbar-item ${location.pathname === '/waste' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">♻️</span>
            <span className="navbar-item-text">Waste</span>
          </Link>
          
          <Link 
            to="/simulation" 
            className={`navbar-item ${location.pathname === '/simulation' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">⏱️</span>
            <span className="navbar-item-text">Simulation</span>
          </Link>
          
          <Link 
            to="/logs" 
            className={`navbar-item ${location.pathname === '/logs' ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="navbar-item-icon">📝</span>
            <span className="navbar-item-text">Logs</span>
          </Link>
        </div>
        
        <div className="navbar-actions">
          <div className="theme-toggle-wrapper">
            <span className="theme-label">{theme === 'light' ? 'Light' : 'Dark'} Mode</span>
            <ThemeToggle />
          </div>
          <button className="mobile-menu-toggle" onClick={toggleMobileMenu}>
            <span className={`menu-icon ${mobileMenuOpen ? 'open' : ''}`}></span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 