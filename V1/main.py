import sys 
import math
import random
import pygame
from config import *
from physics import margin_at
from renderer import load_menu_bg, init_clouds

win = pygame.display.set_mode((W, H))
pygame.display.set_caption("version1_with_TVCLANDING")

launch_bg = load_menu_bg()

def txt(s, color, x, y, font=f_sm):
    win.blit(font.render(s, True, color), (x, y))

def mcol(m):
    return GREEN if m >= 0.5 else (YELLOW if m >= 0 else RED)

def main():
    clk = pygame.time.Clock()
    state = "menu"

    rx, ry = W // 2, H - 138
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

    wind_speed = 0.0 # copy pasted from last project lol cant handle typing all of those old ones out 
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
    log = []
    log_t = 0.0
    log_acc = 0.0
    show_graph = False
    scored = False
    score = 0.0
    rating = "C"
    apogee_error = 0.0
    lateral_offset = 0.0
    mission_failed = False
    fail_reason = ""

    dragging_level = False # the new bee to the gng of toggles
    dragging_ascent_fuel = False
    dragging_descent_fuel = False
    dragging_wind = False
    dragging_apogee = False
    dragging_com = False
    dragging_cop = False

    clouds = init_clouds()

    print("now this gamified sim(kindaa) is more difficult and more accurate from last one(for nerds: go to rep to see what ive changed ) ")

    while True:
        dt = min(clk.tick(60) / 1000.0, 0.05)

        if state != "menu":
            if active_fuel_mode == "ascent":
                frac = ascent_fuel / selected_ascent_fuel if selected_ascent_fuel > 0 else 0
            else:
                frac = descent_fuel / selected_descent_fuel if selected_descent_fuel > 0 else 0
        else:
            frac = 1.0

        cog = com_pos + FUEL_SHIFT * frac
        cop = cop_pos
        margin = cop - cog

        if state in ("boost", "coast", "descent"):
            gust_timer -= dt
            if gust_timer <= 0.0:
                gust_target = random.uniform(-GUST_MAX, GUST_MAX)
                gust_target = random.uniform(2.0, 3.5)
            gust += (gust_target - gust) * 2.0 * dt

        wind_eff = wind_speed + gust

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif state == "menu":
                    if e.key == pygame.K_RETURN:
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
                elif e.key == pygame.K_r and (state == "landed" or state == "descent"):
                    state = "menu"
                    alt = 0.0
                    vel = 0.0
                    h_vel = 0.0  # i added horizontal velocity this time cuz it shows how TVC affects the horizontal drift as well
                    th = 0.0
                    gim = 0.0
                    ang = 0.0
                    om = 0.0
                    max_tilt = 0.0
                    max_alt = 0.0
                    rx = W // 2
                    ry = H - 138
                    print("returning to normal menu (why normal-be abnormal ;) )")
                elif e.key == pygame.K_g and state in ("landed", "failed"):
                    show_graph = not show_graph
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if abs(e.pos[1] - 195) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_level = True
                    elif abs(e.pos[1] - 250) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_ascent_fuel = True
                    elif abs(e.pos[1] - 305) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_descent_fuel = True
                    elif abs(e.pos[1] - 360) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_wind = True
                    elif abs(e.pos[1] - 415) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_apogee = True
                    elif abs(e.pos[1] - 485) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_com = True
                    elif abs(e.pos[1] - 540) <= 15 and 135 <= e.pos[0] <= 435:
                        dragging_cop = True
            elif e.type == pygame.MOUSEBUTTONUP:
                dragging_wind = False
                dragging_apogee = False
                dragging_com = False
                dragging_cop = False
                dragging_level = False
                dragging_ascent_fuel = False
                dragging_descent_fuel = False
            elif e.type == pygame.MOUSEMOTION:
                if state == "menu":
                    rel_x = max(0, min(300, e.pos[0] - 135)) # now i realise that i couldve just given max min here intead of stating every single time
                    if dragging_level:
                        selected_level = 1 if rel_x < 150 else 2
                    if dragging_ascent_fuel:
                        selected_ascent_fuel = 25.0 + (rel_x / 300.0) * (250.0 - 25.0)
                    if dragging_descent_fuel:
                        selected_descent_fuel = 10.0 + (rel_x / 300.0) * (100.0 - 10.0)
                    if dragging_wind:
                        wind_speed = -20.0 + (rel_x / 300.0) * 40.0
                    if dragging_apogee:
                        target_apogee = 200.0 + (rel_x / 300.0) * (3000.0 - 200.0)
                    if dragging_com:
                        com_pos = COM_MIN + (rel_x / 300.0) * (COM_MAX - COM_MIN)
                    if dragging_cop:
                        cop_pos = COP_MIN + (rel_x / 300.0) * (COP_MAX - COP_MIN)
                    
        keys = pygame.key.get_pressed()

        if state == "boost":
            active_fuel_mode = "ascent"
            if ascent_fuel > 0:
                if keys[pygame.K_w]:
                    th = min(100.0, th + 60.0 * dt)
                elif keys[pygame.K_s]:
                    th = max(0.0, th - 60.0 * dt)
                else:
                    th = max(0.0, th - 15.0 * dt)

                ascent_fuel = max(0.0, ascent_fuel - (th * 0.08) * dt)
                if ascent_fuel <= 0:
                    th = 0.0
                    state = "coast"
                    print("ok now we are starting to coast(like life) as you have run out of fuel(i told you to be careful). Now hope that the momentum carries you to your home(apogee)")
            else:
                th = 0.0
                state = "coast"

            if keys[pygame.K_a]:
                gim = max(-7.0, gim - 25.0 * dt)
            elif keys[pygame.K_d]:
                gim = min(7.0, gim + 25.0 * dt)
            else:
                gim *= (0.85 ** (dt * 60.0))
            
            thrust_vert = th * 0.3 * math.cos(math.radians(ang))
            thrust_horiz = th * 0.3 * math.sin(math.radians(ang)) 

            drag_v = -DRAG_COEFF * vel * abs(vel)
            accel = thrust_vert - 9.8 + drag_v

            vel += accel * dt
            alt += vel * dt

            if alt > 0.0:
                h_vel += (thrust_horiz + (wind_eff - h_vel) * 1.5) * dt
                rx += h_vel * dt

            if alt <= 0.0:
                alt = 0.0
                if vel < 0:
                    vel = 0.0
                else:
                    vel = vel

            if vel <= 0 and alt > 5.0:
                th = 0.0
                state = "coast"

        elif state == "coast":
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            drag_v = -DRAG_COEFF * vel * abs(vel)  # ok so this bit till line 198 is ai coded as idk the math of drag or wind
            vel += (-9.8 + drag_v) * dt
            alt += vel * dt

            h_vel += (wind_eff - h_vel) * 0.8 * dt
            rx += h_vel * dt

            if vel < 0:
                state = "descent"
                print("ok good that is good(those who know, know) you have hit apogee and now we are free falling(trust the process) until low alt chute deployement")
        
        elif state == "descent":
            active_fuel_mode = "descent"
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            ang *= (0.9 ** (dt * 60.0))
            om = 0.0
            drag_v = -DRAG_COEFF * vel * abs(vel)  # again ai till line 220 and i copy pasted no worries no inflation of time

            if alt > CHUTE_ALT:
                vel += (-9.8 + drag_v) * dt
            else:
                target_descent_vel = -8.0
                vel += (target_descent_vel - vel) * 0.8 * dt

            alt += vel * dt

            if keys[pygame.K_d]:
                steer = 1
            elif keys[pygame.K_a]:
                steer = -1
            else:
                steer = 0

            h_vel += steer * STEER_ACCEL * dt
            h_vel += (wind_speed * 0.5 - h_vel) * 2.0 * dt
            rx += h_vel * dt

            if alt <= 0.0:
                alt = 0.0
                vel = 0.0
                h_vel = 0.0
                state = "landed"
                print("touchdown now dont you rejoice just yet well see your stats(for nerds:Telemetry )")
            
        if state == "boost" or state == "coast":
            hrel = h_vel - wind_eff
            alpha = max(-90.0, min(90.0, ang - math.degrees(math.atan2(hrel, max(abs(vel), 1.0)))))
            q = DRAG_COEFF * (vel * vel + hrel * hrel)
            om += (-AERO_K * q * alpha * margin + (gim / 7.0) * th * TVC_K * (BODY_L - cog) / BODY_L) * dt
            om *= (1.0 - PITCH_DAMP * dt)
            ang = (ang + om * dt + 180.0) % 360.0 - 180.0
            if alt <= 0.0:
                ang = 0.0
                om = 0.0
            if abs(ang) > max_tilt:
                max_tilt = abs(ang)
            
        if state in ("boost", "coast", "descent"):
            log_t += dt
            log_acc += dt
            if log_acc >= 0.1:
                log_acc -= 0.1
                log.append((log_t, alt, ang))

        if state == "landed" and not scored:
            log.append((log_t, alt, ang))
            apogee_error = abs(max_alt - target_apogee)
            lateral_offset = abs(rx - PAD_X)
            if lateral_offset <= PAD_HALF_WIDTH:
                on_pad = True
            else:
                on_pad = False
            
            apogee_score_part = max(0.0, 1.0 - apogee_error / (0.25 * target_apogee))
            tilt_score_part = max(0.0, 1.0 - max_tilt / 90.0)
            fuel_score_part = (ascent_fuel + descent_fuel) / (selected_ascent_fuel + selected_descent_fuel)
            if on_pad:
                pad_score_part = 1.0
            else:
                pad_score_part = max(0.0, 1.0 - lateral_offset / 300.0)

            score = (45 * apogee_score_part + 30 * tilt_score_part + 15 * fuel_score_part + 10 * pad_score_part)
            
            if score >= 90:
                rating = "S"
            elif score >= 75:
                rating = "A"
            elif score >= 55:
                rating = "B"
            else:
                rating = "C"
            scored = True

        if alt > max_alt:
            max_alt = alt
        
        if rx < 50:
            rx = 50
        elif rx > W - 50:
            rx = W - 50

        if state == "menu":
            if launch_bg:
                win.blit(launch_bg, (0, 0))
            else:
                win.fill((20, 25, 35))
        else:
            sky_factor = min(1.0, alt / 2500.0)
            r_col = int(30 * (1 - sky_factor) + 10 * sky_factor)
            g_col = int(144 * (1 - sky_factor) + 10 * sky_factor)
            b_col = int(255 * (1 - sky_factor) + 15 * sky_factor)
            win.fill((r_col, g_col, b_col))

            ground_y = H - 120 + int(alt * GROUND_SCALE)  # cmn guys this is basic math of scalin
            if ground_y < H + 100:
                pygame.draw.rect(win, (34, 139, 34), (0, ground_y, W, H - ground_y))
                pygame.draw.line(win, (200, 200, 200), (0, ground_y), (W, ground_y), 3)
                pygame.draw.rect(win, RED, (PAD_X - PAD_HALF_WIDTH, ground_y - 3, PAD_HALF_WIDTH * 2, 6))

            cloud_alpha = int(220 * max(0.0, 1.0 - alt / 5000.0))
            for c in clouds:
                cloud_screen_y = (H - 250) + int((c["y"] + alt) * CLOUD_SCALE)
                if cloud_screen_y > -100 and cloud_screen_y < H + 100:
                    c["surf"].set_alpha(cloud_alpha)
                    win.blit(c["surf"], (c["x"], cloud_screen_y))

            if state != "landed" and abs(vel) > 25.0:
                streak_len = int(min(80, abs(vel) * 0.4))
                for i in range(10):
                    sx = (i * 97 + 53) % W
                    sy = int((i * 131 + alt * GROUND_SCALE * 1.5) % (H + 80)) - 40
                    pygame.draw.line(win, (220, 235, 255), (sx, sy), (sx, sy + streak_len), 2)
                
        if state != "menu" and state != "landed":
            if state != "landed":
                phase_color = ORANGE
            else:
                phase_color = GREEN
            win.blit(f_sm.render(f"flight phase: {state.upper()} (if you dont know this get outa here you are not a rocketeer)", True, phase_color), (50, 75))
            win.blit(f_sm.render(f"altitude: {alt:.1f} m", True, WHITE), (50, 105))
            win.blit(f_sm.render(f"vertical velocity: {vel:.1f} m/s", True, WHITE), (50, 130))
            
            cur_fuel = ascent_fuel if active_fuel_mode == "ascent" else descent_fuel
            if cur_fuel > 20:
                fuel_color = BLUE
            else:
                fuel_color = RED
            win.blit(f_sm.render(f"fuel remaining: {cur_fuel:.1f} kg   (ok now be careful with fuel consumption if red else its chill man)", True, fuel_color), (50, 155))
            win.blit(f_sm.render(f"max altitude: {max_alt:.1f} m (ok you be the judge your majesty)", True, YELLOW), (50, 180))
            win.blit(f_sm.render(f"wind: {wind_eff:+.1f} m/s", True, CYAN), (50, 205))
            win.blit(f_sm.render(f"pad offset: {rx - PAD_X:+.0f} px", True, CYAN), (50, 230))
            
            if abs(ang) < TILT_LIMIT:
                tilt_color = GREEN
            else:
                tilt_color = RED
            txt(f"tilt: {ang:+.1f} deg (keep it under {TILT_LIMIT:.0f})", tilt_color, 50, 255)
            txt(f"stability: {margin:+.2f} cal  COG {cog:.2f} m (green dot)  COP {cop:.2f} m (cyan ring)", mcol(margin), 50, 280)
        
        if state == "menu":
            ov = pygame.Surface((800, 520), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 210))
            win.blit(ov, (100, 110))
            win.blit(f_sm.render("rocky rockets game(or you decide the name) configuration", True, WHITE), (135, 130))

            win.blit(f_sm.render(f"mission level: LEVEL {selected_level}", True, ORANGE), (135, 170))
            pygame.draw.rect(win, GRAY, (135, 191, 300, 8))
            lvl_pos = 135 + (0 if selected_level == 1 else 300)
            pygame.draw.circle(win, ORANGE, (lvl_pos, 195), 10)

            win.blit(f_sm.render(f"ascent fuel load: {selected_ascent_fuel:.1f} kg", True, BLUE), (135, 225))
            pygame.draw.rect(win, GRAY, (135, 246, 300, 8))
            fuel_pos = 135 + int(((selected_ascent_fuel - 25.0) / (250.0 - 25.0)) * 300)
            pygame.draw.circle(win, BLUE, (fuel_pos, 250), 10)

            win.blit(f_sm.render(f"descent fuel load: {selected_descent_fuel:.1f} kg", True, CYAN), (135, 280))
            pygame.draw.rect(win, GRAY, (135, 301, 300, 8))
            df_pos = 135 + int(((selected_descent_fuel - 10.0) / (100.0 - 10.0)) * 300)
            pygame.draw.circle(win, CYAN, (df_pos, 305), 10)

            win.blit(f_sm.render(f"wind speed: {wind_speed:.1f} m/s", True, CYAN), (135, 335))
            pygame.draw.rect(win, GRAY, (135, 356, 300, 8))
            wind_pos = 135 + int(((wind_speed + 20.0) / 40.0) * 300)
            pygame.draw.circle(win, CYAN, (wind_pos, 360), 10)

            win.blit(f_sm.render(f"target apogee: {target_apogee:.0f} m", True, YELLOW), (135, 390))
            pygame.draw.rect(win, GRAY, (135, 411, 300, 8))
            apogee_pos = 135 + int(((target_apogee - 200.0) / (3000.0 - 200.0)) * 300)
            pygame.draw.circle(win, YELLOW, (apogee_pos, 415), 10)
            win.blit(f_sm.render("(normally i suggest to aim for the stars but in this case DONT)", True, YELLOW), (135, 435))

            win.blit(f_sm.render(f"COM (when dry): {com_pos:.1f} m from nose", True, GREEN), (135, 465))
            pygame.draw.rect(win, GRAY, (135, 486, 300, 8))
            com_x = 135 + int(((com_pos - COM_MIN) / (COM_MAX - COM_MIN)) * 300)
            pygame.draw.circle(win, GREEN, (com_x, 485), 10)

            win.blit(f_sm.render(f"COP: {cop_pos:.1f} m from nose", True, CYAN), (135, 515))
            pygame.draw.rect(win, GRAY, (135, 536, 300, 8))
            cop_x = 135 + int(((cop_pos - COP_MIN) / (COP_MAX - COP_MIN)) * 300)
            pygame.draw.circle(win, CYAN, (cop_x, 540), 10)

            win.blit(f_sm.render("press [enter] to launch", True, GREEN), (135, 575))

            win.blit(f_sm.render("Controls are w, a, s, d", True, WHITE), (540, 215))
            win.blit(f_sm.render("if you dont know this as well", True, WHITE), (540, 240))
            win.blit(f_sm.render("you are not a gamer", True, WHITE), (540, 265))
            win.blit(f_sm.render("[R] to return back to menu", True, WHITE), (540, 320))
            win.blit(f_sm.render("[ESC] to escape(its there in", True, WHITE), (540, 350))
            win.blit(f_sm.render("the name im not explaining)", True, WHITE), (540, 372))
            win.blit(f_sm.render("goal: hit your apogee and", True, GRAY), (540, 410))
            win.blit(f_sm.render("stay stable (tilt under 30 deg)", True, GRAY), (540, 432))
            win.blit(f_sm.render("as i have upped the heat guys enjoyy ", True, GRAY), (540, 454))

            m_full = margin_at(com_pos, cop_pos, 1.0)
            m_empty = margin_at(com_pos, cop_pos, 0.0)
            txt("stability (cal, +ve is stable)", WHITE, 540, 480)
            txt(f"full tank:  {m_full:+.1f}", mcol(m_full), 540, 505)
            txt(f"empty tank: {m_empty:+.1f} enjoyy", mcol(m_empty), 540, 530)

        if state != "menu":
            ox = 25
            oy = CHUTE_LINE_LEN + 25
            r_surf = pygame.Surface((100, oy + 120), pygame.SRCALPHA)
            pygame.draw.polygon(r_surf, RED, [(ox + 25, oy + 5), (ox + 12, oy + 28), (ox + 38, oy + 28)])
            pygame.draw.rect(r_surf, WHITE, (ox + 12, oy + 28, 26, 50))

            if state == "descent" or state == "landed":
                cx = ox + 25
                canopy_y = 4
                canopy_h = 50
                canopy_mid = canopy_y + canopy_h // 2
                pygame.draw.arc(r_surf, ORANGE, (cx - 45, canopy_y, 90, canopy_h), 0, 3.14, 5)  # i used ai from here to line 330 and only line 335 
                pygame.draw.line(r_surf, GRAY, (cx - 45, canopy_mid), (ox + 14, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx + 45, canopy_mid), (ox + 36, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx - 22, canopy_y + 7), (ox + 20, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx + 22, canopy_y + 7), (ox + 30, oy + 28), 1)

            cur_fuel = ascent_fuel if active_fuel_mode == "ascent" else descent_fuel
            if th > 0 and cur_fuel > 0:
                fh = int(th * 0.35)
                fx = 25 - (gim * 1.4)
                pygame.draw.polygon(r_surf, RED, [(ox + 15, oy + 78), (ox + 35, oy + 78), (int(ox + fx), oy + 78 + fh)])

            pygame.draw.circle(r_surf, GREEN, (ox + 25, int(oy + 5 + cog * 7.3)), 5)
            pygame.draw.circle(r_surf, CYAN, (ox + 25, int(oy + 5 + cop * 7.3)), 8, 2)
            rot_r = pygame.transform.rotate(r_surf, -ang)  # i know these from my actual rocket
            body_offset = (oy + 53) - r_surf.get_height() // 2
            rect = rot_r.get_rect(center=(int(rx), int(ry) - 7 - body_offset))
            win.blit(rot_r, rect.topleft)

        if state == "landed":
            ov = pygame.Surface((880, 430), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 210))
            win.blit(ov, (80, 150))

            if show_graph and len(log) >= 2:
                x0 = 100
                y0 = 210
                gw = 800
                gh = 250
                total_t = max(log[-1][0], 0.1)
                max_a = max(max(p[1] for p in log), 1.0)
                txt("flight graph: yellow = altitude, cyan = tilt", WHITE, 100, 165)
                pygame.draw.rect(win, GRAY, (x0, y0, gw, gh), 2)
                for sgn in (-1, 1):
                    ly = y0 + gh // 2 - int(sgn * TILT_LIMIT / 90.0 * (gh / 2))
                    pygame.draw.line(win, RED, (x0, ly), (x0 + gw, ly), 1)
                if target_apogee <= max_a:
                    ty = y0 + gh - int(target_apogee / max_a * gh)
                    pygame.draw.line(win, WHITE, (x0, ty), (x0 + gw, ty), 1)
                
                alt_pts = []
                tilt_pts = []
                for t, a, g in log:
                    pt_x = x0 + int(t / total_t * gw)
                    pt_alt_y = y0 + gh - int(a / max_a * gh)
                    alt_pts.append((pt_x, pt_alt_y))
                    
                    clamped_g = max(-90.0, min(90.0, g))
                    pt_tilt_y = y0 + gh // 2 - int(clamped_g / 90.0 * (gh / 2))
                    tilt_pts.append((pt_x, pt_tilt_y))

                pygame.draw.lines(win, YELLOW, False, alt_pts, 2)
                pygame.draw.lines(win, CYAN, False, tilt_pts, 2)
                txt(f"peak {max_a:.0f} m", YELLOW, x0 + 5, y0 + 4)
                txt("0 s", WHITE, x0, y0 + gh + 6)
                txt(f"{total_t:.0f} s", WHITE, x0 + gw - 50, y0 + gh + 6)
                txt("white line = target apogee(dont aim for stars gng), red lines = tilt limit", GRAY, 100, 495)
                txt("[G] back to results", WHITE, 100, 520)
            else:
                if max_tilt < TILT_LIMIT:
                    stable = True
                else:
                    stable = False

                if stable and apogee_error <= 0.05 * target_apogee:
                    goal = True
                else:
                    goal = False

                win.blit(f_lg.render("ok i guess you did it- touchdown", True, GREEN), (100, 165))
                win.blit(f_sm.render("(im jeleous no worries ill make it impossible to win next time im not kidding)", True, GREEN), (100, 205))
                win.blit(f_sm.render(f"lets see your apogee: {max_alt:.1f} m", True, YELLOW), (100, 245))
                win.blit(f_sm.render("now compare with your target apogee(if you didnt achieve it then very good", True, WHITE), (100, 280))
                win.blit(f_sm.render(f"i will not have to make it harder): {target_apogee:.1f} m (Error: {apogee_error:.1f} m)", True, WHITE), (100, 302))
                win.blit(f_sm.render(f"pad offset: {lateral_offset:.1f} px (i.e how much you screwed up)", True, CYAN), (100, 340))
                
                if on_pad:
                    pad_text = "PAD HIT!"
                    pad_color = GREEN
                else:
                    pad_text = "PAD MISSED"
                    pad_color = RED
                win.blit(f_sm.render(pad_text, True, pad_color), (100, 375))

                if stable:
                    stab_desc = "Stable flight- good"
                else:
                    stab_desc = "Tumbled-RIP rocket"
                txt(f"max tilt: {max_tilt:.1f} deg  ->  {stab_desc}", GREEN if stable else RED, 100, 400)

                if goal:
                    goal_desc = "goal met you did it even after i made it harder"
                else:
                    goal_desc = "goal not met gng keep tryin and i see that my method worked"
                txt(goal_desc, GREEN if goal else RED, 100, 425)

                if rating == "S":
                    rate_color = GREEN
                elif rating == "A":
                    rate_color = YELLOW
                elif rating == "B":
                    rate_color = ORANGE
                else:
                    rate_color = RED
                txt(f"score: {score:.0f}/100 rating: {rating}", rate_color, 100, 455, f_lg)
                
                win.blit(f_sm.render("press [R] to return to menu or [ESC] to exit(dont you dare i wnat you to play again)", True, WHITE), (100, 495))
                txt("press [G] to see your flight graph(hopefully not too shabby)", GRAY, 100, 520)
                if goal:
                    txt("Damn you did it come back next week for final boss level", RED, 100, 545)

        pygame.display.flip()

if __name__ == "__main__":
    main()