import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import uuid
from utils.image_processor import process_image, analyze_scan
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
import matplotlib.patches as patches
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure upload folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Session storage for multiple uploads
TEMP_STORAGE = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page with upload form"""
    return render_template('index.html')

@app.route('/enhanced')
def enhanced_upload():
    """Render the enhanced upload page"""
    return render_template('enhanced_upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to result page"""
    # Check if a file was submitted
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    scan_type = request.form.get('scan_type')
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    # Validate scan type
    if not scan_type:
        flash('Please select a scan type', 'error')
        return redirect(request.url)
    
    # Check if file is allowed
    if file and allowed_file(file.filename):
        # Create a unique filename to prevent overwrites
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Process image for better viewing
        processed_filepath = process_image(filepath)
        
        # Generate a session ID to store images
        session_id = str(uuid.uuid4())
        TEMP_STORAGE[session_id] = {
            'original': unique_filename,
            'processed': os.path.basename(processed_filepath),
            'scan_type': scan_type
        }
        
        return redirect(url_for('result', session_id=session_id))
    else:
        flash('File type not allowed. Please upload a PNG or JPEG image.', 'error')
        return redirect(request.url)

@app.route('/result/<session_id>')
def result(session_id):
    """Display the uploaded and processed image with analysis results"""
    if session_id not in TEMP_STORAGE:
        flash('Session expired or invalid. Please upload again.', 'error')
        return redirect(url_for('index'))
    
    session_data = TEMP_STORAGE[session_id]
    original_image = session_data['original']
    processed_image = session_data['processed']
    scan_type = session_data['scan_type']
    
    # Analyze the processed image
    analysis_result = analyze_scan(
        os.path.join(app.config['UPLOAD_FOLDER'], processed_image),
        scan_type
    )
    
    return render_template(
        'result.html',
        original_image=original_image,
        processed_image=processed_image,
        scan_type=scan_type,
        analysis_result=analysis_result
    )

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    flash('File too large. Please upload a smaller file.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    flash('An error occurred while processing your request. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
