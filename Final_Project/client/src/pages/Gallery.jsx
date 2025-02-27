import { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function Gallery() {
  const [allImages, setAllImages] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12); // Images per page
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await axios.get('http://localhost:8000/gallery');
        setAllImages(response.data);
      } catch (error) {
        console.error('Error fetching images:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchImages();
  }, []);

  // Calculate pagination values
  const totalPages = Math.ceil(allImages.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentImages = allImages.slice(startIndex, endIndex);

  const handlePrevious = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const handleNext = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1));
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (loading) return <div className="loading">Loading gallery...</div>;

  return (
    <div className="gallery-container">
      <h2>Photo Gallery</h2>
      <div className="image-grid">
        {currentImages.map((image) => (
          <div key={image.id} className="image-card">
            <Link to={`/dashboard/gallery/${image.id}`} state={{ image }}>
              <img
                src={`http://localhost:8000/${image.filename}`}
                alt={image.title || 'Gallery image'}
                className="gallery-thumbnail"
              />
            </Link>
          </div>
        ))}
      </div>
      
      {/* Pagination Controls */}
      <div className="pagination-controls">
        <button 
          onClick={handlePrevious} 
          disabled={currentPage === 1}
        >
          Previous
        </button>
        
        {/* Page Numbers */}
        {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
          <button
            key={page}
            onClick={() => handlePageChange(page)}
            className={currentPage === page ? 'active' : ''}
          >
            {page}
          </button>
        ))}
        
        <button 
          onClick={handleNext} 
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default Gallery;