import pandas as pd

class TypecastColumnLearner:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer

    def generate_suggestions(self):
        suggestions = []

        if not self.data_analyzer or self.data_analyzer.df is None:
            return suggestions

        df = self.data_analyzer.df

        for col_name in df.columns:
            col_data = df[col_name]
            dtype = col_data.dtype

            # Float columns
            if pd.api.types.is_float_dtype(dtype):
                tolerance = 1e-8

                # Float → Int (only if values are all whole)
                if ((col_data.dropna() % 1).abs() < tolerance).all():
                    suggestions.append(self._make_suggestion(
                        col_name, "int",
                        "All values are whole numbers. Safe to cast to int.",
                        f"df['{col_name}'] = df['{col_name}'].astype('Int64')",
                        quality=4.5
                    ))
                else:
                    # Float → Int (with rounding)
                    suggestions.append(self._make_suggestion(
                        col_name, "int",
                        "Values have decimals. Round before casting to int (may cause precision loss).",
                        f"df['{col_name}'] = df['{col_name}'].round().astype('Int64')",
                        quality=3.5
                    ))

                    # Float → Int (truncation)
                    suggestions.append(self._make_suggestion(
                        col_name, "int",
                        "Values have decimals. Truncate before casting to int (may cause data loss).",
                        f"df['{col_name}'] = df['{col_name}'].astype('Int64')",
                        quality=3
                    ))

                # Float → Category
                if col_data.nunique(dropna=True) <= 10:
                    suggestions.append(self._make_suggestion(
                        col_name, "category",
                        "Float column with few unique values. Can be cast to category.",
                        f"df['{col_name}'] = df['{col_name}'].astype('category')",
                        quality=3
                    ))

            # Int → Bool
            if pd.api.types.is_integer_dtype(dtype):
                unique_vals = set(col_data.dropna().unique())
                if unique_vals.issubset({0, 1}):
                    suggestions.append(self._make_suggestion(
                        col_name, "bool",
                        "Only 0 and 1 values. Can be cast to boolean.",
                        f"df['{col_name}'] = df['{col_name}'].astype(bool)",
                        quality=3.5
                    ))

            # Object → Datetime / Category
            if pd.api.types.is_object_dtype(dtype):
                try:
                    pd.to_datetime(col_data.dropna().sample(min(10, len(col_data))), errors='raise')
                    suggestions.append(self._make_suggestion(
                        col_name, "datetime",
                        "Values look like dates. Can be cast to datetime.",
                        f"df['{col_name}'] = pd.to_datetime(df['{col_name}'])",
                        quality=4.5
                    ))
                except Exception:
                    pass

                if col_data.nunique(dropna=True) <= 20:
                    suggestions.append(self._make_suggestion(
                        col_name, "category",
                        "Low-cardinality text column. Can be cast to category.",
                        f"df['{col_name}'] = df['{col_name}'].astype('category')",
                        quality=3
                    ))

        return suggestions

    def _make_suggestion(self, column, to_type, reason, code, quality):
        return {
            "type": "typecast_column",
            "title": f"Cast '{column}' to {to_type}",
            "explanation": f"REASON: {reason}",
            "column": column,
            "target_type": to_type,
            "code": code,
            "quality_improvement": quality
        }

    def apply_transformation(self, suggestion):
        if not self.data_analyzer or self.data_analyzer.df is None:
            return False

        if suggestion["type"] != "typecast_column":
            print(f"Incorrect suggestion type: {suggestion['type']}")
            return False

        try:
            column = suggestion["column"]
            target_type = suggestion["target_type"]
            code = suggestion["code"]
            col_data = self.data_analyzer.df[column]

            original_dtype = col_data.dtype

            # Smart casting logic
            if "round()" in code:
                self.data_analyzer.df[column] = col_data.round().astype('Int64')
            elif "astype('Int64')" in code:
                self.data_analyzer.df[column] = col_data.astype('Int64')
            elif target_type == "datetime":
                self.data_analyzer.df[column] = pd.to_datetime(col_data)
            else:
                self.data_analyzer.df[column] = col_data.astype(target_type)

            new_dtype = self.data_analyzer.df[column].dtype
            self.data_analyzer._generate_profile()

            print(f"Casted '{column}' from {original_dtype} to {new_dtype}")
            return True

        except Exception as e:
            print(f"Error casting column '{column}': {str(e)}")
            return False
