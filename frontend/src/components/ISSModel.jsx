import React, { useState, useEffect } from 'react';

const ISSModel = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Use the high-resolution ISS model directly from public folder
  const modelUrl = '/ISS_stationary.glb';
  const viewerUrl = '/model-viewer.html';

  useEffect(() => {
    // Check if the model file exists
    const checkModelExists = async () => {
      try {
        const response = await fetch(modelUrl);
        if (!response.ok) {
          throw new Error(`Model not found: ${modelUrl}`);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error loading model:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    checkModelExists();
  }, [modelUrl]);

  return (
    <div className="iss-model-container">
      {error ? (
        <div className="model-error">
          <p>Error loading 3D model: {error}</p>
          <p>Please ensure the model file is in the correct location: {modelUrl}</p>
        </div>
      ) : (
        <div className="model-viewer-container">
          <iframe
            title="ISS 3D Model Viewer"
            className="model-viewer-iframe"
            src={viewerUrl}
            frameBorder="0"
            allowFullScreen
            loading="lazy"
          ></iframe>
          <div className="model-caption">
            <h3>International Space Station</h3>
            <p>High-resolution 3D model • Drag to rotate • Scroll to zoom</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ISSModel; 