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
BACKGROUND_PATH = "loops/production ID_4650933.mp4"



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


# Maak een nieuwe window
cv2.namedWindow("Chroma Key")
autoHsv = True

avg_h, avg_s, avg_v = 0, 0, 0

if autoHsv:
    # We loopen over 200x frames om het beeld (kleur te stabiliseren)
    for x in range(200):
        ret_fg, frame_fg = cap_foreground.read()
        cv2.imshow("FrameFG", frame_fg)
        small_cube = center_cube(frame_fg)
        cv2.imshow("40x40 blokje", small_cube)
        avg_h, avg_s, avg_v = avg_color_hsv(small_cube)

    cv2.createTrackbar("Hue", "Chroma Key", 2, 179, nothing)
    cv2.createTrackbar("Saturation", "Chroma Key", 4, 255, nothing)
    cv2.createTrackbar("Value", "Chroma Key", 4, 255, nothing)
else:
    cv2.createTrackbar("Lower-H", "Chroma Key", 0, 179, nothing)
    cv2.createTrackbar("Lower-S", "Chroma Key", 0, 255, nothing)
    cv2.createTrackbar("Lower-V", "Chroma Key", 0, 255, nothing)
    cv2.createTrackbar("Upper-H", "Chroma Key", 10, 179, nothing)
    cv2.createTrackbar("Upper-S", "Chroma Key", 5, 255, nothing)
    cv2.createTrackbar("Upper-V", "Chroma Key", 255, 255, nothing)



# Blijf eindeloos loopen
print("Start greenscreen")
while True:
    ret_fg, frame_fg = cap_foreground.read()

    # We stoppen een frame uit een video in frame_bg
    ret_bg, frame_bg = cap_background.read()

    if not ret_fg or not ret_bg:
        # Einde van de video stream bereikt, we openen hem opnieuw en starten bij het begin.
        cap_background = cv2.VideoCapture(BACKGROUND_PATH)
        ret_fg, frame_fg = cap_foreground.read()
        ret_bg, frame_bg = cap_background.read()
        # break

    # Achtergrond video even groot maken als voorgrond video.
    frame_bg = cv2.resize(frame_bg, (frame_fg.shape[1], frame_fg.shape[0]))

    # Pas een blurr to om het beeld minder scherp te maken voordat je gaat masken
    blurr = True
    if blurr:
        # Create a new video with a small blurr
        frame_fg_blurr = cv2.GaussianBlur(frame_fg, (5, 5), 0)
        # BGR naar HSV conversie
        hsv = cv2.cvtColor(frame_fg_blurr, cv2.COLOR_BGR2HSV)
    else:
        # BGR naar HSV conversie
        hsv = cv2.cvtColor(frame_fg, cv2.COLOR_BGR2HSV)



    # Lees HSV grenzen van trackbars
    if autoHsv:

        color_space_h = cv2.getTrackbarPos("Hue", "Chroma Key")
        color_space_s = cv2.getTrackbarPos("Saturation", "Chroma Key")
        color_space_v = cv2.getTrackbarPos("Value", "Chroma Key")

        l_h = avg_h - color_space_h
        l_s = avg_s - color_space_s
        l_v = avg_v - color_space_v
        u_h = avg_h + color_space_h
        u_s = avg_s + color_space_s
        u_v = avg_v + color_space_v
    else:
        l_h = cv2.getTrackbarPos("Lower-H", "Chroma Key")
        l_s = cv2.getTrackbarPos("Lower-S", "Chroma Key")
        l_v = cv2.getTrackbarPos("Lower-V", "Chroma Key")
        u_h = cv2.getTrackbarPos("Upper-H", "Chroma Key")
        u_s = cv2.getTrackbarPos("Upper-S", "Chroma Key")
        u_v = cv2.getTrackbarPos("Upper-V", "Chroma Key")

    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    # Masker voor chroma key (welke pixels vervangen we)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Masker voor origineel (welke pixels laten we zoals ze zijn)
    mask_inv = cv2.bitwise_not(mask)

    # Extract foreground en background
    fg = cv2.bitwise_and(frame_fg, frame_fg, mask=mask_inv)
    bg = cv2.bitwise_and(frame_bg, frame_bg, mask=mask)

    # Combineer foreground en background afbeeldingen
    combined_fg_bg = cv2.add(fg, bg)

    # Voeg tekst toe aan het schem
    # draw_text_bubble(combined_fg_bg, 'NOS het weerbericht', position=(50,50), font_scale=1, thickness=2)

    # Verdubbel de grootte van de opname om weer te geven op het scherm
    combined_fg_bg_large = cv2.resize(combined_fg_bg, (combined_fg_bg.shape[1]*2, combined_fg_bg.shape[0]*2))
    cv2.imshow("Chroma Key", combined_fg_bg_large)

    # Sla frame op in video bestand
    outputVideo.write(combined_fg_bg)


    # Stop op ESC
    key = cv2.waitKey(1)
    if key == 27:
        break


# Cleanup
cap_foreground.release()
cap_background.release()
cv2.destroyAllWindows()
