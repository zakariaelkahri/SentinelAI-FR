import React from 'react';

const streamParams = [
  { name: 'YOLO FPS', value: '12' },
  { name: 'Process Every Nth Frame', value: '2' },
  { name: 'MJPEG FPS', value: '10' },
  { name: 'MJPEG JPEG Quality', value: '80' },
  { name: 'RTSP Transport', value: 'tcp' },
];

const serviceEndpoints = [
  { name: 'Backend API', url: 'http://localhost:8000' },
  { name: 'Frontend', url: 'http://localhost' },
  { name: 'PgAdmin', url: 'http://localhost:5050' },
  { name: 'Jupyter', url: 'http://localhost:8890' },
  { name: 'MediaMTX RTSP', url: 'rtsp://localhost:8554/live.stream' },
];

function Params() {
  return (
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">System Configuration</p>
        <h1 className="page-title">Params</h1>
        <p className="page-subtitle">
          Review the active stream parameters and local service endpoints used by SentinelAI.
        </p>
      </header>

      <section className="summary-strip">
        <div className="summary-pill">
          <span className="summary-pill-label">Streaming Params</span>
          <span className="summary-pill-value">{streamParams.length}</span>
        </div>
        <div className="summary-pill">
          <span className="summary-pill-label">Service Endpoints</span>
          <span className="summary-pill-value">{serviceEndpoints.length}</span>
        </div>
        <div className="summary-pill">
          <span className="summary-pill-label">Primary API</span>
          <span className="summary-pill-value">:8000</span>
        </div>
      </section>

      <div className="dashboard-grid">
        <section className="card">
          <h2>Streaming Params</h2>
          <ul className="params-list">
            {streamParams.map((param) => (
              <li key={param.name}>
                <span>{param.name}</span>
                <code>{param.value}</code>
              </li>
            ))}
          </ul>
          <p className="section-subtitle">
            These values reflect the current Docker Compose defaults for stable live streaming.
          </p>
        </section>

        <section className="card">
          <h2>Platform Endpoints</h2>
          <ul className="params-list">
            {serviceEndpoints.map((service) => (
              <li key={service.name}>
                <span>{service.name}</span>
                {service.url.startsWith('http') ? (
                  <a className="endpoint-link" href={service.url} target="_blank" rel="noopener noreferrer">
                    {service.url}
                  </a>
                ) : (
                  <code>{service.url}</code>
                )}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

export default Params;
