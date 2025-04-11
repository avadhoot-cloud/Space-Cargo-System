import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import ThemeToggle from './components/ThemeToggle';
import './styles/App.css';
import './styles/themes.css';

// Import pages
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Logs from './pages/Logs';
import Placement from './pages/Placement';
import ItemSearch from './pages/ItemSearch';
import Rearrangement from './pages/Rearrangement';
import WasteManagement from './pages/WasteManagement';
import TimeSimulation from './pages/TimeSimulation';
import PlacementTester from './Placement_Tester';
// Star field background component
const StarField = () => {
  const stars = useMemo(() => {
    // Generate random stars
    const starCount = 150;
    const generatedStars = [];
    
    for (let i = 0; i < starCount; i++) {
      const size = Math.random() * 2;
      generatedStars.push({
        id: i,
        size: size,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 10}s`,
        animationDuration: `${4 + Math.random() * 6}s`
      });
    }
    
    return generatedStars;
  }, []);
  
  const particles = useMemo(() => {
    // Generate floating particles
    const particleCount = 25;
    const generatedParticles = [];
    
    for (let i = 0; i < particleCount; i++) {
      const size = 3 + Math.random() * 8;
      generatedParticles.push({
        id: i,
        size: size,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 15}s`,
        animationDuration: `${15 + Math.random() * 15}s`
      });
    }
    
    return generatedParticles;
  }, []);
  
  return (
    <>
      <div className="star-field">
        {stars.map(star => (
          <div
            key={star.id}
            className="star"
            style={{
              width: `${star.size}px`,
              height: `${star.size}px`,
              left: star.left,
              top: star.top,
              animationDelay: star.animationDelay,
              animationDuration: star.animationDuration
            }}
          />
        ))}
      </div>
      <div className="particle-field">
        {particles.map(particle => (
          <div
            key={particle.id}
            className="particle"
            style={{
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              left: particle.left,
              top: particle.top,
              animationDelay: particle.animationDelay,
              animationDuration: particle.animationDuration
            }}
          />
        ))}
      </div>
    </>
  );
};

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <Router>
      <div className="app">
        <StarField />
        <header className="app-header">
          <div className="app-logo">
            <span>🚀 Space Cargo System</span>
          </div>
          <nav className={mobileMenuOpen ? 'active' : ''}>
            <ul>
              <li><NavLink to="/" end>Dashboard</NavLink></li>
              <li><NavLink to="/upload">Upload</NavLink></li>
              <li><NavLink to="/placement">Placement</NavLink></li>
              <li><NavLink to="/search">Item Search</NavLink></li>
              <li><NavLink to="/rearrangement">Rearrangement</NavLink></li>
              <li><NavLink to="/waste">Waste Management</NavLink></li>
              <li><NavLink to="/simulation">Time Simulation</NavLink></li>
              <li><NavLink to="/logs">Logs</NavLink></li>
              <li><NavLink to="/placement-tester">Placement Tester</NavLink></li>
            </ul>
          </nav>
          <div className="actions">
            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
            <button 
              className="mobile-menu-toggle" 
              onClick={toggleMobileMenu}
              aria-label="Toggle menu"
            >
              <span className={`menu-icon ${mobileMenuOpen ? 'open' : ''}`}></span>
            </button>
          </div>
        </header>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/placement" element={<Placement />} />
            <Route path="/search" element={<ItemSearch />} />
            <Route path="/rearrangement" element={<Rearrangement />} />
            <Route path="/waste" element={<WasteManagement />} />
            <Route path="/simulation" element={<TimeSimulation />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/placement-tester" element={<PlacementTester />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <p>&copy; 2025 Space Cargo System | <a href="#">Documentation</a> | <a href="#">Support</a></p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 