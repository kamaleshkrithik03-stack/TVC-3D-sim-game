import sys
import math
import random
from raylib import *
from config_3d import *
from renderer_3d import load_menu_texture

def main():
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    SetTargetFPS(60)

    bg_texture = load_menu_texture()

    camera = Camera3D()
    camera.position = Vector3(0.0, 8.0, 18.0)
    camera.target = Vector3(0.0, 3.0, 0.0)
    camera.up = Vector3(0.0, 1.0, 0.0)
    camera.fovy = 45.0
    camera.projection = CAMERA_PERSPECTIVE
    
    orbit_mode = False
    orbit_angle = 0.0

    state = "menu"

    rocket_pos = Vector3(0.0, 1.5, 0.0)
    h_vel = 0.0
    th = 0.0
    gim = 0.0
    alt = 0.0
    vel = 0.0

    selected_level = 1
    selected_ascent_fuel = 100.0
    selected_descent_fuel = 30.0
    ascent_fuel = selected_ascent_fuel
    descent_fuel = selected_descent_fuel
    active_fuel_mode = "ascent"

    wind_speed = 0.0
    target_apogee = 1000.0
    max_alt = 0.0
    ang = 0.0
    om = 0.0
    max_tilt = 0.0
    com_pos = 4.0
    cop_pos = 7.5
    gust = 0.0
    gust_target = 0.0
    gust_timer = 0.0
    
