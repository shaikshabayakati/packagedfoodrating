"""
Robust Windows webcam test for OpenCV.
- Tries multiple device indices (0..3)
- Tries common Windows backends (CAP_DSHOW, CAP_MSMF, fallback)
- Shows preview and prints which combo worked
- Press 'q' to quit
"""
import time
import cv2
import numpy as np


def try_open(idx, backend=None):
    try:
        if backend is None:
            cap = cv2.VideoCapture(idx)
        else:
            cap = cv2.VideoCapture(idx, backend)
        if cap.isOpened():
            # Grab one test frame to verify it really works
            ok, frame = cap.read()
            if ok and frame is not None:
                return cap
        cap.release()
    except Exception:
        pass
    return None


def enumerate_backends():
    backends = []
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(cv2.CAP_MSMF)
    backends.append(cv2.CAP_ANY if hasattr(cv2, "CAP_ANY") else None)
    return backends


def main():
    backends = enumerate_backends()
    worked = None

    for idx in range(0, 4):
        for be in backends:
            cap = try_open(idx, be)
            if cap is not None:
                worked = (idx, be)
                print(f"Camera opened: index={idx}, backend={'CAP_ANY' if be in (None, getattr(cv2,'CAP_ANY',None)) else be}")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                win = f"Camera Test (idx={idx}, be={be})"
                cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
                t0 = time.time()
                try:
                    while True:
                        ok, frame = cap.read()
                        if not ok or frame is None:
                            frame = np.zeros((480, 640, 3), dtype=np.uint8)
                            cv2.putText(frame, "No frame", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                        cv2.imshow(win, frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        if time.time() - t0 > 5:
                            # Show 5 seconds then move on automatically
                            break
                finally:
                    cap.release()
                    cv2.destroyAllWindows()
            else:
                print(f"Failed: index={idx}, backend={be}")

    if worked is None:
        print("No camera combination worked. Suggestions:\n"
              "1) Windows Settings > Privacy & security > Camera: allow apps and desktop apps\n"
              "2) Close apps that might be using the camera (Teams, Zoom, etc.)\n"
              "3) Update camera drivers in Device Manager\n"
              "4) Try USB replug or a different port\n"
              "5) Try installing opencv-contrib-python if missing backends\n")


if __name__ == "__main__":
    main()
