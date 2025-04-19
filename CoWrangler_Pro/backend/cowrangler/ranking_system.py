import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib
import os
import copy

class MLRankingSystem:
    def __init__(self, model_path=None):
        # Initialize ML components
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path

        # Always initialize training data
        self.training_data = {
        'features': [],
        'scores': []
        }
        
        # Try to load pre-trained model if available
        if model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"Loaded ranking model from {model_path}")
            except:
                print(f"Could not load model from {model_path}, will train a new one")
                
        # Initialize with a default model if none loaded
        if self.model is None:
            self.model = RandomForestRegressor(
                n_estimators=50, 
                max_depth=10,
                random_state=42
            )
            # self.training_data = {
            #     'features': [],
            #     'scores': []
            # }
    
    def rank_suggestions(self, data_analyzer, suggestions):
        """Rank suggestions using machine learning model"""
        if not suggestions:
            return []
            
        # Extract features for each suggestion
        features = []
        for suggestion in suggestions:
            suggestion_features = self._extract_features(suggestion, data_analyzer)
            features.append(suggestion_features)
            # Store features in suggestion for feedback later
            suggestion['_features'] = suggestion_features.tolist()
            
        # Convert to numpy array for prediction
        features_array = np.array(features)
            
        # If we have a trained model, use it for prediction
        if hasattr(self.model, 'predict') and len(self.training_data['features']) > 10:
            # Scale features
            scaled_features = self.scaler.transform(features_array)
            
            # Predict quality improvement scores
            predicted_scores = self.model.predict(scaled_features)
            
            # Assign scores to suggestions
            for i, suggestion in enumerate(suggestions):
                suggestion['quality_improvement'] = float(predicted_scores[i])
                suggestion['ml_score'] = float(predicted_scores[i])  # Store ML score separately
        else:
            # Fall back to simulation-based scoring if model isn't trained yet
            self._score_suggestions_by_simulation(suggestions, data_analyzer)
            
            # Store features and scores for later training
            for i, suggestion in enumerate(suggestions):
                self.training_data['features'].append(features[i])
                self.training_data['scores'].append(suggestion['quality_improvement'])
                
            # Try to train model if we have enough data
            if len(self.training_data['features']) >= 10:
                self._train_model()
        
        # Sort suggestions by quality improvement (descending)
        ranked_suggestions = sorted(
            suggestions,
            key=lambda x: x.get('quality_improvement', 0),
            reverse=True
        )

        for suggestion in ranked_suggestions:
            if '_features' in suggestion and isinstance(suggestion['_features'], np.ndarray):
                suggestion['_features'] = suggestion['_features'].tolist()
        
        return ranked_suggestions
    
    def _extract_features(self, suggestion, analyzer):
        """Extract features for ML model from suggestion and data"""
        features = []
        
        # Get suggestion type as one-hot encoded feature
        type_map = {
            'drop_column': [1, 0, 0, 0, 0],
            'split_column': [0, 1, 0, 0, 0],
            'typecast_column': [0, 0, 1, 0, 0],
            'impute_missing': [0, 0, 0, 1, 0],
            'encode_categorical': [0, 0, 0, 0, 1]
        }
        suggestion_type = suggestion.get('type', 'unknown')
        features.extend(type_map.get(suggestion_type, [0, 0, 0, 0, 0]))
        
        # Add data quality metrics
        df = analyzer.df
        profile = analyzer.profile if hasattr(analyzer, 'profile') else {}
        
        # Dataset size features
        features.append(len(df.columns))
        features.append(len(df))
        
        # Column-specific features if this is a column operation
        if 'column' in suggestion:
            col = suggestion['column']
            if col in df.columns:
                # Missing value rate for column
                features.append(df[col].isna().mean())
                
                # Uniqueness ratio
                features.append(df[col].nunique() / len(df))
                
                # Is column numeric?
                features.append(1 if pd.api.types.is_numeric_dtype(df[col]) else 0)
                
                # Is column datetime?
                features.append(1 if pd.api.types.is_datetime64_dtype(df[col]) else 0)
                
                # Is column categorical?
                features.append(1 if pd.api.types.is_categorical_dtype(df[col]) else 0)
                
                # Column position (normalized)
                features.append(list(df.columns).index(col) / len(df.columns))
            else:
                # Placeholder values if column not found
                features.extend([0, 0, 0, 0, 0, 0])
        else:
            # Placeholder values for non-column operations
            features.extend([0, 0, 0, 0, 0, 0])
        
        # Special features for specific operation types
        if suggestion_type == 'split_column' and 'delimiter' in suggestion:
            delim_features = [0, 0, 0, 0, 0, 0]  # space, comma, dash, underscore, pipe, colon
            delim_map = {' ': 0, ',': 1, '-': 2, '_': 3, '|': 4, ':': 5}
            delim = suggestion.get('delimiter', '')
            if delim in delim_map:
                delim_features[delim_map[delim]] = 1
            features.extend(delim_features)
        else:
            features.extend([0, 0, 0, 0, 0, 0])  # Placeholder for delimiter features
        
        # Special features for typecast operations
        if suggestion_type == 'typecast_column' and 'target_type' in suggestion:
            type_features = [0, 0, 0, 0]  # int, bool, datetime, category
            target_type = suggestion.get('target_type', '')
            if target_type == 'int':
                type_features[0] = 1
            elif target_type == 'bool':
                type_features[1] = 1
            elif target_type == 'datetime':
                type_features[2] = 1
            elif target_type == 'category':
                type_features[3] = 1
            features.extend(type_features)
        else:
            features.extend([0, 0, 0, 0])  # Placeholder for typecast features
            
        # Overall dataset features
        features.append(df.isna().mean().mean())  # Overall missing rate
        
        # Add potential complexity score
        complexity_map = {
            'drop_column': 0.1,      # Very simple
            'impute_missing': 0.3,    
            'typecast_column': 0.4,
            'encode_categorical': 0.6,
            'split_column': 0.7      # More complex
        }
        features.append(complexity_map.get(suggestion_type, 0.5))
        
        # Return feature vector
        return np.array(features)
    
    def _score_suggestions_by_simulation(self, suggestions, data_analyzer):
        """Score suggestions by simulating transformations and measuring quality improvement"""
        # Calculate current quality as baseline
        current_quality = self._calculate_data_quality(data_analyzer)
        
        for suggestion in suggestions:
            # Clone the data analyzer to simulate the transformation
            simulated_analyzer = self._clone_analyzer(data_analyzer)
            
            # Apply the transformation to the clone
            success = self._apply_transformation(simulated_analyzer, suggestion)
            
            if success:
                # Calculate new quality after transformation
                new_quality = self._calculate_data_quality(simulated_analyzer)
                
                # Calculate improvement
                suggestion["quality_improvement"] = max(0, new_quality - current_quality)
            else:
                # If simulation failed, fall back to heuristic scoring
                self._score_heuristically(suggestion, data_analyzer)
    
    def _score_heuristically(self, suggestion, data_analyzer):
        """Score suggestions using heuristics when simulation fails"""
        suggestion_type = suggestion.get('type', '')
        
        if suggestion_type == 'drop_column':
            column = suggestion.get('column', '')
            col_data = data_analyzer.df.get(column)
            
            if col_data is not None:
                # Score based on column characteristics
                missing_rate = col_data.isna().mean()
                uniqueness = col_data.nunique() / len(data_analyzer.df)
                
                # Lower score for dropping columns with high uniqueness (more information)
                # Higher score for dropping columns with high missing rates
                suggestion['quality_improvement'] = (missing_rate * 8) - (uniqueness * 5) + 2
            else:
                suggestion['quality_improvement'] = 1
        else:
            # Default scores for other suggestion types
            type_scores = {
                'split_column': 5,
                'typecast_column': 4,
                'impute_missing': 6,
                'encode_categorical': 3
            }
            suggestion['quality_improvement'] = type_scores.get(suggestion_type, 2)
    
    def _calculate_data_quality(self, analyzer):
        """Calculate overall data quality score"""
        if not analyzer or not hasattr(analyzer, 'df') or analyzer.df is None:
            return 0
            
        df = analyzer.df
        profile = analyzer.profile if hasattr(analyzer, 'profile') else {}
        
        # Define weights for different quality factors
        weights = {
            "completeness": 0.35,  # Missing value reduction
            "redundancy": 0.25,    # Removal of redundant information
            "type_consistency": 0.20,  # Improvement in data types
            "uniformity": 0.20     # Data pattern consistency
        }
        
        # Calculate completeness score (penalize missing values)
        completeness = 1.0 - (df.isna().sum().sum() / (df.shape[0] * df.shape[1]))
        
        # Calculate redundancy score (penalize duplicate or constant columns)
        redundancy = 0.0
        if profile and "columns" in profile:
            constant_columns = sum(1 for col_info in profile["columns"].values() if col_info.get("is_constant", False))
            redundancy = constant_columns / max(len(profile["columns"]), 1)
        
        # Calculate type consistency score (reward proper data types)
        type_consistency = 0.0
        if profile and "columns" in profile:
            # Count columns with proper data types (not string/object for numeric data)
            proper_types = sum(1 for col_info in profile["columns"].values() 
                              if col_info.get("data_type") in ["numeric", "datetime"])
            type_consistency = proper_types / max(len(profile["columns"]), 1)
        
        # Calculate uniformity score (how consistent data patterns are)
        uniformity = 0.0
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check string length consistency for string columns
                str_lengths = df[col].astype(str).str.len()
                # Normalize standard deviation by mean (coefficient of variation)
                if str_lengths.mean() > 0:
                    variation = str_lengths.std() / str_lengths.mean()
                    uniformity += 1.0 - min(variation, 1.0)  # Lower variation = higher uniformity
        
        uniformity = uniformity / max(len(df.columns), 1)
        
        # Combine scores using weights
        quality_score = (
            weights["completeness"] * completeness +
            weights["redundancy"] * (1.0 - redundancy) +  # Lower redundancy is better
            weights["type_consistency"] * type_consistency +
            weights["uniformity"] * uniformity
        ) * 100  # Scale to 0-100
        
        return quality_score
    
    def _train_model(self):
        """Train the ML model on collected data"""
        if len(self.training_data['features']) < 10:
            return  # Need more data
            
        try:
            # Convert to numpy arrays
            X = np.array(self.training_data['features'])
            y = np.array(self.training_data['scores'])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            # Save model if path specified
            if self.model_path:
                joblib.dump(self.model, self.model_path)
                print(f"Saved trained ranking model to {self.model_path}")
                
            print("Trained ranking model on", len(y), "examples")
        except Exception as e:
            print(f"Error training model: {str(e)}")
    
    def _clone_analyzer(self, analyzer):
        """Create a copy of data analyzer to simulate transformations"""
        # Create a new instance
        clone = copy.copy(analyzer)
        
        # Deep copy the dataframe and profile
        if hasattr(analyzer, 'df') and analyzer.df is not None:
            clone.df = analyzer.df.copy()
        
        if hasattr(analyzer, 'profile'):
            clone.profile = copy.deepcopy(analyzer.profile)
            
        return clone
    
    def _apply_transformation(self, analyzer, suggestion):
        """Apply a transformation to the analyzer based on suggestion type"""
        try:
            suggestion_type = suggestion.get("type", "")
            
            if suggestion_type == "drop_column" and "column" in suggestion:
                column = suggestion["column"]
                if column in analyzer.df.columns:
                    analyzer.df = analyzer.df.drop(columns=[column])
                    if hasattr(analyzer, '_generate_profile'):
                        analyzer._generate_profile()
                    return True
                
            elif suggestion_type == "impute_missing" and "column" in suggestion and "strategy" in suggestion:
                column = suggestion["column"]
                strategy = suggestion["strategy"]
                
                if column in analyzer.df.columns:
                    if strategy == "mean":
                        analyzer.df[column] = analyzer.df[column].fillna(analyzer.df[column].mean())
                    elif strategy == "mode":
                        mode_value = analyzer.df[column].mode().iloc[0] if not analyzer.df[column].mode().empty else None
                        analyzer.df[column] = analyzer.df[column].fillna(mode_value)
                    else:
                        return False
                        
                    if hasattr(analyzer, '_generate_profile'):
                        analyzer._generate_profile()
                    return True
                    
            elif suggestion_type == "encode_categorical" and "column" in suggestion:
                column = suggestion["column"]
                
                if column in analyzer.df.columns:
                    # Simple simulation - replace with dummy value
                    analyzer.df[column] = 0  # Representing encoded values
                    if hasattr(analyzer, '_generate_profile'):
                        analyzer._generate_profile()
                    return True
                    
            elif suggestion_type == "split_column" and "column" in suggestion and "delimiter" in suggestion:
                column = suggestion["column"]
                delimiter = suggestion["delimiter"]
                
                if column in analyzer.df.columns:
                    # Simple simulation - replace with split columns
                    split_cols = analyzer.df[column].astype(str).str.split(delimiter, expand=True)
                    num_parts = split_cols.shape[1]
                    new_columns = [f"{column}_{i+1}" for i in range(num_parts)]
                    split_cols.columns = new_columns
                    
                    analyzer.df = analyzer.df.drop(columns=[column]).join(split_cols)
                    if hasattr(analyzer, '_generate_profile'):
                        analyzer._generate_profile()
                    return True
                    
            elif suggestion_type == "typecast_column" and "column" in suggestion and "target_type" in suggestion:
                column = suggestion["column"]
                target_type = suggestion["target_type"]
                
                if column in analyzer.df.columns:
                    # Simple simulation of type casting
                    try:
                        if target_type == "int":
                            analyzer.df[column] = analyzer.df[column].fillna(0).astype(int)
                        elif target_type == "datetime":
                            analyzer.df[column] = pd.to_datetime(analyzer.df[column], errors='coerce')
                        elif target_type == "category":
                            analyzer.df[column] = analyzer.df[column].astype('category')
                        elif target_type == "bool":
                            analyzer.df[column] = analyzer.df[column].astype(bool)
                            
                        if hasattr(analyzer, '_generate_profile'):
                            analyzer._generate_profile()
                        return True
                    except:
                        return False
                
            return False
        except Exception as e:
            print(f"Error simulating transformation: {str(e)}")
            return False
            
    def record_feedback(self, suggestion, quality_score):
        """Record user feedback to improve model"""
        # Extract features for the suggestion
        features = suggestion.get('_features')  # Should be stored during ranking
        
        if features is not None and isinstance(quality_score, (int, float)):
            # Add to training data
            self.training_data['features'].append(features)
            self.training_data['scores'].append(quality_score)
            
            # Retrain if we have enough new data
            if len(self.training_data['scores']) % 5 == 0:  # Retrain every 5 new samples
                self._train_model()
                
    def get_feature_importances(self):
        """Get feature importances from the trained model"""
        if hasattr(self.model, 'feature_importances_'):
            # Feature names for interpretation
            feature_names = [
                # Operation type one-hot encoding
                'op_drop_column', 'op_split_column', 'op_typecast', 'op_impute', 'op_encode',
                
                # Dataset features
                'num_columns', 'num_rows',
                
                # Column features
                'col_missing_rate', 'col_uniqueness', 'col_is_numeric', 
                'col_is_datetime', 'col_is_categorical', 'col_position',
                
                # Delimiter features
                'delim_space', 'delim_comma', 'delim_dash', 'delim_underscore', 
                'delim_pipe', 'delim_colon',
                
                # Typecast features
                'typecast_int', 'typecast_bool', 'typecast_datetime', 'typecast_category',
                
                # Overall features
                'dataset_missing_rate', 'operation_complexity'
            ]
            
            # Get importances
            importances = self.model.feature_importances_
            
            # Return as a sorted dictionary
            importance_dict = {name: imp for name, imp in zip(feature_names, importances)}
            return {k: v for k, v in sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)}
        
        return None