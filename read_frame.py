import base64
import datetime
import os

import cv2

def readframe():
    cap = cv2.VideoCapture(os.environ.get("BILI_VIDEO_CHANNEL"))
    rets = []
    begin = datetime.datetime.now()
    while (datetime.datetime.now()-begin).total_seconds()<15:
        ret, frame = cap.read()
        _, buffer = cv2.imencode(".jpg", frame)
        rets.append(base64.b64encode(buffer).decode("utf-8"))
    return rets
    # 将帧保存为图像


