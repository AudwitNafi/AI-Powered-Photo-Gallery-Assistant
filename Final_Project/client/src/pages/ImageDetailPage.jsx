import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from "react-markdown";
import axios from 'axios';

const ImageDetailPage = () => {
  const { id } = useParams(); // Get the image ID from the URL
  const navigate = useNavigate();
  const location = useLocation()
  const [details, setDetails] = useState(null);
  const [image, setImage] = useState(location.state?.image);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImageDetails = async () => {
      try {
        // Fetch image details from the backend
        const response = await axios.get(`http://localhost:8000/gallery/${id}`);
        setDetails(response.data);
      } catch (error) {
        console.error('Error fetching image details:', error);
        setError('Failed to load image details');
        navigate('/gallery'); // Redirect to gallery if image not found
      } finally {
        setLoading(false);
      }
    };
    fetchImageDetails();
  }, [id, navigate]);

  if (loading) return <div className="loading">Loading image details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!image) return <div>Image not found</div>;

  return (
    <div className="image-detail-container">
      <button onClick={() => navigate(-1)} className="back-button">
        &larr; Back to Gallery
      </button>

      <div className="image-detail-content">
        <img
          src={`http://localhost:8000/${image.filename}`}
          alt={image.title || 'Gallery image'}
          className="enlarged-image"
        />

        <div className="image-metadata">
          <div className="metadata-section">
            <h3>Details</h3>
            <p><strong>Date:</strong> {image.date}</p>
            <p><strong>Location:</strong> {details.location || 'Unknown'}</p>
            <p><ReactMarkdown>{details.description || 'No description available'}</ReactMarkdown></p>
          </div>
          <div className="metadata-section">
            <h4>People & Entities</h4>
            <ul className="entities-list">
              {details.entities || 'None'}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageDetailPage;