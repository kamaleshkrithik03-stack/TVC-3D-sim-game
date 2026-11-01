import sys
import math
import random
from pyray import *
from raylib import CAMERA_PERSPECTIVE
from config_3d import *
from renderer_3d import load_main_texture as load_menu_texture

WHITE = Color(255, 255, 255, 255)
BLACK = Color(0, 0, 0, 255)
RED = Color(230, 41, 55, 255)
GREEN = Color(0, 228, 48, 255)
BLUE = Color(0, 121, 241, 255)
YELLOW = Color(253, 249, 0, 255)
ORANGE = Color(255, 161, 0, 255)
CYAN = Color(0, 158, 47, 255) 
DARKGRAY = Color(80, 80, 80, 255)
RAYWHITE = Color(245, 245, 245, 255)

def main():
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    set_target_fps(60)

    bg_texture = load_menu_texture()

    clouds = [
        {"pos": Vector3(random.uniform(-30, 30), random.uniform(20, 80), random.uniform(-30, 30)), "radius": random.uniform(3, 6)}
        for _ in range(15)
    ]

    camera = Camera3D(
        Vector3(0.0, 8.0, 18.0),  
        Vector3(0.0, 3.0, 0.0),   
        Vector3(0.0, 1.0, 0.0),   
        45.0,                     
        CAMERA_PERSPECTIVE        
    )
    
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

    while not window_should_close():
        dt = min(get_frame_time(), 0.05)
        mouse_pos = get_mouse_position()

        if state != "menu":
            frac = ascent_fuel / selected_ascent_fuel if (active_fuel_mode == "ascent" and selected_ascent_fuel > 0) else (descent_fuel / selected_descent_fuel if selected_descent_fuel > 0 else 0)
        else:
            frac = 1.0

        cog = com_pos + FUEL_SHIFT * frac
        cop = cop_pos
        margin = cop_pos - cog

        if state in ("boost", "coast", "descent"):
            gust_timer -= dt
            if gust_timer <= 0.0:
                gust_target = random.uniform(-GUST_MAX, GUST_MAX)
                gust_timer = random.uniform(2.0, 3.5)
            gust += (gust_target - gust) * 2.0 * dt
        wind_eff = wind_speed + gust

        if state == "menu":
            if is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
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
            
            if is_mouse_button_released(MOUSE_BUTTON_LEFT):
                dragging_level = dragging_ascent_fuel = dragging_descent_fuel = dragging_wind = dragging_apogee = dragging_com = dragging_cop = False
            
            if is_mouse_button_down(MOUSE_BUTTON_LEFT):
                delta_x = (mouse_pos.x - last_mouse_x) * DRAGGING_SENSITIVITY # The word "delta" gives me phy and calc nightmares
                rel_x = max(0, min(300, mouse_pos.x - 135))
                if dragging_level: selected_level = 1 if rel_x < 150 else 2
                if dragging_ascent_fuel: selected_ascent_fuel = max(25.0, min(250.0, selected_ascent_fuel + (delta_x / 300.0) * 225.0))
                if dragging_descent_fuel: selected_descent_fuel = max(10.0, min(100.0, selected_descent_fuel + (delta_x / 300.0) * 90.0))
                if dragging_wind: wind_speed = max(-20.0, min(20.0, wind_speed + (delta_x / 300.0) * 40.0))
                if dragging_apogee: target_apogee = max(200.0, min(3000.0, target_apogee + (delta_x / 300.0) * 2800.0))
                if dragging_com: com_pos = max(COM_MIN, min(COM_MAX, com_pos + (delta_x / 300.0) * (COM_MAX - COM_MIN)))
                if dragging_cop: cop_pos = max(COP_MIN, min(COP_MAX, cop_pos + (delta_x / 300.0) * (COP_MAX - COP_MIN)))
                last_mouse_x = mouse_pos.x

            if is_key_pressed(KEY_ENTER):
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
            if is_key_pressed(KEY_ESCAPE):
                close_window()
                sys.exit()
            elif is_key_pressed(KEY_L):
                legs_deployed = not legs_deployed
                print(f"landing legs status: {'deployed' if legs_deployed else 'not open ofc you didnt open it'}")
            elif is_key_pressed(KEY_O):
                orbit_mode = not orbit_mode
                print(f"orbit your pov [using o]: {'ON' if orbit_mode else 'OFF'}")
            elif is_key_pressed(KEY_R) and (state in ("landed", "crashed", "descent")):
                state = "menu"
                alt = vel = h_vel = th = gim = ang = om = max_tilt = max_alt = 0.0
                rocket_pos = Vector3(0.0, 1.5, 0.0)
                print("returning to normal menu (why normal-be abnormal is a good life lesson(maybe ig))")
            elif is_key_pressed(KEY_G) and state in ("landed", "crashed"):
                show_graph = not show_graph
            
        keys = is_key_down

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
            if vel <= 0 and alt > 5.0:
                th = 0.0
                state = "coast"

        elif state == "coast":
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            drag_v = -DRAG_COEFF * vel * abs(vel)
            vel += (-GRAVITY + drag_v) * dt
            alt += vel * dt
            h_vel += (wind_eff - h_vel) * 0.8 * dt

            if vel < 0:
                state = "descent"
                print("hit apogee and free falling until chute deployment")
        
        elif state == "descent":
            active_fuel_mode = "descent"
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            ang *= (0.9 ** (dt * 60.0))
            om = 0.0
            drag_v = -DRAG_COEFF * vel * abs(vel)

            if alt > CHUTE_ALT:
                vel += (-GRAVITY + drag_v) * dt
            else:
                target_descent_vel = -8.0
                vel += (target_descent_vel - vel) * 0.8 * dt

            alt += vel * dt
            steer = 1 if keys(KEY_D) else (-1 if keys(KEY_A) else 0)
            h_vel += steer * STEER_ACCEL * dt
            h_vel += (wind_speed * 0.5 - h_vel) * 2.0 * dt

            if alt <= 0.0:
                alt = vel = h_vel = 0.0
                state = "landed"
                print("touchdown! let's see your telemetry stats")
            
        if state in ("boost", "coast"):
            hrel = h_vel - wind_eff
            alpha = max(-90.0, min(90.0, ang - math.degrees(math.atan2(hrel, max(abs(vel), 1.0)))))
            q = DRAG_COEFF * (vel * vel + hrel * hrel)
            om += (-AERO_K * q * alpha * margin + (gim / 7.0) * th * TVC_K * (BODY_HEIGHT - cog) / BODY_HEIGHT) * dt
            om *= (1.0 - PITCH_DAMP * dt)
            ang = (ang + om * dt + 180.0) % 360.0 - 180.0
            if alt <= 0.0: ang = om = 0.0
            if abs(ang) > max_tilt: max_tilt = abs(ang)
        
        if state in ("boost", "coast", "descent"):
            log_t += dt
            log_acc += dt
            if log_acc >= 0.1:
                log_acc -= 0.1
                log.append((log_t, alt, ang))
            
        if state == "landed" and not scored:
            log.append((log_t, alt, ang))
            apogee_error = abs(max_alt - target_apogee)
            lateral_offset = abs(h_vel * 10.0)
            on_pad = lateral_offset <= PAD_SIZE

            apogee_score_part = max(0.0, 1.0 - apogee_error / (0.25 * target_apogee))
            tilt_score_part = max(0.0, 1.0 - max_tilt / 90.0)
            fuel_score_part = (ascent_fuel + descent_fuel) / (selected_ascent_fuel + selected_descent_fuel)
            pad_score_part = 1.0 if on_pad else max(0.0, 1.0 - lateral_offset / 300.0)

            score = (45 * apogee_score_part + 30 * tilt_score_part + 15 * fuel_score_part + 10 * pad_score_part)
            rating = "S" if score >= 90 else ("A" if score >= 75 else ("B" if score >= 55 else "C"))  #throwback to high school
            scored = True

        if alt > max_alt: max_alt = alt

        rocket_pos.y = 1.5 + (alt * 0.02)

        if orbit_mode:
            orbit_angle += 1.0 * dt
            camera.position.x = rocket_pos.x + math.sin(orbit_angle) * 18.0 # got a sudden speed run from here for no reason
            camera.position.y = rocket_pos.y + 4.0
            camera.position.z = rocket_pos.z + math.cos(orbit_angle) * 18.0
            camera.target = rocket_pos
        else:
            camera.position = Vector3(0.0, max(8.0, rocket_pos.y + 2.0), 18.0)
            camera.target = Vector3(0.0, rocket_pos.y, 0.0)

        begin_drawing()
        clear_background(RAYWHITE)

        if state == "menu":
            if bg_texture:
                source_rec = Rectangle(0.0, 0.0, float(bg_texture.width), float(bg_texture.height))
                dest_rec = Rectangle(0.0, 0.0, float(SCREEN_WIDTH), float(SCREEN_HEIGHT))
                origin = Vector2(0.0, 0.0)
                draw_texture_pro(bg_texture, source_rec, dest_rec, origin, 0.0, WHITE)
            else:
                clear_background(DARKGRAY)

            draw_rectangle(100, 100, 800, 560, Color(0, 0, 0, 220))
            draw_text(b"ok its the game config (3d version now)", 135, 120, 18, WHITE)

            draw_text(bytes(f"mission level(I hope u chose the harder one cuz I DARE YOU): LEVEL {selected_level}", "utf-8"), 135, 170, 16, RED)
            draw_rectangle(135, 191, 300, 8, DARKGRAY)
            draw_circle(135 + (0 if selected_level == 1 else 300), 195, 10, RED)

            draw_text(bytes(f"ascent fuel load: {selected_ascent_fuel:.1f} kg", "utf-8"), 135, 230, 16, BLUE)
            draw_rectangle(135, 251, 300, 8, DARKGRAY)
            draw_circle(135 + int(((selected_ascent_fuel - 25.0) / 225.0) * 300), 255, 10, BLUE)

            draw_text(bytes(f"descent fuel load: {selected_descent_fuel:.1f} kg", "utf-8"), 135, 290, 16, CYAN)
            draw_rectangle(135, 311, 300, 8, DARKGRAY)
            draw_circle(135 + int(((selected_descent_fuel - 10.0) / 90.0) * 300), 315, 10, CYAN)

            draw_text(bytes(f"wind speed: {wind_speed:.1f} m/s", "utf-8"), 135, 350, 16, CYAN)
            draw_rectangle(135, 371, 300, 8, DARKGRAY)
            draw_circle(135 + int(((wind_speed - (-20.0)) / 40.0) * 300), 375, 10, CYAN)

            draw_text(bytes(f"target apogee(aim for the stars and fail MISERABLY): {target_apogee:.1f} m", "utf-8"), 135, 410, 16, YELLOW)
            draw_rectangle(135, 431, 300, 8, DARKGRAY)
            draw_circle(135 + int(((target_apogee - 200.0) / 2800.0) * 300), 435, 10, YELLOW)

            draw_text(bytes(f"COM (when dry): {com_pos:.1f} m from nose cone", "utf-8"), 135, 485, 16, RED)
            draw_rectangle(135, 506, 300, 8, DARKGRAY)
            draw_circle(135 + int(((com_pos - COM_MIN) / (COM_MAX - COM_MIN)) * 300), 510, 10, RED)

            draw_text(bytes(f"COP (if this is bove 9 or smth its not a rocket anymore ppl): {cop_pos:.1f} m from nose cone", "utf-8"), 135, 545, 16, CYAN)
            draw_rectangle(135, 566, 300, 8, DARKGRAY)
            draw_circle(135 + int(((cop_pos - COP_MIN) / (COP_MAX - COP_MIN)) * 300), 570, 10, CYAN)

            draw_text(b"press [enter] to launch", 135, 615, 18, GREEN)
            draw_text(b"controls: youll figure it out but th eunusual ones are [l] for legs(ik you do i meant the rocket), [o] orbit(not sat orbit), [r] menu", 540, 230, 16, WHITE)

        else:
            begin_mode_3d(camera)

            draw_grid(20, 1.0)
            draw_cube(Vector3(0.0, 0.0, 0.0), PAD_SIZE, 0.2, PAD_SIZE, DARKGRAY)

            for c in clouds:
                draw_sphere(c["pos"], c["radius"], fade(WHITE, 0.6))

            draw_cylinder(rocket_pos, BODY_RADIUS, BODY_RADIUS, BODY_HEIGHT, 16, RED)
            nose_pos = Vector3(rocket_pos.x, rocket_pos.y + (BODY_HEIGHT / 2) + 0.5, rocket_pos.z)
            draw_cylinder(nose_pos, 0.0, BODY_RADIUS, 1.0, 16, DARKGRAY)

            if legs_deployed:
                base_y = rocket_pos.y - (BODY_HEIGHT / 2)
                draw_line_3d(Vector3(rocket_pos.x, base_y, rocket_pos.z), Vector3(rocket_pos.x - 0.8, base_y - 1.0, rocket_pos.z - 0.8), BLACK)
                draw_line_3d(Vector3(rocket_pos.x, base_y, rocket_pos.z), Vector3(rocket_pos.x + 0.8, base_y - 1.0, rocket_pos.z - 0.8), BLACK)
                draw_line_3d(Vector3(rocket_pos.x, base_y, rocket_pos.z), Vector3(rocket_pos.x - 0.8, base_y - 1.0, rocket_pos.z + 0.8), BLACK)
                draw_line_3d(Vector3(rocket_pos.x, base_y, rocket_pos.z), Vector3(rocket_pos.x + 0.8, base_y - 1.0, rocket_pos.z + 0.8), BLACK)

            cur_fuel = ascent_fuel if active_fuel_mode == "ascent" else descent_fuel
            if th > 0 and cur_fuel > 0:
                flame_pos = Vector3(rocket_pos.x, rocket_pos.y - (BODY_HEIGHT / 2) - 0.5, rocket_pos.z)
                flame_radius = BODY_RADIUS * 0.6
                flame_height = th * 0.05
                draw_cylinder(flame_pos, flame_radius, flame_radius * 0.1, flame_height, 16, ORANGE)
                draw_cylinder(flame_pos, flame_radius * 0.1, flame_radius * 0.05, flame_height * 1.5, 16, YELLOW)

            end_mode_3d()

            if abs(ang) > TILT_LIMIT:
                draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(255, 0, 0, 75))

            if show_graph and len(log) >= 2:
                draw_rectangle(80, 150, 840, 430, Color(0, 0, 0, 220))
                x0, y0, gw, gh = 120, 210, 760, 250
                total_t = max(log[-1][0], 0.1)
                max_a = max(max(p[1] for p in log), 1.0)

                draw_text(b"flight graph(hopefully not too shabby right): yellow = altitude, cyan = tilt", 120, 170, 16, WHITE)
                draw_rectangle_lines(x0, y0, gw, gh, DARKGRAY)

                for sgn in (-1, 1):
                    ly = y0 + gh // 2 - int(sgn * TILT_LIMIT / 90.0 * (gh // 2))
                    draw_line(x0, ly, x0 + gw, ly, RED)

                if target_apogee <= max_a:
                    ty = y0 + gh - int(target_apogee / max_a * gh)
                    draw_line(x0, ty, x0 + gw, ty, WHITE)

                for i in range(len(log) - 1):
                    t1, a1, g1 = log[i]
                    t2, a2, g2 = log[i+1]
                    px1 = x0 + int(t1 / total_t * gw)
                    px2 = x0 + int(t2 / total_t * gw)
                    ay1 = y0 + gh - int(a1 / max_a * gh)
                    ay2 = y0 + gh - int(a2 / max_a * gh)
                    draw_line(px1, ay1, px2, ay2, YELLOW)
                    gy1 = y0 + gh // 2 - int(max(-90, min(90, g1)) / 90.0 * (gh // 2))
                    gy2 = y0 + gh // 2 - int(max(-90, min(90, g2)) / 90.0 * (gh // 2))
                    draw_line(px1, gy1, px2, gy2, CYAN)

                draw_text(bytes(f"peak {max_a:.0f} m", "utf-8"), x0 + 5, y0 + 4, 14, YELLOW)
                draw_text(bytes(f"{total_t:.0f} s", "utf-8"), x0 + gw - 40, y0 + gh + 6, 14, WHITE)
                draw_text(b"[G] to see ur results", 120, 490, 16, WHITE)

            else:
                draw_text(b"TVC landing/parachute(for dummies)", 30, 25, 20, DARKBLUE)
                phase_col = ORANGE if state != "landed" else GREEN
                draw_text(bytes(f"flight phase: {state.upper()}", "utf-8"), 30, 60, 16, phase_col)
                draw_text(bytes(f"altitude: {alt:.1f} m", "utf-8"), 30, 85, 16, WHITE)
                draw_text(bytes(f"vertical velocity(better be fast like a rocket): {vel:.1f} m/s", "utf-8"), 30, 110, 16, WHITE)

                fuel_col = BLUE if cur_fuel > 20 else RED
                draw_text(bytes(f"fuel remaining: {cur_fuel:.1f} kg", "utf-8"), 30, 135, 16, fuel_col)
                draw_text(bytes(f"max altitude: {max_alt:.1f} m", "utf-8"), 30, 160, 16, YELLOW)
                draw_text(bytes(f"wind: {wind_eff:.1f} m/s", "utf-8"), 30, 185, 16, CYAN)

                tilt_col = GREEN if abs(ang) < TILT_LIMIT else RED
                draw_text(bytes(f"tilt angle: {ang:+.1f} deg", "utf-8"), 30, 210, 16, tilt_col)
                draw_text(bytes(f"stability margin(hope its bad): {margin:.2f} m", "utf-8"), 30, 235, 16, GREEN if margin >= 0.5 else RED)

                leg_status = "deployed" if legs_deployed else "not deployed(danger but whats life without danger)"
                draw_text(bytes(f"landing legs: {leg_status}", "utf-8"), 30, 260, 16, GREEN if legs_deployed else RED)
                draw_text(bytes(f"orbit camera mode: {'ON' if orbit_mode else 'OFF'}", "utf-8"), 30, 285, 16, ORANGE)

                if state == "landed":
                    draw_rectangle(80, 290, 840, 240, Color(0, 0, 0, 210))
                    draw_text(b"touchdown(if u see this then nxt time im making it harder):", 110, 310, 20, GREEN)
                    draw_text(bytes(f"target apogee: {target_apogee:.1f} m (error(i.e.how far u messed up): {apogee_error:.1f} m)", "utf-8"), 110, 350, 16, WHITE)
                    draw_text(bytes(f"Score: {score:.0f}/100 | Rating: {rating}", "utf-8"), 110, 385, 20, YELLOW)
                    draw_text(b"press [R] to return to menu, [G] to view flight graph", 110, 430, 16, WHITE)

        end_drawing()

    close_window()

if __name__ == "__main__":
    main()