import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Card, Button } from 'react-bootstrap';

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

function LegislationDetail() {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/posts/${id}`);
        setPost(response.data);
      } catch (err) {
        setError('Failed to fetch post details.');
        console.error(err);
      }
    };

    if (id) {
      fetchPost();
    }
  }, [id]);

  if (error) {
    return <div>{error}</div>;
  }

  if (!post) {
    return <div>Loading...</div>;
  }

  // Extract filename from pdf_path for download attribute
  const getFilenameFromPath = (path: string | null) => {
    if (!path) return 'download.pdf';
    const parts = path.split('/');
    return parts[parts.length - 1];
  };

  return (
    <Card>
      <Card.Header>Legislation Details</Card.Header>
      <Card.Body>
        <Card.Title>{post.legislation_number}</Card.Title>
        <Card.Text>
          <strong>ID:</strong> {post.id} <br />
          <strong>Submission Date:</strong> {post.submission_date} <br />
          <strong>PDF Downloaded:</strong> {post.pdf_downloaded ? 'Yes' : 'No'} <br />
          <strong>URL:</strong> <a href={post.url} target="_blank" rel="noopener noreferrer">{post.url}</a> <br />
          {post.pdf_path && <><strong>PDF Path:</strong> {post.pdf_path} <br /></>}
        </Card.Text>
        {post.pdf_path && (
          <div className="mt-3">
            <Button
              variant="primary"
              href={`${import.meta.env.VITE_BACKEND_URL}/download/pdf/${post.id}`}
              download={getFilenameFromPath(post.pdf_path)}
            >
              Download PDF
            </Button>
          </div>
        )}
        <Card.Text className="mt-3">
          <h5>Summary</h5>
          <p>{post.summary || 'No summary available.'}</p>
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default LegislationDetail;
