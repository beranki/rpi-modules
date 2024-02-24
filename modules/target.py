import cv2
import math
from vision_input import VisionInput

class Target:
    def __init__(self, contour, target_type):
        self.contour = contour
        self.target_type = target_type
        self.heights = {"CUBE": 0.24/2, "CONE": 0.33/2}

    def __str__(self):
        return self.target_type + " coords - " + self.contour

    def getType(self):
        return self.target_type

    def getContour(self):
        return self.contour

    def getBoundingRect(self):
        return cv2.boundingRect(self.contour)

    def get_yaw_degrees(self):
        x, y, w, h = self.getBoundingRect()
        center_tag = x + (w/2)
        center_cam = VisionInput.RES[0]/2
        B = center_tag - center_cam
        A = center_cam
        theta = math.atan(B * math.tan(math.radians(VisionInput.FOV[0] / 2)) / A)
        return math.degrees(theta)

    def get_pitch_degrees(self):
        x, y, w, h = self.getBoundingRect()
        center_tag = y + (h/2)
        center_cam = VisionInput.RES[1]/2
        B = center_cam - center_tag
        A = center_cam
        theta = math.atan(B * math.tan(math.radians(VisionInput.FOV[1] / 2)) / A)
        return math.degrees(theta)

    def get_distance_meters(self):
        height = self.heights[self.getType()]
        return (height - VisionInput.CAM_HEIGHT) / math.tan(math.radians(VisionInput.CAM_ANGLE + self.get_pitch_degrees()))
