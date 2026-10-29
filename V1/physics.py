from config import FUEL_SHIFT

def margin_at(com, cop, frac):
    return cop - (com + FUEL_SHIFT * frac)
    