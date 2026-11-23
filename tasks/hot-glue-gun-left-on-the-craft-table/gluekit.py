"""Geometry and measurements for tidying a child's craft table on which a hot glue gun was left plugged in.

A craft table. A mini hot-melt glue gun lies on its side on the craft paper, plugged into a power strip that is
switched on (its lamp is lit, a bead of glue hangs at the nozzle, a drip lies on the paper). Round it: child's
scissors, two spare glue sticks, a small glued paper house. An open craft storage box with paper and felt in it
stands at the right. The gun's silicone drip mat lies at the back. The child's place (place mat, cup, crayons) is
to the left of the craft paper.

Frame: metres, x away from the arm bases, y left, z up; TOP is the table. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WHITE = (0.95, 0.95, 0.93)
RED = (0.84, 0.10, 0.10)
KRAFT = (0.80, 0.66, 0.46)
TEAL = (0.10, 0.62, 0.60)
BLUE = (0.62, 0.80, 0.93)
MILKY = (0.96, 0.95, 0.88)

# -- the sheet of craft paper everything was glued on (195 x 300 mm), fixed ------------------------------------------
SHEET_C = (0.2875, 0.0)
SHEET = (0.195, 0.300)
SHEET_TOP = 0.001

# -- the glue gun (mini, 130 g): handle 34 x 30 x 85 mm, barrel housing on top, wire stand folded out ------------------
# The gun's own frame (as it stands): origin at the centre of the handle's base, X along the barrel towards the nozzle,
# Z up the handle. The body's frame in the simulation is that of the gun as it starts, lying on its side: body x = gun Z,
# body y = -gun X, body z = -gun Y, with its origin at the centre of the handle.
HANDLE = (0.034, 0.030, 0.085)       # gun X, Y, Z
GUN_MASS = 0.13
GUN_BASE0 = (0.240, 0.060)           # where the centre of the handle's base starts; the nozzle points to -y, the handle base to -x
GUN_Z0 = SHEET_TOP + 0.0265          # the handle's centre as spawned (the gun then settles on its side and one stand foot)
NOZZLE_G = (0.108, 0.0, 0.100)       # nozzle tip in the gun's frame
BODY_G = (0.0135, 0.0, 0.102)        # centre of the barrel housing
FOOT_X, FOOT_HALF_Y = 0.074, 0.0255  # the wire stand's foot bar
GRIP_G = (0.0, 0.0, 0.045)           # where a hand takes the handle: below the trigger


def _g(p):
    """A point of the gun's frame in the body's frame (origin at the handle's centre)."""
    return (p[2] - HANDLE[2] / 2, -p[0], -p[1])


# -- the silicone drip mat (130 x 170 mm, floor 3 mm, rim 5.5 mm) at the back, fixed -----------------------------------
MAT_C = (0.455, -0.020)
MAT = (0.130, 0.170)
MAT_FLOOR, MAT_RIM = 0.003, 0.0055
GUN_PUT = (0.460, 0.030)             # where the demo stands the handle's base

# -- the craft storage box (230 x 170 x 75 mm, paper and felt 15 mm deep in it), free --------------------------------
BOX_C = (0.300, -0.305)
BOX = (0.230, 0.170, 0.075)
BOX_WALL = 0.0025
BOX_FILL = 0.015                     # top of the paper and felt already in it
BOX_MASS = 0.50

# -- the cool things to put away ---------------------------------------------------------------------------------
SCISSORS_C = (0.315, -0.110)         # centre of the scissors' footprint (135 x 64 x 12 mm), blades towards +x
SC_GRIP = -0.041                     # the handle loops are this far behind the footprint's centre
SC_MASS = 0.030
STICK = (0.100, 0.0105)              # glue stick: 100 mm long, 11 mm across (collider: a square bar, so it does not roll)
STICKS = ((0.250, -0.030), (0.410, -0.160))
STICK_MASS = 0.012
HOUSE_C = (0.212, 0.135)             # the glued paper house (56 x 44 mm, 66 mm tall, 12 g)
HOUSE_MASS = 0.012
COOL = ("scissors", "glue_stick1", "glue_stick2")

# -- the child's place, to the left of the craft paper -----------------------------------------------------------------
PLACE_C = (0.290, 0.330)             # centre of the place mat (260 mm along x, 180 mm along y)
PLACE = (0.260, 0.180)
CHILD_Y = PLACE_C[1] - PLACE[1] / 2 - 0.040      # the child's side of the table: from 4 cm short of the place mat leftwards

# -- power strip (62 x 300 x 40 mm) the gun is plugged into, lying along y at the back right; fixed -------------------
STRIP_C = (0.500, -0.265)
STRIP = (0.062, 0.300, 0.040)
STRIP_BOX_H = 0.036                  # the strip's collider stops 4 mm short of its top, so its master switch has room to travel
SW_XY = (STRIP_C[0], STRIP_C[1] + 0.125)   # the master switch, at the strip's end nearest the drip mat
SW_SIZE = (0.022, 0.018, 0.004)
SW_Z = 0.0405                        # the cap's centre above the table
SW_TRAVEL, SW_K, SW_ON = 0.0025, 600.0, 0.0015


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def sheet_object() -> Part:
    return Part("craft_paper", pos=(SHEET_C[0], SHEET_C[1], TOP + SHEET_TOP - 0.002), size=(SHEET[0], SHEET[1], 0.004), exact_z=True,
                color=KRAFT, friction=(0.9, 0.8), **_vis("craft_paper", (0.0, 0.0, 0.002 - SHEET_TOP)))


def gun_object() -> Part:
    """The glue gun: one free rigid body. Colliders (hidden): the handle, the barrel housing, the nozzle, the glue
    stick in its back and the stand's foot bar, all boxes. The trigger, the stand's legs and the cord are drawn only."""
    def box(size_g, centre_g):
        return Piece("box", (size_g[2], size_g[0], size_g[1]), _g(centre_g), color=RED)
    pieces = (
        box((0.117, 0.032, 0.042), (0.0135, 0.0, 0.102)),
        box((0.038, 0.010, 0.010), (0.089, 0.0, 0.100)),
        box((0.050, 0.011, 0.011), (-0.070, 0.0, 0.104)),
        box((0.004, 2 * FOOT_HALF_Y, 0.003), (FOOT_X, 0.0, 0.0015)),
    )
    pos = (GUN_BASE0[0] + HANDLE[2] / 2, GUN_BASE0[1], TOP + GUN_Z0)
    return Part("glue_gun", pos=pos, size=(HANDLE[2], HANDLE[0], HANDLE[1]), exact_z=True, mass=GUN_MASS, color=RED,
                friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002, com=_g((0.008, 0.0, 0.080)),
                **_vis(("glue_gun", "gun_lamp_on", "gun_lamp_off"), (-HANDLE[2] / 2, 0.0, 0.0), visual_rpy_deg=(-90.0, 0.0, -90.0),
                       visual_hide=("lamp", "lamp_side")))


def mat_object() -> Part:
    """The drip mat: fixed. Colliders: its floor and the four sides of its rim."""
    hx, hy = MAT[0] / 2, MAT[1] / 2
    rz = (MAT_RIM - MAT_FLOOR) / 2 + MAT_FLOOR / 2
    rh = MAT_RIM - MAT_FLOOR
    pieces = (Piece("box", (0.005, MAT[1], rh), (-hx + 0.0025, 0.0, rz), color=TEAL),
              Piece("box", (0.005, MAT[1], rh), (hx - 0.0025, 0.0, rz), color=TEAL),
              Piece("box", (MAT[0], 0.005, rh), (0.0, -hy + 0.0025, rz), color=TEAL),
              Piece("box", (MAT[0], 0.005, rh), (0.0, hy - 0.0025, rz), color=TEAL))
    return Part("drip_mat", pos=(MAT_C[0], MAT_C[1], TOP + MAT_FLOOR / 2), size=(MAT[0], MAT[1], MAT_FLOOR), exact_z=True, color=TEAL,
                friction=(0.9, 0.8), pieces=pieces, **_vis("drip_mat", (0.0, 0.0, -MAT_FLOOR / 2)))


def box_object() -> Part:
    """The craft box: one free rigid body. Colliders (hidden): the paper and felt in it as a slab, and four walls."""
    zc = BOX_FILL / 2
    hx, hy, t = BOX[0] / 2, BOX[1] / 2, 0.004
    wz = BOX[2] / 2 - zc
    pieces = (Piece("box", (t, BOX[1], BOX[2]), (-hx + t / 2, 0.0, wz), color=BLUE),
              Piece("box", (t, BOX[1], BOX[2]), (hx - t / 2, 0.0, wz), color=BLUE),
              Piece("box", (BOX[0], t, BOX[2]), (0.0, -hy + t / 2, wz), color=BLUE),
              Piece("box", (BOX[0], t, BOX[2]), (0.0, hy - t / 2, wz), color=BLUE))
    return Part("craft_box", pos=(BOX_C[0], BOX_C[1], TOP + zc), size=(BOX[0] - 0.004, BOX[1] - 0.004, BOX_FILL), exact_z=True,
                mass=BOX_MASS, color=BLUE, friction=(0.6, 0.5), pieces=pieces, **_vis("craft_box", (0.0, 0.0, -zc)))


def scissors_object() -> Part:
    """Child's scissors, closed: one free rigid body. Colliders: the two handle loops as one block, the blades a bar."""
    pieces = (Piece("box", (0.068, 0.014, 0.003), (0.034 - SC_GRIP, 0.0, 0.0), color=WHITE),)
    return Part("scissors", pos=(SCISSORS_C[0] + SC_GRIP, SCISSORS_C[1], TOP + SHEET_TOP + 0.0065), size=(0.048, 0.064, 0.012),
                exact_z=True, mass=SC_MASS, color=(0.45, 0.78, 0.15), friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002,
                **_vis("scissors", (-SC_GRIP, 0.0, -0.006)))


def stick_object(i: int) -> Part:
    x, y = STICKS[i]
    on_sheet = abs(x - SHEET_C[0]) < SHEET[0] / 2 and abs(y - SHEET_C[1]) < SHEET[1] / 2
    z = TOP + (SHEET_TOP if on_sheet else 0.0) + STICK[1] / 2 + 0.0005
    return Part(f"glue_stick{i + 1}", pos=(x, y, z), size=(STICK[0], STICK[1], STICK[1]), exact_z=True, mass=STICK_MASS, color=MILKY,
                friction=(1.2, 1.0), contact_offset=0.002, **_vis("glue_stick", (0.0, 0.0, -STICK[1] / 2 - 0.00025)))


def house_object() -> Part:
    pieces = (Piece("box", (0.062, 0.030, 0.014), (0.0, 0.0, 0.026), color=RED),)
    return Part("paper_house", pos=(HOUSE_C[0], HOUSE_C[1], TOP + SHEET_TOP + 0.0195), size=(0.056, 0.044, 0.038), exact_z=True,
                mass=HOUSE_MASS, color=(0.97, 0.94, 0.84), friction=(1.0, 0.9), pieces=pieces, contact_offset=0.002,
                **_vis("paper_house", (0.0, 0.0, -0.019)))


def place_object() -> Part:
    """The child's place: place mat, drawing, cup with straw and crayons; fixed set dressing."""
    pieces = (Piece("cylinder", (0.036, 0.092, 0.036), (-0.085, 0.035, 0.047), color=(0.96, 0.50, 0.65)),)
    return Part("child_place", pos=(PLACE_C[0], PLACE_C[1], TOP + 0.001), size=(PLACE[0], PLACE[1], 0.002), exact_z=True,
                color=(0.99, 0.90, 0.45), friction=(0.8, 0.7), pieces=pieces, yaw=math.pi, **_vis("child_place", (0.0, 0.0, -0.001)))


def strip_object() -> Part:
    """The power strip with the gun's plug in it: fixed. Colliders (hidden): the strip and the plug as boxes; the gun's
    cord is drawn only (two lays, switched by the task). A phone charger and a mains adapter are plugged in beside it
    (boxes; their leads are drawn only). Its socket switches are drawn lit or unlit by the task."""
    zc = STRIP_BOX_H / 2
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, 0.015, zc + 0.013), color=WHITE),
              Piece("box", (0.046, 0.046, 0.028), (0.006, -0.045, STRIP[2] + 0.014 - zc), color=WHITE),      # a phone charger
              Piece("box", (0.034, 0.040, 0.044), (0.006, -0.105, STRIP[2] + 0.022 - zc), color=WHITE))      # a mains adapter
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=(STRIP[0], STRIP[1], STRIP_BOX_H), exact_z=True, color=WHITE,
                friction=(0.5, 0.4), pieces=pieces,
                **_vis(("power_set", "strip_lamps_on", "strip_lamps_off", "cord_lying", "cord_stand", "strip_clutter"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main")))


def switch_object() -> Part:
    """The strip's master switch: a sprung cap that is pushed straight down."""
    spring = Spring(axis="Z", lower=-SW_TRAVEL, upper=0.0, stiffness=SW_K, damping=6.0, target=0.0)
    return Part("strip_switch", pos=(SW_XY[0], SW_XY[1], TOP + SW_Z), size=SW_SIZE, exact_z=True, mass=0.003,
                color=(1.0, 0.45, 0.04), friction=(0.8, 0.7), spring=spring, contact_offset=0.001,
                **_vis(("strip_main_on", "strip_main_off"), (STRIP_C[0] - SW_XY[0], STRIP_C[1] - SW_XY[1], -SW_Z)))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def gun_point(gun, p_gun) -> np.ndarray:
    """A point given in the gun's own frame, in the world."""
    gun = np.asarray(gun, float)
    return gun[:3] + quat_matrix(gun[3:7]) @ np.asarray(_g(p_gun), float)


def gun_tilt_deg(gun) -> float:
    """Angle between the gun's handle axis and straight up (0 = standing upright, 90 = lying)."""
    r = quat_matrix(np.asarray(gun, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 0], -1.0, 1.0))))


