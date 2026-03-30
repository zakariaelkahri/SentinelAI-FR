import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';

function Dashboard() {
  const [health, setHealth] = useState(null);
  const [models, setModels] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await api.checkHealth();
        setHealth(healthRes);

        const modelsRes = await api.listModels();
        setModels(modelsRes);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const mockMetrics = [
    { time: '00:00', requests: 120, latency: 45 },
    { time: '04:00', requests: 80, latency: 42 },
    { time: '08:00', requests: 200, latency: 50 },
    { time: '12:00', requests: 350, latency: 55 },
    { time: '16:00', requests: 280, latency: 48 },
    { time: '20:00', requests: 180, latency: 44 },
  ];

  const totalRequests = mockMetrics.reduce((sum, point) => sum + point.requests, 0);
  const averageLatency =
    mockMetrics.reduce((sum, point) => sum + point.latency, 0) / mockMetrics.length;
  const peakRequests = Math.max(...mockMetrics.map((point) => point.requests));
  const healthStatus = String(health?.status || '').toLowerCase();
  const isHealthy = healthStatus === 'healthy';

  return (
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">Control Center</p>
        <h1 className="page-title">Dashboard Statistics</h1>
        <p className="page-subtitle">
          Track platform health, model registry, and system activity from one operations view.
        </p>
        <div className="chip-link-row">
          <a className="chip-link" href="http://localhost:3000" target="_blank" rel="noopener noreferrer">
            Grafana
          </a>
          <a className="chip-link" href="http://localhost:9090" target="_blank" rel="noopener noreferrer">
            Prometheus
          </a>
          <a className="chip-link" href="http://localhost:5000" target="_blank" rel="noopener noreferrer">
            MLflow
          </a>
        </div>
      </header>

      <section className="kpi-grid">
        <article className="kpi-card">
          <p className="kpi-label">Requests (24h)</p>
          <p className="kpi-value">{totalRequests.toLocaleString()}</p>
          <p className="kpi-meta">Peak per interval: {peakRequests}</p>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">Average Latency</p>
          <p className="kpi-value">{averageLatency.toFixed(1)} ms</p>
          <p className="kpi-meta">Mocked trend data window</p>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">Registered Models</p>
          <p className="kpi-value">{models.length}</p>
          <p className="kpi-meta">{models.length > 0 ? 'Model catalog is available' : 'No models yet'}</p>
        </article>
        <article className="kpi-card">
          <p className="kpi-label">API Health</p>
          <p className="kpi-value">{health?.status || 'Checking...'}</p>
          <span className={`status-chip ${isHealthy ? 'status-healthy' : 'status-unhealthy'}`}>
            {isHealthy ? 'Healthy' : 'Needs Attention'}
          </span>
        </article>
      </section>

      <div className="dashboard-grid">
        <section className="card metric-card">
          <h2>API Status</h2>
          <div className="status-indicator">
            <span className={`status-dot ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
            <span className="status-text">{health?.status || 'Checking...'}</span>
          </div>
          {health?.timestamp && (
            <p className="muted-text">
              Last check: {new Date(health.timestamp).toLocaleTimeString()}
            </p>
          )}
        </section>

        <section className="card metric-card">
          <h2>Registered Models</h2>
          {models.length > 0 ? (
            <ul className="resource-list">
              {models.map((model, idx) => (
                <li key={idx}>
                  <span className="resource-name">{model.name}</span>
                  <span className="meta-chip">v{model.latest_version || 'N/A'}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">No models registered.</p>
          )}
        </section>

        <section className="card metric-card">
          <h2>Quick Links</h2>
          <div className="quick-links">
            <a className="endpoint-link" href="http://localhost:5000" target="_blank" rel="noopener noreferrer">
              MLflow UI
            </a>
            <a className="endpoint-link" href="http://localhost:8080" target="_blank" rel="noopener noreferrer">
              Airflow UI
            </a>
            <a className="endpoint-link" href="http://localhost:3001" target="_blank" rel="noopener noreferrer">
              Grafana
            </a>
            <a className="endpoint-link" href="http://localhost:9090" target="_blank" rel="noopener noreferrer">
              Prometheus
            </a>
          </div>
        </section>

        <section className="card card-span-two">
          <h2>Request Metrics (24h)</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={mockMetrics} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#c8d7e2" />
              <XAxis dataKey="time" stroke="#345164" />
              <YAxis yAxisId="left" stroke="#345164" />
              <YAxis yAxisId="right" orientation="right" stroke="#345164" />
              <Tooltip />
              <Line yAxisId="left" type="monotone" dataKey="requests" stroke="#0b88a0" name="Requests" strokeWidth={2.4} dot={false} />
              <Line yAxisId="right" type="monotone" dataKey="latency" stroke="#1d9864" name="Latency (ms)" strokeWidth={2.4} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
