import cv2
import numpy as np
import os
from PIL import Image
import pytesseract

# Check if Tesseract is available
TESSERACT_AVAILABLE = True
try:
    pytesseract.get_tesseract_version()
except:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract OCR is not installed. OCR functionality will be limited.")
    print("To install Tesseract on Windows:")
    print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Install and add to PATH")
    print("3. Or use: pip install tesseract-ocr")

def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    if not TESSERACT_AVAILABLE:
        return "OCR not available. Please install Tesseract OCR."
    
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            return "Error: Could not read the image file."
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply median blur to remove noise
        gray = cv2.medianBlur(gray, 3)
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(gray)
        
        return text.strip()
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

def preprocess_image_for_better_ocr(image_path):
    """
    Advanced preprocessing for better OCR accuracy.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        numpy.ndarray: Preprocessed image
    """
    if not TESSERACT_AVAILABLE:
        return None
    
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Apply morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Apply closing to fill gaps
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        
        return closing
        
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return None

def extract_text_with_preprocessing(image_path):
    """
    Extract text using advanced preprocessing for better accuracy.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    if not TESSERACT_AVAILABLE:
        return "OCR not available. Please install Tesseract OCR."
    
    try:
        # Apply preprocessing
        preprocessed = preprocess_image_for_better_ocr(image_path)
        if preprocessed is None:
            return "Error: Could not preprocess the image."
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(preprocessed)
        
        return text.strip()
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

def validate_image_file(file_path):
    """
    Validate if the uploaded file is a valid image.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist."
        
        # Check file size (max 10MB)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return False, "File size too large. Maximum size is 10MB."
        
        # Check if it's a valid image
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, "Valid image file."
        except Exception:
            return False, "Invalid image file format."
            
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def parse_raw_materials(text):
    """
    Parse raw materials from OCR text.
    
    Args:
        text (str): OCR extracted text
        
    Returns:
        list: List of raw material names
    """
    if not TESSERACT_AVAILABLE:
        return ["Sample: Onions", "Sample: Tomatoes", "Sample: Potatoes"]
    
    # Common raw materials for street food vendors
    common_materials = [
        'onion', 'onions', 'tomato', 'tomatoes', 'potato', 'potatoes',
        'ginger', 'garlic', 'chili', 'chillies', 'coriander', 'mint',
        'lemon', 'lime', 'oil', 'ghee', 'butter', 'flour', 'rice',
        'lentils', 'pulses', 'spices', 'salt', 'sugar', 'milk',
        'cheese', 'bread', 'eggs', 'chicken', 'mutton', 'fish',
        'vegetables', 'fruits', 'herbs', 'seasoning', 'sauce',
        'ketchup', 'mayonnaise', 'mustard', 'vinegar', 'soy sauce'
    ]
    
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Find matching materials
    found_materials = []
    for material in common_materials:
        if material in text_lower:
            found_materials.append(material.title())
    
    # Remove duplicates and return
    return list(set(found_materials))

# Test function for development
def test_ocr():
    """
    Test OCR functionality.
    """
    if not TESSERACT_AVAILABLE:
        print("Tesseract not available. OCR functionality disabled.")
        return False
    
    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "Sample Bill: Onions, Tomatoes, Potatoes", fill='black', font=font)
        
        # Save test image
        test_path = "test_bill.png"
        img.save(test_path)
        
        # Test OCR
        text = extract_text_from_image(test_path)
        print(f"OCR Test Result: {text}")
        
        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)
        
        return True
        
    except Exception as e:
        print(f"OCR test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_ocr() 