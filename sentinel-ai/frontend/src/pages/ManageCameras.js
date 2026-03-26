import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

function ManageCameras() {
  const { user } = useAuth();
  const isAdmin = user?.role_name === 'admin';

  const [formData, setFormData] = useState({
    name: '',
    rtsp_url: '',
    location: '',
    status: 'offline',
    operator_id: '',
  });
  const [cameras, setCameras] = useState([]);
  const [isLoadingCameras, setIsLoadingCameras] = useState(false);
  const [isCreatingCamera, setIsCreatingCamera] = useState(false);
  const [editingCameraId, setEditingCameraId] = useState(null);
  const [editData, setEditData] = useState({
    name: '',
    rtsp_url: '',
    location: '',
    status: 'offline',
    operator_id: '',
  });
  const [cameraActionState, setCameraActionState] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadCameras = useCallback(async () => {
    if (!isAdmin) {
      return;
    }

    setIsLoadingCameras(true);
    setError('');

    try {
      const cameraList = await api.listCameras();
      setCameras(Array.isArray(cameraList) ? cameraList : []);
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to load cameras.';
      setError(errorMessage);
    } finally {
      setIsLoadingCameras(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    loadCameras();
  }, [loadCameras]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsCreatingCamera(true);
    setError('');
    setSuccess('');

    const payload = {
      name: formData.name.trim(),
      rtsp_url: formData.rtsp_url.trim(),
      location: formData.location.trim(),
      status: formData.status,
    };
    const operatorId = formData.operator_id.trim();
    if (operatorId) {
      payload.operator_id = operatorId;
    }

    try {
      const createdCamera = await api.adminCreateCamera(payload);
      setCameras((previous) => [createdCamera, ...previous]);
      setSuccess(`Camera "${createdCamera.name}" created successfully.`);
      setFormData({
        name: '',
        rtsp_url: '',
        location: '',
        status: 'offline',
        operator_id: '',
      });
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to create camera.';
      setError(errorMessage);
    } finally {
      setIsCreatingCamera(false);
    }
  };

  const startEditCamera = (camera) => {
    setError('');
    setSuccess('');
    setEditingCameraId(camera.id);
    setEditData({
      name: camera.name || '',
      rtsp_url: camera.rtsp_url || '',
      location: camera.location || '',
      status: camera.status || 'offline',
      operator_id: camera.operator_id || '',
    });
  };

  const cancelEditCamera = () => {
    setEditingCameraId(null);
    setEditData({
      name: '',
      rtsp_url: '',
      location: '',
      status: 'offline',
      operator_id: '',
    });
  };

  const handleEditChange = (event) => {
    const { name, value } = event.target;
    setEditData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleUpdateCamera = async (cameraId) => {
    setCameraActionState((previous) => ({
      ...previous,
      [cameraId]: 'updating',
    }));
    setError('');
    setSuccess('');

    const payload = {
      name: editData.name.trim(),
      rtsp_url: editData.rtsp_url.trim(),
      location: editData.location.trim(),
      status: editData.status,
      operator_id: editData.operator_id.trim() || null,
    };

    try {
      const updatedCamera = await api.adminUpdateCamera(cameraId, payload);
      setCameras((previous) =>
        previous.map((camera) => (camera.id === cameraId ? updatedCamera : camera))
      );
      setSuccess(`Camera "${updatedCamera.name}" updated successfully.`);
      cancelEditCamera();
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to update camera.';
      setError(errorMessage);
    } finally {
      setCameraActionState((previous) => ({
        ...previous,
        [cameraId]: 'idle',
      }));
    }
  };

  const handleDeleteCamera = async (camera) => {
    const shouldDelete = window.confirm(
      `Delete camera "${camera.name}"? This action cannot be undone.`
    );
    if (!shouldDelete) {
      return;
    }

    setCameraActionState((previous) => ({
      ...previous,
      [camera.id]: 'deleting',
    }));
    setError('');
    setSuccess('');

    try {
      await api.adminDeleteCamera(camera.id);
      setCameras((previous) => previous.filter((item) => item.id !== camera.id));
      if (editingCameraId === camera.id) {
        cancelEditCamera();
      }
      setSuccess(`Camera "${camera.name}" deleted successfully.`);
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Failed to delete camera.';
      setError(errorMessage);
    } finally {
      setCameraActionState((previous) => ({
        ...previous,
        [camera.id]: 'idle',
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
        <h1 className="page-title">Manage Cameras</h1>
        <p className="page-subtitle">
          Register and maintain surveillance cameras, connectivity, and operator assignment.
        </p>
      </header>

      {!isAdmin && (
        <section className="card">
          <h2>Access Restricted</h2>
          <p className="section-subtitle">
            Only administrators can create or manage cameras.
          </p>
        </section>
      )}

      {isAdmin && (
        <>
          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}

          <div className="dashboard-grid admin-grid">
            <section className="card">
              <h2>Create New Camera</h2>
              <p className="section-subtitle">
                Add camera metadata and stream source to make it available for monitoring.
              </p>
              <form className="auth-form" onSubmit={handleSubmit}>
                <label className="form-group" htmlFor="name">
                  <span>Camera Name</span>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    className="form-input"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    minLength={2}
                    maxLength={100}
                    disabled={isCreatingCamera}
                  />
                </label>

                <label className="form-group" htmlFor="rtsp_url">
                  <span>RTSP URL</span>
                  <input
                    id="rtsp_url"
                    name="rtsp_url"
                    type="text"
                    className="form-input"
                    placeholder="rtsp://localhost:8554/live.stream"
                    value={formData.rtsp_url}
                    onChange={handleChange}
                    required
                    minLength={10}
                    maxLength={500}
                    disabled={isCreatingCamera}
                  />
                </label>

                <label className="form-group" htmlFor="location">
                  <span>Location</span>
                  <input
                    id="location"
                    name="location"
                    type="text"
                    className="form-input"
                    value={formData.location}
                    onChange={handleChange}
                    required
                    minLength={2}
                    maxLength={255}
                    disabled={isCreatingCamera}
                  />
                </label>

                <label className="form-group" htmlFor="status">
                  <span>Status</span>
                  <select
                    id="status"
                    name="status"
                    className="form-input"
                    value={formData.status}
                    onChange={handleChange}
                    disabled={isCreatingCamera}
                  >
                    <option value="online">Online</option>
                    <option value="offline">Offline</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="error">Error</option>
                  </select>
                </label>

                <label className="form-group" htmlFor="operator_id">
                  <span>Operator ID (Optional)</span>
                  <input
                    id="operator_id"
                    name="operator_id"
                    type="text"
                    className="form-input"
                    placeholder="UUID from operators table"
                    value={formData.operator_id}
                    onChange={handleChange}
                    disabled={isCreatingCamera}
                  />
                </label>

                <button type="submit" className="btn" disabled={isCreatingCamera}>
                  {isCreatingCamera ? 'Creating...' : 'Create Camera'}
                </button>
              </form>
            </section>

            <section className="card">
              <h2>Registered Cameras</h2>
              <div className="section-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={loadCameras}
                  disabled={isLoadingCameras}
                >
                  {isLoadingCameras ? 'Refreshing...' : 'Refresh Cameras'}
                </button>
              </div>

              {isLoadingCameras && <p className="section-subtitle">Loading cameras...</p>}

              {!isLoadingCameras && cameras.length === 0 && (
                <p className="empty-state">No cameras found.</p>
              )}

              {!isLoadingCameras && cameras.length > 0 && (
                <ul className="cameras-list">
                  {cameras.map((camera) => (
                    <li key={camera.id}>
                      {editingCameraId === camera.id ? (
                        <div className="camera-edit-block">
                          <label className="form-group" htmlFor={`edit-name-${camera.id}`}>
                            <span>Camera Name</span>
                            <input
                              id={`edit-name-${camera.id}`}
                              name="name"
                              type="text"
                              className="form-input"
                              value={editData.name}
                              onChange={handleEditChange}
                              minLength={2}
                              maxLength={100}
                              required
                            />
                          </label>

                          <label className="form-group" htmlFor={`edit-rtsp-url-${camera.id}`}>
                            <span>RTSP URL</span>
                            <input
                              id={`edit-rtsp-url-${camera.id}`}
                              name="rtsp_url"
                              type="text"
                              className="form-input"
                              value={editData.rtsp_url}
                              onChange={handleEditChange}
                              minLength={10}
                              maxLength={500}
                              required
                            />
                          </label>

                          <label className="form-group" htmlFor={`edit-location-${camera.id}`}>
                            <span>Location</span>
                            <input
                              id={`edit-location-${camera.id}`}
                              name="location"
                              type="text"
                              className="form-input"
                              value={editData.location}
                              onChange={handleEditChange}
                              minLength={2}
                              maxLength={255}
                              required
                            />
                          </label>

                          <label className="form-group" htmlFor={`edit-status-${camera.id}`}>
                            <span>Status</span>
                            <select
                              id={`edit-status-${camera.id}`}
                              name="status"
                              className="form-input"
                              value={editData.status}
                              onChange={handleEditChange}
                            >
                              <option value="online">Online</option>
                              <option value="offline">Offline</option>
                              <option value="maintenance">Maintenance</option>
                              <option value="error">Error</option>
                            </select>
                          </label>

                          <label className="form-group" htmlFor={`edit-operator-id-${camera.id}`}>
                            <span>Operator ID (Optional)</span>
                            <input
                              id={`edit-operator-id-${camera.id}`}
                              name="operator_id"
                              type="text"
                              className="form-input"
                              value={editData.operator_id}
                              onChange={handleEditChange}
                              placeholder="Leave empty to unassign operator"
                            />
                          </label>

                          <div className="camera-item-actions">
                            <button
                              type="button"
                              className="btn"
                              onClick={() => handleUpdateCamera(camera.id)}
                              disabled={cameraActionState[camera.id] === 'updating'}
                            >
                              {cameraActionState[camera.id] === 'updating' ? 'Saving...' : 'Save'}
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              onClick={cancelEditCamera}
                              disabled={cameraActionState[camera.id] === 'updating'}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="camera-header-row">
                            <p className="entity-name">{camera.name}</p>
                            <span className={getStatusClassName(camera.status)}>
                              {String(camera.status || 'unknown').toUpperCase()}
                            </span>
                          </div>
                          <p>
                            <span>Location:</span> {camera.location}
                          </p>
                          <p>
                            <span>Operator ID:</span> {camera.operator_id || 'Unassigned'}
                          </p>
                          <div className="camera-item-actions">
                            <button type="button" className="btn btn-secondary" onClick={() => startEditCamera(camera)}>
                              Edit
                            </button>
                            <button
                              type="button"
                              className="btn btn-danger"
                              onClick={() => handleDeleteCamera(camera)}
                              disabled={cameraActionState[camera.id] === 'deleting'}
                            >
                              {cameraActionState[camera.id] === 'deleting' ? 'Deleting...' : 'Delete'}
                            </button>
                          </div>
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

export default ManageCameras;
