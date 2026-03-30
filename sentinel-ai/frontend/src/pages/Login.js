import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!username || !password) {
      setError('Please enter your username and password.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const signedInUser = await login(username, password);
      const requestedPath = location.state?.from?.pathname;
      const canOpenDashboard =
        signedInUser?.role_name === 'admin' || signedInUser?.role_name === 'supervisor';
      const defaultPath = canOpenDashboard ? '/dashboard' : '/live-streams';
      const nextPath =
        requestedPath === '/dashboard' && !canOpenDashboard
          ? '/live-streams'
          : requestedPath || defaultPath;

      navigate(nextPath, { replace: true });
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Unable to sign in. Please try again.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-shell">
        <section className="auth-brand-panel">
          <p className="auth-eyebrow">SentinelAI Security Operations</p>
          <h1>Secure Access Portal</h1>
          <p className="auth-brand-copy">
            Sign in to monitor cameras, detect threats, and keep your environment protected in
            real time.
          </p>
          <div className="auth-pill-list" aria-hidden="true">
            <span className="auth-pill">24/7 Monitoring</span>
            <span className="auth-pill">Role-Based Access</span>
            <span className="auth-pill">Real-Time Alerts</span>
          </div>
          <div className="auth-metric-grid" aria-hidden="true">
            <div className="auth-metric">
              <span className="auth-metric-value">99.9%</span>
              <span className="auth-metric-label">Availability</span>
            </div>
            <div className="auth-metric">
              <span className="auth-metric-value">&lt;5s</span>
              <span className="auth-metric-label">Alert Latency</span>
            </div>
            <div className="auth-metric">
              <span className="auth-metric-value">RBAC</span>
              <span className="auth-metric-label">Secure Access</span>
            </div>
          </div>
        </section>

        <section className="auth-card">
          <h2>Sign In</h2>
          <p className="auth-subtitle">
            Use your SentinelAI account to access dashboards, streams, and predictions.
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="form-group" htmlFor="username">
              <span>Username</span>
              <input
                id="username"
                type="text"
                className="form-input"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                disabled={isSubmitting}
              />
            </label>

            <label className="form-group" htmlFor="password">
              <span>Password</span>
              <input
                id="password"
                type="password"
                className="form-input"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={isSubmitting}
              />
            </label>

            {error && <div className="auth-error">{error}</div>}

            <button type="submit" className="btn auth-submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

export default Login;
