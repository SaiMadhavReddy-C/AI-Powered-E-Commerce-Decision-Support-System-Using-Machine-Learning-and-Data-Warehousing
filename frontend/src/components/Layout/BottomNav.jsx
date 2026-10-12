import React from 'react';
import { NavLink } from 'react-router-dom';
import './BottomNav.css';

const BottomNav = () => {
  return (
    <nav className="bottom-nav mobile-nav">
      <NavLink to="/" className={({ isActive }) => isActive ? 'bottom-nav-link active' : 'bottom-nav-link'} end>
        <span className="icon">🏠</span>
        <span className="label">Home</span>
      </NavLink>
      <NavLink to="/search" className={({ isActive }) => isActive ? 'bottom-nav-link active' : 'bottom-nav-link'}>
        <span className="icon">🔍</span>
        <span className="label">Search</span>
      </NavLink>
      <NavLink to="/watchlist" className={({ isActive }) => isActive ? 'bottom-nav-link active' : 'bottom-nav-link'}>
        <span className="icon">👀</span>
        <span className="label">Watchlist</span>
      </NavLink>
      <NavLink to="/alerts" className={({ isActive }) => isActive ? 'bottom-nav-link active' : 'bottom-nav-link'}>
        <span className="icon">🔔</span>
        <span className="label">Alerts</span>
      </NavLink>
    </nav>
  );
};

export default BottomNav;
