from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/upload', methods=['POST'])
def upload_data():
    return jsonify({'message': 'File upload endpoint (to be implemented)'})

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    return jsonify({'message': 'Suggestions endpoint (to be implemented)'})

@app.route('/api/apply-transformation', methods=['POST'])
def apply_transformation():
    return jsonify({'message': 'Apply transformation endpoint (to be implemented)'})

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from CoWrangler backend!'})

if __name__ == '__main__':
    app.run(debug=True)