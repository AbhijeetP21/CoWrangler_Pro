import pandas as pd
from sklearn.preprocessing import LabelEncoder

class EncodeCategoricalLearner:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer
        self.max_unique_threshold = 10  # You can adjust as needed

    def generate_suggestions(self):
        suggestions = []

        if not self.data_analyzer or not self.data_analyzer.profile:
            return suggestions

        for col_name, col_info in self.data_analyzer.profile["columns"].items():
            if (
                col_info["data_type"] in ["string", "potential_datetime"]
                and not col_info.get("is_constant", False)
                and not col_info.get("is_mostly_empty", False)
                and col_info.get("unique_values", float("inf")) <= self.max_unique_threshold
            ):
                suggestions.append({
                    "type": "encode_categorical",
                    "title": f"Label encode {col_name}",
                    "explanation": f"REASON: Low-cardinality categorical column with {col_info['unique_values']} unique values.",
                    "column": col_name,
                    "strategy": "label_encoding",
                    "code": self._generate_code(col_name),
                    "quality_improvement": 4
                })

        return suggestions

    def _generate_code(self, column_name):
        return (
            f"from sklearn.preprocessing import LabelEncoder\n"
            f"le = LabelEncoder()\n"
            f"df['{column_name}'] = le.fit_transform(df['{column_name}'])"
        )

    def apply_transformation(self, suggestion):
        if not self.data_analyzer or self.data_analyzer.df is None:
            print("DataAnalyzer or DataFrame is not available.")
            return False

        if suggestion["type"] != "encode_categorical":
            print(f"Incorrect suggestion type: {suggestion['type']}")
            return False

        try:
            column = suggestion["column"]

            if column not in self.data_analyzer.df.columns:
                print(f"Column '{column}' not found in DataFrame.")
                return False

            le = LabelEncoder()
            self.data_analyzer.df[column] = le.fit_transform(self.data_analyzer.df[column].astype(str))

            # Re-profile after transformation
            self.data_analyzer._generate_profile()
            print(f"Successfully label-encoded column '{column}'")
            return True

        except Exception as e:
            print(f"Error applying label encoding: {str(e)}")
            return False
