"""Geometry and measurements for starting a reflux whose condenser cooling water is still turned off.

An organic chemistry bench. A reflux apparatus is set up on a retort stand: a 250 mL round-bottomed flask of solvent
sits in a heating mantle, a water-cooled reflux condenser is clamped upright on top of it. Two hoses run from the
condenser: one to a bench cooling-water outlet with a quarter-turn lever valve and a ball flow indicator, one to a
drain cup. The valve is closed. The mantle's controller box, with a sprung on/off switch and a lamp, is off.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
GREY = (0.8, 0.8, 0.8)
DARK = (0.2, 0.2, 0.22)
BLUE = (0.08, 0.33, 0.80)
RED = (0.5, 0.07, 0.05)

# -- the apparatus: everything is placed about the flask's axis -------------------------------------------------
FLASK_C = (0.585, 0.050)
BASE_X = (-0.080, 0.120)             # the stand's base plate about the flask axis, along x
BASE_HALF_Y = 0.140
BASE_T = 0.008
ROD_X, ROD_R, ROD_TOP = 0.105, 0.006, 0.480
STAND_MASS = 2.5
MANTLE_R, MANTLE_TOP = 0.080, 0.104  # the mantle's housing (it stands on the base plate)
BULB_R, BULB_Z = 0.0425, 0.120       # the flask's bulb, seated in the mantle's well
NECK_R, NECK_TOP = 0.015, 0.220
MANTLE_MASS = 1.6
COND_R, COND_Z0, COND_TOP = 0.020, NECK_TOP + 0.0003, 0.480   # the condenser's collider stands on the flask's neck
COND_MASS = 0.25
MOVE_MM, MOVE_DEG = 5.0, 3.0         # further than this from where it started, a part of the apparatus has been displaced

# -- bench cooling-water outlet: pipe along y, supply riser at -y, valve, then the flow indicator at +y ----------
VALVE_C = (0.360, -0.210)            # the valve's stem axis
LEVER_LEN, LEVER_W = 0.088, 0.016
LEVER_Z = (0.070, 0.084)             # the lever's underside and top above the bench
LEVER_MASS = 0.06
LEVER_DAMP = 0.004                   # N m s / degree (about 0.23 N m s / rad): viscous friction of the stem packing
LEVER_OPEN_DEG = 90.0                # the quarter turn; stops at 0 (closed) and 90 (open)
WATER_ON_DEG = 60.0                  # water runs once the lever is at least this far round
SIGHT_Y, SIGHT_Z = 0.055, (0.062, 0.122)   # the flow indicator's sight tube: along the pipe from the stem, and its height
TUB_C = (VALVE_C[0] + 0.200, VALVE_C[1] + 0.040)   # a clear catch tub the return hose hangs into (a bench stand-in for a sink)
TUB_R, TUB_H = 0.064, 0.088

# -- drawings switched by the task's rules (nothing here is simulated) ------------------------------------------
JACKET_STEPS, JACKET_FILL_S = 5, 2.0  # the jacket is drawn filling from the bottom in five steps over 2 s of running water
TUB_STEPS, TUB_STEP_S = 8, 0.9        # then the tub's water level is drawn rising one step every 0.9 s of running water, to eight
BOIL_S = 2.0                          # the solvent is drawn boiling once the mantle has been on this long
JACKET_VIS = tuple(f"jacket_glass_{i + 1}" for i in range(JACKET_STEPS)) + tuple(f"jacket_water_{i + 1}" for i in range(JACKET_STEPS))
COND_VIS = ("condenser", *JACKET_VIS, "plume_a", "plume_b")
MANTLE_VIS = ("mantle_flask", "boil_a", "boil_b")
HOOD_VIS = ("fume_hood", "hood_marks")
OUTLET_VIS = ("water_outlet", "flow_still", "flow_on", "tub_stream", *(f"tub_water_{i + 1}" for i in range(TUB_STEPS)))

# -- the mantle's controller box (110 x 150 x 60 mm), its switch and lamp on the top panel ----------------------
CTRL_C = (0.330, 0.215)
CTRL = (0.110, 0.150, 0.060)
CTRL_BOX_H = 0.056                   # the main collider stops 4 mm short of the panel, so the switch cap has room to travel
SW_LOCAL = (-0.025, -0.040)          # the cap's centre on the panel, about the box centre
SW_XY = (CTRL_C[0] + SW_LOCAL[0], CTRL_C[1] + SW_LOCAL[1])
SW_SIZE = (0.022, 0.018, 0.004)
SW_Z = 0.061                         # the cap's centre above the bench at rest (its top 3 mm proud of the panel)
SW_TRAVEL, SW_K, SW_ON = 0.0025, 600.0, 0.0015
LAMP_XY = (CTRL_C[0] + 0.025, CTRL_C[1] - 0.040)
KNOB_LOCAL = (0.008, 0.032)

# -- a 1 L amber solvent bottle with a flame pictogram on its label, standing at the back; dressing, fixed --------
BOTTLE_C = (0.500, 0.360)
BOTTLE_R, BOTTLE_H = 0.046, 0.200
AMBER = (0.36, 0.17, 0.04)

# -- a four-way power strip at the back of the bench, switched on, with the controller's plug in it; fixed scenery --
STRIP_C = (0.765, 0.205)
STRIP = (0.062, 0.300, 0.040)        # lying along y, turned half a turn: its plug's cord grip points at the controller
STRIP_YAW = math.pi

# -- the bench-top fume hood the whole apparatus stands in (fixed): heights are above the bench ------------------
HOOD_IN_Y = 0.500                    # half the interior width (1.00 m between the side panels)
HOOD_POST_W = 0.050                  # each front post stands this far into the opening (0.90 m between the posts)
HOOD_WALL = 0.050                    # side panels (the right one is a glazed frame)
HOOD_BACK_T = 0.030                  # back panel
HOOD_X0 = 0.000                      # the front face of the posts and of the panel above the sash
HOOD_POST_X1 = 0.080                 # the front posts run back to here
HOOD_BACK = 0.875                    # inner face of the back panel
HOOD_BAFFLE_X = (0.862, 0.870)       # the slotted baffle in front of the back panel
HOOD_CEIL, HOOD_TOP = 1.200, 1.500   # interior ceiling and the top of the housing
SASH_X = (0.031, 0.049)              # the sash: its bottom pull rail's depth (the glass is 6 mm at the middle of it)
SASH_OPEN = 0.500                    # the sash's lower edge: the marked working height
SASH_FULL = 0.850                    # the opening's full height (the panel above the sash starts here)
SILL_X, SILL_H = (0.050, 0.125), 0.022   # the airfoil sill across the front, between the posts
HOOD_DUCT = (0.480, 0.0, 0.125)      # exhaust collar on the top: axis x, y and radius
HOOD_LIGHT = 12000.0                 # the ceiling light panel's brightness (a lamp in the simulator)
ARM_R = 0.050                        # an arm's links, taken as this far round their centre lines, are at the sash when they reach it

HAND_CLEAR = 0.05                    # both hands must end at least this far from the lever, the switch and the apparatus


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


# -- start poses of the three parts of the apparatus (body origins) ------------------------------------------------
_BASE_CX = (BASE_X[0] + BASE_X[1]) / 2
STAND_POS = (FLASK_C[0] + _BASE_CX, FLASK_C[1], TOP + BASE_T / 2)
_M_Z0 = BASE_T + 0.0002                                  # the mantle's underside: on the base plate
_M_ZC = (_M_Z0 + MANTLE_TOP) / 2
MANTLE_POS = (FLASK_C[0], FLASK_C[1], TOP + _M_ZC)
_C_ZC = (COND_Z0 + COND_TOP) / 2
COND_POS = (FLASK_C[0], FLASK_C[1], TOP + _C_ZC)
START = {"stand": STAND_POS, "mantle_flask": MANTLE_POS, "condenser": COND_POS}


def stand_object() -> Part:
    """The retort stand: a free body. Colliders (hidden): the base plate and the rod. Boss heads and clamps are drawn."""
    rod_h = ROD_TOP - BASE_T
    pieces = (Piece("cylinder", (ROD_R, rod_h, ROD_R), (ROD_X - _BASE_CX, 0.0, BASE_T / 2 + rod_h / 2), color=GREY),)
    return Part("stand", pos=STAND_POS, size=(BASE_X[1] - BASE_X[0], 2 * BASE_HALF_Y, BASE_T), exact_z=True, mass=STAND_MASS,
                color=DARK, friction=(0.6, 0.5), pieces=pieces, com=(0.02, 0.0, 0.004), contact_offset=0.002,
                **_vis("retort_stand", (-_BASE_CX, 0.0, -BASE_T / 2)))


def mantle_object() -> Part:
    """The heating mantle with the flask seated in it: one free body standing on the stand's base plate. Colliders
    (hidden): the housing as a cylinder, the flask's bulb as a sphere and its neck as a cylinder."""
    neck_z0 = BULB_Z + BULB_R - 0.006
    pieces = (Piece("sphere", (BULB_R, BULB_R, BULB_R), (0.0, 0.0, BULB_Z - _M_ZC), color=GREY),
              Piece("cylinder", (NECK_R, NECK_TOP - neck_z0, NECK_R), (0.0, 0.0, (neck_z0 + NECK_TOP) / 2 - _M_ZC), color=GREY))
    return Part("mantle_flask", pos=MANTLE_POS, size=(MANTLE_R, MANTLE_TOP - _M_Z0, MANTLE_R), shape="cylinder", exact_z=True,
                mass=MANTLE_MASS, color=GREY, friction=(0.7, 0.6), pieces=pieces, com=(0.0, 0.0, 0.050 - _M_ZC),
                contact_offset=0.002, **_vis(MANTLE_VIS, (0.0, 0.0, -_M_ZC), visual_glass_opacity=0.16))


