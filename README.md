<h1>Webcam Gesture Mouse</h1>

- The aim of this project is to create a gesture based mouse that can control your computer through any webcam.

<h2>Features</h2>

| Mouse Action | Gesture | Implemented |
|:---:|:---|:---:|
| Mouse Move | Raise index finger, mouse should track with its location. | Y |
| Click | Raise index and middle finger, bring together to click | Y |
| Double click | Raise index and middle finger, bring together twice in rapid succession | Y |
| Fine Mouse Movement | Index finger and thumb are raised, mouse tracks at a reduced speed to allow for finer adjustments. | Y|
| Click and Drag | Pinch index finger and thumb when mouse is over the element you want to drag, mouse should now track with left mouse button being held down | Y |
| Right Click | Raise index, middle and ring finger, bring together to click | Y |
| Scroll Up | Face palm up, bring hand up and palm towards self. | N |
| Scroll Down | Face palm towards camera, bring hand down, palm towards floor. | N | 

<h2>Requirements</h2>

- Python3.x
- [numpy](https://numpy.org/)
- [Pyautogui](https://pyautogui.readthedocs.io/en/latest/): For enacting mouse actions from the python code
- [cv2](https://pypi.org/project/opencv-python/) (Python wrapper for openCV): Majority of the heavy lifting for feature detection & image recognition
- [MediaPipe](https://pypi.org/project/mediapipe/): Display video feed with hand tracking skeleton & feature points. Can be configured to display additional information.

<h3>Not Yet Implemented</h3>
<h3>Hotkey actions</h3>
 
| Hotkey Action | Gesture | 
|:---:|:---|
| Netflix (Edge) | Hold index and middle finger pointing to left. (Sideways "2") |
| Prime Video (Edge) | Index, Middle, Ring finger pointing left. (Sideways "3") |
| Youtube (Firefox) | Index, Middle, Ring, Pinkey pointing left. (Sideways "4") |
| Switch Speaker Output???| Recognize putting headphones on or off? |
