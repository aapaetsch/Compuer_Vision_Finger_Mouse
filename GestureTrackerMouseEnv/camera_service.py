import pyautogui
import numpy as np
import hand_tracker as track_hand
from hand_tracker import HandDetector
from hand_enums import Fingers, FingerDistanceInfo
from camera_enums import StatsPosition, ColorTuples
import time
import math
import cv2

# TODO: Move Settings elsewhere
# settings
global isDebug, isDisplayMirrorMode
global cam_width, cam_height, screen_width, screen_height
global ThumbFingerTip, IndexFingerTip, MiddleFingerTip, RingFingerTip, PinkyFingerTip
isDebug = True
cam_width, cam_height = 1280, 720
ThumbFingerTip = 4
IndexFingerTip = 8
MiddleFingerTip = 12
RingFingerTip = 16


class CameraService():
    def __init__(max_hands: int = 1, cam_width: int = 1280, cam_height: int = 720) -> None:
        """
        Initializes the CameraService class

        :param is_debug_mode: If True, prints debug statements
        :param cam_width: an integer representing the width of the camera feed
        :param cam_height: an integer representing the height of the camera feed
        """
        self.__isDebug = is_debug_mode
        self.__cam_width = cam_width
        self.__cam_height = cam_height
        # max frame rate
        self.__frame_r = 100
        # cursor smoothing
        self.__smoothing = 5
        self.__prev_frame_time = 0
        self.__prev_mouse_loc = { "x": 0, "y": 0 }
        self.__curr_mouse_loc = { "x": 0, "y": 0 }
        # Used to reduce the sensitivity of the mouse movement during pinch mode
        self.__fine_move_multiplier = 0.125
        self.__video_capture = cv2.VideoCapture(0)
        self.__video_capture.set(3, self.__cam_width)
        self.__video_capture.set(4, self.__cam_height)
        # Open camera window on main display
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.moveWindow("Image", 0, 0)
        self.__detector = HandDetector(maxHands=max_hands)
        self.__screen_width, self.__screen_height = pyautogui.size()

        self.__small_circle_radius = 7
        self.__medium_circle_radius = 15
    
    def run(self) -> None:
        """
        Runs the camera service, detecting movement and performing actions based on the movement/gestures
        - Also displays the camera feed
        - Mouse Move: Index Finger Raised
        - Left Click: Index + Middle Fingers Raised, Bring Fingers Together (Distance < 40)
        - Right Click: Index + Middle + Ring Fingers Raised, Bring Fingers Together (Distance < 40)
        - Drag: Pinch Index + Thumb Fingers, Bring Fingers Together (Distance < 50). Movement tracking reduced to 1/8th of normal speed
        """
        self.__fingers = [0,0,0,0,0]
        success, img = self.__video_capture.read() 
        self.__img = self.__detector.findHands(img)
        self.__lm_list, self.__bbox = self.__detector.findPosition(self.__img)

        if len(self.__lm_list) != 0:
            self.__thumb_x, self.__thumb_y = self.__lm_list[ThumbFingerTip][1:]
            self.__index_finger_x, self.__index_finger_y = self.__lm_list[IndexFingerTip][1:]
            self.__middle_finger_x, self.__middle_finger_x = self.__lm_list[MiddleFingerTip][1:]

            #Detect Raised Fingers
            self.__fingers = self.__detector.fingersUp()
            self.print_finger_info(self.__fingers)
            cv2.rectangle(self.__img, (self.__frame_r, self.__frame_r), (self.__cam_width - self.__frame_r, self.__cam_height - self.__frame_r), ColorTuples.PINK.value, 2)

            isRightClick = False
            isLeftClick = False

            #Move Mouse: Index Finger Raised
            if HandDetector.isFingerUp(self.__fingers, Fingers.INDEX, True):
                self.print_mode_text("Move Mouse", ColorTuples.LIGHT_PINK)
                # Convert Coordinates
                x3 = np.interp(self.__index_finger_x, (self.__frame_r, self.__cam_width - self.__frame_r), (0, self.__screen_width))
                y3 = np.interp(self.__index_finger_y, (self.__frame_r, self.__cam_height - self.__frame_r), (0, self.__screen_height))
                # Smoothen Values
                self.__curr_mouse_loc["x"] = self.__prev_mouse_loc["x"] + (x3 - self.__prev_mouse_loc["x"]) / self.__smoothing
                self.__curr_mouse_loc["y"] = self.__prev_mouse_loc["y"] + (y3 - self.__prev_mouse_loc["y"]) / self.__smoothing
                # Mouse Movement
                pyautogui.moveTo(self.__screen_width - self.__curr_mouse_loc["x"], self.__curr_mouse_loc["y"], 0.1, pyautogui.easeOutQuad)
                cv2.circle(self.__img, (self.__index_finger_x, self.__index_finger_y), 15, ColorTuples.BLUE.value, cv2.FILLED)
                self.__prev_mouse_loc["x"], self.__prev_mouse_loc["y"] = self.__curr_mouse_loc["x"], self.__curr_mouse_loc["y"]

            elif HandDetector.areFingersUp(self.__fingers, [Fingers.THUMB, Fingers.INDEX]):
                self.print_mode_text("Holding Left Click", ColorTuples.LIGHT_PINK)
                thumb_to_index_info = FingerDistanceInfo(*self.__detector.findDistance(4, 8, self.__img))
                if self.__isDebug:
                    print("Thumb -> Index Length is:", thumb_to_index_info.length)

                #TODO: Replace this, this is the blue finger tracking dot
                x3 = np.interp((self.__thumb_x + self.__index_finger_x) / 2, (self.__frame_r, self.__cam_width - self.__frame_r), (0, self.__screen_width))
                y3 = np.interp((self.__thumb_y + self.__index_finger_y) / 2, (self.__frame_r, self.__cam_height - self.__frame_r), (0, self.__screen_height))
                dx = (x3 - self.__prev_mouse_loc["x"]) * self.__fine_move_multiplier
                dy = (y3 - self.__prev_mouse_loc["y"]) * self.__fine_move_multiplier
                self.__curr_mouse_loc["x"] = self.__prev_mouse_loc["x"] + dx
                self.__curr_mouse_loc["y"] = self.__prev_mouse_loc["y"] + dy
                pyautogui.move(-dx, dy, 0.1, pyautogui.easeOutQuad)
                print("dx:", dx, "dy:", dy)

                if thumb_to_index_info.length < 50:
                    draw_circle_midpoint(thumb_to_index_info, self.__medium_circle_radius, ColorTuples.GREEN, cv2.FILLED)
                    pyautogui.mouseDown(button='left')
                    self.print_action_text("Left Mouse Down")
                
                elif thumb_to_index_info.length > 70:
                    pyautogui.mouseUp()
                    self.print_action_text("Left Mouse Up")
                    draw_circle_midpoint(thumb_to_index_info, self.__small_circle_radius, ColorTuples.BLUE, cv2.FILLED)
                    
                self.__prev_mouse_loc["x"], self.__prev_mouse_loc["y"] = self.__curr_mouse_loc["x"], self.__curr_mouse_loc["y"]
            
            # Clicking Mode
            elif HandDetector.areFingersUp(self.__fingers, [Fingers.INDEX, Fingers.MIDDLE]):
                self.print_mode_text("Left Click", ColorTuples.LIGHT_PINK)
                index_to_middle_info = FingerDistanceInfo(*self.__detector.findDistance(IndexFingerTip, MiddleFingerTip, self.__img))
                if self.__isDebug:
                    print("Index -> Middle Length is:", index_to_middle_info.length)
                if index_to_middle_info.length < 40:
                    draw_circle_midpoint(index_to_middle_info, self.__medium_circle_radius, ColorTuples.GREEN, cv2.FILLED)
                    self.print_action_text("Left Click")
                    if (not isLeftClick):
                        isLeftClick = True
                        pyautogui.click()
                elif index_to_middle_info.length < 80:
                    draw_circle_midpoint(index_to_middle_info, self.__small_circle_radius, ColorTuples.RED, cv2.FILLED)
            
            elif HandDetector.areFingersUp(self.__fingers, [Fingers.INDEX, Fingers.MIDDLE, Fingers.RING]):
                self.print_mode_text("Right Click", ColorTuples.LIGHT_PINK)
                index_to_middle_info = FingerDistanceInfo(*self.__detector.findDistance(IndexFingerTip, MiddleFingerTip, self.__img))
                middle_to_ring_info = FingerDistanceInfo(*self.__detector.findDistance(MiddleFingerTip, RingFingerTip, self.__img))
                if self.__isDebug:
                    print("Index -> Middle Length is:", index_to_middle_info.length, "Middle -> Ring Length is:", middle_to_ring_info.length)
                if index_to_middle_info.length < 40 and middle_to_ring_info.length < 40:
                    draw_circle_midpoint(index_to_middle_info, self.__medium_circle_radius, ColorTuples.GREEN, cv2.FILLED)
                    draw_circle_midpoint(middle_to_ring_info, self.__medium_circle_radius, ColorTuples.GREEN, cv2.FILLED)
                    pyautogui.rightClick()
                    self.print_action_text("Right Click")


                elif index_to_middle_info.length < 80 and middle_to_ring_info.length < 80:
                    draw_circle_midpoint(index_to_middle_info, self.__small_circle_radius, ColorTuples.RED, cv2.FILLED)
                    draw_circle_midpoint(middle_to_ring_info, self.__small_circle_radius, ColorTuples.RED, cv2.FILLED)

    def get_starting_pos_location(self, print_location: StatsPostion: text_size: tuple) -> tuple:
        """
        Gets the starting position for one of the 8 locations on the screen that text can be printed to

        :param print_location: an enum representing the location of the text to be printed
        :param text_size: a tuple representing the size of the text to be printed
        """
        if print_location == StatsPosition.TOP_LEFT:
            return (20, 50)
        
        elif print_location == StatsPosition.TOP_CENTER:
            return (int((self.__cam_width - text_size[0]) / 2), 50)
        
        elif print_location == StatsPosition.TOP_RIGHT:
            return (self.__cam_width - text_size[0] - 20, 50)
        
        elif print_location == StatsPosition.MIDDLE_LEFT:
            return (20, int((self.__cam_height + text_size[1]) / 2))
        
        elif print_location == StatsPosition.MIDDLE_RIGHT:
            return (self.__cam_width - text_size[0] - 20, int((self.__cam_height + text_size[1]) / 2))
        
        elif print_location == StatsPosition.BOTTOM_LEFT:
            return (20, self.__cam_height - 50)
        
        elif print_location == StatsPosition.BOTTOM_CENTER:
            return (int((self.__cam_width - text_size[0]) / 2), self.__cam_height - 50)
        
        elif print_location == StatsPosition.BOTTOM_RIGHT:
            return (self.__cam_width - text_size[0] - 20, self.__cam_height - 50)
        
        elif print_location == StatsPosition.CENTER:
            return (int((self.__cam_width - text_size[0]) / 2), int((self.__cam_height + text_size[1]) / 2))


    def print_finger_info(self, font_color: tuple = ColorTuples.BLUE) -> None:
        """
        Prints the state of each finger to the screen

        :param fingers: a list of integers representing the state of each finger
        :param print_location: an enum representing the location of the text to be printed
        :param font_color: a tuple representing the color of the text in BGR format
        """
        finger_names = [finger.name for finger in Fingers]
        finger_states = ["Up" if finger == 1 else "Down" for finger in self.__fingers]
        finger_text = ", ".join([f"{name}: {state}" for name, state in zip(finger_names, finger_states)])
        text_size, _ = cv2.getTextSize(finger_text, cv2.FONT_HERSHEY_PLAIN, 2, 2)
        pos = get_starting_pos_location(StatsPosition.TOP_RIGHT, text_size, self.__cam_width, self.__cam_height)
        cv2.putText(self.__img, finger_text, pos, cv2.FONT_HERSHEY_PLAIN, 2, font_color.value, 2)
        cv2.putText(self.__img, finger_text, pos, cv2.FONT_HERSHEY_PLAIN, 2, font_color.value, 2)

    def print_fps_counter(self, fps: float, font_color: tuple = ColorTuples.BLUE) -> None:
        """
        Prints the FPS counter to the screen

        :param fps: a float representing the FPS of the camera feed
        :param print_location: an enum representing the location of the text to be printed
        :param font_color: a tuple representing the color of the text in BGR format
        """
        fps_text = str(int(fps))
        text_size, _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_PLAIN, 2, 2)
        pos = get_starting_pos_location(StatsPosition.TOP_LEFT, text_size, self.__cam_width, self.__cam_height)
        cv2.putText(self.__img, fps_text, pos, cv2.FONT_HERSHEY_PLAIN, 2, font_color.value, 2)    
    
    def print_action_text(self, text: str, font_color: tuple = ColorTuples.BLUE) -> None:
        """
        Prints the action text to the screen

        :param text: a string representing the text to be printed
        :param print_location: an enum representing the location of the text to be printed
        :param font_color: a tuple representing the color of the text in BGR format
        """
        textStr = "Action: " + text
        text_size, _ = cv2.getTextSize(textStr, cv2.FONT_HERSHEY_PLAIN, 2, 2)
        pos = get_starting_pos_location(StatsPosition.BOTTOM_CENTER, text_size, self.__cam_width, self.__cam_height)
        cv2.putText(self.__img, textStr, pos, cv2.FONT_HERSHEY_PLAIN, 2, font_color.value, 2)
    
    def print_mode_text(text: str, font_color: tuple = ColorTuples.BLUE) -> None:
        """
        Prints the mode text to the screen

        :param text: a string representing the text to be printed
        :param print_location: an enum representing the location of the text to be printed
        :param font_color: a tuple representing the color of the text in BGR format
        """
        textStr = "Mode: " + text
        text_size, _ = cv2.getTextSize(textStr, cv2.FONT_HERSHEY_PLAIN, 2, 2)
        pos = get_starting_pos_location(StatsPosition.BOTTOM_LEFT, text_size, self.__cam_width, self.__cam_height)
        cv2.putText(self.__img, textStr, pos, cv2.FONT_HERSHEY_PLAIN, 2, font_color.value, 2)

    @staticmethod
    def draw_circle_midpoint(distance_info: FingerDistanceInfo, circle_radius: int, circle_color: tuple, cv2_style: int = cv2.FILLED) -> None:
        """
        Draws a circle at the midpoint of the line between two points

        :param img: a NumPy array representing an image
        :param line_info: a list containing information about a line, including its start and end points
        :param circle_radius: an integer representing the radius of the circle to be drawn
        :param circle_color: a tuple representing the color of the circle in BGR format
        :param cv2_style: an integer representing the style of the circle (default is cv2.FILLED)
        """
        cv2.circle(distance_info.img, (distance_info.line_info[4], distance_info.line_info[5]), circle_radius, circle_color.value, cv2_style)


def main():
    cameraService = CameraService()
    while True:
        cameraService.run()
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        cameraService.print_fps_counter(fps)
        p_time = c_time
        # cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        # Display Camera Feed
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()