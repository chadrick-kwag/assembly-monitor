import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Table, Alert } from 'react-bootstrap';

interface Legislation {
  id: number;
  legislation_name: string;
  submitted_date: string;
  summary: string;
  legislation_number: string;
}

function DBSearchPage() {
  const [legislationNumber, setLegislationNumber] = useState('');
  const [searchResult, setSearchResult] = useState<Legislation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSearchResult(null);
    setLoading(true);

    if (!legislationNumber.trim()) {
      setError('Please enter a legislation number.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/posts/legislation/${legislationNumber}`);
      if (!response.ok) {
        if (response.status === 404) {
          setError(`No legislation found with number: ${legislationNumber}`);
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        setLoading(false);
        return;
      }
      const data: Legislation = await response.json();
      setSearchResult(data);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(`Failed to fetch legislation: ${e.message}`);
      } else {
        setError('An unknown error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h2>DB Search</h2>
          <Form onSubmit={handleSearch}>
            <Form.Group className="mb-3" controlId="legislationNumberSearch">
              <Form.Label>Search by Legislation Number</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., AB1234"
                value={legislationNumber}
                onChange={(e) => setLegislationNumber(e.target.value)}
              />
            </Form.Group>
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Form>
        </Col>
      </Row>
      <Row>
        <Col>
          {error && <Alert variant="danger">{error}</Alert>}
          {loading && <p>Loading...</p>}
          {searchResult ? (
            <div>
              <h3>Search Result</h3>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>Legislation Number</th>
                    <th>Name</th>
                    <th>Submitted Date</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{searchResult.legislation_number}</td>
                    <td>{searchResult.legislation_name}</td>
                    <td>{searchResult.submitted_date}</td>
                    <td>{searchResult.summary}</td>
                  </tr>
                </tbody>
              </Table>
            </div>
          ) : (
            !error && !loading && <p>Enter a legislation number to search.</p>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default DBSearchPage;