def condenser_object() -> Part:
    """The condenser: a free body (a cylinder, hidden) standing on the flask's neck. Nothing but its weight and
    friction holds it there: its ground joint and its clamp are drawn, not simulated, so a knock topples it. Its
    jacket is drawn in five slices, each empty (clear glass) or filled with light see-through water; a vapour plume at
    its open top is drawn when the task's rule says vapour is escaping."""
    return Part("condenser", pos=COND_POS, size=(COND_R, COND_TOP - COND_Z0, COND_R), shape="cylinder", exact_z=True,
                mass=COND_MASS, color=GREY, friction=(0.7, 0.6), contact_offset=0.002,
                **_vis(COND_VIS, (0.0, 0.0, -_C_ZC)))


def outlet_object() -> Part:
    """The cooling-water outlet: fixed. Colliders (hidden): pipe, valve body and riser as one box, the flow indicator
    as a cylinder, the clear catch tub as a cylinder. The flow indicator's ball is drawn low (no flow) or high (flow);
    a thin stream from the hose end and the water level in the tub (eight slices) are drawn by the task's rule."""
    h = 0.060
    y0, y1 = -0.086, SIGHT_Y - 0.014
    cy = (y0 + y1) / 2
    zc = h / 2
    sight_h = 0.146 - 0.040
    pieces = (Piece("cylinder", (0.0135, sight_h, 0.0135), (0.0, SIGHT_Y - cy, 0.040 + sight_h / 2 - zc), color=GREY),
              Piece("box", (0.032, 0.012, 0.012), (0.024, SIGHT_Y - cy, 0.130 - zc), color=GREY),
              Piece("cylinder", (TUB_R, TUB_H, TUB_R), (TUB_C[0] - VALVE_C[0], TUB_C[1] - VALVE_C[1] - cy, TUB_H / 2 - zc), color=GREY))
    return Part("water_outlet", pos=(VALVE_C[0], VALVE_C[1] + cy, TOP + zc), size=(0.036, y1 - y0, h), exact_z=True, color=GREY,
                friction=(0.5, 0.4), pieces=pieces, **_vis(OUTLET_VIS, (0.0, -cy, -zc)))


