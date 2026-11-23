"""Geometry and measurements for scanning three items of shopping with a handheld barcode scanner.

A shop checkout counter. A cordless pistol-grip barcode scanner stands in its charging cradle. Three packaged goods
stand on the counter mat: a carton of crackers, a small juice carton and a tin of beans. Each has one barcode on one
face. A bagging tray is at one side and a small customer display on a pole has one lamp per item.

Frame: metres, x away from the arm bases, y left, z up; TOP is the counter. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Part, Piece

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
GREY = (0.72, 0.74, 0.76)
DARK = (0.20, 0.20, 0.22)
BLACK = (0.07, 0.07, 0.08)
MAT = (0.10, 0.10, 0.11)

# -- checkout counter mat (a thin rubber strip the goods stand on); fixed -----------------------------------------
MAT_C = (0.435, 0.000)
MAT_SIZE = (0.220, 0.380, 0.002)

# -- handheld scanner (cordless, pistol grip; 100 x 64 x 160 mm, 180 g) -------------------------------------------
# Scanner frame: origin under the centre of the grip's foot, the grip along +z, the scan window looking along +x.
S_GRIP = (0.034, 0.030, 0.112)       # the grip: a bar 34 mm deep (x), 30 mm thick (y), 112 mm tall
S_HEAD = (0.098, 0.056, 0.054)       # the head's collider
S_HEAD_C = (0.017, 0.0, 0.132)
S_MASS = 0.18
S_COM = (0.004, 0.0, 0.072)          # the battery is in the grip
S_GRASP_Z = 0.058                    # where the grip is meant to be held, above its foot
NOD = math.radians(10.0)             # the head nods forward: the window looks 10 degrees below the grip's normal
WINDOW = np.array([0.068, 0.0, 0.128])                     # the window's centre in the scanner frame
WINDOW_AXIS = np.array([math.cos(NOD), 0.0, -math.sin(NOD)])  # the direction the window looks along, scanner frame

# -- its cradle (96 x 86 x 30 mm), fixed. The grip's foot stands in a socket 42 x 38 mm, 18 mm deep ---------------
CRADLE_C = (0.330, -0.360)
CR_H = 0.030
SOCKET = (0.042, 0.038)
SOCKET_COLLIDER = (0.046, 0.046)     # the collider's socket: 2 to 4 mm wider each side than drawn, standing for the drawn socket's flared mouth
SOCKET_Z = 0.012                     # the socket's floor above the counter
CR_X = (-0.040, 0.056)               # the cradle's footprint about the socket's centre
CR_HALF_Y = 0.043

# -- the goods: name -> size, mass, where it stands, and its barcode -----------------------------------------------
# Item frames: origin at the centre of the body. A barcode is a patch 45 x 30 mm: its centre and outward normal are
# given in the item's frame.
JUICE_YAW = math.radians(70.0)      # the juice carton stands turned: its barcode faces the robot's right front
ITEM_Z0 = MAT_SIZE[2]                # the goods stand on the mat
ITEMS = {
    "cracker_carton": dict(shape="box", size=(0.110, 0.055, 0.170), mass=0.20, xy=(0.400, -0.010), yaw=0.0,
                           code=(-0.055, 0.0, 0.025), normal=(-1.0, 0.0, 0.0), color=(0.96, 0.78, 0.20)),
    "juice_carton": dict(shape="box", size=(0.060, 0.060, 0.112), mass=0.25, xy=(0.470, -0.110), yaw=JUICE_YAW,
                         code=(-0.030, 0.0, 0.034), normal=(-1.0, 0.0, 0.0), color=(0.96, 0.96, 0.94)),
    # the tin's barcode is on its label at the asset's -x side; the tin stands turned half round, so the code faces +x
    "bean_tin": dict(shape="cylinder", size=(0.033, 0.110, 0.033), mass=0.30, xy=(0.375, 0.130), yaw=math.pi,
                     code=(-0.033, 0.0, 0.030), normal=(-1.0, 0.0, 0.0), color=(0.05, 0.42, 0.55)),
}
ITEM_NAMES = tuple(ITEMS)
JUICE_TOP = 0.140                    # the juice carton's gable top stands to this height
VISUAL = {"cracker_carton": ("cracker_carton", "cracker_labels"), "juice_carton": ("juice_carton", "juice_labels"),
          "bean_tin": ("food_can", "can_labels")}

# -- bagging tray (240 x 220 mm outside, rim 22 mm, floor 5 mm); fixed ---------------------------------------------
TRAY_C = (0.360, 0.290)
TRAY = (0.240, 0.220, 0.022)
TRAY_FLOOR = 0.005
TRAY_WALL = 0.006

# -- customer display on a pole (three lamps, one per item, in the order the goods stand, left to right); fixed ----
DISPLAY_C = (0.620, 0.120)
DISPLAY_YAW = math.radians(50.0)     # turned so that its screen can be seen from the robot and from its right
LAMP_OF = {"bean_tin": 1, "cracker_carton": 2, "juice_carton": 3}

# -- the scan rule ---------------------------------------------------------------------------------------------
SCAN_MIN, SCAN_MAX = 0.05, 0.20      # distance from the window to the barcode's centre
SCAN_ANGLE = 30.0                    # most the window's axis may be off the barcode's normal, degrees
SCAN_OFF = 0.030                     # most the barcode's centre may be off the window's axis line
SCAN_HOLD = 10                       # steps (0.5 s at 20 Hz) the aim must be held for a read
SCAN_REARM = 10                      # steps the aim must have been off that code before it can be read again
# A read also needs a clear line of sight: see `sight_clear`.


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    if not all((ASSETS / f"{n}.usdc").exists() for n in names):
        return {}                    # no meshes shipped: the primitive colliders are drawn instead
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def mat_object() -> Part:
    return Part("counter_mat", pos=(MAT_C[0], MAT_C[1], TOP + MAT_SIZE[2] / 2), size=MAT_SIZE, exact_z=True, color=MAT,
                friction=(0.9, 0.8))


def scanner_object() -> Part:
    """The scanner: a free rigid body. Colliders (hidden): the grip and the head as two boxes."""
    zc = S_GRIP[2] / 2
    head = Piece("box", S_HEAD, (S_HEAD_C[0], S_HEAD_C[1], S_HEAD_C[2] - zc), rot=(0.0, NOD, 0.0), color=GREY)
    return Part("scanner", pos=(CRADLE_C[0], CRADLE_C[1], TOP + SOCKET_Z + zc + 0.001), size=S_GRIP, exact_z=True, mass=S_MASS,
                color=BLACK, friction=(1.2, 1.0), pieces=(head,), contact_offset=0.002,
                com=(S_COM[0], S_COM[1], S_COM[2] - zc), **_vis("handheld_scanner", (0.0, 0.0, -zc)))


def cradle_object() -> Part:
    """The cradle: fixed. Colliders (hidden): the socket's floor and four blocks round it."""
    zc = SOCKET_Z / 2
    hx, hy = SOCKET_COLLIDER[0] / 2, SOCKET_COLLIDER[1] / 2
    h = CR_H - 0.001
    pieces = []
    for x0, x1, y0, y1 in ((hx, CR_X[1], -CR_HALF_Y, CR_HALF_Y), (CR_X[0], -hx, -CR_HALF_Y, CR_HALF_Y),
                           (-hx, hx, hy, CR_HALF_Y), (-hx, hx, -CR_HALF_Y, -hy)):
        pieces.append(Piece("box", (x1 - x0, y1 - y0, h), ((x0 + x1) / 2, (y0 + y1) / 2, h / 2 - zc), color=DARK))
    return Part("scanner_cradle", pos=(CRADLE_C[0], CRADLE_C[1], TOP + zc), size=(SOCKET[0], SOCKET[1], SOCKET_Z), exact_z=True,
                color=DARK, friction=(0.5, 0.4), pieces=tuple(pieces), **_vis("scanner_cradle", (0.0, 0.0, -zc)))


