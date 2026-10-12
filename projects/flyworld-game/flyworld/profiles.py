"""Who the flies are: name, sex and colour. Index 0 is the big fly the player drives."""

FLY_PROFILES = [
    dict(name="Nick",   sex="male",   color=(0.96, 0.96, 0.96)),   # big white fly, the player
    dict(name="Kathy",  sex="female", color=(1.00, 0.45, 0.75), style="jigglypuff"),   # pink, round, big eyes, wings
    dict(name="Isshan", sex="male",   color=(0.90, 0.15, 0.15)),   # red
    dict(name="Parth",  sex="male",   color=(0.12, 0.18, 0.62)),   # dark blue
    dict(name="Leyla",  sex="female", color=(0.60, 0.82, 1.00)),   # baby blue
    dict(name="Jack",   sex="male",   color=(1.00, 0.55, 0.10)),   # orange
    dict(name="Rodela", sex="female", color=(1.00, 0.90, 0.15)),   # yellow
]
EYE_WHITE = (0.98, 0.98, 1.00)          # Kathy's eyes (distinct from Nick's white body)
EYE_PUPIL = (0.10, 0.45, 0.45)
FOOD_COLOR = (0.62, 1.00, 0.25)          # lime, distinct from every fly
FOCUS_COLOR = (0.20, 1.00, 0.95)         # cyan marker for the selected fly

# Groups shown as LEDs in the per-fly activity panel (senses first, then descending / motor)
LED_GROUPS = ["LC4", "LPLC2", "LC16", "LC6", "LC11", "ORN_DM1", "ORN_DA1", "LB3c",
              "DNp01", "DNp09", "MDN", "DNa02_L", "DNa02_R", "DNg11", "MN9", "KC", "MBON", "PPL101", "DN_all"]
LED_LABELS = ["LC4", "LPLC2", "LC16", "LC6", "LC11", "DM1", "DA1", "LB3c",
              "p01", "p09", "MDN", "a02L", "a02R", "g11", "MN9", "KC", "MBON", "PPL1", "DNs"]
# Groups drawn as rows of the focus fly's spike raster
RASTER_GROUPS = ["LC4", "LPLC2", "LC16", "LC6", "LC11", "ORN_DM1", "ORN_DA1", "LB3c", "PPL101", "KC", "MBON",
                 "DNp01_L", "DNp01_R", "DNp09_L", "DNp09_R", "MDN", "DNa01_L", "DNa01_R", "DNa02_L", "DNa02_R",
                 "DNg11", "MN9", "DN_all"]


def by_name(name):
    for i, p in enumerate(FLY_PROFILES):
        if p["name"].lower() == name.lower():
            return i
    raise KeyError(name)


def rgb255(color):
    return tuple(int(round(c * 255)) for c in color)
