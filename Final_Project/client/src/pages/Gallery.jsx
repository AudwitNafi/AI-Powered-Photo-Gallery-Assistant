
import { Form, redirect, useLoaderData, useNavigation, Link } from "react-router-dom";
import React, { useState, useEffect, createContext, useContext } from "react";
import axios from "axios";


function Gallery() {


  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await axios.get('http://localhost:8000/gallery');
        setImages(response.data);
      } catch (error) {
        console.error('Error fetching images:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchImages();
  }, []);

  if (loading) return <div className="loading">Loading gallery...</div>;

  return (
    <div className="gallery-container">
      <h2>Photo Gallery</h2>
      <div className="image-grid">
        {images.map((image) => (
          <div key={image.id} className="image-card">
            <Link to={`/dashboard/gallery/${image.id}`} state={{ image }}>
              <img
                src={`http://localhost:8000/${image.filename}`}
                alt={image.title || 'Gallery image'}
                className="gallery-thumbnail"
              />
              <div className="image-info">
                <p>{image.title || 'Untitled'}</p>
                <p>{image.date}</p>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Gallery;
