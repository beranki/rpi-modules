import cv2
import math
import numpy as np
from target import Target


class Detector:
    def __init__(self, color_data):
        self.obj_data = color_data

    def detectGameElement(self, frame, frame_ann):
        results = []
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        for type, color_ranges in self.obj_data.items():
            mask = cv2.inRange(hsv_frame,
                               np.array(color_ranges[0]),
                               np.array(color_ranges[1]))
            if (type == "CUBE"):
                results = results + self.cube_pipeline(mask, frame_ann)
            elif (type == "CONE"):
                results = results + self.cone_pipeline(mask, frame_ann)
        return results
    
    def cube_pipeline(self, mask, frame):
            results = []
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
            morph = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.medianBlur(mask, 5)
            contours, hier = cv2.findContours(morph,
                                                  cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_NONE)
            contours = sorted(contours, key=cv2.contourArea)
            CNT_AREA_THRESH = 1000
            BBX_AREA_THRESH = 200
            for contour in contours:  
                if(cv2.contourArea(contour) > CNT_AREA_THRESH):
                        tx,ty,tw,th = cv2.boundingRect(contour)
                        if (not (tx == 0 and ty == 0 and tw == mask.shape[1] and th == mask.shape[0])):
                            if (tw * th > BBX_AREA_THRESH):
                                cv2.rectangle(frame, (tx, ty), (tx + tw, ty + th),
                                                    (0, 0, 255), 2)
                                cv2.circle(frame, (int(tx + tw / 2), int(ty + th / 2)),
                                        radius=0, color=(0, 0, 255), thickness=5)
                                cv2.putText(frame, "CUBE", (tx, ty - 5),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255),
                                            2, cv2.LINE_AA)
                                results.append(Target(contour, "CUBE"))
            return results

    def cone_pipeline(self, mask, frame):
            results = []
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
            morph = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.medianBlur(mask, 5)
            straight_contours, hier = cv2.findContours(morph,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_NONE)
            straight_contours = sorted(straight_contours,
                                            key=cv2.contourArea)
            CNT_AREA_THRESH = 1000
            BBX_AREA_THRESH = 200
            for contour in straight_contours:
                if(cv2.contourArea(contour) > CNT_AREA_THRESH):
                    tx,ty,tw,th = cv2.boundingRect(contour)
                    if (not (tx == 0 and ty == 0 and tw == mask.shape[1] and th == mask.shape[0])):
                                if (tw * th > BBX_AREA_THRESH):
                                    passed = True
                                if passed:
                                    cv2.rectangle(frame, (tx, ty),
                                                        (tx + tw, ty + th), (0, 0, 255), 2)
                                    cv2.circle(frame, (int(tx + tw/2),
                                                    int(ty + th/2)), radius=0,
                                            color=(0, 0, 255), thickness=5)
                                    cv2.putText(frame, "CONE", (tx, ty - 5),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                1.0, (0, 0, 255), 2, cv2.LINE_AA)
                                    results.append(Target(contour, "CONE"))
            return results

        