def item_object(name) -> Part:
    """One of the goods: a free rigid body with a single primitive collider (the juice carton has its gable on top)."""
    it = ITEMS[name]
    if it["shape"] == "cylinder":
        h = it["size"][1]
        size = (it["size"][0] - 0.0005, h, it["size"][0] - 0.0005)
    else:
        h = it["size"][2]
        size = it["size"]
    pieces = ()
    if name == "juice_carton":
        pieces = (Piece("box", (0.060, 0.022, JUICE_TOP - h - 0.004), (0.0, 0.0, h / 2 + (JUICE_TOP - h - 0.004) / 2), color=it["color"]),)
    return Part(name, pos=(it["xy"][0], it["xy"][1], TOP + ITEM_Z0 + h / 2 + 0.0005), size=size, shape=it["shape"], exact_z=True,
                mass=it["mass"], color=it["color"], friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002, yaw=it["yaw"],
                com=(0.0, 0.0, -0.010), **_vis(VISUAL[name], (0.0, 0.0, -h / 2)))


def tray_object() -> Part:
    """The bagging tray: fixed. Colliders (hidden): its floor and four rim walls."""
    zc = TRAY_FLOOR / 2
    lx, ly, h = TRAY
    w = TRAY_WALL
    pieces = [Piece("box", (lx, w, h), (0.0, s * (ly / 2 - w / 2), h / 2 - zc), color=GREY) for s in (1, -1)]
    pieces += [Piece("box", (w, ly, h), (s * (lx / 2 - w / 2), 0.0, h / 2 - zc), color=GREY) for s in (1, -1)]
    return Part("bagging_tray", pos=(TRAY_C[0], TRAY_C[1], TOP + zc), size=(lx, ly, TRAY_FLOOR), exact_z=True, color=GREY,
                friction=(0.8, 0.7), pieces=tuple(pieces), **_vis("bagging_tray", (0.0, 0.0, -zc)))


