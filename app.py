"""
Flask web application for nutrition score analysis
"""
import os
import tempfile
import json
import subprocess
import sys
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our modular components
from barcode_scanner import fetch_openfood, scan_barcode_from_image
from nutrition_analyzer import calculate_nutrition_score
from utils import clean_markdown, validate_file_upload

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/')
def index():
    return render_template('nutrition_score.html')



@app.route('/analyze_barcode', methods=['POST'])
def analyze_barcode():
    try:
        data = request.get_json()
        barcode = data.get('barcode', '').strip()
        
        if not barcode:
            return jsonify({'error': 'No barcode provided'}), 400

        # Get nutrition data from barcode
        nutrition_data, error = fetch_openfood(barcode)
        
        if error:
            return jsonify({'error': error}), 400
        
        if not nutrition_data:
            return jsonify({'error': 'No nutrition data found for this barcode'}), 404

        # Calculate nutrition score and get comment
        score, comment = calculate_nutrition_score(nutrition_data)
        
        # Clean markdown from comment
        clean_comment = clean_markdown(comment)
        
        # Format nutrition details for display
        details = json.dumps(nutrition_data, indent=2)
        
        return jsonify({
            'score': score,
            'comment': clean_comment,
            'details': details
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        try:
            try:
                nutrition_data = scan_barcode_from_image(temp_path)
            except Exception as scan_error:
                return jsonify({'error': str(scan_error), 'show_manual': True}), 400
            
            if not nutrition_data:
                return jsonify({'error': 'No nutrition data found for this product', 'show_manual': True}), 404

            score, comment = calculate_nutrition_score(nutrition_data)
            
            # Clean markdown from comment
            clean_comment = clean_markdown(comment)
            
            # Format nutrition details for display
            details = json.dumps(nutrition_data, indent=2)
            
            return jsonify({
                'score': score,
                'comment': clean_comment,
                'details': details
            })

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({'error': str(e), 'show_manual': True}), 500

@app.route('/start_live_scan', methods=['POST'])
def start_live_scan():
    """Start the live camera barcode scanner and return results"""
    try:
        opencv_path = os.path.join(os.path.dirname(__file__), 'opencv_auto_stop.py')
        if not os.path.exists(opencv_path):
            return jsonify({'error': 'Camera scanner not found. Please ensure opencv_auto_stop.py exists.'}), 500
        
        try:
            result = subprocess.run([
                sys.executable, opencv_path
            ], capture_output=True, text=True, timeout=120, cwd=os.path.dirname(__file__))  # 2 minute timeout
            
            results_file = os.path.join(os.path.dirname(__file__), 'live_scan_results.json')
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        results = json.load(f)
                    
                    os.remove(results_file)
                    
                    return jsonify({
                        'score': results['score'],
                        'comment': results['comment'],
                        'details': results['details']
                    })
                    
                except Exception as e:
                    return jsonify({'error': f'Error reading scan results: {str(e)}'}), 500
            else:
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "Camera scanning failed"
                    return jsonify({'error': error_msg}), 500
                else:
                    return jsonify({'error': 'Scanning was cancelled by user'}), 400
            
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Camera scanning timed out after 2 minutes'}), 408
        except Exception as e:
            return jsonify({'error': f'Failed to start camera scanner: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1000)