// For the data grid panel

import React from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const DataPreview = ({ data }) => {
  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true,
    minWidth: 100
  };

  // Sample data for demonstration
  const sampleData = [
    {
      lat: 40.29, 
      long: -75.58,
      desc: "REINDEER CT & DEAD END; NEW HANOVER; Station 332; 2015-12-10 @ 17:10:52",
      zip: 19525,
      title: "EMS: BACK PAINS/INJURY",
      emergency: 1
    },
    {
      lat: 40.12, 
      long: -75.35,
      desc: "HAWS AVE; NORRISTOWN; Station STA27; 2015-12-10 @ 14:39:21",
      zip: 19401,
      title: "Fire: GAS-ODOR/LEAK",
      emergency: 1
    },
    {
      lat: 40.10, 
      long: -75.29,
      desc: "BLUEROUTE & RAMP I476 NB TO CHEMICAL RD; PLYMOUTH; ; 2015-12-10 @ 17:35:41",
      zip: 19462,
      title: "Traffic: VEHICLE ACCIDENT",
      emergency: 1
    }
  ];

  const sampleColumns = [
    { headerName: 'lat', field: 'lat' },
    { headerName: 'long', field: 'long' },
    { headerName: 'desc', field: 'desc' },
    { headerName: 'zip', field: 'zip' },
    { headerName: 'title', field: 'title' },
    { headerName: 'emergency', field: 'emergency' }
  ];

  // Use the provided data or fall back to sample data for demonstration
  const rowData = data.length > 0 ? data : sampleData;
  const columnDefs = data.length > 0 && data[0] ? 
    Object.keys(data[0]).map(key => ({ field: key })) : 
    sampleColumns;

  return (
    <div className="h-100 d-flex flex-column">
      <div className="p-2 bg-light border-bottom">
        <h5 className="m-0">Dataframe (911.csv)</h5>
      </div>
      <div className="flex-grow-1 ag-theme-alpine">
        <AgGridReact
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          rowSelection="multiple"
        />
      </div>
    </div>
  );
};

export default DataPreview;