LEVER_ARM = (0.010, 0.086)           # the lever's collider runs from here to here along the lever, from the stem axis
_L_MID = (LEVER_ARM[0] + LEVER_ARM[1]) / 2
_L_ZC = (LEVER_Z[0] + LEVER_Z[1]) / 2


def lever_object() -> Part:
    """The valve's lever: a free body on a hinge about the stem (vertical), with stops at closed (lying across the
    pipe, pointing at the arms) and open (a quarter turn anticlockwise seen from above, lying along the pipe), and
    viscous friction, so it stays where it is left."""
    hinge = Hinge(pivot=(VALVE_C[0], VALVE_C[1], TOP + _L_ZC), axis="Z", damping=LEVER_DAMP, lower_deg=0.0, upper_deg=LEVER_OPEN_DEG)
    pieces = (Piece("cylinder", (0.013, 0.018, 0.013), (_L_MID, 0.0, 0.001), color=BLUE),)
    return Part("valve_lever", pos=(VALVE_C[0] - _L_MID, VALVE_C[1], TOP + _L_ZC), size=(LEVER_ARM[1] - LEVER_ARM[0], LEVER_W, LEVER_Z[1] - LEVER_Z[0]),
                exact_z=True, mass=LEVER_MASS, color=BLUE, friction=(0.8, 0.6), pieces=pieces, hinge=hinge, contact_offset=0.002,
                **_vis("valve_lever", (_L_MID, 0.0, -_L_ZC)))


