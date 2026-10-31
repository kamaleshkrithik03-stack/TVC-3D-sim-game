import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WINDOW_TITLE = b"version2_3d_tvc_rocket - 3d physics version now"

GRAVITY = 9.81 
DRAG_COEFF = 0.4
TVC_K = 0.5
PITCH_DAMP = 0.4
TILT_LIMIT = 30.0
GUST_MAX = 6.0

#rocket dimensions 
BODY_HEIGHT = 2.5
BODY_RADIUS = 0.25 #juz feels right ig
PAD_SIZE = 4.0
FUEL_SHIFT = 1.5
COM_MIN = 3.0
COM_MAX = 6.5
COP_MIN = 4.5
COP_MAX = 9.0

DRAGGING_SENSITIVITY = 1.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



