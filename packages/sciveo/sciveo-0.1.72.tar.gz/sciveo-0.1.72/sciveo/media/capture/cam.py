#
# Pavlin Georgiev, Softel Labs
#
# This is a proprietary file and may not be copied,
# distributed, or modified without express permission
# from the owner. For licensing inquiries, please
# contact pavlin@softel.bg.
#
# 2024
#

import time
import numpy as np
import cv2
import base64
import threading
import mss

from sciveo.tools.logger import *
from sciveo.tools.daemon import DaemonBase
from sciveo.tools.timers import FPSCounter


class CaptureBase(DaemonBase):
  def __init__(self, src, tag="capture", period=0):
    super().__init__(period=period)
    self.src = src
    self.tag = tag
    self.lock_frame = threading.Lock()
    self.frame = None
    self.fps = FPSCounter(period=10, tag=f"{self.tag} [{self.src}]")

  def close(self):
    pass

  def read(self):
    with self.lock_frame:
      return self.frame

  def read_buf(self):
    frame = self.read()
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

  def read_frame(self):
    pass

  def loop(self):
    with self.lock_frame:
      self.read_frame()
      self.fps.update()


class CameraDaemon(CaptureBase):
  def __init__(self, cam_id=0, period=0):
    super().__init__(src=cam_id, tag="cam", period=period)
    self.cap = cv2.VideoCapture(cam_id)
    debug(cam_id, "warming...")
    time.sleep(1)

  def close(self):
    self.cap.release()

  def read_frame(self):
    ret, self.frame = self.cap.read()


class PredictorCameraDaemon(DaemonBase):
  def __init__(self, args, cam, client):
    super().__init__()
    self.args = args
    self.client = client
    self.cam = cam
    self.frame = None
    self.fps = FPSCounter(period=10, tag="predictor")
    self.lock_frame = threading.Lock()

  def loop(self):
    frame = self.cam.read()
    image_base64 = self.client.image_encoded(image=frame)

    if self.args.input_type == 0:
      params = {
        "predictor": self.args.predictor,
        "compressed": self.args.compressed,
        "X": [{
          "messages": [{
            "role": "user",
            "content": [
              {"type": "image"},
              {"type": "text", "text": self.args.prompt},
            ]
          }],
          "images": [image_base64]
        }]
      }
    elif self.args.input_type == 1:
      params = {
        "predictor": self.args.predictor,
        "compressed": self.args.compressed,
        "X": [image_base64]
      }

    r = self.client.predict(params)
    prediction = r[self.args.predictor][0]
    info(prediction)
    self.fps.update()

    if isinstance(prediction, list) == False and isinstance(prediction, dict) == False:
      cv2.putText(frame, prediction, (10, 100),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.3, color=(255, 255, 255), thickness=3
      )

    with self.lock_frame:
      self.frame = frame

  def read(self):
    with self.lock_frame:
      return self.frame


class ScreenDaemon(CaptureBase):
  def __init__(self, src=1, period=0, region=None):
    super().__init__(src=src, tag="screen", period=period)
    self.sct = mss.mss()
    self.monitor = self.sct.monitors[src]

    if region:
      self.monitor = {
        "left": region[0],
        "top": region[1],
        "width": region[2],
        "height": region[3],
      }
      debug(f"Capturing screen region: {self.monitor}")
    else:
      self.monitor = self.sct.monitors[src]
      debug(f"Capturing full monitor {src}: {self.monitor}")

  def close(self):
    self.sct.close()

  def read_frame(self):
    sct_img = self.sct.grab(self.monitor)
    self.frame = np.array(sct_img)
    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGRA2BGR)


if __name__ == '__main__':
  cap = ScreenDaemon(src=1, region=[300,300, 800,800])
  cap.start()
  while(True):
    frame = cap.read()
    frame = cv2.resize(frame, (250, 250))
    cv2.imshow("captured", frame)
    cv2.waitKey(1)
