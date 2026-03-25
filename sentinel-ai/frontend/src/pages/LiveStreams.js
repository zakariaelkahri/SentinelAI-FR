import React, { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../services/api';

function LiveStreams() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [streamNonces, setStreamNonces] = useState({});
  const [streamStatuses, setStreamStatuses] = useState({});
  const [streamErrors, setStreamErrors] = useState({});
  const reconnectTimeoutsRef = useRef({});

  useEffect(() => {
    const loadCameras = async () => {
      try {
        const cameraList = await api.listCameras();
        setCameras(cameraList);
      } catch (requestError) {
        const errorMessage =
          requestError?.response?.data?.detail ||
          requestError?.message ||
          'Failed to load camera list.';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    loadCameras();
  }, []);

  const activeCameras = useMemo(
    () =>
      cameras.filter((camera) =>
        ['online', 'active'].includes(String(camera.status || '').toLowerCase())
      ),
    [cameras]
  );

  useEffect(() => {
    const activeIds = activeCameras.map((camera) => camera.id);
    const activeIdSet = new Set(activeIds);

    setStreamNonces((previous) => {
      const next = {};
      activeIds.forEach((id) => {
        next[id] = previous[id] || Date.now();
      });
      return next;
    });

    setStreamStatuses((previous) => {
      const next = {};
      activeIds.forEach((id) => {
        next[id] = previous[id] || 'connecting';
      });
      return next;
    });

    setStreamErrors((previous) => {
      const next = {};
      activeIds.forEach((id) => {
        next[id] = previous[id] || '';
      });
      return next;
    });

    Object.keys(reconnectTimeoutsRef.current).forEach((cameraId) => {
      if (!activeIdSet.has(cameraId)) {
        clearTimeout(reconnectTimeoutsRef.current[cameraId]);
        delete reconnectTimeoutsRef.current[cameraId];
      }
    });
  }, [activeCameras]);

  useEffect(() => {
    return () => {
      Object.values(reconnectTimeoutsRef.current).forEach((timeoutId) => {
        clearTimeout(timeoutId);
      });
      reconnectTimeoutsRef.current = {};
    };
  }, []);

  const requestReconnect = (cameraId, delayMs = 1500) => {
    if (reconnectTimeoutsRef.current[cameraId]) {
      clearTimeout(reconnectTimeoutsRef.current[cameraId]);
    }

    reconnectTimeoutsRef.current[cameraId] = setTimeout(() => {
      setStreamNonces((previous) => ({
        ...previous,
        [cameraId]: Date.now(),
      }));
      setStreamStatuses((previous) => ({
        ...previous,
        [cameraId]: 'reconnecting',
      }));
    }, delayMs);
  };

  if (loading) {
    return (
      <div className="auth-loading">
        <p>Loading live stream cameras...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Live Streaming</h1>

      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h2>Camera Overview</h2>
        {error && <div className="auth-error">{error}</div>}

        {!error && cameras.length === 0 && (
          <p style={{ color: '#6b7280' }}>No cameras found in database.</p>
        )}

        {cameras.length > 0 && (
          <p style={{ color: '#374151' }}>
            Showing {activeCameras.length} active camera(s) out of {cameras.length}.
          </p>
        )}

        {cameras.length > 0 && activeCameras.length === 0 && (
          <p style={{ color: '#6b7280', marginTop: '0.75rem' }}>
            No active cameras detected. Set camera status to ONLINE to display streams.
          </p>
        )}
      </div>

      {activeCameras.length > 0 && (
        <div className="stream-grid">
          {activeCameras.map((camera) => {
            const streamStatus = streamStatuses[camera.id] || 'connecting';
            const streamError = streamErrors[camera.id] || '';
            const yoloStreamUrl = api.getCameraMjpegStreamUrl(
              camera.id,
              'yolo',
              streamNonces[camera.id]
            );

            return (
              <div className="card stream-panel" key={camera.id}>
                <h2>{camera.name}</h2>
                <div className="camera-meta" style={{ marginBottom: '0.75rem' }}>
                  <span>
                    <strong>Location:</strong> {camera.location}
                  </span>
                  <span>
                    <strong>Status:</strong> {String(camera.status).toUpperCase()}
                  </span>
                </div>
                <div className="stream-toolbar">
                  <span className={`stream-status stream-status-${streamStatus}`}>
                    {streamStatus === 'live' ? 'Live' : 'Reconnecting...'}
                  </span>
                  <button
                    type="button"
                    className="btn"
                    onClick={() => {
                      setStreamStatuses((previous) => ({
                        ...previous,
                        [camera.id]: 'reconnecting',
                      }));
                      requestReconnect(camera.id, 0);
                    }}
                  >
                    Reconnect
                  </button>
                </div>
                {streamError && <div className="auth-error">{streamError}</div>}
                <img
                  key={`${camera.id}-${streamNonces[camera.id] || 'init'}`}
                  src={yoloStreamUrl}
                  alt={`${camera.name} YOLO stream`}
                  className="stream-frame"
                  onLoad={() => {
                    setStreamStatuses((previous) => ({
                      ...previous,
                      [camera.id]: 'live',
                    }));
                    setStreamErrors((previous) => ({
                      ...previous,
                      [camera.id]: '',
                    }));
                  }}
                  onError={() => {
                    setStreamStatuses((previous) => ({
                      ...previous,
                      [camera.id]: 'reconnecting',
                    }));
                    setStreamErrors((previous) => ({
                      ...previous,
                      [camera.id]: 'Stream interrupted. Reconnecting...',
                    }));
                    requestReconnect(camera.id);
                  }}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default LiveStreams;
