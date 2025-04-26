import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const ApiService = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  },
  
  getData: async () => {
    try {
      const response = await axios.get(`${API_URL}/data`);
      return response.data;
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  },
  
  getSuggestions: async () => {
    try {
      const response = await axios.get(`${API_URL}/suggestions`);
      return response.data.suggestions;
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      throw error;
    }
  },
  
  applyTransformation: async (suggestion) => {
    try {
      const response = await axios.post(`${API_URL}/apply-transformation`, {
        suggestion
      });
      return response.data;
    } catch (error) {
      console.error('Error applying transformation:', error);
      throw error;
    }
  }, 

  exportCsv: async () => {
    try {
      // Use window.open for direct download instead of axios
      window.open(`${API_URL}/export-csv`);
      return true;
    } catch (error) {
      console.error('Error exporting CSV:', error);
      throw error;
    }
  }
};

export default ApiService;