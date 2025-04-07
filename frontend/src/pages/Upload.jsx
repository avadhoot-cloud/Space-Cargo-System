// frontend/src/pages/Upload.jsx

import React, { useState, useRef } from 'react';
import apiService from '../services/api';
import '../styles/Upload.css';

function Upload() {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('items'); // 'items' or 'containers'
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadResult, setUploadResult] = useState(null);
  const [isDuplicate, setIsDuplicate] = useState(false);
  const fileInputRef = useRef(null);
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage('');
      setUploadResult(null);
      setIsDuplicate(false);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setMessage('');
        setUploadResult(null);
        setIsDuplicate(false);
      } else {
        setMessage('Only CSV files are allowed');
      }
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a file to upload');
      return;
    }
    
    // Check file extension
    if (!file.name.endsWith('.csv')) {
      setMessage('Only CSV files are allowed');
      return;
    }
    
    setUploading(true);
    setMessage('Uploading file...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      let response;
      if (fileType === 'items') {
        response = await apiService.data.importItems(formData);
      } else {
        response = await apiService.data.importContainers(formData);
      }
      
      const data = response.data;
      setMessage(`${data.message || 'Upload successful'}!`);
      setUploadResult(data);
      setIsDuplicate(data.duplicate || false);
      setFile(null);
      
      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.message || error.message}`);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="upload-container">
      <h2>Upload Data</h2>
      <p>Upload container and item data in CSV format to manage your space cargo system efficiently</p>
      
      <div className="csv-templates">
        <h3>CSV Templates</h3>
        <div className="template-info">
          <div className="template">
            <h4>Item Template</h4>
            <pre>item_id,name,width_cm,depth_cm,height_cm,mass_kg,priority,expiry_date,usage_limit,preferred_zone</pre>
            <p>Example: MED001,Medical Supplies,30,20,15,20,5,2025-12-31,10,Medical_Bay</p>
            <p>Required fields: item_id, name, width_cm, depth_cm, height_cm</p>
          </div>
          <div className="template">
            <h4>Container Template</h4>
            <pre>zone,container_id,width_cm,depth_cm,height_cm</pre>
            <p>Example: Medical_Bay,MB01,100,60,80</p>
            <p>Required fields: container_id, width_cm, depth_cm, height_cm, zone</p>
          </div>
        </div>
        <div className="template-note">
          <p><strong>Note:</strong> CSV files must include all required headers. Files are stored in the Data folder and checked for duplicates.</p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-type-selector">
          <label>
            <input
              type="radio"
              value="items"
              checked={fileType === 'items'}
              onChange={() => setFileType('items')}
            />
            Items
          </label>
          <label>
            <input
              type="radio"
              value="containers"
              checked={fileType === 'containers'}
              onChange={() => setFileType('containers')}
            />
            Containers
          </label>
        </div>
        
        <div className="file-input">
          <label htmlFor="file-upload">Select CSV File</label>
          <div 
            className="file-input-wrapper"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <div className="file-input-icon">📁</div>
            <div className="file-input-text">Drag and drop your CSV file here</div>
            <div className="file-input-subtext">or click to browse files</div>
            <input 
              type="file" 
              id="file-upload" 
              ref={fileInputRef}
              accept=".csv"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>
        </div>
        
        {file && (
          <div className="file-info">
            <div className="file-info-icon">📄</div>
            <div className="file-info-content">
              <p>Selected file: {file.name}</p>
              <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
              <p>Type: {fileType === 'items' ? 'Items' : 'Containers'} CSV</p>
            </div>
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
          <div className={`message ${message.includes('!') && !message.includes('Error') ? (isDuplicate ? 'warning' : 'success') : 'error'}`}>
            {message}
          </div>
        )}
        
        {uploadResult && (
          <div className="upload-result">
            <h3>
              {isDuplicate 
                ? 'Duplicate file detected' 
                : `${fileType === 'items' ? 'Items' : 'Containers'} uploaded successfully`}
            </h3>
            {uploadResult.itemsImported && (
              <p>{uploadResult.itemsImported} items imported</p>
            )}
            {uploadResult.containersImported && (
              <p>{uploadResult.containersImported} containers imported</p>
            )}
          </div>
        )}
      </form>
    </div>
  );
}

export default Upload;