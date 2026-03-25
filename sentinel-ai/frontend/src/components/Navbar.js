import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, isAuthenticated, isInitializing, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  if (isInitializing || !isAuthenticated) {
    return null;
  }

  const isAdmin = user?.role_name === 'admin';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>
          <Link className="sidebar-brand" to="/dashboard">
            SentinelAI
          </Link>
        </h1>
        <p className="sidebar-subtitle">Security Operations</p>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-section-title">Monitoring</p>
        <NavLink
          className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          to="/dashboard"
        >
          Dashboard Statistics
        </NavLink>
        <NavLink
          className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          to="/live-streams"
        >
          Live Streams
        </NavLink>
        <NavLink
          className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          to="/predictions"
        >
          Predictions
        </NavLink>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-section-title">Administration</p>
        {isAdmin ? (
          <>
            <NavLink
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              to="/users-management"
            >
              Users Management
            </NavLink>
            <NavLink
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              to="/manage-cameras"
            >
              Manage Cameras
            </NavLink>
          </>
        ) : (
          <>
            <div className="sidebar-link disabled">Users Management</div>
            <div className="sidebar-link disabled">Manage Cameras</div>
          </>
        )}
        <NavLink
          className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          to="/params"
        >
          Params
        </NavLink>
      </div>

      <div className="sidebar-footer">
        <p className="sidebar-user">
          {user?.username}
          {user?.role_name ? ` (${user.role_name})` : ''}
        </p>
        <button type="button" className="btn btn-sidebar" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Navbar;
