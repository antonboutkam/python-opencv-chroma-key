import cv2
import numpy as np

# === PARAMETERS ===
# Blue range in HSV (tune for your exact stick)
LOWER_BLUE = np.array([100, 150, 50])
UPPER_BLUE = np.array([140, 255, 255])

# Lightsaber colors (BGR)
CORE_COLOR = (255, 255, 255)     # Bright white core
GLOW_COLOR = (0, 255, 255)       # Cyan/blue glow

def draw_lightsaber(frame, pt1, pt2, core_thickness=4, glow_layers=6):
    """
    Draws a glowing lightsaber line on a frame.
    """
    overlay = frame.copy()

    # Draw glow from thick to thin
    for i in range(glow_layers, 0, -1):
        alpha = 0.03 * i
        thickness = core_thickness + i * 2
        cv2.line(overlay, pt1, pt2, GLOW_COLOR, thickness, cv2.LINE_AA)
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Draw bright white core
    cv2.line(frame, pt1, pt2, CORE_COLOR, core_thickness, cv2.LINE_AA)
    return frame

def detect_stick_line(mask):
    """
    Detects the largest contour and approximates it as a stick (line).
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 100:  # Ignore tiny noise
        return None

    [vx, vy, x, y] = cv2.fitLine(largest, cv2.DIST_L2, 0, 0.01, 0.01)
    left_y = int((-x * vy / vx) + y)
    right_y = int(((mask.shape[1] - x) * vy / vx) + y)
    pt1 = (0, left_y)
    pt2 = (mask.shape[1] - 1, right_y)
    return pt1, pt2

def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    result = frame.copy()

    stick_line = detect_stick_line(mask)
    if stick_line:
        pt1, pt2 = stick_line
        result = draw_lightsaber(result, pt1, pt2)

    return result

cap = cv2.VideoCapture(1)  # or "your_video.mp4"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    result = process_frame(frame)
    cv2.imshow("Lightsaber Effect", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()