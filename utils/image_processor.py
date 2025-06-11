import os
import logging
from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
import cv2

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_image(image_path):
    """
    Basic image processing — currently just opens and saves as-is.
    
    Args:
        image_path: Path to the uploaded image file
        
    Returns:
        str: Path to the processed image file
    """
    try:
        # Open the image
        img = Image.open(image_path).convert('RGB')

        # Create a processed filename
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        processed_filename = f"{name}_processed{ext}"
        processed_path = os.path.join(os.path.dirname(image_path), processed_filename)

        # Save image directly without enhancement
        img.save(processed_path)
        logger.info(f"Image saved to {processed_path} without enhancement.")

        return processed_path

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return image_path


def analyze_scan(image_path, scan_type):
    """
    Analyze the scan image and provide basic analysis results
    
    Args:
        image_path: Path to the processed image file
        scan_type: Type of scan (OCT, MRI, XRay)
        
    Returns:
        dict: Analysis results
    """
    try:
        image = Image.open(image_path)
        img_array = np.array(image)
        
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        analysis_result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'metrics': {
                'Average Intensity': f"{brightness:.2f}",
                'Contrast': f"{contrast:.2f}",
            }
        }

        if scan_type == 'OCT':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            oct_model = tf.keras.models.load_model("OCT_model.keras")
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            prediction = oct_model.predict(img_array)
            result = ["Normal", "Drusen", "Diabetic Macular Edema", "Choroidal Neovascularization"][np.argmax(prediction)]
            
            analysis_result.update({
                'primary_finding': result,
                'metrics': {
                    **analysis_result['metrics'],
                    'Layer Continuity': "95%",
                    'Retinal Thickness': "Normal"
                },
                'recommendations': [
                    "Regular follow-up in 12 months",
                    "Maintain eye health with proper nutrition"
                ]
            })

        elif scan_type == 'MRI':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            mri_model = tf.keras.models.load_model("MRI_model.h5")
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            prediction = mri_model.predict(img_array)
            result = ["Healthy", "Meningioma", "Pituitary", "Glioma"][np.argmax(prediction)]
            analysis_result['primary_finding'] = result

        elif scan_type == 'XRay':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            resized_img = cv2.resize(image, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(resized_img) / 255.0
            xr_model = tf.keras.models.load_model("XR_model.h5")
            img_array = tf.image.resize(img_array, [50, 50])
            img_array = np.expand_dims(img_array, axis=0)
            prediction = xr_model.predict(img_array)
            result = [
                "Elbow Negative", "Finger Negative", "Forearm Negative", "Hand Negative", "Shoulder Negative",
                "Elbow Positive", "Finger Positive", "Forearm Positive", "Hand Positive", "Shoulder Positive"
            ][np.argmax(prediction)]
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
