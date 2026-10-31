import math
import random
from raylib import *
from config_3d import *
from renderer_3d import * load_menu_texture

def main():
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    SetTargetFPS(60)
    
    bg_texture = load_menu_texture()

    camera = Camer3D()
    camera.position = Vector3(0.0, 8.0, 18.0)
    camera.target = Vector3(0.0, 3.0, 0.0)
    camera.fovy = 45.0
    camera.projection = CAMERA_PERSPECTIVE

    state = "menu"

    rocket_pos = Vector3(0.0, 1.5, 0.0)
    rocket_vel = Vector3(0.0, 0.0, 0.0)
    h_vel = 0.0
    th = 0.0
    gim = 0.0
    alt = 0.0
    vel = 0.0

    ang = 0.0
    om = 0.0
    max_tilt = 0.0
    max_alt = 0.0
    legs_deployed = False

    selected_level = 1
    selected_ascent_fuel = 100.0
    selected_descent_fuel = 30.0
    ascent_fuel = selected_ascent_fuel
    descent_fuel = selected_descent_fuel
    active_fuel_mode = "ascent"

    wind_speed = 0.0
    target_apogee = 1000.0
    com_pos = 4.0
    cop_pos = 7.5
    gust = 0.0
    gust_target = 0.0
    gust_timer = 0.0
#telemetry bit
    log = []
    log_t = 0.0
    

    
