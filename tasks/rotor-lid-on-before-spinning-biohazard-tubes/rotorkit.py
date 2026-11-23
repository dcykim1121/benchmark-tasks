"""Geometry and measurements for spinning biohazard samples in a benchtop microcentrifuge whose rotor lid was left off.

A biology bench. A microcentrifuge stands with its hinged outer lid open; its fixed-angle rotor is loaded with a
balanced set of capped sample tubes. The rotor's own aerosol-tight lid (a clear disc with a centre knob) lies on the
bench beside it, next to the tube rack the samples came from, which carries a biohazard sign.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Every body spawns with identity
orientation (the rack and its tubes are turned about z), so a measured rotation is the body's rotation from rest.
Sizes are from the CAD models, themselves estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WHITE = (0.90, 0.91, 0.92)
STEEL = (0.74, 0.75, 0.76)
DARK = (0.09, 0.10, 0.12)
GREEN = (0.10, 0.60, 0.24)
CLEAR = (0.80, 0.90, 0.95)
BLUE = (0.10, 0.33, 0.68)
ORANGE = (1.00, 0.42, 0.02)
TUBE = (0.86, 0.90, 0.93)

# -- microcentrifuge (230 mm wide, 300 mm deep, 216 mm tall with its lid shut). CF_C is the rotor's axis ---------
CF_C = (0.380, 0.060)
BODY_X = (-0.095, 0.125)             # the housing round the chamber, about the rotor axis, along x
CONSOLE_X = (-0.175, -0.095)         # the low control console in front of it
BODY_HALF_Y = 0.115
DECK_Z = 0.180                       # the top of the housing round the chamber's mouth, above the bench
CH_R = 0.082                         # chamber radius (as drawn)
CH_COLLIDER_R = 0.084                # the collider's bore: 2 mm more
CH_FLOOR_Z = 0.088
ROTOR_R = 0.066
RIM_Z = 0.140                        # the rotor's rim: the rotor lid's underside rests here when it is on
SHUT_TOP_Z = 0.216                   # the top of the outer lid when shut

# -- the rotor's catch: a sprung nose on the rotor's hub that the rotor lid's socket goes over -------------------
CATCH_R = 0.0083
CATCH_CYL = 0.014
CATCH_UP = 0.004                     # at rest the nose holds a lid laid on it this far above the rim
SOCKET_Z = 0.012                     # the lid's socket: its ceiling above the disc's underside
CATCH_TRAVEL, CATCH_K = 0.005, 400.0
CATCH_REST, CATCH_HOLD = 0.0025, -0.0046     # the spring's rest target (a 1 N preload) and where the click parks it
CLICK_Z = 0.0008                     # the lid clicks on when pressed to within this of the rim

# -- the rotor lid: a clear disc 136 mm across with a fluted centre knob 28 mm across (about 60 g) ---------------
RL_R, RL_THICK, RL_HOLE = 0.068, 0.004, 0.010
KNOB = (0.024, 0.026, 0.022)         # the knob's collider (the drawn knob is round, 28 mm across)
KNOB_Z = SOCKET_Z + KNOB[2] / 2      # the knob collider's centre above the disc's underside
KNOB_TOP = 0.034
RL_MASS = 0.06
RL0 = (0.300, -0.170)                # where it lies on the bench
ON_XY, ON_Z, ON_TILT = 0.003, 0.0015, 3.0    # on: axis within 3 mm of the rotor's, within 1.5 mm of seated, level within 3 deg

# -- the outer lid: hinged along y at the back of the deck; it stands open at 72 degrees --------------------------
HINGE = (0.108, 0.0, 0.182)          # hinge line in the centrifuge's frame (CAD joints.json)
PIVOT = (CF_C[0] + HINGE[0], CF_C[1] + HINGE[1], TOP + HINGE[2])
LID_L, LID_W, LID_T = 0.205, 0.216, 0.034
LID_GAP = 0.004                      # the lid's collider starts this far above its underside
LID_OPEN = 72.0
LID_MASS = 0.15
LID_K, LID_DAMP = 0.006, 0.002       # N m per degree, N m s per degree: a light stay that holds the lid open
LID_TARGET = 4.0                     # the stay's rest angle beyond the open pose, so the lid's weight is carried at 72
LID_UPPER = 6.0
SHUT_DEG = 3.0                       # within this of shut the lid's catch engages (and the interlock reads shut)
LID_ROOT_UP = 0.012

# -- START key on the console: a sprung cap 24 mm across, pushed 3 mm straight down ------------------------------
START_LOCAL = (-0.13153, -0.062, 0.08598)        # the cap's centre in the centrifuge's frame
START_R, START_H = 0.012, 0.006
START_XYZ = (CF_C[0] + START_LOCAL[0], CF_C[1] + START_LOCAL[1], TOP + START_LOCAL[2])
START_TOP = START_XYZ[2] + START_H / 2
START_TRAVEL, START_K, START_ON = 0.003, 700.0, 0.0018

# -- the tube rack (100 x 50 x 44 mm, eight places) with its sign plate, turned so the sign faces the room ------
RACK_C = (0.455, -0.235)
RACK_YAW = math.radians(42.0)
RACK = (0.100, 0.050, 0.044)
RACK_FLOOR = 0.007
RACK_MASS = 0.12
HOLES = tuple((x, y) for x in (-0.030, -0.010, 0.010, 0.030) for y in (-0.010, 0.010))
TUBE_HOLES = (1, 2, 5)               # which places still hold a tube
N_TUBES = len(TUBE_HOLES)
TUBE_R, TUBE_H, TUBE_MASS = 0.0053, 0.0415, 0.0025
SIGN = (0.108, 0.066, 0.003)
SIGN_TILT = math.radians(42.0)
SIGN_C = (0.0, -0.0505, 0.0239)      # the sign plate's centre in the rack's frame

# -- the power strip the centrifuge is plugged into (62 x 300 x 40 mm): fixed scenery behind the centrifuge, to its left --
STRIP_C = (0.650, 0.410)
STRIP = (0.062, 0.300, 0.040)
STRIP_YAW = math.pi                  # turned so that the plug's lead leaves toward the centrifuge and the strip's own lead toward the bench's left edge
INLET = (0.125, 0.060, 0.027)        # the mains inlet on the back of the housing, in the centrifuge's frame

# -- fixed scenery: the blue absorbent bench pad the rotor lid lies on, and a benchtop biohazard waste container --------
PAD_C = RL0
PAD = (0.190, 0.190, 0.0012)
BIN_C = (0.610, -0.150)
BIN = (0.118, 0.118, 0.130)
PAD_BLUE = (0.22, 0.47, 0.85)
YELLOW = (0.98, 0.80, 0.05)


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _staves(r, thick, z0, z1, zc, n, color, phase=0.0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        out.append(Piece("box", (thick, 2 * math.pi * r / n + 0.004, z1 - z0),
                         (r * math.cos(a), r * math.sin(a), (z0 + z1) / 2 - zc), rot=(0.0, 0.0, a), color=color))
    return out


def centrifuge_object() -> Part:
    """The centrifuge body with its rotor: fixed. Colliders (hidden): the rotor as a plug with a raised rim, the
    chamber as a ring of blocks on a base, the housing's sides and back and the console as boxes. Its mains lead to
    the power strip (and the strip's own lead) are drawn only."""
    z0, z1 = 0.092, 0.127
    zc = (z0 + z1) / 2
    pieces = _staves(ROTOR_R - 0.008, 0.016, z1, RIM_Z, zc, 16, DARK)                       # the rotor's rim
    pieces += _staves(CH_COLLIDER_R + 0.0055, 0.011, CH_FLOOR_Z, DECK_Z, zc, 20, WHITE)    # the chamber wall
    bx = (BODY_X[0] + BODY_X[1]) / 2
    pieces.append(Piece("box", (BODY_X[1] - BODY_X[0], 2 * BODY_HALF_Y, CH_FLOOR_Z), (bx, 0.0, CH_FLOOR_Z / 2 - zc), color=WHITE))
    for sy in (-1.0, 1.0):
        pieces.append(Piece("box", (BODY_X[1] - BODY_X[0], 0.020, DECK_Z - CH_FLOOR_Z),
                            (bx, sy * (BODY_HALF_Y - 0.010), (DECK_Z + CH_FLOOR_Z) / 2 - zc), color=WHITE))
    pieces.append(Piece("box", (0.030, 2 * BODY_HALF_Y - 0.040, 0.172 - CH_FLOOR_Z), (BODY_X[1] - 0.015, 0.0, (0.172 + CH_FLOOR_Z) / 2 - zc), color=WHITE))
    pieces.append(Piece("box", (0.060, 2 * BODY_HALF_Y, 0.074), (-0.145, 0.0, 0.037 - zc), color=WHITE))      # console, under the START key
    pieces.append(Piece("box", (0.020, 2 * BODY_HALF_Y, 0.086), (-0.105, 0.0, 0.043 - zc), color=WHITE))
    kw = _vis(("centrifuge", "side_label", "run_lamp_on", "run_lamp_off", "mains_lead", "rotor_still", "rotor_marks", "rotor_spin", "spray"),
              (0.0, 0.0, -zc), visual_hide=("start_cap", "run_lamp"))
    return Part("centrifuge", pos=(CF_C[0], CF_C[1], TOP + zc), size=(ROTOR_R, z1 - z0, ROTOR_R), shape="cylinder", exact_z=True,
                color=DARK, friction=(0.4, 0.3), pieces=tuple(pieces), **kw)


def strip_object() -> Part:
    """The power strip with the centrifuge's plug in it: fixed scenery, drawn switched on. Colliders (hidden): the
    strip and the plug as boxes."""
    zc = STRIP[2] / 2
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, -0.015, zc + 0.013), color=DARK),)
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=WHITE,
                friction=(0.5, 0.4), pieces=pieces, yaw=STRIP_YAW,
                **_vis(("power_set", "strip_lamps_on", "strip_main_on"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main", "cooker_cord", "lead")))


def pad_object() -> Part:
    """The blue absorbent bench pad the rotor lid lies on: fixed, a thin slab."""
    return Part("bench_pad", pos=(PAD_C[0], PAD_C[1], TOP + PAD[2] / 2), size=PAD, exact_z=True, color=PAD_BLUE, friction=(0.9, 0.8))


def bin_object() -> Part:
    """A benchtop biohazard waste container with its lid shut: fixed scenery (collider: a box)."""
    return Part("waste_bin", pos=(BIN_C[0], BIN_C[1], TOP + BIN[2] / 2), size=BIN, exact_z=True, color=YELLOW, friction=(0.5, 0.4),
                **_vis(("waste_bin", "waste_bin_label"), (0.0, 0.0, -BIN[2] / 2)))


def catch_object() -> Part:
    """The rotor's sprung catch: a steel nose on the hub that the rotor lid's socket goes over. Pressed 4 mm down it
    lets the lid down onto the rotor's rim."""
    zc = RIM_Z + SOCKET_Z + CATCH_UP - CATCH_R - CATCH_CYL / 2        # so that the nose's tip is 4 mm above a seated lid's socket ceiling
    spring = Spring(axis="Z", lower=-CATCH_TRAVEL, upper=0.0, stiffness=CATCH_K, damping=4.0, target=CATCH_REST)
    nose = Piece("sphere", (CATCH_R, CATCH_R, CATCH_R), (0.0, 0.0, CATCH_CYL / 2), color=STEEL)
    return Part("rotor_catch", pos=(CF_C[0], CF_C[1], TOP + zc), size=(CATCH_R, CATCH_CYL, CATCH_R), shape="cylinder", exact_z=True,
                mass=0.010, color=STEEL, friction=(0.3, 0.25), spring=spring, pieces=(nose,), contact_offset=0.001)


CATCH_Z0 = RIM_Z + SOCKET_Z + CATCH_UP - CATCH_R - CATCH_CYL / 2


def rotor_lid_object() -> Part:
    """The rotor lid: a free rigid body. Colliders (hidden): the knob as a block, the disc as twelve overlapping
    spokes round its centre socket, and four blocks for the boss round the socket."""
    pieces = []
    r0, r1 = RL_HOLE, RL_R
    for i in range(12):
        a = 2 * math.pi * i / 12
        rm = (r0 + r1) / 2
        pieces.append(Piece("box", (r1 - r0, 0.036, RL_THICK), (rm * math.cos(a), rm * math.sin(a), RL_THICK / 2 - KNOB_Z),
                            rot=(0.0, 0.0, a), color=CLEAR))
    for (sx, sy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        size = (0.010, 0.020, 0.006) if sx else (0.020, 0.010, 0.006)
        pieces.append(Piece("box", size, (0.0155 * sx, 0.0155 * sy, 0.007 - KNOB_Z), color=DARK))
    return Part("rotor_lid", pos=(RL0[0], RL0[1], TOP + PAD[2] + KNOB_Z + 0.0005), size=KNOB, exact_z=True, mass=RL_MASS, color=DARK,
                friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.002, com=(0.0, 0.0, 0.007 - KNOB_Z),
                **_vis(("rotor_lid", "rotor_lid_label", "lid_button_up", "lid_button_down", "rotor_lid_spin"), (0.0, 0.0, -KNOB_Z),
                       visual_glass_opacity=0.30))


def _open_xz(r, n, deg=LID_OPEN):
    """A point of the outer lid given along it from the hinge (r) and out of its underside (n), relative to the hinge."""
    t = math.radians(deg)
    return (-r * math.cos(t) + n * math.sin(t), r * math.sin(t) + n * math.cos(t))


def outer_lid_object() -> Part:
    """The outer lid: one rigid body on a hinge along y, spawned standing open at 72 degrees (so the hinge reads 0
    there and -72 shut). Collider (hidden): one slab. A light stay holds it open; the task's rule is its catch."""
    hinge = Hinge(pivot=PIVOT, axis="Y", damping=LID_DAMP, lower_deg=-LID_OPEN, upper_deg=LID_UPPER,
                  stiffness=LID_K, target_deg=LID_TARGET)
    cx, cz = _open_xz(LID_L / 2, (LID_GAP + LID_T) / 2)
    slab = Piece("box", (LID_L, LID_W, LID_T - LID_GAP), (cx, 0.0, cz - LID_ROOT_UP), rot=(0.0, math.radians(LID_OPEN), 0.0), color=WHITE)
    pos = (PIVOT[0], PIVOT[1], PIVOT[2] + LID_ROOT_UP)
    return Part("outer_lid", pos=pos, size=(0.006, 0.060, 0.004), exact_z=True, mass=LID_MASS, color=WHITE, friction=(0.6, 0.5),
                hinge=hinge, pieces=(slab,), contact_offset=0.002,
                **_vis(("outer_lid", "lid_label", "window_spray"), (0.0, 0.0, -LID_ROOT_UP), visual_rpy_deg=(0.0, LID_OPEN, 0.0),
                       visual_glass_opacity=0.15))


def start_object() -> Part:
    """The START key: a sprung cap pushed straight down (the drawn cap follows the console's 15-degree slope)."""
    spring = Spring(axis="Z", lower=-START_TRAVEL, upper=0.0, stiffness=START_K, damping=5.0, target=0.0)
    off = (CF_C[0] - START_XYZ[0], CF_C[1] - START_XYZ[1], TOP - START_XYZ[2])
    return Part("start_button", pos=START_XYZ, size=(START_R, START_H, START_R), shape="cylinder", exact_z=True, mass=0.004,
                color=GREEN, friction=(0.8, 0.7), spring=spring, contact_offset=0.001, **_vis(("start_cap_on", "start_cap_off"), off))


def _turn(x, y, yaw=RACK_YAW):
    c, s = math.cos(yaw), math.sin(yaw)
    return (c * x - s * y, s * x + c * y)


def rack_object() -> Part:
    """The tube rack with its sign plate: one free rigid body. Colliders (hidden): a floor the tubes stand on, the end
    walls, a grid of bars round each tube place, and the sign plate."""
    zc = RACK_FLOOR / 2
    pieces = [Piece("box", (0.004, RACK[1], RACK[2]), (sx * 0.048, 0.0, RACK[2] / 2 - zc), color=BLUE) for sx in (-1, 1)]
    gz, gh = 0.039 - zc, 0.010
    for (yc, w) in ((-0.02075, 0.0085), (0.0, 0.007), (0.02075, 0.0085)):
        pieces.append(Piece("box", (RACK[0], w, gh), (0.0, yc, gz), color=BLUE))
    for (xc, w) in ((-0.04325, 0.0135), (-0.020, 0.007), (0.0, 0.007), (0.020, 0.007), (0.04325, 0.0135)):
        pieces.append(Piece("box", (w, RACK[1], gh), (xc, 0.0, gz), color=BLUE))
    pieces.append(Piece("box", SIGN, (SIGN_C[0], SIGN_C[1], SIGN_C[2] - zc), rot=(SIGN_TILT, 0.0, 0.0), color=ORANGE))
    return Part("tube_rack", pos=(RACK_C[0], RACK_C[1], TOP + zc), size=(RACK[0], RACK[1], RACK_FLOOR), exact_z=True, mass=RACK_MASS,
                color=BLUE, friction=(0.6, 0.5), pieces=tuple(pieces), yaw=RACK_YAW, contact_offset=0.002,
                **_vis(("tube_rack", "sign_label"), (0.0, 0.0, -zc)))


def tube_start(i):
    hx, hy = HOLES[TUBE_HOLES[i]]
    dx, dy = _turn(hx, hy)
    return (RACK_C[0] + dx, RACK_C[1] + dy, TOP + RACK_FLOOR + TUBE_H / 2 + 0.0005)


def tube_object(i: int) -> Part:
    """A capped 1.5 ml sample tube standing in the rack: a free rigid body (collider: a cylinder)."""
    return Part(f"tube{i + 1}", pos=tube_start(i), size=(TUBE_R, TUBE_H, TUBE_R), shape="cylinder", exact_z=True, mass=TUBE_MASS,
                color=TUBE, friction=(0.6, 0.5), contact_offset=0.001, yaw=RACK_YAW + 1.3 * i,
                **_vis("tube", (0.0, 0.0, -TUBE_H / 2), visual_glass_opacity=0.28))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def rotor_lid_seat(pose):
    """Where the rotor lid's seat (the centre of its underside) is: (distance of that point from the rotor's axis,
    its height above the rotor's rim, the lid's tilt in degrees)."""
    p = np.asarray(pose, float)
    seat = p[:3] + quat_matrix(p[3:7]) @ np.array([0.0, 0.0, -KNOB_Z])
    return (float(math.hypot(seat[0] - CF_C[0], seat[1] - CF_C[1])), float(seat[2] - (TOP + RIM_Z)), tilt_deg(p))


def rotor_lid_on(pose) -> bool:
    """The rotor lid is on: centred on the rotor within 3 mm, down at its seated height, level."""
    off, up, tilt = rotor_lid_seat(pose)
    return bool(off <= ON_XY and abs(up) <= ON_Z and tilt <= ON_TILT)


def rotor_lid_clicks(pose) -> bool:
    """Pressed home: centred and level as above and within 0.8 mm of the rim. This is when the catch lets go."""
    off, up, tilt = rotor_lid_seat(pose)
    return bool(off <= ON_XY and up <= CLICK_Z and tilt <= ON_TILT)


def rotor_lid_away(pose) -> bool:
    """Taken off again: its seat more than 15 mm above the rim or 25 mm off the axis (the catch springs back up)."""
    off, up, _ = rotor_lid_seat(pose)
    return bool(up > 0.015 or off > 0.025)


def outer_open_deg(pose) -> float:
    """How far the outer lid stands open, in degrees (0 = shut flat, 72 = as it starts)."""
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return LID_OPEN + math.degrees(math.atan2(r[0, 2], r[0, 0]))


def outer_shut(pose) -> bool:
    return bool(outer_open_deg(pose) <= SHUT_DEG)


def start_press(pose) -> float:
    """How far the START key is pushed down (m)."""
    return float(START_XYZ[2] - np.asarray(pose, float)[2])


def rack_standing(rack) -> bool:
    """The rack stands on the bench: upright within 15 degrees and not lifted."""
    rack = np.asarray(rack, float)
    return bool(tilt_deg(rack) <= 15.0 and abs(rack[2] - (TOP + RACK_FLOOR / 2)) <= 0.010)


def tube_in_rack(rack, tube, i) -> bool:
    """Tube i still stands in its place in the rack: within 8 mm of its place's axis (in the rack's own frame), not
    lifted out, and upright within 25 degrees of the rack."""
    rack, tube = np.asarray(rack, float), np.asarray(tube, float)
    rr = quat_matrix(rack[3:7])
    q = rr.T @ (tube[:3] - rack[:3])
    hx, hy = HOLES[TUBE_HOLES[i]]
    axis = rr.T @ quat_matrix(tube[3:7]) @ np.array([0.0, 0.0, 1.0])
    lean = math.degrees(math.acos(float(np.clip(axis[2], -1.0, 1.0))))
    return bool(math.hypot(q[0] - hx, q[1] - hy) <= 0.008 and abs(q[2] - (RACK_FLOOR / 2 + TUBE_H / 2)) <= 0.012 and lean <= 25.0)


def hand_points(arm, side):
    """Points on a gripper's outline from its measured joints: fingertips, grasp point, the fingers' spread and two
    points up the hand. Falls back to the grasp point alone when only that is given."""
    tcp = np.asarray(arm["tcp"], float)[:3]
    if "joints" not in arm:
        return [tcp]
    from yam_arena import ik, station
    pos, rot = ik.tcp_pose(np.asarray(arm["joints"], float), station.BASES[side])
    x, a = rot[:, 0], rot[:, 2]
    spread = max(abs(float(v)) for v in arm.get("fingers", (0.0, 0.0))) + 0.006
    tip = pos + 0.013 * a
    return [tip, pos, tip + spread * x, tip - spread * x, pos - 0.06 * a, pos - 0.12 * a]


def hand_clearance(arm, side) -> float:
    """Smallest distance (m) from a gripper's outline to the centrifuge's outline."""
    return min(centrifuge_clearance(p) for p in hand_points(arm, side))


def hand_to_start(arm, side) -> float:
    """Distance (m) from a gripper's fingertips to the START key's top."""
    key = np.array([START_XYZ[0], START_XYZ[1], START_TOP])
    return min(float(np.linalg.norm(p - key)) for p in hand_points(arm, side)[:2])


def centrifuge_clearance(p) -> float:
    """Distance (m) from a point to the centrifuge's outline: a box over its footprint as tall as its shut lid."""
    p = np.asarray(p, float)
    lo = np.array([CF_C[0] + CONSOLE_X[0], CF_C[1] - BODY_HALF_Y, TOP])
    hi = np.array([CF_C[0] + BODY_X[1], CF_C[1] + BODY_HALF_Y, TOP + SHUT_TOP_Z])
    d = np.maximum(np.maximum(lo - p[:3], p[:3] - hi), 0.0)
    return float(np.linalg.norm(d))


# -- the three disclosed rules, as one state machine (the task applies its outputs to the joints and lamps) ---------

class Rules:
    """(1) The rotor lid's click: pressed home (see ``rotor_lid_clicks``), the hub's sprung nose is parked retracted so
    the lid stays seated; taken off again, the nose springs back up. (2) The outer lid's catch: pushed to within
    SHUT_DEG of shut, it latches. (3) START and the lid interlock: each time the key is pushed down START_ON or more,
    the centrifuge starts spinning if the outer lid is within SHUT_DEG of shut at that moment; with the lid open the
    key does nothing. Spinning then lasts for the rest of the trial."""

    def __init__(self):
        self.clicked = False
        self.latched = False
        self.down = False
        self.spinning = False
        self.sprayed = False
        self.presses = 0

    def update(self, step, rotor_lid, outer_lid, start_button):
        """Returns (mechanics, events); events is a list of 'click', 'unclick', 'latch', 'start', 'spray'."""
        events = []
        if not self.clicked and step > 20 and rotor_lid_clicks(rotor_lid):
            self.clicked = True
            events.append("click")
        elif self.clicked and rotor_lid_away(rotor_lid):
            self.clicked = False
            events.append("unclick")
        deg = outer_open_deg(outer_lid)
        if not self.latched and step > 20 and deg <= SHUT_DEG:
            self.latched = True
            events.append("latch")
        press = start_press(start_button)
        if not self.down and press >= START_ON:
            self.down = True
            self.presses += 1
            if deg <= SHUT_DEG and not self.spinning:
                self.spinning = True
                events.append("start")
                if not rotor_lid_on(rotor_lid):          # it starts with the rotor unsealed: the spray is drawn from now on
                    self.sprayed = True
                    events.append("spray")
        elif self.down and press < START_ON * 0.4:
            self.down = False
        mech = {"spinning": bool(self.spinning), "start_press_mm": round(1000 * press, 2), "start_presses": int(self.presses),
                "outer_open_deg": round(float(deg), 2), "outer_latched": bool(self.latched), "rotor_lid_clicked": bool(self.clicked),
                "spray_drawn": bool(self.sprayed)}
        return mech, events
