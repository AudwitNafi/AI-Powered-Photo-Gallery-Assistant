// ImageDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ImageDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImageDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/gallery/${id}`);
        setImage(response.data);
      } catch (error) {
        console.error('Error fetching image details:', error);
        navigate('/gallery'); // Redirect if image not found
      } finally {
        setLoading(false);
      }
    };

    fetchImageDetails();
  }, [id, navigate]);

  if (loading) return <div className="loading">Loading image details...</div>;

  return (
    <div className="image-detail-container">
      <button onClick={() => navigate(-1)} className="back-button">
        &larr; Back to Gallery
      </button>

      <div className="image-detail-content">
        <img
          src={`http://localhost:8000/uploads/${image.filename}`}
          alt={image.title || 'Gallery image'}
          className="enlarged-image"
        />

        <div className="image-metadata">
          <h3>{image.title || 'Untitled'}</h3>

          <div className="metadata-section">
            <h4>Details</h4>
            <p><strong>Date:</strong> {new Date(image.date).toLocaleDateString()}</p>
            <p><strong>Location:</strong> {image.location || 'Unknown'}</p>
          </div>

          {image.entities && image.entities.length > 0 && (
            <div className="metadata-section">
              <h4>People & Entities</h4>
              <ul className="entities-list">
                {image.entities.map((entity, index) => (
                  <li key={index}>{entity}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageDetailPage;