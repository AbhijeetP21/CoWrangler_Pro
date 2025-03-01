// For the suggestions list

import React from 'react';
import { ListGroup } from 'react-bootstrap';

const SuggestionsPanel = ({ onSelectSuggestion, selectedSuggestion }) => {
  // Sample suggestions based on the paper
  const sampleSuggestions = [
    {
      id: 1,
      title: "Split title using delimiter colon (:)",
      explanation: "Title contains consistent pattern that can be split"
    },
    {
      id: 2,
      title: "Split desc using delimiter semicolon (;)",
      explanation: "Desc contains multiple fields separated by semicolons"
    },
    {
      id: 3,
      title: "Drop emergency",
      explanation: "REASON: contains constant value 1"
    },
    {
      id: 4,
      title: "Fill Missing Values in zip",
      explanation: "REASON: 12% missing values"
    },
    {
      id: 5,
      title: "Label-encode title",
      explanation: "REASON: contains 102 unique values"
    },
    {
      id: 6,
      title: "Click here to add custom operation",
      explanation: ""
    }
  ];

  return (
    <div className="mb-2">
      <h5 className="p-2 bg-light m-0 border-bottom">CoWrangler Suggestions</h5>
      <ListGroup>
        {sampleSuggestions.map((suggestion) => (
          <ListGroup.Item 
            key={suggestion.id}
            action
            active={selectedSuggestion && selectedSuggestion.id === suggestion.id}
            onClick={() => onSelectSuggestion(suggestion)}
            className="d-flex flex-column align-items-start py-2"
          >
            <div className="d-flex w-100 align-items-center">
              <span className="me-2">{suggestion.id}</span>
              <strong>{suggestion.title}</strong>
            </div>
            {suggestion.explanation && (
              <small className="text-muted mt-1">{suggestion.explanation}</small>
            )}
          </ListGroup.Item>
        ))}
      </ListGroup>
    </div>
  );
};

export default SuggestionsPanel;