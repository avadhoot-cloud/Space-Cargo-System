import React from 'react';
import Toggle from 'react-toggle';
import 'react-toggle/style.css';
import '../styles/ThemeToggle.css';

const ThemeToggle = ({ theme, toggleTheme }) => {
  const isDark = theme === 'dark';

  return (
    <div className="theme-toggle">
      <Toggle
        id="theme-toggle-checkbox"
        className="custom-toggle"
        checked={isDark}
        onChange={toggleTheme}
        icons={{
          checked: <span className="toggle-icon moon">🌙</span>,
          unchecked: <span className="toggle-icon sun">☀️</span>,
        }}
        aria-label="Toggle dark mode"
      />
    </div>
  );
};

export default ThemeToggle; 