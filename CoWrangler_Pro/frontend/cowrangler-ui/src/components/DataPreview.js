import React from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const DataPreview = ({ data, columns }) => {
  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true,
    minWidth: 100
  };

  // Create column definitions from the provided columns
  const columnDefs = columns && columns.length > 0
    ? columns.map(col => ({ 
        headerName: col, 
        field: col,
        // Special rendering for null values
        cellRenderer: params => {
          if (params.value === null) return '<span class="text-muted">null</span>';
          return params.value;
        }
      }))
    : [];

  return (
    <div className="h-100 d-flex flex-column">
      <div className="p-2 bg-light border-bottom">
        <h5 className="m-0">Dataframe Preview</h5>
      </div>
      <div className="flex-grow-1 ag-theme-alpine">
        {data && data.length > 0 ? (
          <AgGridReact
            rowData={data}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            rowSelection="multiple"
            pagination={true}
            paginationPageSize={100}
          />
        ) : (
          <div className="d-flex justify-content-center align-items-center h-100 text-muted">
            No data loaded. Please upload a CSV or Excel file.
          </div>
        )}
      </div>
    </div>
  );
};

export default DataPreview;