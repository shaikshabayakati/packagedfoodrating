import cv2
import numpy as np
import json
import time
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
            'nutrition_data': nutrition_data
        }, None

    except Exception as e:
        return None, f"Analysis error: {str(e)}"


def display_results(frame, results, y_offset=30):
    """Display nutrition analysis results on the frame."""
    if not results:
        return frame
    
    # Create semi-transparent overlay
    overlay = frame.copy()
    
    # Display barcode
    cv2.putText(overlay, f"Barcode: {results['barcode']}", 
                (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Display nutrition score with color coding
    score = results['score']
    color = (0, 255, 0) if score >= 70 else (0, 165, 255) if score >= 40 else (0, 0, 255)
    cv2.putText(overlay, f"Nutrition Score: {score}/100", 
                (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Display comment (truncated for display)
    comment = results['comment']
    lines = []
    max_width = 80
    words = comment.split()
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    
    # Display up to 3 lines of comment
    for i, line in enumerate(lines[:3]):
        cv2.putText(overlay, line, 
                    (10, y_offset + 60 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return overlay


def main():
    cap = open_camera()
    if cap is None:
        raise RuntimeError(
            "Unable to access the webcam. Check Windows Camera privacy settings, close other apps using the camera, and try CAP_DSHOW/CAP_MSMF."
        )

    # Set a reasonable resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    window = "Nutrition Barcode Scanner"
    cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)

    # Variables for barcode analysis
    last_barcode = None
    last_analysis_time = 0
    analysis_cooldown = 3  # seconds between analyses of same barcode
    current_results = None
    analyzing = False
    
    print("Nutrition Barcode Scanner Started!")
    print("Controls:")
    print("  SPACE - Force analyze detected barcode")
    print("  S - Save current analysis to file")
    print("  C - Clear current results")
    print("  Q - Quit")

    try:
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                # Couldn't grab a frame; continue trying
                cv2.imshow(window, np.zeros((480, 640, 3), dtype=np.uint8))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # Decode barcodes from the live frame
            barcodes = zbar_decode(frame)
            detected_barcode = None
            
            for barcode in barcodes:
                data = barcode.data.decode('utf-8', errors='ignore')
                detected_barcode = data
                
                # Draw polygon around the detected barcode
                pts = np.array([barcode.polygon], dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (255, 0, 255), 3)
                
                # Put decoded text near the barcode rectangle
                x, y, w, h = barcode.rect
                cv2.putText(frame, data, (x, max(0, y - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 220, 50), 2)
                
                # Auto-analyze if it's a new barcode or enough time has passed
                current_time = time.time()
                if (not analyzing and 
                    (data != last_barcode or current_time - last_analysis_time > analysis_cooldown)):
                    
                    analyzing = True
                    print(f"Auto-analyzing barcode: {data}")
                    
                    results, error = analyze_barcode(data)
                    if results:
                        current_results = results
                        last_barcode = data
                        last_analysis_time = current_time
                        print(f"Analysis complete: Score {results['score']}/100")
                    else:
                        print(f"Analysis failed: {error}")
                        current_results = None
                    
                    analyzing = False

            # Display current results if available
            if current_results:
                frame = display_results(frame, current_results)
            
            # Add status text
            status_text = "Analyzing..." if analyzing else ("Barcode detected!" if detected_barcode else "Scan a barcode...")
            cv2.putText(frame, status_text, (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Show the live preview
            cv2.imshow(window, frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and detected_barcode and not analyzing:
                # Force analysis
                analyzing = True
                print(f"Force analyzing barcode: {detected_barcode}")
                results, error = analyze_barcode(detected_barcode)
                if results:
                    current_results = results
                    last_barcode = detected_barcode
                    last_analysis_time = time.time()
                    print(f"Analysis complete: Score {results['score']}/100")
                else:
                    print(f"Analysis failed: {error}")
                analyzing = False
            elif key == ord('c'):
                # Clear results
                current_results = None
                last_barcode = None
                print("Results cleared")
            elif key == ord('s') and current_results:
                # Save results to file
                filename = f"nutrition_analysis_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(current_results, f, indent=2)
                print(f"Results saved to {filename}")

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()