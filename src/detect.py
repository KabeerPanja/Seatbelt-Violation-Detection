from ultralytics import YOLO
import cv2
import numpy as np
from config import *
from src.ocr import extract_text
from src.db import insert

seatbelt_model = YOLO(SEATBELT_MODEL)
plate_model = YOLO(PLATE_MODEL)


def center(box):
    x1, y1, x2, y2 = box
    return ((x1+x2)//2, (y1+y2)//2)


def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


# ================= IMAGE / FRAME PROCESSING =================
def process_frame(frame):

    result = seatbelt_model(frame)[0]

    violators = []
    plates = []

    # seatbelt detection
    for box in result.boxes:
        cls = int(box.cls[0])
        label = result.names[cls]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if "no" in label:
            violators.append((x1, y1, x2, y2))

    # plate detection
    plate_result = plate_model(frame)[0]

    for box in plate_result.boxes:
        conf = float(box.conf[0])

        if conf < 0.5:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        plates.append((x1, y1, x2, y2))

    # matching
    for v in violators:
        vc = center(v)

        best = None
        best_d = 999999

        for p in plates:
            pc = center(p)
            d = dist(vc, pc)

            if d < best_d:
                best_d = d
                best = p

        if best:
            x1,y1,x2,y2 = best
            crop = frame[y1:y2, x1:x2]

            text = extract_text(crop)
            if text and len(text) > 3:
                insert(text)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,text,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

    return frame


# ================= IMAGE WRAPPER =================
def process_image(path):
    img = cv2.imread(path)
    return process_frame(img)


# ================= VIDEO PROCESSING =================
def process_video(path):
    cap = cv2.VideoCapture(path)

    w = int(cap.get(3))
    h = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(
        "output.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w,h)
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = process_frame(frame)
        out.write(frame)

    cap.release()
    out.release()

    return "output.mp4"