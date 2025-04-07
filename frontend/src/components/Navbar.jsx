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

  const navItems = [
    { path: "/", icon: "📊", text: "Dashboard" },
    { path: "/placement", icon: "📍", text: "Placement" },
    { path: "/search", icon: "🔍", text: "Search" },
    { path: "/upload", icon: "📤", text: "Upload" },
    { path: "/rearrangement", icon: "🔄", text: "Rearrangement" },
    { path: "/waste", icon: "♻️", text: "Waste" },
    { path: "/simulation", icon: "⏱️", text: "Simulation" },
    { path: "/logs", icon: "📝", text: "Logs" }
  ];
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🚀</span>
          <span className="logo-text">Space Cargo System</span>
        </Link>
        
        <div className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          {navItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={`navbar-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="navbar-item-icon">{item.icon}</span>
              <span className="navbar-item-text">{item.text}</span>
            </Link>
          ))}
        </div>
        
        <div className="navbar-actions">
          <div className="theme-toggle-wrapper">
            <ThemeToggle />
          </div>
          <button 
            className="mobile-menu-toggle" 
            onClick={toggleMobileMenu}
            aria-label="Toggle menu"
          >
            <span className={`menu-icon ${mobileMenuOpen ? 'open' : ''}`}></span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 