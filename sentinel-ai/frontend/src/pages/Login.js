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
      const defaultPath =
        signedInUser?.role_name === 'admin' ? '/dashboard' : '/live-streams';
      const nextPath =
        requestedPath === '/dashboard' && signedInUser?.role_name !== 'admin'
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
      <div className="auth-card">
        <h1>Sign In</h1>
        <p className="auth-subtitle">
          Use your SentinelAI account to access the dashboard and predictions.
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

          <button type="submit" className="btn" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