def display_object() -> Part:
    """The customer display: fixed. Colliders (hidden): foot, pole and head. Its three lamps are drawn lit or unlit
    by the task."""
    zc = 0.006
    tilt = math.radians(15.0)
    pieces = (Piece("cylinder", (0.009, 0.205, 0.009), (0.0, 0.0, 0.112 - zc), color=GREY),
              Piece("box", (0.030, 0.180, 0.076), (0.0, 0.0, 0.245 - zc), rot=(0.0, tilt, 0.0), color=DARK))
    names = ["customer_display"] + [f"lamp{i}_{s}" for i in (1, 2, 3) for s in ("on", "off")] + ["display_labels"]
    return Part("customer_display", pos=(DISPLAY_C[0], DISPLAY_C[1], TOP + zc), size=(0.050, 0.012, 0.050), shape="cylinder",
                exact_z=True, color=DARK, friction=(0.5, 0.4), pieces=pieces, yaw=DISPLAY_YAW,
                **_vis(names, (0.0, 0.0, -zc), visual_hide=("lamp_1", "lamp_2", "lamp_3")))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def window(scanner):
    """The scan window's centre and the direction it looks along, in the world."""
    s = np.asarray(scanner, float)
    r = quat_matrix(s[3:7])
    foot = np.array([0.0, 0.0, -S_GRIP[2] / 2])
    return s[:3] + r @ (foot + WINDOW), r @ WINDOW_AXIS


def grip_centre(scanner):
    s = np.asarray(scanner, float)
    return s[:3] + quat_matrix(s[3:7]) @ np.array([0.0, 0.0, S_GRASP_Z - S_GRIP[2] / 2])


def barcode(name, pose):
    """An item's barcode: its centre and outward normal, in the world."""
    p = np.asarray(pose, float)
    r = quat_matrix(p[3:7])
    return p[:3] + r @ np.asarray(ITEMS[name]["code"], float), r @ np.asarray(ITEMS[name]["normal"], float)


def aim(scanner, name, pose):
    """How the window is aimed at an item's barcode: (distance m, angle off the normal deg, centre off the axis m)."""
    w, a = window(scanner)
    c, n = barcode(name, pose)
    v = c - w
    d = float(np.linalg.norm(v))
    along = float(v @ a)
    off = float(np.linalg.norm(v - along * a)) if along > 0 else d
    ang = math.degrees(math.acos(float(np.clip(-(a @ n), -1.0, 1.0))))
    return d, ang, off


def inside(name, pose, p, shrink=0.002) -> bool:
    """A point inside an item's body (its collider, drawn in by `shrink`): the carton and the juice carton as boxes
    (the juice carton with its gable), the tin as a cylinder."""
    it = ITEMS[name]
    pose = np.asarray(pose, float)
    q = quat_matrix(pose[3:7]).T @ (np.asarray(p, float)[:3] - pose[:3])
    if it["shape"] == "cylinder":
        return bool(math.hypot(q[0], q[1]) <= it["size"][0] - shrink and abs(q[2]) <= it["size"][1] / 2 - shrink)
    hx, hy, hz = (v / 2 - shrink for v in it["size"])
    if abs(q[0]) <= hx and abs(q[1]) <= hy and abs(q[2]) <= hz:
        return True
    return bool(name == "juice_carton" and abs(q[0]) <= hx and abs(q[1]) <= 0.011 and hz <= q[2] <= JUICE_TOP - it["size"][2] / 2 - shrink)


def sight_clear(scanner, name, poses) -> bool:
    """Line of sight from the window to an item's barcode: the window is on the barcode's outward side, and the
    straight line from the window's centre to the barcode's centre passes through no item's body (neither another
    item nor the item's own)."""
    w, _ = window(scanner)
    c, n = barcode(name, poses[name])
    if float((w - c) @ n) <= 0.0:
        return False
    for t in np.linspace(0.02, 0.98, 49):
        p = w + t * (c - w)
        if any(inside(other, poses[other], p) for other in ITEM_NAMES):
            return False
    return True


def in_read_zone(scanner, name, pose, poses=None) -> bool:
    d, ang, off = aim(scanner, name, pose)
    if not (SCAN_MIN <= d <= SCAN_MAX and ang <= SCAN_ANGLE and off <= SCAN_OFF):
        return False
    return bool(poses is None or sight_clear(scanner, name, poses))


