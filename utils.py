import cv2
import numpy as np


def center_cube(frame):
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    blokje = frame[cy - 40:cy + 40, cx - 40:cx + 40]
    return blokje


def avg_color_hsv(frame):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(frame_hsv)
    mean_h = int(np.mean(h))
    mean_s = int(np.mean(s))
    mean_v = int(np.mean(v))

    return mean_h, mean_s, mean_v


def draw_text_bubble(frame, text, position, font_scale=1, thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_w, text_h = text_size

    x, y = position

    padding = 10
    radius = 15

    # Bepaal grootte van de 'bubble'
    box_x1 = x
    box_y1 = y - text_h - padding
    box_x2 = x + text_w + 2 * padding
    box_y2 = y + padding

    # Zorg dat de ROI binnen het frame valt
    box_x1 = max(box_x1, 0)
    box_y1 = max(box_y1, 0)
    box_x2 = min(box_x2, frame.shape[1])
    box_y2 = min(box_y2, frame.shape[0])

    # Teken witte rechthoek met afgeronde hoeken (simulatie)
    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x1 + radius, box_y1), (box_x2 - radius, box_y2), (255, 255, 255), -1)
    cv2.rectangle(overlay, (box_x1, box_y1 + radius), (box_x2, box_y2 - radius), (255, 255, 255), -1)
    cv2.circle(overlay, (box_x1 + radius, box_y1 + radius), radius, (255, 255, 255), -1)
    cv2.circle(overlay, (box_x2 - radius, box_y1 + radius), radius, (255, 255, 255), -1)
    cv2.circle(overlay, (box_x1 + radius, box_y2 - radius), radius, (255, 255, 255), -1)
    cv2.circle(overlay, (box_x2 - radius, box_y2 - radius), radius, (255, 255, 255), -1)

    # Voeg de bubble toe met wat transparantie (optioneel)
    alpha = 0.85
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Teken de tekst erbovenop
    text_org = (x + padding, y)
    cv2.putText(frame, text, text_org, font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
