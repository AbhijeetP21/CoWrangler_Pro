from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import json
import pandas as pd
from cowrangler.data_analysis import DataAnalyzer
from cowrangler.suggestion_engine import SuggestionEngine

app = Flask(__name__)
CORS(app)

# Global state - in a real application, you would use a database
data_analyzer = None
suggestion_engine = None

@app.route('/api/upload', methods=['POST'])
def upload_data():
    global data_analyzer, suggestion_engine
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Determine file type from extension
        file_type = 'csv'  # Default
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            file_type = 'excel'
        
        # Create data analyzer and load file
        data_analyzer = DataAnalyzer()
        file_content = file.read()
        file_stream = io.BytesIO(file_content)
        
        if file_type == 'csv':
            df = pd.read_csv(file_stream)
        else:
            df = pd.read_excel(file_stream)
        
        data_analyzer.df = df
        data_analyzer._generate_profile()
        
        # Initialize suggestion engine
        suggestion_engine = SuggestionEngine(data_analyzer)
        
        # Return basic info about the loaded data
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': file.filename,
            'row_count': data_analyzer.profile.get('row_count', 0),
            'column_count': data_analyzer.profile.get('column_count', 0),
            'columns': data_analyzer.get_column_names()
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    global data_analyzer
    
    if data_analyzer is None or data_analyzer.df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    max_rows = int(request.args.get('max_rows', 100))
    data = data_analyzer.get_data_as_dict(max_rows)
    
    return jsonify({
        'data': data,
        'columns': data_analyzer.get_column_names(),
        'total_rows': len(data_analyzer.df),
        'returned_rows': len(data)
    })

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    global suggestion_engine
    
    if suggestion_engine is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    suggestions = suggestion_engine.generate_suggestions()
    
    # Add IDs to suggestions for frontend reference
    for i, suggestion in enumerate(suggestions):
        suggestion['id'] = i + 1
    
    return jsonify({'suggestions': suggestions})

@app.route('/api/apply-transformation', methods=['POST'])
def apply_transformation():
    global suggestion_engine, data_analyzer
    
    if suggestion_engine is None or data_analyzer is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    suggestion = request.json.get('suggestion')
    if not suggestion:
        return jsonify({'error': 'No suggestion provided'}), 400
    
    success = suggestion_engine.apply_transformation(suggestion)
    
    if success:
        return jsonify({
            'message': 'Transformation applied successfully',
            'new_data': data_analyzer.get_data_as_dict(100),
            'columns': data_analyzer.get_column_names(),
            'total_rows': len(data_analyzer.df)
        })
    else:
        return jsonify({'error': 'Failed to apply transformation'}), 400

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000...")
    app.run(debug=True)