#telemtry bit
    log = []
    log_t = 0.0
    log_acc = 0.0
    show_graph = False
    scored = False
    score = 0.0
    rating = "C"
    apogee_error = 0.0
    lateral_offset = 0.0
    on_pad = True

    legs_deployed = False

    dragging_level = False
    dragging_ascent_fuel = False
    dragging_descent_fuel = False
    dragging_wind = False
    dragging_apogee = False
    dragging_com = False
    dragging_cop = False
    last_mouse_x = 0

    print("Its now 3d- should be harder if not tell me i will make it more harder such that u cant pass")

    while not WindowShouldClose():
        dt = min(GetFrameTime(), 0.05)
        mouse_pos = GetMousePosition()

        if state != "menu":
            frac = ascent_fuel / selected_ascent_fuel if (active_fuel_mode == "ascent" and selected_ascent_fuel > 0)
        else:
            frac = 1.0

        cog = com_pos + FUEL_SHIFT * frac
        cop = cop_pos
        margin = cop_pos - cog

        if state in ("boost", "coast", "descent"):
            gust_timer -= dt
            if gust_timer <- 0.0:
                gust_target = random.uniform(-GUST_max, GUST_MAX)
            gust += (gust_target - gust) * 2.0 * dt
        wind_eff = wind_speed + gust

        if state == "menu":
            if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                if abs(mouse_pos.y - 170) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_level = True
                elif abs(mouse_pos.y - 230) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_ascent_fuel = True
                elif abs(mouse_pos.y - 290) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_descent_fuel = True
                elif abs(mouse_pos.y - 350) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_wind = True
                elif abs(mouse_pos.y - 410) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_apogee = True
                elif abs(mouse_pos.y - 485) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_com = True
                elif abs(mouse_pos.y - 545) <= 15 and 135 <= mouse_pos.x <= 435:
                    dragging_cop = True
                last_mouse_x = mouse_pos.x
            
            if IsMouseButtonReleased(MOUSE_BUTTON_LEFT):
                dragging_level = dragging_ascent_fuel = dragging_descent_fuel = dragging_wind = dragging_apogee = dragging_com = dragging_cop = False
            
            if IsMouseButtonDown(MOUSE_BUTTON_LEFT):
                delta_x = (mouse_pos.x - last_mouse_x) * DRAGGING_SENSITIVITY # The word "delta" gives me phy and calc nightmares
                rel_x = max(0, min(300, mouse_pos.x - 135))
                if dragging_level: selected_level = 1 if rel_x < 150 else 2
                if dragging_ascent_fuel: selected_ascent_fuel = max(25.0, min(250.0, selected_ascent_fuel + (delta_x / 300.0) * 225.0))
                if dragging_descent_fuel: selected_descent_fuel = max(10.0, min(100.0, selected_descent_fuel + (delta_x / 300.0) * 90.0))
                if dragging_level: wind_speed = max(-20.0, min(20.0, wind_speed + (delta_x / 300.0) * 40.0))
                if dragging_apogee: target_apogee = max(200.0, min(3000.0, target_apogee + (delta_x / 300.0) * 2800.0))
                if dragging_com: com_pos = max(COM_MIN, min(COM_MAX, com_pos + (delta_x / 300.0) * (COM_MAX - COM_MIN)))
                if dragging_cop: cop_pos = max(COP_MIN, min(COP_MAX, cop_pos + (delta_x / 300.0) * (COP_MAX - COP_MIN)))
                last_mouse_x = mouse_pos.x

            if IsKeyPressed(KEY_ENTER):
                state = "boost"
                ascent_fuel = selected_ascent_fuel
                descent_fuel = selected_descent_fuel
                active_fuel_mode = "ascent"
                th = 50.0
                vel = 5.0
                max_alt = 0.0
                ang = 0.0
                om = 0.0
                max_tilt = 0.0
                gust = 0.0
                gust_target = 0.0
                gust_timer = 0.0
                log = []
                log_t = 0.0
                log_acc = 0.0
                show_graph = False
                scored = False
                print("liftoff gng - i would say congrats but this is not a real rocket")

        else:
            if IsKeyPressed(KEY_ESCAPE):
                CloseWindow()
                sys.exit()
            elif IsKeyPressed(KEY_L):
                legs_deployed = not legs_deployed
                print(f"landing legs status: {'deployed' if legs_deployed else 'not open ofc you didnt open it'}")
            elif IsKeyPressed(KEY_O):
                orbit_mode = not orbit_mode
                print(f"orbit your pov [using o]: {'ON' if orbit_mode else 'OFF'}")
            elif IsKeyPressed(KEY_R) and (state in ("landed", "crashed", "descent")):
                state = "menu"
                alt = vel = h_vel = th = gim = ang = om = max_tilt = max_alt = 0.0
                rocket_pos = Vector3(0.0, 1.5, 0.0)
                print("returning to normal menu (why normal-be abnormal is a good life lesson(maybe ig))")
            elif IsKeyPressed(KEY_G) and state in ("landed", "crashed"):
                show_graph = not show_graph
            
        keys = IsKeyDown

        if state == "boost":
            active_fuel_mode = "ascent"
            if ascent_fuel > 0:
                if keys(KEY_W): th = min(100.0, th + 60.0 * dt)
                elif keys(KEY_S): th = max(0.0, th - 60.0 * dt)
                else: th = max(0.0, th - 15.0 * dt)

                ascent_fuel = max(0.0, ascent_fuel - (th * 0.08) * dt)
                if ascent_fuel <= 0:
                    th = 0.0
                    state = "coast"
                    print("out of fuel- now juz hope that the laws of phy are kind to you as we are coastin (like life) on inertia")
                else:
                    th = 0.0
                    state = "coast"

                if keys(KEY_A): gim = max(-7.0, gim - 25.0 * dt)
                elif keys(KEY_D): gim = min(7.0, gim + 25.0 * dt)
                else: gim *= (0.85 ** (dt * 60.0))

                thrust_vert = th * 0.3 * math.cos(math.radians(ang))
                thrust_horiz = th * 0.3 * math.sin(math.radians(ang))

                drag_v = -DRAG_COEFF * vel * abs(vel)
                accel = thrust_vert - GRAVITY + drag_v
                vel += accel * dt
                alt += vel * dt

                if alt > 0.0:
                    h_vel += (thrust_horiz + (wind_eff - h_vel) * 1.5) * dt
                if alt <= 0.0: alt = 0.0
                





    
