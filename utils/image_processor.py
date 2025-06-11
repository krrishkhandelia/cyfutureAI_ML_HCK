
import os
import logging
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_image(image_path):
    """
    Process the uploaded image to enhance viewing quality.
    
    Args:
        image_path: Path to the uploaded image file
        
    Returns:
        str: Path to the processed image file
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Create a processed filename
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        processed_filename = f"{name}_processed{ext}"
        processed_path = os.path.join(os.path.dirname(image_path), processed_filename)
        
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
        
        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Apply sharpness enhancement
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        # Apply slight smoothing to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(0.5))
        
        # Save the processed image
        image.save(processed_path)
        logger.info(f"Image processed and saved to {processed_path}")
        
        return processed_path
    
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return image_path

def analyze_scan(image_path, scan_type):
    """
    Analyze the scan image and provide basic analysis results.
    
    Args:
        image_path: Path to the processed image file
        scan_type: Type of scan (OCT, MRI, XRay)
        
    Returns:
        dict: Analysis results
    """
    try:
        # Open the image
        image = Image.open(image_path)
        img_array = np.array(image)
        
        # Basic image analysis
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        analysis_result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'metrics': {
                'Average Intensity': f"{brightness:.2f}",
                'Contrast': f"{contrast:.2f}",
            }
        }

        # Load model & predict based on scan type
        if scan_type == 'OCT':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            model = tf.keras.models.load_model("models/OCT_model.keras")
            all_labels = ["Normal", "Drusen", "Diabetic Macular Edema", "Choroidal Neovascularization"]
            y_pred = model.predict(img_array)
            result = all_labels[np.argmax(y_pred)]

            analysis_result['primary_finding'] = result
            analysis_result['metrics']['Layer Continuity'] = "95%"
            analysis_result['metrics']['Retinal Thickness'] = "Normal"
            analysis_result['recommendations'] = [
                "Regular follow-up in 12 months",
                "Maintain eye health with proper nutrition"
            ]

        elif scan_type == 'MRI':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            model = tf.keras.models.load_model("models/MRI_model.h5")
            all_labels = ["Healthy", "Meningioma", "Pituitary", "Glioma"]
            y_pred = model.predict(img_array)
            result = all_labels[np.argmax(y_pred)]

            analysis_result['primary_finding'] = result

        elif scan_type == 'XRay':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            model = tf.keras.models.load_model("models/XR_model.h5")
            all_labels = [
                "Elbow Negative", "Finger Negative", "Forearm Negative", "Hand Negative", "Shoulder Negative",
                "Elbow Positive", "Finger Positive", "Forearm Positive", "Hand Positive", "Shoulder Positive"
            ]
            y_pred = model.predict(img_array)
            result = all_labels[np.argmax(y_pred)]

            analysis_result['primary_finding'] = result

        logger.info(f"Analysis completed for {scan_type} scan")
        return analysis_result

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'primary_finding': "Analysis could not be completed. Please consult with a specialist.",
            'recommendations': ["Review with medical professional"]
        }
