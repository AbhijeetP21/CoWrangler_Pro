import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib
import os

class MLRankingSystem:
    def __init__(self, model_path=None):
        # Initialize ML components
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        
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
            self.training_data = {
                'features': [],
                'scores': []
            }
    
    def rank_suggestions(self, data_analyzer, suggestions):
        """Rank suggestions using machine learning model"""
        if not suggestions:
            return []
            
        # Extract features for each suggestion
        features = []
        for suggestion in suggestions:
            suggestion_features = self._extract_features(suggestion, data_analyzer)
            features.append(suggestion_features)
            
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
            # Fall back to heuristic scoring if model isn't trained yet
            self._score_suggestions_heuristically(suggestions, data_analyzer)
            
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
        
        return ranked_suggestions
    
    def _extract_features(self, suggestion, analyzer):
        """Extract features for ML model from suggestion and data"""
        features = []
        
        # Get suggestion type as one-hot encoded feature
        type_map = {
            'drop_column': [1, 0, 0, 0, 0],
            'split': [0, 1, 0, 0, 0],
            'typecast': [0, 0, 1, 0, 0],
            'fill_missing': [0, 0, 0, 1, 0],
            'encoding': [0, 0, 0, 0, 1]
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
            
        # Overall dataset features
        features.append(df.isna().mean().mean())  # Overall missing rate
        
        # Return normalized feature vector
        return np.array(features)
        
    def _score_suggestions_heuristically(self, suggestions, data_analyzer):
        """Score suggestions using heuristics when ML model isn't ready"""
        # Calculate current quality as baseline
        for suggestion in suggestions:
            # Clone the data analyzer to simulate the transformation
            simulated_analyzer = self._clone_analyzer(data_analyzer)
            
            # Apply the transformation to the clone
            success = self._apply_transformation(simulated_analyzer, suggestion)
            
            if success:
                # Simple heuristic scoring based on suggestion type and data characteristics
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
                        'split': 5,
                        'typecast': 4,
                        'fill_missing': 6,
                        'encoding': 3
                    }
                    suggestion['quality_improvement'] = type_scores.get(suggestion_type, 2)
            else:
                suggestion['quality_improvement'] = 0
    
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
        import copy
        
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
            if suggestion["type"] == "drop_column":
                column = suggestion["column"]
                analyzer.df = analyzer.df.drop(columns=[column])
                # Update profile after transformation
                if hasattr(analyzer, '_generate_profile'):
                    analyzer._generate_profile()
                return True
            # elif suggestion["type"] == "split"
                
            # Additional transformation types would be implemented here
            # elif suggestion["type"] == "split":
            #     ...
            # elif suggestion["type"] == "typecast":
            #     ...
            
            return False
        except Exception as e:
            print(f"Error simulating transformation: {str(e)}")
            return False
            
    def record_feedback(self, suggestion, quality_score):
        """Record user feedback to improve model"""
        # Extract features for the suggestion
        features = suggestion.get('_features')  # Would need to store features in suggestion
        
        if features is not None and isinstance(quality_score, (int, float)):
            # Add to training data
            self.training_data['features'].append(features)
            self.training_data['scores'].append(quality_score)
            
            # Retrain if we have enough new data
            if len(self.training_data['scores']) % 5 == 0:  # Retrain every 5 new samples
                self._train_model()