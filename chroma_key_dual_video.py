import cv2
import numpy as np

def nothing(x):
    pass

# === CONFIG ===
USE_WEBCAM = True  # Als False, gebruik dan foreground.mp4 als input
FOREGROUND_PATH = "foreground.mp4"
BACKGROUND_PATH = "background.mp4"

# === VIDEO INPUT ===
if USE_WEBCAM:
    cap_foreground = cv2.VideoCapture(0)
else:
    cap_foreground = cv2.VideoCapture(FOREGROUND_PATH)

cap_background = cv2.VideoCapture(BACKGROUND_PATH)

# === WINDOW & TRACKBARS ===
cv2.namedWindow("Chroma Key")
cv2.createTrackbar("Lower-H", "Chroma Key", 35, 179, nothing)
cv2.createTrackbar("Lower-S", "Chroma Key", 40, 255, nothing)
cv2.createTrackbar("Lower-V", "Chroma Key", 40, 255, nothing)
cv2.createTrackbar("Upper-H", "Chroma Key", 85, 179, nothing)
cv2.createTrackbar("Upper-S", "Chroma Key", 255, 255, nothing)
cv2.createTrackbar("Upper-V", "Chroma Key", 255, 255, nothing)

while True:
    ret_fg, frame_fg = cap_foreground.read()
    ret_bg, frame_bg = cap_background.read()

    if not ret_fg or not ret_bg:
        print("🚨 Einde van een van de videostreams bereikt.")
        break

    # Resize background to match foreground
    frame_bg = cv2.resize(frame_bg, (frame_fg.shape[1], frame_fg.shape[0]))

    # HSV conversie
    hsv = cv2.cvtColor(frame_fg, cv2.COLOR_BGR2HSV)

    # Lees HSV grenzen van trackbars
    l_h = cv2.getTrackbarPos("Lower-H", "Chroma Key")
    l_s = cv2.getTrackbarPos("Lower-S", "Chroma Key")
    l_v = cv2.getTrackbarPos("Lower-V", "Chroma Key")
    u_h = cv2.getTrackbarPos("Upper-H", "Chroma Key")
    u_s = cv2.getTrackbarPos("Upper-S", "Chroma Key")
    u_v = cv2.getTrackbarPos("Upper-V", "Chroma Key")

    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    # Masker voor chroma key
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask_inv = cv2.bitwise_not(mask)

    # Extract foreground en background
    fg = cv2.bitwise_and(frame_fg, frame_fg, mask=mask_inv)
    bg = cv2.bitwise_and(frame_bg, frame_bg, mask=mask)

    # Combineer
    final = cv2.add(fg, bg)

    # Toon resultaat
    cv2.imshow("Chroma Key", final)

    # Stop op ESC
    key = cv2.waitKey(1)
    if key == 27:
        break

# Cleanup
cap_foreground.release()
cap_background.release()
cv2.destroyAllWindows()
