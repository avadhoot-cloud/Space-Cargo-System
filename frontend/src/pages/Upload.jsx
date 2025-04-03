import React, { useState } from 'react';
import '../styles/Upload.css';

function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a file to upload');
      return;
    }
    
    setUploading(true);
    setMessage('Uploading file...');
    
    // Mock upload functionality
    // In a real app, you would send the file to your API
    setTimeout(() => {
      setUploading(false);
      setMessage('File uploaded successfully!');
      setFile(null);
    }, 2000);
  };
  
  return (
    <div className="upload-container">
      <h2>Upload Data</h2>
      <p>Upload container and item data in CSV format</p>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input">
          <label htmlFor="file-upload">Select CSV File:</label>
          <input 
            type="file" 
            id="file-upload" 
            accept=".csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </div>
        
        {file && (
          <div className="file-info">
            <p>Selected file: {file.name}</p>
            <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
          </div>
        )}
        
        <button 
          type="submit" 
          className="upload-button"
          disabled={uploading || !file}
        >
          {uploading ? 'Uploading...' : 'Upload File'}
        </button>
        
        {message && (
          <div className={`message ${message.includes('successfully') ? 'success' : ''}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
}

export default Upload; 