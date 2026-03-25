import React, { useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

function UsersManagement() {
  const { user } = useAuth();
  const isAdmin = user?.role_name === 'admin';

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'operator',
    status: 'active',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [createdUsers, setCreatedUsers] = useState([]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const createdUser = await api.adminCreateUser(formData);
      setCreatedUsers((previous) => [createdUser, ...previous].slice(0, 8));
      setSuccess(`User "${createdUser.username}" created successfully.`);
      setFormData((previous) => ({
        ...previous,
        username: '',
        password: '',
      }));
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to create user.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Users Management</h1>

      {!isAdmin && (
        <div className="card">
          <h2>Access Restricted</h2>
          <p style={{ color: '#6b7280' }}>
            Only administrators can create operator or supervisor accounts.
          </p>
        </div>
      )}

      {isAdmin && (
        <div className="dashboard-grid">
          <div className="card">
            <h2>Create Operator / Supervisor</h2>
            <form className="auth-form" onSubmit={handleSubmit}>
              <label className="form-group" htmlFor="username">
                <span>Username</span>
                <input
                  id="username"
                  name="username"
                  type="text"
                  className="form-input"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  minLength={3}
                  maxLength={100}
                  disabled={loading}
                />
              </label>

              <label className="form-group" htmlFor="password">
                <span>Password</span>
                <input
                  id="password"
                  name="password"
                  type="password"
                  className="form-input"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength={6}
                  disabled={loading}
                />
              </label>

              <label className="form-group" htmlFor="role">
                <span>Role</span>
                <select
                  id="role"
                  name="role"
                  className="form-input"
                  value={formData.role}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="operator">Operator</option>
                  <option value="supervisor">Supervisor</option>
                </select>
              </label>

              <label className="form-group" htmlFor="status">
                <span>Status</span>
                <select
                  id="status"
                  name="status"
                  className="form-input"
                  value={formData.status}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </label>

              {error && <div className="auth-error">{error}</div>}
              {success && <div className="auth-success">{success}</div>}

              <button type="submit" className="btn" disabled={loading}>
                {loading ? 'Creating...' : 'Create User'}
              </button>
            </form>
          </div>

          <div className="card">
            <h2>Recent Created Accounts</h2>
            {createdUsers.length === 0 ? (
              <p style={{ color: '#6b7280' }}>
                No new accounts created in this session.
              </p>
            ) : (
              <ul className="users-list">
                {createdUsers.map((createdUser) => (
                  <li key={createdUser.id}>
                    <span>{createdUser.username}</span>
                    <span>{createdUser.role}</span>
                    <span>{createdUser.status}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default UsersManagement;
