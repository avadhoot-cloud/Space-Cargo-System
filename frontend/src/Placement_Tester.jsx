import React, { useState } from 'react';
import { API } from './services/api';

const PlacementTester = () => {
  const [responseText, setResponseText] = useState('');

  const testPlacement = async () => {
    const payload = {
      items: [
        {
          itemId: 'test-item-1',
          name: 'Test Item 1',
          width: 10,
          depth: 10,
          height: 10,
          mass: 1,
          priority: 1,
          preferredZone: 'A'
        }
      ],
      containers: [
        {
          containerId: 'test-container-1',
          zone: 'A',
          width: 100,
          depth: 100,
          height: 100
        }
      ]
    };

    try {
      // Using the authorized axios instance from api.jsx
      const response = await API.post('/api/placement', payload, {
        headers: { 'Content-Type': 'application/json' }
      });
      setResponseText(JSON.stringify(response.data));
    } catch (error) {
      setResponseText('Error: ' + error.message);
    }
  };

  return (
    <div style={{ margin: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Placement Endpoint Tester</h2>
      <button
        onClick={testPlacement}
        style={{ padding: '10px 20px', fontSize: '16px' }}
      >
        Test Placement
      </button>
      <div style={{ marginTop: '20px', fontSize: '18px' }}>
        Response: {responseText}
      </div>
    </div>
  );
};

export default PlacementTester;
