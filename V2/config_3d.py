import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WINDOW_TITLE = b"version2_3d_tvc_rocket - 3d physics version now"

GRAVITY = 9.81 
DRAG_COEFF = 0.0005
TVC_K = 0.5
PITCH_DAMP = 0.4
TILT_LIMIT = 30.0
GUST_MAX = 6.0

CHUTE_ALT = 50.0
STEER_ACCEL = 5.0
AERO_K = 0.08

#rocket dimensions 
BODY_HEIGHT = 5.0
BODY_RADIUS = 0.25 
PAD_SIZE = 4.0
FUEL_SHIFT = 1.5
COM_MIN = 1.5
COM_MAX = 3.5
COP_MIN = 2.0
COP_MAX = 4.5

DRAGGING_SENSITIVITY = 1.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))