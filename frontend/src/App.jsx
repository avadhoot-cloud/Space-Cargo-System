import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import Toggle from 'react-toggle';
import "react-toggle/style.css";
import './styles/App.css';
import './styles/themes.css';

// Import pages
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Logs from './pages/Logs';

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

// Create placeholders for the new pages
const PlacementRecommendations = () => (
  <div className="placeholder-page">
    <h1>Placement Recommendations</h1>
    <p>This page will provide automatic suggestions for where to place items based on available space and priority.</p>
    <div className="feature-cards">
      <div className="feature-card">
        <h3>Priority-Based Placement</h3>
        <p>Automatically suggest optimal placement locations based on item priority and available space.</p>
      </div>
      <div className="feature-card">
        <h3>Space Optimization</h3>
        <p>If space is insufficient, recommend rearranging existing items to make room.</p>
      </div>
      <div className="feature-card">
        <h3>Accessibility Focus</h3>
        <p>Ensure high-priority items remain easily accessible and in preferred zones.</p>
      </div>
    </div>
  </div>
);

const ItemSearch = () => (
  <div className="placeholder-page">
    <h1>Item Search & Retrieval</h1>
    <p>Find items quickly and get optimized retrieval instructions.</p>
    <div className="feature-cards">
      <div className="feature-card">
        <h3>Precise Location</h3>
        <p>Suggest the exact module and position of the requested item.</p>
      </div>
      <div className="feature-card">
        <h3>Smart Selection</h3>
        <p>Choose items based on ease of retrieval and closeness to expiry date.</p>
      </div>
      <div className="feature-card">
        <h3>Retrieval Logging</h3>
        <p>Log retrieval actions including who retrieved the item, when, and from where.</p>
      </div>
    </div>
  </div>
);

const Rearrangement = () => (
  <div className="placeholder-page">
    <h1>Rearrangement Recommendations</h1>
    <p>Get smart suggestions for reorganizing cargo to maximize space efficiency.</p>
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

const WasteManagement = () => (
  <div className="placeholder-page">
    <h1>Waste Management & Return Planning</h1>
    <p>Track expired items and plan for waste disposal during undocking operations.</p>
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

const TimeSimulation = () => (
  <div className="placeholder-page">
    <h1>Time Simulation</h1>
    <p>Simulate the passage of time to forecast inventory status and plan missions.</p>
    <div className="feature-cards">
      <div className="feature-card">
        <h3>Next Day Simulation</h3>
        <p>Simulate one day of operations with configurable item usage.</p>
        <button className="sim-button">Simulate Next Day</button>
      </div>
      <div className="feature-card">
        <h3>Fast Forward</h3>
        <p>Simulate multiple days at once to see longer-term effects.</p>
        <div className="sim-control">
          <input type="number" min="1" max="90" defaultValue="7" className="sim-input" />
          <button className="sim-button">Fast Forward</button>
        </div>
      </div>
      <div className="feature-card">
        <h3>Mission Planning</h3>
        <p>Use time simulation to help with future mission planning and resource allocation.</p>
      </div>
    </div>
  </div>
);

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleThemeChange = (e) => {
    setTheme(e.target.checked ? 'dark' : 'light');
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
            </ul>
          </nav>
          <div className="app-controls">
            <label className="theme-toggle-wrapper">
              <Toggle
                checked={theme === 'dark'}
                onChange={handleThemeChange}
                icons={{
                  checked: <span aria-hidden>🌙</span>,
                  unchecked: <span aria-hidden>☀️</span>,
                }}
                aria-label="Dark mode toggle"
                className="custom-toggle"
              />
              <span className="sr-only">Toggle theme</span>
            </label>
            <button 
              className="mobile-toggle" 
              onClick={toggleMobileMenu}
              style={{ display: 'none' }}
            >
              ☰
            </button>
          </div>
        </header>
        
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/placement" element={<PlacementRecommendations />} />
            <Route path="/search" element={<ItemSearch />} />
            <Route path="/rearrangement" element={<Rearrangement />} />
            <Route path="/waste" element={<WasteManagement />} />
            <Route path="/simulation" element={<TimeSimulation />} />
          </Routes>
        </main>
        
        <footer className="app-footer">
          <p>Space Cargo System &copy; {new Date().getFullYear()}</p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 