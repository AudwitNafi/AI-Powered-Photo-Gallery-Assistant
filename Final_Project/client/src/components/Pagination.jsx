import React from "react";

function Pagination({ perPage, length }) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(length / perPage);
  // Handle page change
  const goToPage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const goToNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  const goToPreviousPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const indexOfLast = currentPage * perPage;
  const indexOfFirst = indexOfLast - perPage;
  const current = items.slice(indexOfFirst, indexOfLast);

  return (
    <PaginationContainer>
      <PageButton onClick={goToPreviousPage} disabled={currentPage === 1}>
        Previous
      </PageButton>

      {/* Page Numbers */}
      {Array.from({ length: totalPages }, (_, index) => index + 1).map(
        (number) => (
          <PageButton
            key={number}
            onClick={() => goToPage(number)}
            active={currentPage === number}
          >
            {number}
          </PageButton>
        )
      )}

      <PageButton onClick={goToNextPage} disabled={currentPage === totalPages}>
        Next
      </PageButton>
    </PaginationContainer>
  );
}

export default Pagination;

// const Pagination = ({ currentPage, totalPages, onPageChange }) => {
//   const pages = [];

//   for (let i = 1; i <= totalPages; i++) {
//     pages.push(i);
//   }

//   return (
//     <nav>
//       <ul className="pagination justify-content-center">
//         {pages.map((page) => (
//           <li
//             key={page}
//             className={`page-item ${currentPage === page ? "active" : ""}`}
//           >
//             <button onClick={() => onPageChange(page)} className="page-link">
//               {page}
//             </button>
//           </li>
//         ))}
//       </ul>
//     </nav>
//   );
// };

// export default Pagination;
