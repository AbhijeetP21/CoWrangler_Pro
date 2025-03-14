class DropColumnLearner:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer
    
    def generate_suggestions(self):
        """Generate suggestions for dropping columns"""
        suggestions = []
        
        if not self.data_analyzer or not self.data_analyzer.profile:
            return suggestions
        
        for col_name, col_info in self.data_analyzer.profile["columns"].items():
            # Suggest dropping constant columns
            if col_info["is_constant"]:
                value = self.data_analyzer.df[col_name].iloc[0]
                value_str = str(value) if value is not None else "null"
                
                suggestions.append({
                    "type": "drop_column",
                    "title": f"Drop {col_name}",
                    "explanation": f"REASON: contains constant value {value_str}",
                    "column": col_name,
                    "code": self._generate_code(col_name),
                    "quality_improvement": 5  # Fixed score for demonstration
                })
            
            # Suggest dropping mostly empty columns
            elif col_info["is_mostly_empty"]:
                percentage = round(col_info["missing_percentage"])
                suggestions.append({
                    "type": "drop_column",
                    "title": f"Drop {col_name}",
                    "explanation": f"REASON: {percentage}% missing values",
                    "column": col_name,
                    "code": self._generate_code(col_name),
                    "quality_improvement": min(percentage / 10, 10)  # Score based on missing percentage
                })
        
        return suggestions
    
    def _generate_code(self, column_name):
        """Generate Python code for dropping a column"""
        return f"df = df.drop(columns = ['{column_name}'])"
    
    def apply_transformation(self, suggestion):
        """Apply the transformation to the dataframe"""
        if not self.data_analyzer or not self.data_analyzer.df is not None:
            return False
        
        if suggestion["type"] != "drop_column":
            return False
        
        try:
            column = suggestion["column"]
            self.data_analyzer.df = self.data_analyzer.df.drop(columns=[column])
            
            # Update profile after transformation
            self.data_analyzer._generate_profile()
            return True
        except Exception as e:
            print(f"Error applying drop column transformation: {str(e)}")
            return False