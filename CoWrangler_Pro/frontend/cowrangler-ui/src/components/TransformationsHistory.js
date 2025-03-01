// For the applied transformations panel

import React from 'react';
import { ListGroup } from 'react-bootstrap';

const TransformationsHistory = ({ transformations }) => {
  return (
    <div>
      <h5 className="mb-2">Applied Transformations</h5>
      {transformations.length === 0 ? (
        <p className="text-muted">No transformations applied yet</p>
      ) : (
        <ListGroup>
          {transformations.map((transform, index) => (
            <ListGroup.Item key={index} className="py-2">
              <div className="d-flex align-items-center">
                <span className="me-2">{index + 1}</span>
                <span>{transform.title}</span>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </div>
  );
};

export default TransformationsHistory;