import React, { useCallback, useEffect, useState } from 'react';
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
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [users, setUsers] = useState([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editData, setEditData] = useState({
    username: '',
    password: '',
    role: 'operator',
    status: 'active',
  });
  const [userActionState, setUserActionState] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadUsers = useCallback(async () => {
    if (!isAdmin) {
      return;
    }

    setIsLoadingUsers(true);
    setError('');

    try {
      const userList = await api.adminListUsers();
      setUsers(Array.isArray(userList) ? userList : []);
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to load users.';
      setError(errorMessage);
    } finally {
      setIsLoadingUsers(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsCreatingUser(true);
    setError('');
    setSuccess('');

    try {
      const createdUser = await api.adminCreateUser(formData);
      setUsers((previous) => {
        const newUser = {
          id: createdUser.id,
          username: createdUser.username,
          role: createdUser.role,
          status: createdUser.status,
          profile_id: createdUser.profile_id,
        };
        const filtered = previous.filter((item) => item.id !== createdUser.id);
        return [newUser, ...filtered];
      });
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
      setIsCreatingUser(false);
    }
  };

  const startEditUser = (managedUser) => {
    setError('');
    setSuccess('');
    setEditingUserId(managedUser.id);
    setEditData({
      username: managedUser.username || '',
      password: '',
      role: managedUser.role || 'operator',
      status: managedUser.status || 'active',
    });
  };

  const cancelEditUser = () => {
    setEditingUserId(null);
    setEditData({
      username: '',
      password: '',
      role: 'operator',
      status: 'active',
    });
  };

  const handleEditChange = (event) => {
    const { name, value } = event.target;
    setEditData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleUpdateUser = async (userId) => {
    setUserActionState((previous) => ({
      ...previous,
      [userId]: 'updating',
    }));
    setError('');
    setSuccess('');

    const payload = {
      username: editData.username.trim(),
      role: editData.role,
      status: editData.status,
    };
    const password = editData.password.trim();
    if (password) {
      payload.password = password;
    }

    try {
      const updatedUser = await api.adminUpdateUser(userId, payload);
      setUsers((previous) =>
        previous.map((managedUser) =>
          managedUser.id === userId ? updatedUser : managedUser
        )
      );
      setSuccess(`User "${updatedUser.username}" updated successfully.`);
      cancelEditUser();
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to update user.';
      setError(errorMessage);
    } finally {
      setUserActionState((previous) => ({
        ...previous,
        [userId]: 'idle',
      }));
    }
  };

  const getStatusClassName = (statusValue) =>
    `status-chip status-${String(statusValue || 'unknown')
      .toLowerCase()
      .replace(/\s+/g, '-')}`;

  return (
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">Administration</p>
        <h1 className="page-title">Users Management</h1>
        <p className="page-subtitle">
          Create and manage operator and supervisor accounts with role-based status control.
        </p>
      </header>

      {!isAdmin && (
        <section className="card">
          <h2>Access Restricted</h2>
          <p className="section-subtitle">
            Only administrators can create or edit operator and supervisor accounts.
          </p>
        </section>
      )}

      {isAdmin && (
        <>
          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}

          <section className="summary-strip">
            <div className="summary-pill">
              <span className="summary-pill-label">Managed Users</span>
              <span className="summary-pill-value">{users.length}</span>
            </div>
            <div className="summary-pill">
              <span className="summary-pill-label">Active</span>
              <span className="summary-pill-value">
                {users.filter((managedUser) => managedUser.status === 'active').length}
              </span>
            </div>
            <div className="summary-pill">
              <span className="summary-pill-label">Supervisors</span>
              <span className="summary-pill-value">
                {users.filter((managedUser) => managedUser.role === 'supervisor').length}
              </span>
            </div>
          </section>

          <div className="dashboard-grid admin-grid">
            <section className="card">
              <h2>Create Operator / Supervisor</h2>
              <p className="section-subtitle">New accounts get immediate access based on selected role.</p>
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
                    disabled={isCreatingUser}
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
                    disabled={isCreatingUser}
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
                    disabled={isCreatingUser}
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
                    disabled={isCreatingUser}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </label>

                <button type="submit" className="btn" disabled={isCreatingUser}>
                  {isCreatingUser ? 'Creating...' : 'Create User'}
                </button>
              </form>
            </section>

            <section className="card">
              <h2>Managed Users</h2>
              <div className="section-actions">
                <button type="button" className="btn btn-secondary" onClick={loadUsers} disabled={isLoadingUsers}>
                  {isLoadingUsers ? 'Refreshing...' : 'Refresh Users'}
                </button>
              </div>

              {isLoadingUsers && <p className="section-subtitle">Loading users...</p>}

              {!isLoadingUsers && users.length === 0 && (
                <p className="empty-state">No operator or supervisor users found.</p>
              )}

              {!isLoadingUsers && users.length > 0 && (
                <ul className="users-list">
                  {users.map((managedUser) => (
                    <li key={managedUser.id}>
                      {editingUserId === managedUser.id ? (
                        <div className="user-edit-block">
                          <label className="form-group" htmlFor={`edit-username-${managedUser.id}`}>
                            <span>Username</span>
                            <input
                              id={`edit-username-${managedUser.id}`}
                              name="username"
                              type="text"
                              className="form-input"
                              value={editData.username}
                              onChange={handleEditChange}
                              minLength={3}
                              maxLength={100}
                              required
                            />
                          </label>

                          <label className="form-group" htmlFor={`edit-password-${managedUser.id}`}>
                            <span>New Password (Optional)</span>
                            <input
                              id={`edit-password-${managedUser.id}`}
                              name="password"
                              type="password"
                              className="form-input"
                              value={editData.password}
                              onChange={handleEditChange}
                              minLength={6}
                              placeholder="Leave empty to keep current password"
                            />
                          </label>

                          <label className="form-group" htmlFor={`edit-role-${managedUser.id}`}>
                            <span>Role</span>
                            <select
                              id={`edit-role-${managedUser.id}`}
                              name="role"
                              className="form-input"
                              value={editData.role}
                              onChange={handleEditChange}
                            >
                              <option value="operator">Operator</option>
                              <option value="supervisor">Supervisor</option>
                            </select>
                          </label>

                          <label className="form-group" htmlFor={`edit-status-${managedUser.id}`}>
                            <span>Status</span>
                            <select
                              id={`edit-status-${managedUser.id}`}
                              name="status"
                              className="form-input"
                              value={editData.status}
                              onChange={handleEditChange}
                            >
                              <option value="active">Active</option>
                              <option value="inactive">Inactive</option>
                              <option value="suspended">Suspended</option>
                            </select>
                          </label>

                          <div className="user-item-actions">
                            <button
                              type="button"
                              className="btn"
                              onClick={() => handleUpdateUser(managedUser.id)}
                              disabled={userActionState[managedUser.id] === 'updating'}
                            >
                              {userActionState[managedUser.id] === 'updating' ? 'Saving...' : 'Save'}
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              onClick={cancelEditUser}
                              disabled={userActionState[managedUser.id] === 'updating'}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="list-row-main">
                            <span className="entity-name">{managedUser.username}</span>
                            <div className="meta-chip-row">
                              <span className="meta-chip">{managedUser.role}</span>
                              <span className={getStatusClassName(managedUser.status)}>
                                {managedUser.status}
                              </span>
                            </div>
                          </div>
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => startEditUser(managedUser)}
                          >
                            Edit
                          </button>
                        </>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}

export default UsersManagement;
