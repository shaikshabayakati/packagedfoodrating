"""
Barcode scanning and OpenFoodFacts API integration modules
"""
import requests
import json
from PIL import Image, ImageOps
from pyzbar.pyzbar import decode, ZBarSymbol


def validate_and_format_barcode(barcode):
    """Validate and format barcode for OpenFoodFacts"""
    # Remove any non-digit characters
    clean_barcode = ''.join(filter(str.isdigit, barcode))
    
    if not clean_barcode:
        return None, "Invalid barcode: no digits found"
    
    # Handle different barcode lengths
    if len(clean_barcode) == 12:  # UPC-A
        return clean_barcode, None
    elif len(clean_barcode) == 13:  # EAN-13
        return clean_barcode, None
    elif len(clean_barcode) == 8:   # EAN-8
        return clean_barcode, None
    elif len(clean_barcode) == 11:  # Convert to EAN-13 by adding leading zeros
        return clean_barcode.zfill(13), None
    elif len(clean_barcode) < 8:
        return clean_barcode.zfill(13), None
    else:
        return clean_barcode, None


def fetch_openfood(barcode):
    """Fetch nutrition data from OpenFoodFacts API"""
    # Validate and format barcode first
    formatted_barcode, error = validate_and_format_barcode(barcode)
    if error:
        return None, error
    
    url = f"https://world.openfoodfacts.net/api/v2/product/{formatted_barcode}.json"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return None, f"Product not found for barcode: {formatted_barcode}"
        elif response.status_code != 200:
            return None, f"API Error: {response.status_code} - {response.reason}"
        
        json_data = response.json()
        
        if json_data.get('status') != 1:
            return None, f"Product not found in OpenFoodFacts database for barcode: {formatted_barcode}"
        
        nutriments = json_data.get('product', {}).get('nutriments', {})
        
        if not nutriments:
            return None, f"No nutrition data available for barcode: {formatted_barcode}"
        
        return nutriments, None
        
    except requests.exceptions.Timeout:
        return None, "Request timeout - please try again"
    except requests.exceptions.ConnectionError:
        return None, "Connection error - please check your internet connection"
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except json.JSONDecodeError:
        return None, "Invalid response from API"


def scan_barcode_from_image(image_path):
    """Extract barcode from image and get nutrition data"""
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise Exception(f"Error opening image: {e}")

    symbols = [ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.UPCA, ZBarSymbol.UPCE]

    for angle in (0, 90, 180, 270):
        im = img.rotate(angle, expand=True)
        im = ImageOps.grayscale(im)
        im = ImageOps.autocontrast(im)
        if min(im.size) < 1000:
            im = im.resize((im.width * 2, im.height * 2))

        results = decode(im, symbols=symbols)
        if results:
            for r in results:
                s = "".join(ch for ch in r.data.decode("utf-8", "ignore") if ch.isdigit())
                
                # Handle different barcode types
                if r.type == "EAN13" and len(s) == 13:
                    data, error = fetch_openfood(s)
                    if not error:
                        return data
                elif r.type == "UPCA" and len(s) == 12:
                    # Try UPC-A as is, then with leading zero
                    data, error = fetch_openfood(s)
                    if not error:
                        return data
                    # Try with leading zero to make it EAN-13
                    data, error = fetch_openfood("0" + s)
                    if not error:
                        return data
                elif r.type == "EAN8" and len(s) == 8:
                    data, error = fetch_openfood(s)
                    if not error:
                        return data
                elif r.type == "UPCE" and len(s) >= 6:
                    # UPC-E needs to be converted to UPC-A format
                    data, error = fetch_openfood(s)
                    if not error:
                        return data
                
                # If we have any valid barcode digits, try as generic barcode
                if len(s) >= 8:
                    data, error = fetch_openfood(s)
                    if not error:
                        return data

    raise Exception("No barcode found in image")