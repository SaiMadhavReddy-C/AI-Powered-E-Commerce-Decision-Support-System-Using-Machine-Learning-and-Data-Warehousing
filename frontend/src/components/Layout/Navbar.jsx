import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar" style={{ backgroundColor: 'var(--bg, #FAF8F5)' }}>
      <div className="navbar-container container">
        <NavLink to="/" className="navbar-logo">
          Shop<span className="navbar-logo-highlight">Q</span>
        </NavLink>
        <div className="navbar-links">
          {/* Desktop-only links (handled by BottomNav on mobile screens) */}
          <div className="desktop-nav" style={{ alignItems: 'center', gap: '24px' }}>
            <NavLink to="/search" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              Search
            </NavLink>
            <NavLink to="/watchlist" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              Watchlist
            </NavLink>
            <NavLink to="/alerts" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              Alerts
            </NavLink>
          </div>
          <NavLink to="/how-it-works" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            How It Works
          </NavLink>
          <NavLink
            to="/preferences"
            className={({ isActive }) => (isActive ? 'user-avatar-link active' : 'user-avatar-link')}
            title="User Preferences"
            aria-label="User Preferences"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}
          >
            {({ isActive }) => (
              <div
                className="user-icon-placeholder"
                style={{
                  outline: isActive ? '2px solid var(--accent)' : 'none',
                  outlineOffset: '2px',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                }}
              >
                <span className="user-initial">U</span>
              </div>
            )}
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

