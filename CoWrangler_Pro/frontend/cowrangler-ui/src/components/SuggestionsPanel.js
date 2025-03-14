import React from 'react';
import { ListGroup } from 'react-bootstrap';

const SuggestionsPanel = ({ suggestions, onSelectSuggestion, selectedSuggestion }) => {
  // Use provided suggestions or an empty array
  const displaySuggestions = suggestions || [];
  
  return (
    <div className="mb-2">
      <h5 className="p-2 bg-light m-0 border-bottom">CoWrangler Suggestions</h5>
      {displaySuggestions.length === 0 ? (
        <div className="p-3 text-center text-muted">
          {suggestions === undefined ? 
            "Upload a file to generate suggestions" : 
            "No suggestions available for this dataset"}
        </div>
      ) : (
        <ListGroup>
          {displaySuggestions.map((suggestion) => (
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
      )}
    </div>
  );
};

export default SuggestionsPanel;