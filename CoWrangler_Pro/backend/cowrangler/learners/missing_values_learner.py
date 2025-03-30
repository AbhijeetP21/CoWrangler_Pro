
class ImputeMissingLearner:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer

    def generate_suggestions(self):
        suggestions = []

        if not self.data_analyzer or not self.data_analyzer.profile:
            return suggestions

        for col_name, col_info in self.data_analyzer.profile["columns"].items():
            if col_info["is_mostly_empty"]:
                strategy = self._determine_strategy(col_name, col_info)
                if strategy:
                    suggestions.append({
                        "type": "impute_missing",
                        "title": f"Impute {col_name}",
                        "explanation": f"REASON: {round(col_info['missing_percentage'])}% missing values. Suggested strategy: {strategy}",
                        "column": col_name,
                        "strategy": strategy,
                        "code": self._generate_code(col_name, strategy),
                        "quality_improvement": min(col_info["missing_percentage"] / 10, 10)
                    })

        return suggestions

    def _determine_strategy(self, column_name, col_info):
        dtype = col_info["data_type"]
        if dtype == "numeric":
            return "mean"
        elif dtype in ["string", "potential_datetime"]:
            return "mode"
        else:
            return None

    def _generate_code(self, column_name, strategy):
        if strategy == "mean":
            return f"df['{column_name}'] = df['{column_name}'].fillna(df['{column_name}'].mean())"
        elif strategy == "mode":
            return f"df['{column_name}'] = df['{column_name}'].fillna(df['{column_name}'].mode().iloc[0])"
        return "# Unknown strategy"

    def apply_transformation(self, suggestion):
        if not self.data_analyzer or self.data_analyzer.df is None:
            return False

        if suggestion["type"] != "impute_missing":
            return False

        try:
            column = suggestion["column"]
            strategy = suggestion["strategy"]

            if strategy == "mean":
                self.data_analyzer.df[column] = self.data_analyzer.df[column].fillna(self.data_analyzer.df[column].mean())
            elif strategy == "mode":
                self.data_analyzer.df[column] = self.data_analyzer.df[column].fillna(self.data_analyzer.df[column].mode().iloc[0])
            else:
                return False

            self.data_analyzer._generate_profile()
            return True
        except Exception as e:
            print(f"Error applying imputation: {str(e)}")
            return False
