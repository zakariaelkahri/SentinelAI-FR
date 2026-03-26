import React, { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../services/api';

const THREAT_POLL_INTERVAL_MS = 5000;

function LiveStreams() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [streamNonces, setStreamNonces] = useState({});
  const [streamStatuses, setStreamStatuses] = useState({});
  const [streamErrors, setStreamErrors] = useState({});
  const [threatAlerts, setThreatAlerts] = useState({});
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

  useEffect(() => {
    if (activeCameras.length === 0) {
      setThreatAlerts({});
      return;
    }

    let isMounted = true;

    const refreshThreatAlerts = async () => {
      const alertEntries = await Promise.all(
        activeCameras.map(async (camera) => {
          try {
            const threatAlert = await api.getCameraThreatAlert(camera.id);
            return [camera.id, threatAlert];
          } catch (requestError) {
            return [
              camera.id,
              {
                camera_id: camera.id,
                detected: false,
              },
            ];
          }
        })
      );

      if (!isMounted) {
        return;
      }

      setThreatAlerts(Object.fromEntries(alertEntries));
    };

    refreshThreatAlerts();
    const intervalId = setInterval(refreshThreatAlerts, THREAT_POLL_INTERVAL_MS);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [activeCameras]);

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
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">Real-Time Monitoring</p>
        <h1 className="page-title">Live Streaming</h1>
        <p className="page-subtitle">
          View active camera feeds with automatic reconnect for resilient monitoring.
        </p>
      </header>

      <section className="card card-overview">
        <h2>Camera Overview</h2>
        {error && <div className="auth-error">{error}</div>}

        {!error && cameras.length === 0 && (
          <p className="empty-state">No cameras found in the database.</p>
        )}

        {cameras.length > 0 && (
          <p className="info-text">
            Showing <strong>{activeCameras.length}</strong> active camera(s) out of{' '}
            <strong>{cameras.length}</strong>.
          </p>
        )}

        {cameras.length > 0 && activeCameras.length === 0 && (
          <p className="section-subtitle">
            No active cameras detected. Set camera status to ONLINE to display streams.
          </p>
        )}
      </section>

      {activeCameras.length > 0 && (
        <div className="stream-grid">
          {activeCameras.map((camera) => {
            const streamStatus = streamStatuses[camera.id] || 'connecting';
            const streamError = streamErrors[camera.id] || '';
            const threatAlert = threatAlerts[camera.id];
            const hasThreatAlert = Boolean(threatAlert?.detected);
            const threatLabel = threatAlert?.label || 'unknown';
            const threatConfidence = Number(threatAlert?.confidence_score || 0);
            const threatTimestamp = threatAlert?.timestamp
              ? new Date(threatAlert.timestamp).toLocaleTimeString()
              : null;
            const yoloStreamUrl = api.getCameraMjpegStreamUrl(
              camera.id,
              'yolo',
              streamNonces[camera.id]
            );

            return (
              <section
                className={`card stream-panel${hasThreatAlert ? ' stream-panel-alert' : ''}`}
                key={camera.id}
              >
                <h2>{camera.name}</h2>
                <div className="camera-meta stream-meta">
                  <span>
                    <strong>Location:</strong> {camera.location}
                  </span>
                  <span>
                    <strong>Status:</strong> {String(camera.status).toUpperCase()}
                  </span>
                </div>
                <div className="stream-toolbar">
                  <span className={`stream-status stream-status-${streamStatus}`}>
                    {streamStatus === 'live'
                      ? 'Live'
                      : streamStatus === 'connecting'
                        ? 'Connecting...'
                        : 'Reconnecting...'}
                  </span>
                  <button
                    type="button"
                    className="btn btn-secondary"
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
                {hasThreatAlert && (
                  <div className="stream-threat-alert" role="alert">
                    <p className="stream-threat-title">
                      Threat Detected: {String(threatLabel).toUpperCase()}
                    </p>
                    <p className="stream-threat-details">
                      Confidence: {(threatConfidence * 100).toFixed(1)}%
                      {threatTimestamp ? ` | Time: ${threatTimestamp}` : ''}
                    </p>
                  </div>
                )}
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
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default LiveStreams;
