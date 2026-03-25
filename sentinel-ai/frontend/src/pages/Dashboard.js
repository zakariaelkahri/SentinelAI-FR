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

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard Statistics</h1>

      <div className="dashboard-grid">
        <div className="card">
          <h2>API Status</h2>
          <div className="status-indicator">
            <span className={`status-dot ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
            <span>{health?.status || 'Checking...'}</span>
          </div>
          {health?.timestamp && (
            <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.875rem' }}>
              Last check: {new Date(health.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>

        <div className="card">
          <h2>Registered Models</h2>
          {models.length > 0 ? (
            <ul style={{ listStyle: 'none' }}>
              {models.map((model, idx) => (
                <li key={idx} style={{ padding: '0.5rem 0', borderBottom: '1px solid #eee' }}>
                  {model.name} (v{model.latest_version || 'N/A'})
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: '#666' }}>No models registered</p>
          )}
        </div>

        <div className="card">
          <h2>Quick Links</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <a href="http://localhost:5000" target="_blank" rel="noopener noreferrer">MLflow UI</a>
            <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer">Airflow UI</a>
            <a href="http://localhost:3001" target="_blank" rel="noopener noreferrer">Grafana</a>
            <a href="http://localhost:9090" target="_blank" rel="noopener noreferrer">Prometheus</a>
          </div>
        </div>

        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h2>Request Metrics (24h)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={mockMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line yAxisId="left" type="monotone" dataKey="requests" stroke="#1a1a2e" name="Requests" />
              <Line yAxisId="right" type="monotone" dataKey="latency" stroke="#22c55e" name="Latency (ms)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
