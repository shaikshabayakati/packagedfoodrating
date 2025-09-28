import cv2
import numpy as np
import json
import time
import sys
from pyzbar.pyzbar import decode as zbar_decode

# Import your existing modules
from barcode_scanner import fetch_openfood
from nutrition_analyzer import calculate_nutrition_score
from utils import clean_markdown


def open_camera():
    """Try opening the default camera on Windows with common backends."""
    backends = []
    # Some OpenCV builds don't expose these constants; guard accordingly
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(cv2.CAP_MSMF)
    # Fallback to any backend
    backends.append(cv2.CAP_ANY if hasattr(cv2, "CAP_ANY") else 0)

    for be in backends:
        try:
            cap = cv2.VideoCapture(0, be) if be != 0 else cv2.VideoCapture(0)
            if cap.isOpened():
                return cap
            cap.release()
        except Exception:
            pass
    return None


def analyze_barcode(barcode_data):
    """Analyze barcode using your existing nutrition analyzer."""
    try:
        print(f"Analyzing barcode: {barcode_data}")
        
        # Get nutrition data from OpenFoodFacts
        nutrition_data, error = fetch_openfood(barcode_data)
        
        if error:
            return None, f"Error: {error}"
        
        if not nutrition_data:
            return None, "No nutrition data found for this barcode"

        # Calculate nutrition score and get comment
        score, comment = calculate_nutrition_score(nutrition_data)
        
        # Clean markdown from comment
        clean_comment = clean_markdown(comment)
        
        return {
            'barcode': barcode_data,
            'score': score,
            'comment': clean_comment,
            'nutrition_data': nutrition_data,
            'details': json.dumps(nutrition_data, indent=2)
        }, None

    except Exception as e:
        return None, f"Analysis error: {str(e)}"


def main():
    """Main function that auto-stops on barcode detection and returns results."""
    cap = open_camera()
    if cap is None:
        print("ERROR: Unable to access webcam")
        return None

    # Set a reasonable resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    window = "Nutrition Barcode Scanner - Point camera at barcode"
    cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
    
    print("Barcode Scanner Started!")
    print("Point camera at a barcode - will auto-detect and process...")
    print("Press Q to quit without scanning")

    detected_results = None
    last_detected_barcode = None
    detection_time = None
    processing = False
    
    try:
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                # Couldn't grab a frame; continue trying
                cv2.imshow(window, np.zeros((480, 640, 3), dtype=np.uint8))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # Skip processing if already processing a barcode
            if processing:
                cv2.putText(frame, "PROCESSING... Please wait", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.imshow(window, frame)
                cv2.waitKey(100)
                continue

            # Add instruction text to frame
            cv2.putText(frame, "Point camera at product barcode", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press Q to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # Decode barcodes from the live frame
            barcodes = zbar_decode(frame)
            
            current_time = time.time()
            
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8', errors='ignore')
                
                # Check if this is the same barcode detected recently (within 3 seconds)
                if (last_detected_barcode == barcode_data and 
                    detection_time and 
                    current_time - detection_time < 3.0):
                    continue  # Skip duplicate detection
                
                # Mark as processing to prevent multiple detections
                processing = True
                last_detected_barcode = barcode_data
                detection_time = current_time
                
                # Draw detection indicator
                pts = np.array([barcode.polygon], dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                
                x, y, w, h = barcode.rect
                cv2.putText(frame, f"DETECTED: {barcode_data}", (x, max(0, y - 10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, "Processing...", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # Show detection frame briefly
                cv2.imshow(window, frame)
                cv2.waitKey(500)  # Show for 0.5 seconds
                
                print(f"Barcode detected: {barcode_data}")
                print("Processing nutrition data...")
                
                # Analyze the barcode
                results, error = analyze_barcode(barcode_data)
                if results:
                    detected_results = results
                    print(f"Analysis complete! Score: {results['score']}/100")
                    
                    # Save results to a temporary file for web interface
                    with open('live_scan_results.json', 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    # Close camera and return results immediately
                    cap.release()
                    cv2.destroyAllWindows()
                    return results
                else:
                    print(f"Analysis failed: {error}")
                    processing = False  # Allow next detection
                    # Continue scanning for another barcode
                    break
            
            # Show the live preview
            cv2.imshow(window, frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
    return detected_results


if __name__ == "__main__":
    results = main()
    if results:
        print("\n=== SCAN RESULTS ===")
        print(f"Barcode: {results['barcode']}")
        print(f"Nutrition Score: {results['score']}/100")
        print(f"Comment: {results['comment']}")
    else:
        print("No barcode was detected or processed.")