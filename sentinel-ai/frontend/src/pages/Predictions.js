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
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Run Predictions</h1>

      <div className="card" style={{ maxWidth: '600px' }}>
        <h2>Upload Image</h2>
        <form onSubmit={handleSubmit}>
          <div className="upload-zone" onClick={() => document.getElementById('file-input').click()}>
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {file ? (
              <p>{file.name}</p>
            ) : (
              <p>Click to select an image or drag and drop</p>
            )}
          </div>

          <button type="submit" className="btn" style={{ marginTop: '1rem' }} disabled={!file || loading}>
            {loading ? 'Processing...' : 'Run Prediction'}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fee2e2', borderRadius: '4px', color: '#dc2626' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: '1.5rem' }}>
            <h3>Results</h3>
            <p><strong>Model:</strong> {result.model_name}</p>
            <p><strong>Inference Time:</strong> {result.inference_time_ms.toFixed(2)} ms</p>
            <p><strong>Detections:</strong> {result.predictions.length}</p>

            {result.predictions.length > 0 && (
              <ul style={{ marginTop: '0.5rem', listStyle: 'none' }}>
                {result.predictions.map((pred, idx) => (
                  <li key={idx} style={{ padding: '0.5rem', backgroundColor: '#f5f5f5', marginTop: '0.5rem', borderRadius: '4px' }}>
                    {pred.class_name} - {(pred.confidence * 100).toFixed(1)}%
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Predictions;
