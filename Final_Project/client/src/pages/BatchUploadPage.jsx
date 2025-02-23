import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Link } from 'react-router-dom';

const BatchUploadPage = () => {
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState({
    person_entity: '',
    location: '',
    date: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {'image/*': ['.jpeg', '.png', '.jpg']},
    multiple: false,
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0]);
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // if (!file || !metadata.person_entity || !metadata.location || !metadata.date) {
    //   setError('All fields are required');
    //   setLoading(false);
    //   return;
    // }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('person_or_entity', metadata.person_entity);
    formData.append('location', metadata.location);
    formData.append('date', metadata.date);

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

      setSuccess(response.data);
      setFile(null);
      setMetadata({ person_entity: '', location: '', date: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h3>Upload Image with Metadata</h3>
      {/*<Link to="/dashboard/gallery" className="back-link">← Back to Gallery</Link>*/}

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-section">
          <h4>Image Upload</h4>
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            {file ? (
              <div className="file-preview">
                <p>{file.name}</p>
                <button
                  type="button"
                  className="remove-file"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                  }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <p>Drag & drop image here, or click to select</p>
            )}
          </div>
        </div>

        <div className="form-section">
          <h4>Metadata</h4>
          <div className="form-group">
            <label>Person/Named Entity:</label>
            <input
              type="text"
              value={metadata.person_entity}
              onChange={(e) => setMetadata({...metadata, person_entity: e.target.value})}
              placeholder="Enter person or entity name"
            />
          </div>

          <div className="form-group">
            <label>Location:</label>
            <input
              type="text"
              value={metadata.location}
              onChange={(e) => setMetadata({...metadata, location: e.target.value})}
              placeholder="Enter location"
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
          disabled={loading}
        >
          {loading ? 'Uploading...' : 'Upload Image'}
        </button>

        {error && <div className="alert error">{error}</div>}
        {success && (
          <div className="alert success">
            <p>✓ Upload successful!</p>
            <p>URL: {success.url}</p>
            <p>Filename: {success.filename}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default BatchUploadPage;