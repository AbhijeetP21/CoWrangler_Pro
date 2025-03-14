import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Button, Alert } from 'react-bootstrap';
import DataPreview from './DataPreview';
import SuggestionsPanel from './SuggestionsPanel';
import CodeEditor from './CodeEditor';
import TransformationsHistory from './TransformationsHistory';
import ApiService from '../services/ApiService';
import 'bootstrap/dist/css/bootstrap.min.css';

const MainLayout = () => {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [transformations, setTransformations] = useState([]);
  const [generatedCode, setGeneratedCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);

  // In the loadData function of MainLayout.js
const loadData = async () => {
  try {
    console.log("Loading data from API...");
    const response = await ApiService.getData();
    console.log("API response:", response);
    
    if (response && response.data) {
      console.log(`Setting data state with ${response.data.length} rows`);
      setData(response.data);
      setColumns(response.columns);
    } else {
      console.error("API returned without data:", response);
    }
  } catch (err) {
    console.error("Error loading data:", err);
    setError('Failed to load data: ' + (err.message || 'Unknown error'));
  }
};

  const loadSuggestions = async () => {
    try {
      const suggestions = await ApiService.getSuggestions();
      setSuggestions(suggestions);
    } catch (err) {
      setError('Failed to load suggestions');
      console.error(err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      console.log("No file selected");
      return;
    }
  
    console.log("File selected:", file.name);
    setLoading(true);
    setError('');
    
    try {
      console.log("Uploading file to backend...");
      const uploadResult = await ApiService.uploadFile(file);
      console.log("Upload result:", uploadResult);
      setFileUploaded(true);
      
      // Load data and suggestions after successful upload
      console.log("Loading data after upload...");
      await loadData();
      console.log("Loading suggestions after upload...");
      await loadSuggestions();
    } catch (err) {
      console.error("Upload error:", err);
      setError('Failed to upload file: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionSelect = (suggestion) => {
    setSelectedSuggestion(suggestion);
    setGeneratedCode(suggestion.code || '# No code generated');
  };

  const handleApplyTransformation = async () => {
    if (!selectedSuggestion) return;
    
    setLoading(true);
    setError('');
    
    try {
      const result = await ApiService.applyTransformation(selectedSuggestion);
      
      // Update data
      setData(result.new_data);
      setColumns(result.columns);
      
      // Add to transformation history
      setTransformations([...transformations, selectedSuggestion]);
      
      // Clear selection
      setSelectedSuggestion(null);
      setGeneratedCode('');
      
      // Refresh suggestions
      await loadSuggestions();
    } catch (err) {
      setError('Failed to apply transformation: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="vh-100 d-flex flex-column">
      <Row className="py-2 bg-light border-bottom">
        <Col>
          <h4 className="m-0">CoWrangler Suggestions Engine</h4>
        </Col>
        <Col xs="auto">
          <input 
            type="file" 
            id="datafileInput" 
            style={{ display: 'none' }} 
            onChange={handleFileUpload}
            accept=".csv,.xlsx,.xls"
          />
          <Button 
            variant="outline-primary" 
            size="sm" 
            onClick={() => document.getElementById('datafileInput').click()}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load'}
          </Button>
          <Button variant="outline-secondary" size="sm" className="ms-2" disabled={!fileUploaded}>
            Export to CSV
          </Button>
          <Button variant="outline-secondary" size="sm" className="ms-2" disabled={!fileUploaded}>
            Export Code
          </Button>
        </Col>
      </Row>
      
      {error && (
        <Alert variant="danger" onClose={() => setError('')} dismissible>
          {error}
        </Alert>
      )}
      
      <Row className="flex-grow-1">
        <Col md={8} className="d-flex flex-column">
          <DataPreview data={data} columns={columns} />
        </Col>
        <Col md={4} className="d-flex flex-column border-start">
          <SuggestionsPanel 
            suggestions={suggestions}
            onSelectSuggestion={handleSuggestionSelect} 
            selectedSuggestion={selectedSuggestion} 
          />
          <div className="border-top mt-2 pt-2">
            <CodeEditor code={generatedCode} />
          </div>
          <div className="d-flex justify-content-end mt-2 mb-2">
            <Button 
              variant="outline-secondary" 
              className="me-2"
              onClick={() => {
                setSelectedSuggestion(null);
                setGeneratedCode('');
              }}
              disabled={!selectedSuggestion}
            >
              Discard
            </Button>
            <Button 
              variant="primary" 
              onClick={handleApplyTransformation}
              disabled={!selectedSuggestion || loading}
            >
              {loading ? 'Applying...' : 'Apply'}
            </Button>
          </div>
          <div className="border-top pt-2">
            <TransformationsHistory transformations={transformations} />
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default MainLayout;