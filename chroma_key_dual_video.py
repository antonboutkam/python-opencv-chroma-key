import cv2
import numpy as np
from utils import center_cube
from utils import avg_color_hsv
from utils import draw_text_bubble
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
outfile = f"output_{timestamp}.avi"

def nothing(x):
    pass

# === CONFIG ===
USE_WEBCAM = True  # Als False, gebruik dan foreground.mp4 als input
FOREGROUND_PATH = "foreground.mp4"
BACKGROUND_PATH = "overlay/silverado.mp4"



# === VIDEO INPUT ===
if USE_WEBCAM:
    cap_foreground = cv2.VideoCapture(1)
else:
    cap_foreground = cv2.VideoCapture(FOREGROUND_PATH)

cap_background = cv2.VideoCapture(BACKGROUND_PATH)


width = int(cap_foreground.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap_foreground.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # correct: it's a function
outputVideo = cv2.VideoWriter(outfile, fourcc, 30.0, (width, height))


# === WINDOW & TRACKBARS ===
cv2.namedWindow("Chroma Key")
black = False
autoHsv = True

if autoHsv:
    cv2.createTrackbar("Color space H", "Chroma Key", 2, 179, nothing)
    cv2.createTrackbar("Color space S", "Chroma Key", 5, 255, nothing)
    cv2.createTrackbar("Color space V", "Chroma Key", 5, 255, nothing)

elif black:
    cv2.createTrackbar("Lower-H", "Chroma Key", 25, 179, nothing)
    cv2.createTrackbar("Lower-S", "Chroma Key", 40, 255, nothing)
    cv2.createTrackbar("Lower-V", "Chroma Key", 0, 255, nothing)
    cv2.createTrackbar("Upper-H", "Chroma Key", 255, 179, nothing)
    cv2.createTrackbar("Upper-S", "Chroma Key", 255, 255, nothing)
    cv2.createTrackbar("Upper-V", "Chroma Key", 255, 255, nothing)
else :
    cv2.createTrackbar("Lower-H", "Chroma Key", 0, 179, nothing)
    cv2.createTrackbar("Lower-S", "Chroma Key", 0, 255, nothing)
    cv2.createTrackbar("Lower-V", "Chroma Key", 0, 255, nothing)
    cv2.createTrackbar("Upper-H", "Chroma Key", 10, 179, nothing)
    cv2.createTrackbar("Upper-S", "Chroma Key", 5, 255, nothing)
    cv2.createTrackbar("Upper-V", "Chroma Key", 255, 255, nothing)

ret_fg, frame_fg = cap_foreground.read()
small_cube = center_cube(frame_fg)
cv2.imshow("20x20 blokje", small_cube)
avg_hsv = avg_color_hsv(small_cube)

while True:
    ret_fg, frame_fg = cap_foreground.read()
    ret_bg, frame_bg = cap_background.read()


    if not ret_fg or not ret_bg:
        print("🚨 Einde van een van de videostreams bereikt.")
        cap_background = cv2.VideoCapture(BACKGROUND_PATH)
        ret_fg, frame_fg = cap_foreground.read()
        ret_bg, frame_bg = cap_background.read()
        # break

    # Resize background to match foreground
    frame_bg = cv2.resize(frame_bg, (frame_fg.shape[1], frame_fg.shape[0]))

    # HSV conversie
    hsv = cv2.cvtColor(frame_fg, cv2.COLOR_BGR2HSV)

    # Lees HSV grenzen van trackbars
    if autoHsv:

        color_space_h = cv2.getTrackbarPos("Color space H", "Chroma Key")
        color_space_s = cv2.getTrackbarPos("Color space S", "Chroma Key")
        color_space_v = cv2.getTrackbarPos("Color space V", "Chroma Key")

        l_h = avg_hsv[0] - color_space_h
        l_s = avg_hsv[1] - color_space_s
        l_v = avg_hsv[2] - color_space_v
        u_h = avg_hsv[0] + color_space_h
        u_s = avg_hsv[1] + color_space_s
        u_v = avg_hsv[2] + color_space_v
    else:
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
    combined_fg_bg = cv2.add(fg, bg)
    draw_text_bubble(combined_fg_bg, 'NOS het weerbericht', position=(50,50), font_scale=1, thickness=2)
    # Toon resultaat
    cv2.imshow("Chroma Key", combined_fg_bg)

    print("Save frame to video")
    outputVideo.write(combined_fg_bg)
    outputVideo.write(combined_fg_bg)

    # Stop op ESC
    key = cv2.waitKey(1)
    if key == 27:
        break


# Cleanup
cap_foreground.release()
cap_background.release()
cv2.destroyAllWindows()
