import React, { useState } from 'react';
import { api } from '../services/api';

function Predictions() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.predict(file);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">Vision Inference</p>
        <h1 className="page-title">Run Predictions</h1>
        <p className="page-subtitle">
          Upload a frame and run the latest model to detect suspicious objects in seconds.
        </p>
      </header>

      <section className="card prediction-card">
        <h2>Upload Image</h2>
        <p className="section-subtitle">
          Supported formats: JPG, PNG, WEBP. Larger files may take longer to process.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div
            className={`upload-zone${file ? ' has-file' : ''}`}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {file ? (
              <p className="upload-file-name">{file.name}</p>
            ) : (
              <p>Click to select an image or drag and drop</p>
            )}
          </div>

          <button type="submit" className="btn" disabled={!file || loading}>
            {loading ? 'Processing...' : 'Run Prediction'}
          </button>
        </form>

        {error && <div className="auth-error">{error}</div>}

        {result && (
          <div className="prediction-results">
            <h3>Results</h3>
            <div className="prediction-summary">
              <p>
                <strong>Model:</strong> {result.model_name}
              </p>
              <p>
                <strong>Inference Time:</strong> {result.inference_time_ms.toFixed(2)} ms
              </p>
              <p>
                <strong>Detections:</strong> {result.predictions.length}
              </p>
            </div>

            {result.predictions.length > 0 && (
              <ul className="detection-list">
                {result.predictions.map((pred, idx) => (
                  <li key={idx} className="detection-item">
                    <span className="resource-name">{pred.class_name}</span>
                    <span className="meta-chip">{(pred.confidence * 100).toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default Predictions;
