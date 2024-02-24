import cv2
import numpy as np
import math


class VisionInput:
    def __init__(self, fov: tuple, res: tuple, height, angle):
        self.w = res[0]
        self.h = res[1]
        self.cap = cv2.VideoCapture(0)
        VisionInput.FOV = fov
        VisionInput.RES = res
        VisionInput.CAM_HEIGHT = height
        VisionInput.CAM_ANGLE = angle

    def getFrame(self):
        ret, frame = self.cap.read()

        if not ret:
            print('frame malf')
        exit

        fr = cv2.resize(frame, (self.w, self.h), interpolation=cv2.INTER_AREA)
        return fr