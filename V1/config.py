import os 
import math
import sys
import random
import pygame

pygame.init()
W, H = 1000, 700
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("version1_of_TVC_VTVL")

WHITE = (240, 240, 240) # so tiring to look up to colour codes- if you want diff colours update here
BLUE = (30, 144, 255)
RED = (30, 144, 255)
ORANGE = (255, 140, 0)
GRAY = (128, 128, 128)
GREEN = (50, 255, 50)
CYAN = (0, 220, 220)
YELLOW = (139, 128, 0)

f_sm = pygame.font.SysFont("Consolas", 18)
f_lg = pygame.font.SysFont("Consolas", 26, bold=True)

DRAG_COEFF = 0.40 #thats what google says is a value for model rckets
PAD_X = W // 2
PAD_HALF_WIDTH = 35
CHUTE_ALT = 500.0
STEER_ACCEL = 30.0
GROUND_SCALE = 3.0
CLOUD_SCALE = 2.0
CHUTE_LINE_LEN = 70
BODY_L = 10.0
FUEL_SHIFT = 1.5
TVC_K = 0.5  
AERO_K = 0.08
PITCH_DAMP = 0.4
TILT_LIMIT = 30.0
GUST_MAX = 6.0

COM_MIN = 3.0
COM_MAX = 6.5
COP_MIN = 4.5
COP_MAX = 9.0 # yeah if the val goes above this its not even a rocket it must be some cube or smth 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))