def over_mat(p, margin=0.0) -> bool:
    return bool(abs(float(p[0]) - MAT_C[0]) <= MAT[0] / 2 + margin and abs(float(p[1]) - MAT_C[1]) <= MAT[1] / 2 + margin)


def gun_standing_on_mat(gun) -> bool:
    """The gun stands on its handle base and wire stand on the drip mat: upright within 20 degrees, the handle's base
    and both stand feet on the mat, and the nozzle over the mat."""
    base = gun_point(gun, (0.0, 0.0, 0.0))
    feet = [gun_point(gun, (FOOT_X, s * FOOT_HALF_Y, 0.0)) for s in (-1.0, 1.0)]
    low = all(p[2] <= TOP + MAT_RIM + 0.006 for p in (base, *feet))
    return bool(gun_tilt_deg(gun) <= 20.0 and low and all(over_mat(p) for p in (base, *feet)) and over_mat(gun_point(gun, NOZZLE_G)))


def _rect_dist(p, c, half):
    dx = max(abs(float(p[0]) - c[0]) - half[0], 0.0)
    dy = max(abs(float(p[1]) - c[1]) - half[1], 0.0)
    return math.hypot(dx, dy)


def box_local(box, p) -> np.ndarray:
    """A world point in the box's frame, z measured from the box's underside."""
    box = np.asarray(box, float)
    q = quat_matrix(box[3:7]).T @ (np.asarray(p, float)[:3] - box[:3])
    return np.array([q[0], q[1], q[2] + BOX_FILL / 2])


