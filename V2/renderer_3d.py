import os
import raylib
from config_3d import BASE_DIR

def load_main_texture():
    path = os.path.join(BASE_DIR, "launch_real_new.jpg")
    if os.path.exists(path):
        try:
            texture = raylib.LoadTexture(path.encode('utf-8'))
            return texture
        except Exception as e:
            print(f"could not load background texture: {e}")
    print("menu bg is not found so go to rep and download it or stick with my horrible colour choices")
    return None