import os
import pygame
from config import W, H, BASE_DIR, GRAY

def load_menu_bg():
    for name in ("launch_real_new.jpg",):
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                return pygame.transform.scale(img, (W, H))
            except pygame.error:
                pass
    print("menu bg image not found- either go to rep and download that as well or findur desired image online else you are stuck with my clour choices(horrid)")
    return None

def init_clouds():
    clouds = []
    cloud_data = [
        {"x": 150, "y": -300, "w": 120, "h": 40},  # copy pasted from last time
        {"x": 500, "y": -500, "w": 100, "h": 35},
        {"x": 650, "y": -700, "w": 180, "h": 50},
        {"x": 850, "y": -1000, "w": 130, "h": 40},
        {"x": 300, "y": -1200, "w": 150, "h": 45},
        {"x": 80, "y": -1500, "w": 160, "h": 45},
        {"x": 750, "y": -1800, "w": 200, "h": 60},
        {"x": 450, "y": -2100, "w": 170, "h": 50},
        {"x": 200, "y": -2500, "w": 140, "h": 40},
        {"x": 600, "y": -3000, "w": 180, "h": 55},
        {"x": 250, "y": -3600, "w": 150, "h": 45},
        {"x": 800, "y": -4200, "w": 190, "h": 55},
    ]
    for c in cloud_data:
        surf = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 255, 255, 255), (0, 0, c["w"], c["h"]))
        clouds.append({"x": c["x"], "y": c["y"], "surf": surf})
    return clouds