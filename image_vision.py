import cv2
import numpy as np

class ImageVision:

    def detect_object(self, image, object):
        
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        object_hsv_color = self.hex_to_hsv(object["object_hex_color"])
        lower_limit, upper_limit = self.get_limits(object_hsv_color, object["hue_delta"], object["saturation_delta"], object["value_delta"])
        mask = cv2.inRange(image_hsv, lower_limit, upper_limit)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if object["min_area"] <= area <= object["max_area"]:
                objects.append(cv2.boundingRect(contour))
        
        return objects, mask
              
    def get_limits(self, hsv, h_delta, s_delta, v_delta):
        hsv16 = np.array(hsv, dtype=np.int16)
        h, s, v = hsv16
       
        lower_limit = np.array([max(h - h_delta, 0), max(s - s_delta, 0), max(v - v_delta, 0)], dtype=np.uint8)
        upper_limit = np.array([min(h + h_delta, 180), min(s + s_delta, 255), min(v + v_delta, 255)], dtype=np.uint8)

        return lower_limit, upper_limit

    def hex_to_hsv(self, hex):
        hex_color = hex.lstrip('#')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        rgb_array = np.array([[[r, g, b]]], dtype=np.uint8)
        hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)
        h, s, v = hsv_array[0][0]

        return h, s, v
    
    def hex_to_bgr(self, hex):
        hex_color = hex.lstrip('#')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    
        return b, g, r