def corners(name, pose):
    """The eight corners of an item's bounding box (the tin's box is the square round it), in the world."""
    it = ITEMS[name]
    if it["shape"] == "cylinder":
        hx = hy = it["size"][0]
        hz = it["size"][1] / 2
    else:
        hx, hy, hz = (v / 2 for v in it["size"])
    p = np.asarray(pose, float)
    r = quat_matrix(p[3:7])
    return [p[:3] + r @ np.array([sx * hx, sy * hy, sz * hz]) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]


def over_tray(p, margin=0.004) -> bool:
    return bool(abs(float(p[0]) - TRAY_C[0]) <= TRAY[0] / 2 + margin and abs(float(p[1]) - TRAY_C[1]) <= TRAY[1] / 2 + margin)


def in_tray_area(name, pose) -> bool:
    """An item is in the bagging tray's area: every corner of its bounding box is within the tray's outline (the
    whole item, not its centre) and its lowest corner is between the tray's floor and 15 cm above the counter (on
    the floor or on other goods in the tray, not held high over it), standing or lying."""
    cs = corners(name, pose)
    low = min(c[2] for c in cs)
    return bool(all(over_tray(c) for c in cs) and TOP + TRAY_FLOOR - 0.006 <= low <= TOP + 0.150)


def in_tray(name, pose) -> bool:
    """In the tray's area and down on its floor (lowest corner no more than 12 mm above the floor)."""
    low = min(c[2] for c in corners(name, pose))
    return bool(in_tray_area(name, pose) and low <= TOP + TRAY_FLOOR + 0.012)


def let_go(name, pose, tcps) -> bool:
    """Neither gripper is at the item: both grasp points are at least 3 cm outside its bounding box."""
    it = ITEMS[name]
    half = np.array([it["size"][0], it["size"][0], it["size"][1] / 2] if it["shape"] == "cylinder" else [v / 2 for v in it["size"]])
    p = np.asarray(pose, float)
    r = quat_matrix(p[3:7])
    for t in tcps:
        q = np.abs(r.T @ (np.asarray(t, float)[:3] - p[:3])) - half
        if float(np.linalg.norm(np.maximum(q, 0.0))) < 0.030:
            return False
    return True


FREE_SPEED = 0.50                    # m/s: an item or the scanner moving faster than this out of the grippers has been dropped, thrown or knocked


def off_counter(pose) -> bool:
    return bool(float(pose[2]) < TOP - 0.05)


def scanner_in_cradle(scanner) -> bool:
    s = np.asarray(scanner, float)
    foot = s[:3] + quat_matrix(s[3:7]) @ np.array([0.0, 0.0, -S_GRIP[2] / 2])
    return bool(math.hypot(foot[0] - CRADLE_C[0], foot[1] - CRADLE_C[1]) <= 0.008 and foot[2] <= TOP + SOCKET_Z + 0.006
                and tilt_deg(s) < 20.0)


def box_distance(name, pose, p) -> float:
    """Distance from a point to an item's bounding box (0 inside it)."""
    it = ITEMS[name]
    half = np.array([it["size"][0], it["size"][0], it["size"][1] / 2] if it["shape"] == "cylinder" else [v / 2 for v in it["size"]])
    pose = np.asarray(pose, float)
    q = np.abs(quat_matrix(pose[3:7]).T @ (np.asarray(p, float)[:3] - pose[:3])) - half
    return float(np.linalg.norm(np.maximum(q, 0.0)))


def scanner_points(scanner):
    """Three points of the scanner: the foot of its grip, the middle of its grip and its window."""
    s = np.asarray(scanner, float)
    r = quat_matrix(s[3:7])
    return [s[:3] + r @ np.array([0.0, 0.0, -S_GRIP[2] / 2]), grip_centre(s), window(s)[0]]


def scanner_put_down(scanner, tcps, poses=None) -> bool:
    """The scanner is out of the hands and put away: both grippers at least 8 cm from its grip, and it either stands
    in its cradle or lies on the counter: low, no part of it over the bagging tray and not on or against the goods
    (its foot, grip and window each at least 2 cm from every item)."""
    s = np.asarray(scanner, float)
    g = grip_centre(s)
    free = all(float(np.linalg.norm(np.asarray(t, float)[:3] - g)) >= 0.08 for t in tcps)
    if not free or off_counter(s):
        return False
    if scanner_in_cradle(s):
        return True
    pts = scanner_points(s)
    if any(over_tray(p, 0.020) for p in pts) or float(s[2]) > TOP + 0.075:
        return False
    if poses is not None and any(box_distance(n, poses[n], p) < 0.020 for n in ITEM_NAMES for p in pts):
        return False
    return True