def in_box(box, p, above=0.0) -> bool:
    """A point inside the box: within its walls and below its rim (or up to ``above`` over the rim)."""
    q = box_local(box, p)
    return bool(abs(q[0]) <= BOX[0] / 2 - BOX_WALL and abs(q[1]) <= BOX[1] / 2 - BOX_WALL and 0.0 <= q[2] <= BOX[2] + above)


def gun_in_box(box, gun) -> bool:
    """The gun is in the box, or lies on top of it: the centre of its housing or its nozzle tip is within the box's
    walls and lower than 4 cm above its rim."""
    return bool(any(in_box(box, gun_point(gun, p), above=0.040) for p in (BODY_G, NOZZLE_G)))


def nozzle_paper_gap(gun, box) -> float:
    """Distance (m) from the nozzle tip to the nearest paper or felt: the craft sheet, or what lies in the box."""
    n = gun_point(gun, NOZZLE_G)
    d_sheet = math.hypot(_rect_dist(n, SHEET_C, (SHEET[0] / 2, SHEET[1] / 2)), max(n[2] - (TOP + SHEET_TOP), 0.0))
    q = box_local(box, n)
    d_box = math.hypot(_rect_dist(q, (0.0, 0.0), (BOX[0] / 2 - BOX_WALL, BOX[1] / 2 - BOX_WALL)), max(q[2] - BOX_FILL, 0.0))
    return float(min(d_sheet, d_box))


def gun_on_childs_side(gun) -> bool:
    """Any of the gun's handle base, housing centre or nozzle on the child's side of the table."""
    return bool(any(gun_point(gun, p)[1] >= CHILD_Y for p in ((0.0, 0.0, 0.0), BODY_G, NOZZLE_G)))


def switch_press(sw) -> float:
    """How far the strip's master switch is pushed down (m)."""
    return float(TOP + SW_Z - np.asarray(sw, float)[2])
