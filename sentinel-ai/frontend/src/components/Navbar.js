import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar({ isSidebarOpen, onToggleSidebar }) {
  const { user, isAuthenticated, isInitializing, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  if (isInitializing || !isAuthenticated) {
    return null;
  }

  const isAdmin = user?.role_name === 'admin';
  const isSupervisor = user?.role_name === 'supervisor';
  const isOperator = user?.role_name === 'operator';
  const canViewDashboard = isAdmin || isSupervisor;
  const canUseAssistant = isOperator || isSupervisor;
  const canManageCameras = isAdmin || isSupervisor;
  const brandHomePath = canViewDashboard ? '/dashboard' : '/live-streams';

  if (!isSidebarOpen) {
    return (
      <button
        type="button"
        className="sidebar-toggle-floating"
        onClick={onToggleSidebar}
      >
        Menu
      </button>
    );
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div>
          <h1>
            <Link className="sidebar-brand" to={brandHomePath}>
              SentinelAI
            </Link>
          </h1>
          <p className="sidebar-subtitle">Security Operations</p>
          {user?.role_name && <span className="sidebar-role-chip">{user.role_name}</span>}
        </div>
        <button
          type="button"
          className="sidebar-toggle-btn"
          onClick={onToggleSidebar}
        >
          Hide
        </button>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-section-title">Monitoring</p>
        {canViewDashboard ? (
          <NavLink
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
            to="/dashboard"
          >
            Dashboard Statistics
          </NavLink>
        ) : (
          <div className="sidebar-link disabled">Dashboard Statistics</div>
        )}
        <NavLink
          className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          to="/live-streams"
        >
          Live Streams
        </NavLink>
        {canUseAssistant ? (
          <NavLink
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
            to="/assistant"
          >
            Security Assistant
          </NavLink>
        ) : (
          <div className="sidebar-link disabled">Security Assistant</div>
        )}
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
          </>
        ) : (
          <div className="sidebar-link disabled">Users Management</div>
        )}

        {canManageCameras ? (
          <>
            <NavLink
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              to="/manage-cameras"
            >
              Manage Cameras
            </NavLink>
          </>
        ) : (
          <div className="sidebar-link disabled">Manage Cameras</div>
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
