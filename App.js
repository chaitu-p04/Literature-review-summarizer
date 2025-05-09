import axios from 'axios';
import React, { useState } from 'react';
import { Button, Container, Form, Spinner } from 'react-bootstrap';
import './App.css';
import SummaryList from './components/SummaryList';

function App() {
  const [query, setQuery] = useState("");
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/process', { query });
      setSummaries(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-bg py-5">
      <Container className="text-center">
        <div className="header-box py-4 px-3 mb-4 rounded shadow-sm">
          <h1 className="display-5 fw-bold gradient-text">📚✨ Research Paper Summarizer ✨📚</h1>
          <p className="lead text-muted">AI-powered summaries of cutting-edge research papers</p>
        </div>

        <Form onSubmit={handleSubmit} className="mt-4 mx-auto" style={{ maxWidth: '600px' }}>
          <Form.Group controlId="formQuery">
            <Form.Control 
              type="text"
              className="form-control-lg shadow-sm"
              placeholder="🔍 Enter a research topic, e.g., Generative AI"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </Form.Group>
          <Button variant="primary" type="submit" className="mt-3 px-4 py-2">
            {loading ? <Spinner animation="border" size="sm" /> : "🚀 Summarize"}
          </Button>
        </Form>

        <hr className="my-5" />

        <SummaryList summaries={summaries} />

        <footer className="text-muted mt-5">
          <small>⚡ Built with React, Flask & Gemini AI</small>
        </footer>
      </Container>
    </div>
  );
}

export default App;
