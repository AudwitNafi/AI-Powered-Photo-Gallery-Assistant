import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Link } from 'react-router-dom';

const BatchUploadPage = () => {
  const [files, setFiles] = useState([]);
  const [metadata, setMetadata] = useState({
    person_entity: '',
    location: '',
    date: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState([]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {'image/*': ['.jpeg', '.png', '.jpg']},
    multiple: true,
    maxFiles: 10,
    onDrop: acceptedFiles => {
      setFiles(prev => [...prev, ...acceptedFiles].slice(0, 10));
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess([]);

    if (files.length === 0) {
      setError('Please select at least one image to upload');
      setLoading(false);
      return;
    }

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    if (metadata.person_entity) formData.append('person_or_entity', metadata.person_entity);
    if (metadata.location) formData.append('location', metadata.location);
    if (metadata.date) formData.append('date', metadata.date);

    try {
      const response = await axios.post(
        'http://localhost:8000/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setSuccess(response.data.uploaded);
      setFiles([]);
      setMetadata({ person_entity: '', location: '', date: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const removeFile = (fileName) => {
    setFiles(current => current.filter(file => file.name !== fileName));
  };

  return (
    <div className="upload-container">
      <h3>Batch Image Upload</h3>
      <h5>(Max 10 files, 5MB each)</h5>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-section">
          <h4>Image Upload</h4>
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            {files.length > 0 ? (
              <div className="files-preview">
                {files.map(file => (
                  <div key={file.name} className="file-item">
                    <span>{file.name} ({Math.round(file.size/1024)}KB)</span>
                    <button
                      type="button"
                      className="remove-file"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(file.name);
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p><i>Drag & drop images here, or click to select</i></p>
            )}
            {files.length > 0 && (
              <div className="files-count">{files.length}/10 files selected</div>
            )}
          </div>
        </div>

        <div className="form-section">
          <h4>Optional Metadata</h4>
          <div className="form-group">
            <label>Person/Named Entity:</label>
            <input
              type="text"
              value={metadata.person_entity}
              onChange={(e) => setMetadata({...metadata, person_entity: e.target.value})}
              placeholder="Optional: Enter person/entity"
            />
          </div>

          <div className="form-group">
            <label>Location:</label>
            <input
              type="text"
              value={metadata.location}
              onChange={(e) => setMetadata({...metadata, location: e.target.value})}
              placeholder="Optional: Enter location"
            />
          </div>

          <div className="form-group">
            <label>Date:</label>
            <input
              type="date"
              value={metadata.date}
              onChange={(e) => setMetadata({...metadata, date: e.target.value})}
            />
          </div>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={loading || files.length === 0}
        >
          {loading ? `Uploading ${files.length} Images...` : 'Upload Images'}
        </button>

        {error && <div className="alert error">{error}</div>}
        {success.length > 0 && (
          <div className="alert success">
            <p>✓ {success.length} Images Uploaded Successfully!</p>
            <div className="uploaded-files">
              {success.map((file, index) => (
                <div key={index} className="uploaded-file">
                  <p>{file.original_name} → <a href={file.url} target="_blank" rel="noopener noreferrer">View</a></p>
                </div>
              ))}
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default BatchUploadPage;