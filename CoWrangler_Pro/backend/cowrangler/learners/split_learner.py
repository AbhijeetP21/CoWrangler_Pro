import pandas as pd

class SplitColumnLearner:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer
        self.default_delimiters = [" ", ",", "-", "_", "|", ":"]

    def generate_suggestions(self):
        suggestions = []

        if not self.data_analyzer or not self.data_analyzer.profile:
            return suggestions

        for col_name, col_info in self.data_analyzer.profile["columns"].items():
            if col_info["data_type"] not in ["string", "potential_datetime"]:
                continue

            sample_series = self.data_analyzer.df[col_name].dropna().astype(str).head(20)

            for delim in self.default_delimiters:
                split_counts = sample_series.apply(lambda x: len(x.split(delim)))
                if (split_counts > 1).mean() >= 0.6:
                    max_parts = int(split_counts.max())
                    preview_cols = [f"{col_name}_{i+1}" for i in range(max_parts)]

                    suggestions.append({
                        "type": "split_column",
                        "title": f"Split '{col_name}' by '{delim}'",
                        "explanation": f"REASON: Values in column '{col_name}' appear to be splittable by '{delim}' into multiple parts.",
                        "column": col_name,
                        "delimiter": delim,
                        "new_columns": preview_cols,
                        "code": self._generate_code(col_name, delim, preview_cols),
                        "quality_improvement": 3 + 0.5 * max_parts
                    })
                    break  # Only one split suggestion per column

        return suggestions

    def _generate_code(self, column_name, delimiter, new_columns):
        col_str = ", ".join([f"'{col}'" for col in new_columns])
        return (
            f"split_cols = df['{column_name}'].str.split('{delimiter}', expand=True)\n"
            f"split_cols.columns = [{col_str}]\n"
            f"df = df.drop(columns=['{column_name}']).join(split_cols)"
        )

    def apply_transformation(self, suggestion):
        if not self.data_analyzer or self.data_analyzer.df is None:
            print("DataAnalyzer or DataFrame is not available.")
            return False

        if suggestion["type"] != "split_column":
            print(f"Incorrect suggestion type: {suggestion['type']}")
            return False

        try:
            column = suggestion["column"]
            delimiter = suggestion["delimiter"]

            if column not in self.data_analyzer.df.columns:
                print(f"Column '{column}' not found in DataFrame.")
                return False

            # Split the column
            split_cols = self.data_analyzer.df[column].astype(str).str.split(delimiter, expand=True)

            # Drop completely empty columns
            non_empty_cols = [
                col_idx for col_idx in split_cols.columns
                if not split_cols[col_idx].replace('', pd.NA).isna().all()
            ]
            split_cols = split_cols[non_empty_cols]

            # Rename columns dynamically
            num_parts = split_cols.shape[1]
            new_columns = [f"{column}_{i+1}" for i in range(num_parts)]
            split_cols.columns = new_columns

            # Apply the transformation
            self.data_analyzer.df = self.data_analyzer.df.drop(columns=[column]).join(split_cols)
            self.data_analyzer._generate_profile()

            print(f"Successfully split column '{column}' into {num_parts} cleaned columns.")
            return True

        except Exception as e:
            print(f"Error splitting column '{column}': {str(e)}")
            return False
