import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children, allowedRoles = null, redirectTo = '/live-streams' }) {
  const { isAuthenticated, isInitializing, user } = useAuth();
  const location = useLocation();

  if (isInitializing) {
    return (
      <div className="auth-loading">
        <p>Checking your session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (
    Array.isArray(allowedRoles) &&
    allowedRoles.length > 0 &&
    !allowedRoles.includes(user?.role_name)
  ) {
    return <Navigate to={redirectTo} replace />;
  }

  if (children) {
    return children;
  }

  return <Outlet />;
}

export default ProtectedRoute;
