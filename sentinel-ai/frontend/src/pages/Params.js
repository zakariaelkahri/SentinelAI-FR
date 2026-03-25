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
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Params</h1>

      <div className="dashboard-grid">
        <div className="card">
          <h2>Streaming Params</h2>
          <ul className="params-list">
            {streamParams.map((param) => (
              <li key={param.name}>
                <span>{param.name}</span>
                <code>{param.value}</code>
              </li>
            ))}
          </ul>
          <p style={{ color: '#6b7280', marginTop: '1rem' }}>
            These values reflect current Docker compose defaults for stable live streaming.
          </p>
        </div>

        <div className="card">
          <h2>Platform Endpoints</h2>
          <ul className="params-list">
            {serviceEndpoints.map((service) => (
              <li key={service.name}>
                <span>{service.name}</span>
                {service.url.startsWith('http') ? (
                  <a href={service.url} target="_blank" rel="noopener noreferrer">
                    {service.url}
                  </a>
                ) : (
                  <code>{service.url}</code>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Params;