def lines_object() -> Part:
    """Hoses, cables and leads (and the charger brick's shape on the power strip): drawn only (they do not move or
    collide). The body is the hose clip on the flow indicator's barb."""
    pos = (VALVE_C[0] + 0.030, VALVE_C[1] + SIGHT_Y, TOP + 0.130)
    return Part("lines", pos=pos, size=(0.008, 0.015, 0.015), exact_z=True, color=GREY, friction=(0.5, 0.4),
                **_vis("lines", (-pos[0], -pos[1], TOP - pos[2])))


def bottle_object() -> Part:
    """The solvent bottle: fixed, a cylinder (hidden). It is there to be seen, not handled."""
    return Part("solvent_bottle", pos=(BOTTLE_C[0], BOTTLE_C[1], TOP + BOTTLE_H / 2), size=(BOTTLE_R, BOTTLE_H, BOTTLE_R), shape="cylinder",
                exact_z=True, color=AMBER, friction=(0.5, 0.4), **_vis("solvent_bottle", (0.0, 0.0, -BOTTLE_H / 2)))


def strip_object() -> Part:
    """The power strip with the controller's plug and a charger in it: fixed scenery, not a control. Colliders (hidden):
    the strip, the plug and the charger as boxes. Its switches are drawn lit; the leads are drawn only."""
    zc = STRIP[2] / 2
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, -0.015, zc + 0.013), color=DARK),
              Piece("box", (0.044, 0.044, 0.027), (0.006, 0.045, zc + 0.0135), color=GREY))
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=GREY, friction=(0.5, 0.4),
                yaw=STRIP_YAW, pieces=pieces,
                **_vis(("power_set", "strip_lamps_on", "strip_main_on"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main", "cooker_cord", "lead")))


def hood_boxes():
    """The hood's colliders as world boxes (lo, hi): what the arms must work round."""
    yo = HOOD_IN_Y + HOOD_WALL
    b = {"back": ((HOOD_BACK, -yo, 0.0), (HOOD_BACK + HOOD_BACK_T, yo, HOOD_TOP)),
         "side_left": ((HOOD_X0, HOOD_IN_Y, 0.0), (HOOD_BACK, yo, HOOD_TOP)),
         "side_right": ((HOOD_X0, -yo, 0.0), (HOOD_BACK, -HOOD_IN_Y, HOOD_TOP)),
         "top": ((HOOD_X0, -HOOD_IN_Y, HOOD_CEIL), (HOOD_BACK, HOOD_IN_Y, HOOD_TOP)),
         "front_panel": ((HOOD_X0, -HOOD_IN_Y, SASH_FULL), (HOOD_X0 + 0.015, HOOD_IN_Y, HOOD_CEIL)),
         "sash": ((SASH_X[0], -HOOD_IN_Y, SASH_OPEN), (SASH_X[1], HOOD_IN_Y, HOOD_CEIL)),
         "sill": ((SILL_X[0], -HOOD_IN_Y, 0.0), (SILL_X[1], HOOD_IN_Y, SILL_H)),
         "post_left": ((HOOD_X0, HOOD_IN_Y - HOOD_POST_W, 0.0), (HOOD_POST_X1, HOOD_IN_Y, HOOD_TOP)),
         "post_right": ((HOOD_X0, -HOOD_IN_Y, 0.0), (HOOD_POST_X1, -HOOD_IN_Y + HOOD_POST_W, HOOD_TOP)),
         "baffle": ((HOOD_BAFFLE_X[0], -HOOD_IN_Y, 0.060), (HOOD_BAFFLE_X[1], HOOD_IN_Y, HOOD_CEIL))}
    return {n: ((lo[0], lo[1], TOP + lo[2]), (hi[0], hi[1], TOP + hi[2])) for n, (lo, hi) in b.items()}


def hood_object() -> Part:
    """The fume hood: fixed. Colliders (hidden boxes): back panel, two side panels, the housing above the ceiling, the
    panel above the sash, the glass sash with its bottom rail at the working height, the airfoil sill and the baffle.
    The sash's glass and the glazed right side are drawn perfectly clear (frames, rail and stiles only).
    The arms work through the opening between the sill and the sash's lower edge."""
    boxes = hood_boxes()
    lo, hi = (np.asarray(v) for v in boxes.pop("back"))
    c0 = (lo + hi) / 2
    pieces = []
    for lo_i, hi_i in boxes.values():
        lo_i, hi_i = np.asarray(lo_i), np.asarray(hi_i)
        pieces.append(Piece("box", tuple(float(v) for v in hi_i - lo_i), tuple(float(v) for v in (lo_i + hi_i) / 2 - c0), color=GREY))
    return Part("fume_hood", pos=tuple(float(v) for v in c0), size=tuple(float(v) for v in hi - lo), exact_z=True, color=GREY,
                friction=(0.5, 0.4), pieces=tuple(pieces), **_vis(HOOD_VIS, (-float(c0[0]), -float(c0[1]), TOP - float(c0[2]))))


def controller_object() -> Part:
    """The mantle's controller box: fixed. Colliders (hidden): the box up to 4 mm below its panel, the panel round the
    switch opening as four slabs, the dial. Its lamp is drawn lit or unlit by the task."""
    zc = CTRL_BOX_H / 2
    sx, sy = SW_LOCAL
    hx, hy = 0.0125, 0.0105              # half the switch opening
    lx, ly = CTRL[0] / 2, CTRL[1] / 2
    z = CTRL[2] - 0.002 - zc
    slab = 0.004
    pieces = (Piece("box", (CTRL[0], ly - (sy + hy), slab), (0.0, (ly + sy + hy) / 2, z), color=GREY),
              Piece("box", (CTRL[0], (sy - hy) + ly, slab), (0.0, (sy - hy - ly) / 2, z), color=GREY),
              Piece("box", (lx - (sx + hx), 2 * hy, slab), ((lx + sx + hx) / 2, sy, z), color=GREY),
              Piece("box", ((sx - hx) + lx, 2 * hy, slab), ((sx - hx - lx) / 2, sy, z), color=GREY),
              Piece("cylinder", (0.020, 0.022, 0.020), (KNOB_LOCAL[0], KNOB_LOCAL[1], CTRL[2] + 0.011 - zc), color=DARK))
    return Part("mantle_controller", pos=(CTRL_C[0], CTRL_C[1], TOP + zc), size=(CTRL[0], CTRL[1], CTRL_BOX_H), exact_z=True, color=GREY,
                friction=(0.5, 0.4), pieces=pieces, **_vis(("mantle_controller", "heat_lamp_on", "heat_lamp_off"), (0.0, 0.0, -zc)))


def switch_object() -> Part:
    """The controller's on/off switch: a sprung cap that is pushed straight down."""
    spring = Spring(axis="Z", lower=-SW_TRAVEL, upper=0.0, stiffness=SW_K, damping=6.0, target=0.0)
    return Part("heat_switch", pos=(SW_XY[0], SW_XY[1], TOP + SW_Z), size=SW_SIZE, exact_z=True, mass=0.003, color=RED,
                friction=(0.8, 0.7), spring=spring, contact_offset=0.001,
                **_vis(("heat_switch_on", "heat_switch_off"), (-SW_LOCAL[0], -SW_LOCAL[1], -SW_Z)))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def turn_deg(pose) -> float:
    """How far a body has turned from its start (which is unturned), about any axis (degrees)."""
    x, y, z, w = (float(v) for v in np.asarray(pose, float)[3:7])
    return math.degrees(2.0 * math.atan2(math.sqrt(x * x + y * y + z * z), abs(w)))


def lever_deg(lever) -> float:
    """The lever's angle from closed (degrees): 0 lying across the pipe, 90 lying along it."""
    r = quat_matrix(np.asarray(lever, float)[3:7])
    return math.degrees(math.atan2(r[1, 0], r[0, 0]))


def water_on(lever) -> bool:
    return bool(lever_deg(lever) >= WATER_ON_DEG)


def switch_press(sw) -> float:
    """How far the switch cap is pushed down (m)."""
    return float(TOP + SW_Z - np.asarray(sw, float)[2])


def shift(name, pose):
    """How far a part of the apparatus is from where it started: (mm, degrees)."""
    p = np.asarray(pose, float)
    return 1000.0 * float(np.linalg.norm(p[:3] - np.asarray(START[name]))), turn_deg(p)


def displaced(name, pose) -> bool:
    mm, deg = shift(name, pose)
    return bool(mm > MOVE_MM or deg > MOVE_DEG)


def condenser_off(condenser, flask):
    """The condenser is no longer seated on the flask's neck: measured against the flask (so that an apparatus moved
    as a whole still counts as seated), it has shifted or lifted more than MOVE_MM or tipped more than MOVE_DEG."""
    c, f = np.asarray(condenser, float), np.asarray(flask, float)
    rf = quat_matrix(f[3:7])
    rel = rf.T @ (c[:3] - f[:3]) - (np.asarray(COND_POS) - np.asarray(MANTLE_POS))
    x, y, z, w = c[3:7]
    rc = quat_matrix(c[3:7])
    tip = math.degrees(math.acos(float(np.clip((rf.T @ rc)[2, 2], -1.0, 1.0))))
    return bool(1000.0 * float(np.linalg.norm(rel)) > MOVE_MM or tip > MOVE_DEG)


def sash_gap(points) -> float:
    """Shortest distance (m) from points along an arm's centre line to the sash (its glass and pull rail, from its
    lower edge up), less the arm's half thickness ARM_R: 0 or less means the arm is at the glass."""
    lo, hi = (np.asarray(v, float) for v in hood_boxes()["sash"])
    p = np.asarray(points, float).reshape(-1, 3)
    d = np.linalg.norm(np.maximum(np.maximum(lo - p, p - hi), 0.0), axis=1)
    return float(d.min() - ARM_R)


def lever_points(lever):
    """The lever's two ends (stem end, tip) as measured."""
    p = np.asarray(lever, float)
    r = quat_matrix(p[3:7])
    half = (LEVER_ARM[1] - LEVER_ARM[0]) / 2
    return p[:3] + r @ np.array([half + LEVER_ARM[0], 0.0, 0.0]), p[:3] - r @ np.array([half, 0.0, 0.0])


def _to_segment(p, a, b) -> float:
    p, a, b = (np.asarray(v, float)[:3] for v in (p, a, b))
    t = float(np.clip((p - a) @ (b - a) / max(float((b - a) @ (b - a)), 1e-12), 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * (b - a))))


def hand_gap(tcp, lever, switch) -> float:
    """Shortest distance (m) from a hand's grasp point to the lever, the switch cap or the apparatus (taken as an
    upright cylinder of the mantle's radius on the flask axis, as tall as the condenser)."""
    tcp = np.asarray(tcp, float)[:3]
    a, b = lever_points(lever)
    d_lever = _to_segment(tcp, a, b) - LEVER_W / 2
    d_switch = float(np.linalg.norm(tcp - np.asarray(switch, float)[:3])) - SW_SIZE[0] / 2
    radial = math.hypot(tcp[0] - FLASK_C[0], tcp[1] - FLASK_C[1]) - MANTLE_R
    above = tcp[2] - (TOP + COND_TOP)
    d_app = math.hypot(max(radial, 0.0), max(above, 0.0)) if (radial > 0 or above > 0) else 0.0
    return float(min(d_lever, d_switch, d_app))
