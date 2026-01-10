import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Table from 'react-bootstrap/Table';
import Pagination from 'react-bootstrap/Pagination';
import axios from 'axios';

interface Post {
  id: number;
  url: string;
  pdf_downloaded: boolean;
  last_checked: string | null;
  last_downloaded: string | null;
  pdf_path: string | null;
  legislation_number: string | null;
  submission_date: string | null;
  summary: string | null;
  summary_model: string | null;
}

interface PostsResponse {
  total_count: number;
  posts: Post[];
}

function LegislationList() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [postsPerPage] = useState(10); // Number of posts per page
  const [totalPosts, setTotalPosts] = useState(0);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const startfrom = (currentPage - 1) * postsPerPage;
        const response = await axios.get<PostsResponse>(
          `${import.meta.env.VITE_BACKEND_URL}/posts/?fetchsize=${postsPerPage}&startfrom=${startfrom}`
        );
        setPosts(response.data.posts);
        setTotalPosts(response.data.total_count);
      } catch (err) {
        setError('Failed to fetch posts.');
        console.error(err);
      }
    };

    fetchPosts();
  }, [currentPage, postsPerPage]);

  if (error) {
    return <div>{error}</div>;
  }

  // Calculate total pages
  const totalPages = Math.ceil(totalPosts / postsPerPage);

  // Pagination logic
  const pageNumbers = [];
  const maxPagesToShow = 5;
  let startPage: number, endPage: number;

  if (totalPages <= maxPagesToShow) {
    // Show all pages
    startPage = 1;
    endPage = totalPages;
  } else {
    // Show a subset of pages
    const maxPagesBeforeCurrent = Math.floor(maxPagesToShow / 2);
    const maxPagesAfterCurrent = Math.ceil(maxPagesToShow / 2) - 1;

    if (currentPage <= maxPagesBeforeCurrent) {
      startPage = 1;
      endPage = maxPagesToShow;
    } else if (currentPage + maxPagesAfterCurrent >= totalPages) {
      startPage = totalPages - maxPagesToShow + 1;
      endPage = totalPages;
    } else {
      startPage = currentPage - maxPagesBeforeCurrent;
      endPage = currentPage + maxPagesAfterCurrent;
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }


  const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

  return (
    <>
      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>ID</th>
            <th>Legislation Number</th>
            <th>Submission Date</th>
            <th>PDF Downloaded</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {posts.map((post) => (
            <tr key={post.id}>
              <td>{post.id}</td>
              <td>
                <Link to={`/post/${post.id}`}>{post.legislation_number}</Link>
              </td>
              <td>{post.submission_date}</td>
              <td>{post.pdf_downloaded ? 'Yes' : 'No'}</td>
              <td>{post.summary}</td>
            </tr>
          ))}
        </tbody>
      </Table>
      <div className="d-flex justify-content-center">
        <Pagination>
          <Pagination.First onClick={() => paginate(1)} disabled={currentPage === 1} />
          <Pagination.Prev onClick={() => paginate(currentPage - 1)} disabled={currentPage === 1} />
          {pageNumbers.map((number) => (
            <Pagination.Item key={number} active={number === currentPage} onClick={() => paginate(number)}>
              {number}
            </Pagination.Item>
          ))}
          <Pagination.Next onClick={() => paginate(currentPage + 1)} disabled={currentPage === totalPages} />
          <Pagination.Last onClick={() => paginate(totalPages)} disabled={currentPage === totalPages} />
        </Pagination>
      </div>
    </>
  );
}

export default LegislationList;
