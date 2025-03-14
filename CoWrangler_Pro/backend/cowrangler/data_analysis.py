import pandas as pd
import numpy as np

class DataAnalyzer:
    def __init__(self, df=None):
        self.df = df
        self.profile = {}
    
    def load_data(self, file_path=None, file_content=None, file_type='csv'):
        """Load data from a file or content and perform initial profiling"""
        try:
            if file_path:
                if file_type == 'csv':
                    self.df = pd.read_csv(file_path)
                elif file_type == 'excel':
                    self.df = pd.read_excel(file_path)
            elif file_content:
                if file_type == 'csv':
                    self.df = pd.read_csv(pd.io.common.StringIO(file_content))
                elif file_type == 'excel':
                    self.df = pd.read_excel(pd.io.common.StringIO(file_content))
            else:
                raise ValueError("Either file_path or file_content must be provided")
            
            # Generate basic profile
            self._generate_profile()
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def _generate_profile(self):
        """Generate a profile of the dataset with information about columns"""
        if self.df is None:
            return {}
        
        self.profile = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "columns": {}
        }
        
        for col in self.df.columns:
            col_data = self.df[col]
            missing_count = col_data.isna().sum()
            missing_percentage = (missing_count / len(self.df)) * 100
            
            unique_values = col_data.nunique()
            is_constant = unique_values == 1
            
            # Determine data type
            if pd.api.types.is_numeric_dtype(col_data):
                data_type = "numeric"
            elif pd.api.types.is_datetime64_dtype(col_data):
                data_type = "datetime"
            else:
                data_type = "string"
                
                # Check if string column might be a datetime
                if data_type == "string" and not col_data.empty:
                    try:
                        non_null = col_data.dropna()
                        if len(non_null) > 0:
                            pd.to_datetime(non_null.iloc[0])
                            data_type = "potential_datetime"
                    except:
                        pass
            
            self.profile["columns"][col] = {
                "data_type": data_type,
                "missing_count": int(missing_count),
                "missing_percentage": float(missing_percentage),
                "unique_values": int(unique_values),
                "is_constant": bool(is_constant),
                "is_mostly_empty": missing_percentage > 50
            }
            
            # Add some basic stats for numeric columns
            if data_type == "numeric":
                self.profile["columns"][col].update({
                    "min": float(col_data.min()) if not col_data.empty else None,
                    "max": float(col_data.max()) if not col_data.empty else None,
                    "mean": float(col_data.mean()) if not col_data.empty else None
                })
        
        return self.profile
    
    def get_data_quality_score(self):
        """Calculate an overall data quality score"""
        if not self.profile or not self.df is not None:
            return 0
        
        # Simple quality scoring based on missing values and redundant columns
        column_scores = []
        for col_name, col_info in self.profile["columns"].items():
            # Penalize for missing values
            missing_score = 1 - (col_info["missing_percentage"] / 100)
            
            # Penalize constant columns
            redundancy_score = 0 if col_info["is_constant"] else 1
            
            # Combined score for this column
            column_score = (missing_score * 0.7) + (redundancy_score * 0.3)
            column_scores.append(column_score)
        
        # Overall data quality score (0-100)
        if column_scores:
            return round(sum(column_scores) / len(column_scores) * 100, 2)
        return 0
    
    def get_data_as_dict(self, max_rows=100):
        """Return dataframe as a list of dictionaries (for JSON serialization)"""
        if self.df is None:
            return []
        
        # Limit number of rows for performance
        df_sample = self.df.head(max_rows)
        
        # Convert to list of dicts, handling NaN values
        records = df_sample.replace({np.nan: None}).to_dict(orient='records')
        return records
    
    def get_column_names(self):
        """Get list of column names"""
        if self.df is None:
            return []
        return list(self.df.columns)