"""Geometry and measurements for putting an ammeter into a lamp circuit on a school physics bench.

A base board carries a 12 V sealed lead-acid battery, a rocker switch and a lamp in a holder, each with a terminal
block of 4 mm sockets that face the arms, joined by leads with 4 mm plugs. An analog ammeter stands at the board's
right end with its two leads plugged into it; their free plugs lie on the board.

Every lead is two plug bodies joined by a chain of short hinged links that collide with everything. Every socket has a
sprung detent ball that a plug's pin has to push past, going in and coming out.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Every body spawns with identity orientation.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WOOD = (0.78, 0.66, 0.46)
GREY = (0.30, 0.31, 0.33)
STEEL = (0.74, 0.75, 0.76)
RED = (0.80, 0.06, 0.05)
BLACK = (0.05, 0.05, 0.05)
YELLOW = (0.95, 0.78, 0.05)
BLUE = (0.08, 0.25, 0.70)

# -- base board ----------------------------------------------------------------------------------------------
BT = 0.012                           # board thickness
S = TOP + BT                         # the board's top: what plugs and leads lie on
BOARD_X = (0.190, 0.530)
BOARD_Y = (-0.400, 0.300)

# -- 4 mm sockets: all in one row, mouths facing the arms (-x), axes along x ----------------------------------------
XF = 0.400                           # the plane of the socket mouths
AXIS_H = 0.012                       # socket axis above the board
PITCH = 0.046
SOCKET_Y = tuple(round(0.270 - PITCH * i, 4) for i in range(12)) + (-0.308, -0.352)
N_SOCKETS = len(SOCKET_Y)
BLOCK_DEPTH = 0.036
BORE_Y, BORE_Z = 0.008, 0.010        # the bore's collider: a channel this wide and tall (the pin's head is 5 mm)
MOUTH = 0.005                        # the mouth is chamfered over this depth, 18 mm wide at the face
DETENT_X = 0.009                     # the detent ball's depth behind the mouth
DETENT_R = 0.0025
DETENT_UP = 0.0041                   # its centre above the socket's axis at rest: 0.9 mm in the pin head's way
DETENT_K, DETENT_PRELOAD, DETENT_TRAVEL = 800.0, 0.0025, 0.005      # N/m; preload as spring travel (2 N); free travel

# -- 4 mm plugs: a flat-sided grip 40 mm long, 14 mm thick, 28 mm tall; pin 19 mm long with a sprung head ---------
BODY = (0.040, 0.014, 0.028)
PIN_DZ = -0.002                      # pin axis below the grip's centre (the grip's foot is 12 mm below the axis)
SHANK_R = 0.0015
HEAD_R = 0.0025
HEAD_X = 0.0365                      # the head's centre ahead of the grip's centre
TIP_X = HEAD_X + HEAD_R              # the pin's tip
PLUG_MASS = 0.030
SEAT_X = XF - 0.0205                 # a seated plug's centre: its tip 18.5 mm deep, its face 0.5 mm off the block
PLUG_Z = S + BODY[2] / 2
CONNECT = 0.015                      # a plug is connected when its tip is this deep: its head is past the detent
IN_TOL = 0.0005                      # ... with its head inside the socket's bore (the bore's cross-section and this much)
TOUCH = 0.008                        # a plug's pin touches a socket's contact (it conducts) from this depth on, seated or not
REAR = (-BODY[0] / 2, 0.0, -0.0114)  # where the lead leaves the plug (in the plug's frame): the foot of its rear face

# -- leads: chains of hinged links 4.4 mm thick -----------------------------------------------------------------
LINK_R = 0.0022
LINK_MASS = 0.0012
LINK_DAMP = 2e-6                     # N m s per degree
LINK_LIMIT = 100.0
LEAD_Z = S + REAR[2] + BODY[2] / 2   # the height the links lie at


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def socket_xyz(i):
    return np.array([XF, SOCKET_Y[i], S + AXIS_H])


def seat_pos(i):
    """Centre of a plug seated in socket i."""
    return (SEAT_X, SOCKET_Y[i], PLUG_Z + 0.0002)


def rear_of(pos):
    return (pos[0] + REAR[0], pos[1] + REAR[1], LEAD_Z)


# -- fixed parts ---------------------------------------------------------------------------------------------

def _box(x, y, z, origin, color, **kw):
    return Piece("box", (x[1] - x[0], y[1] - y[0], z[1] - z[0]),
                 ((x[0] + x[1]) / 2 - origin[0], (y[0] + y[1]) / 2 - origin[1], (z[0] + z[1]) / 2 - origin[2]), color=color, **kw)


# -- what stands behind the terminal blocks (colliders: boxes), as (x, y, z above the board, colour) ---------------
BATTERY_X, BATTERY_Y, BATTERY_H = (0.445, 0.510), (0.1255, 0.2765), 0.094     # 12 V 7 Ah battery: 151 x 65 x 94 mm
SWITCH_X, SWITCH_Y, SWITCH_H = (0.436, 0.488), (-0.020, 0.054), 0.026
LAMP_C, LAMP_BASE, LAMP_H = (0.470, -0.167), 0.060, 0.0715
METER_X, METER_Y, METER_H = (0.436, 0.530), (-0.385, -0.275), 0.045
NEEDLE_PIVOT = (0.452, -0.330, S + METER_H + 0.002)       # the ammeter's needle turns about z here
NEEDLE_LEN = 0.062
FULL_SCALE_A = 5.0                   # the scale runs from 0 A (45 degrees left of straight ahead) to 5 A (45 degrees right)
HOUSINGS = (
    (BATTERY_X, BATTERY_Y, (0.0, BATTERY_H), (0.12, 0.12, 0.13)),
    (SWITCH_X, SWITCH_Y, (0.0, SWITCH_H), (0.85, 0.85, 0.83)),
    ((LAMP_C[0] - LAMP_BASE / 2, LAMP_C[0] + LAMP_BASE / 2), (LAMP_C[1] - LAMP_BASE / 2, LAMP_C[1] + LAMP_BASE / 2), (0.0, 0.020), (0.85, 0.85, 0.83)),
    (METER_X, METER_Y, (0.0, METER_H), (0.10, 0.10, 0.11)),
)

# -- rocker switch: turns about y at ROCKER_PIVOT; +12 degrees (far end down, marked I) is on, -12 is off ----------
ROCKER_PIVOT = (0.462, 0.017, S + 0.036)
ROCKER = (0.040, 0.024, 0.008)
ROCKER_ON_DEG = 12.0
ROCKER_K = 0.0012                    # N m per degree
ROCKER_DAMP = 0.00002
ROCKER_REST = (3.0, -27.0)           # the drive's rest angle (joint degrees) on and off: 3 degrees beyond each stop
ROCKER_PRESS = 0.012                 # where a fingertip presses an end, from the pivot


def socket_rows():
    """(y low, y high) of each terminal block."""
    out = []
    for a, b in ((0, 3), (4, 7), (8, 11), (12, 13)):
        out.append((min(SOCKET_Y[a], SOCKET_Y[b]) - 0.020, max(SOCKET_Y[a], SOCKET_Y[b]) + 0.020))
    return out


def board_object(sockets=range(N_SOCKETS)) -> Part:
    """The base board with the terminal blocks: fixed. Each block is a floor, a roof in two strips (the detent balls
    sit in the gap between them), and for every socket two side walls with a chamfered mouth."""
    c = ((BOARD_X[0] + BOARD_X[1]) / 2, (BOARD_Y[0] + BOARD_Y[1]) / 2, TOP + BT / 2)
    z0, z1 = S + AXIS_H - BORE_Z / 2, S + AXIS_H + BORE_Z / 2
    top = S + 0.024
    pieces = []
    for (ya, yb) in socket_rows():
        pieces.append(_box((XF, XF + BLOCK_DEPTH), (ya, yb), (S, z0), c, GREY, friction=(0.4, 0.3)))
        pieces.append(_box((XF, XF + DETENT_X - DETENT_R - 0.0005), (ya, yb), (z1, top), c, GREY, friction=(0.4, 0.3)))
        pieces.append(_box((XF + DETENT_X + DETENT_R + 0.0005, XF + BLOCK_DEPTH), (ya, yb), (z1, top), c, GREY, friction=(0.4, 0.3)))
        pieces.append(_box((XF + 0.024, XF + BLOCK_DEPTH), (ya, yb), (z0, z1), c, GREY, friction=(0.4, 0.3)))
    d = MOUTH * math.sqrt(2.0)
    half = BORE_Y / 2 + MOUTH
    for i in sockets:
        y = SOCKET_Y[i]
        for s in (-1.0, 1.0):
            ya, yb = sorted((y + s * BORE_Y / 2, y + s * (BORE_Y / 2 + 0.004)))
            pieces.append(_box((XF + MOUTH, XF + 0.024), (ya, yb), (z0, z1), c, GREY, friction=(0.4, 0.3)))
            pieces.append(Piece("box", (d, d, BORE_Z), (XF + MOUTH - c[0], y + s * half - c[1], (z0 + z1) / 2 - c[2]),
                                rot=(0.0, 0.0, math.pi / 4), color=GREY, friction=(0.4, 0.3)))
    for (ya, yb) in socket_rows():                       # the block's face between the mouths
        ys = sorted(SOCKET_Y[i] for i in sockets if ya < SOCKET_Y[i] < yb)
        edges = [ya] + [v for y in ys for v in (y - half, y + half)] + [yb]
        for a, b in zip(edges[0::2], edges[1::2]):
            if b - a > 0.001:
                pieces.append(_box((XF, XF + 0.010), (a, b), (z0, z1), c, GREY, friction=(0.4, 0.3)))
    for (x, y, z, col) in HOUSINGS:
        pieces.append(_box(x, y, (S + z[0], S + z[1]), c, col))
    return Part("board", pos=c, size=(BOARD_X[1] - BOARD_X[0], BOARD_Y[1] - BOARD_Y[0], BT), exact_z=True, color=WOOD,
                friction=(0.6, 0.5), pieces=tuple(pieces), contact_offset=0.001, **_vis("board_set", (0.0, 0.0, -BT / 2)))


def lamp_object() -> Part:
    """The lamp's bulb in its holder: fixed (collider: a cylinder). Two drawings: unlit glass and lit."""
    h = LAMP_H - 0.020
    zc = S + 0.020 + h / 2
    return Part("lamp_bulb", pos=(LAMP_C[0], LAMP_C[1], zc), size=(0.0095, h, 0.0095), shape="cylinder", exact_z=True,
                color=(0.95, 0.90, 0.70), friction=(0.5, 0.4), **_vis(("bulb", "bulb_lit"), (0.0, 0.0, TOP - zc), visual_glass_opacity=0.35))


def needle_object() -> Part:
    """The ammeter's needle: fixed; it is a drawing that the circuit rule turns (collider: a small hub)."""
    return Part("needle", pos=NEEDLE_PIVOT, size=(0.008, 0.008, 0.002), exact_z=True, color=RED, friction=(0.5, 0.4),
                **_vis("needle", (0.0, 0.0, 0.0), visual_rpy_deg=(0.0, 0.0, 45.0)))


def needle_deg(amps: float) -> float:
    """The needle's turn from its zero mark for a current, in degrees clockwise seen from above; it stops just
    beyond each end of the scale."""
    return 90.0 * float(np.clip(amps, -0.35, FULL_SCALE_A + 0.35)) / FULL_SCALE_A


def detent_object(i: int) -> Part:
    """Socket i's contact spring: a sprung steel ball in the bore's roof that the pin's head pushes up to pass."""
    spring = Spring(axis="Z", lower=0.0, upper=DETENT_TRAVEL, stiffness=DETENT_K, damping=2.0, target=-DETENT_PRELOAD)
    return Part(f"detent{i}", pos=(XF + DETENT_X, SOCKET_Y[i], S + AXIS_H + DETENT_UP), size=(DETENT_R,) * 3, shape="sphere",
                exact_z=True, mass=0.002, color=STEEL, friction=(0.3, 0.25), spring=spring, contact_offset=0.0005)


# -- plugs and leads -----------------------------------------------------------------------------------------

def plug_object(name: str, pos, color, hinge=None) -> Part:
    """A 4 mm plug: one rigid body. Colliders: the grip as a block, the pin as a thin shank with a ball head."""
    pin = (Piece("cylinder", (SHANK_R, HEAD_X - BODY[0] / 2, SHANK_R), ((HEAD_X + BODY[0] / 2) / 2, 0.0, PIN_DZ), axis="X",
                 color=STEEL, friction=(0.3, 0.25)),
           Piece("sphere", (HEAD_R,) * 3, (HEAD_X, 0.0, PIN_DZ), color=STEEL, friction=(0.3, 0.25)))
    look = {RED: "plug_red", BLACK: "plug_black", YELLOW: "plug_yellow", BLUE: "plug_blue"}[color]
    return Part(name, pos=tuple(pos), size=BODY, exact_z=True, mass=PLUG_MASS, color=color, friction=(1.2, 1.0), pieces=pin,
                contact_offset=0.001, hinge=hinge, com=(0.0, 0.0, -0.004), **_vis(look, (0.0, 0.0, 0.0)))


def lead_objects(name: str, a_pos, b_pos, via, color, seg=0.024):
    """A lead: plug ``name``a at a_pos, plug ``name``b at b_pos, and between their rear ends a chain of links laid
    along the corner points ``via``: (x, y) or (x, y, height above the lying height), in axis-parallel runs; a change
    of height alone makes a short upright link, so that a lead can be laid over another one. Joints alternate between
    a vertical axis and a horizontal axis across the link, so the chain bends every way. Returns the list of Parts."""
    pts = [np.array(rear_of(a_pos))] + [np.array([v[0], v[1], LEAD_Z + (v[2] if len(v) > 2 else 0.0)]) for v in via] + [np.array(rear_of(b_pos))]
    links = []
    for p, q in zip(pts[:-1], pts[1:]):
        n = max(1, int(round(float(np.linalg.norm(q - p)) / seg)))
        for k in range(n):
            links.append((p + (q - p) * k / n, p + (q - p) * (k + 1) / n))
    parts = [plug_object(name + "a", a_pos, color)]
    prev_name, prev_pos = name + "a", tuple(float(v) for v in a_pos)
    for j, (p, q) in enumerate(links):
        d = np.abs(q - p)
        along = "XYZ"[int(np.argmax(d))]
        axis = {"X": "Y", "Y": "X", "Z": "Y"}[along] if j % 2 == 0 else "Z"
        mid = tuple(float(v) for v in (p + q) / 2)
        length = float(np.linalg.norm(q - p))
        hinge = Hinge(pivot=tuple(float(v) for v in p), axis=axis, damping=LINK_DAMP, lower_deg=-LINK_LIMIT, upper_deg=LINK_LIMIT,
                      parent=prev_name, parent_pos=prev_pos)
        ln = f"{name}_{j:02d}"
        parts.append(Part(ln, pos=mid, size=(LINK_R, max(length - LINK_R, 0.004), LINK_R), shape="capsule",
                          axis=along, exact_z=True, mass=LINK_MASS, color=color, friction=(0.6, 0.5),
                          hinge=hinge, contact_offset=0.001))
        prev_name, prev_pos = ln, mid
    end = Hinge(pivot=tuple(float(v) for v in pts[-1]), axis="Y", damping=LINK_DAMP, lower_deg=-LINK_LIMIT, upper_deg=LINK_LIMIT,
                parent=prev_name, parent_pos=prev_pos)
    parts.append(plug_object(name + "b", b_pos, color, hinge=end))
    return parts


def rocker_object() -> Part:
    """The switch's rocker: a slab on a hinge along y, spawned on (far end down). Its over-centre spring is the
    task's rule: a drive toward the stop it is nearer to."""
    hinge = Hinge(pivot=ROCKER_PIVOT, axis="Y", damping=ROCKER_DAMP, lower_deg=-2 * ROCKER_ON_DEG, upper_deg=0.0,
                  stiffness=ROCKER_K, target_deg=ROCKER_REST[0])
    slab = Piece("box", ROCKER, (0.0, 0.0, 0.0), rot=(0.0, math.radians(ROCKER_ON_DEG), 0.0), color=RED)
    return Part("rocker", pos=ROCKER_PIVOT, size=(0.002, ROCKER[1], 0.002), shape="cylinder", axis="Y", exact_z=True, mass=0.02,
                color=RED, friction=(0.8, 0.6), hinge=hinge, pieces=(slab,), contact_offset=0.001,
                **_vis("rocker", (0.0, 0.0, 0.0), visual_rpy_deg=(0.0, ROCKER_ON_DEG, 0.0)))


# -- the scene's leads: (name, socket of plug a, where plug b is, corner points, colour, link length) -------------
FREE_MP = (0.300, -0.006, PLUG_Z + 0.0002)          # the meter's + lead's free plug, lying on the board in front of the switch's right terminal
FREE_MN = (0.300, -0.200, PLUG_Z + 0.0002)          # the meter's - lead's free plug, in front of the lamp
RISE = 0.007
START = {"l1a": 3, "l1b": 4, "l2a": 7, "l2b": 8, "l3a": 11, "l3b": 1, "mpa": 13, "mna": 12}


def lead_specs():
    y = SOCKET_Y
    yp, yn = FREE_MP[1], FREE_MN[1]
    return (
        ("l1", seat_pos(3), seat_pos(4), ((0.2595, y[3]), (0.2595, y[4])), RED, 0.025),
        ("l2", seat_pos(7), seat_pos(8), ((0.2595, y[7]), (0.2595, y[8])), YELLOW, 0.025),
        ("l3", seat_pos(11), seat_pos(1), ((0.2395, y[11]), (0.2395, y[1])), BLUE, 0.030),
        # the meter's two leads are laid over the blue lead where they cross it
        ("mn", seat_pos(12), FREE_MN, ((0.218, y[12]), (0.218, yn), (0.228, yn), (0.228, yn, RISE), (0.252, yn, RISE), (0.252, yn)), BLACK, 0.025),
        ("mp", seat_pos(13), FREE_MP, ((0.200, y[13]), (0.200, yp), (0.224, yp), (0.224, yp, RISE), (0.253, yp, RISE), (0.253, yp)), RED, 0.025),
    )


def scene_parts():
    out = [board_object(), lamp_object(), needle_object()] + [detent_object(i) for i in range(N_SOCKETS)] + [rocker_object()]
    for name, a, b, via, color, seg in lead_specs():
        out += lead_objects(name, a, b, via, color, seg)
    return out


# -- measurements --------------------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def plug_head(pose):
    """Centre of the pin's head (the ball at its end)."""
    p = np.asarray(pose, float)
    return p[:3] + quat_matrix(p[3:7]) @ np.array([HEAD_X, 0.0, PIN_DZ])


def plug_in(pose):
    """(socket index, depth of the pin's end behind the mouth, distance of the head's centre from that socket's axis)
    for the socket the pin's head is nearest to. The depth is that of the head's foremost point."""
    head = plug_head(pose)
    i = min(range(N_SOCKETS), key=lambda k: abs(head[1] - SOCKET_Y[k]))
    s = socket_xyz(i)
    return i, float(head[0] + HEAD_R - s[0]), float(math.hypot(head[1] - s[1], head[2] - s[2]))


def plug_socket(pose, depth=CONNECT):
    """The socket a plug is in, or None: its pin's end at least ``depth`` deep and its head inside the bore's
    cross-section (so a pin that is physically in the bore counts however the plug is tilted). With the default depth
    the plug is seated (past the catch); with TOUCH it is far enough in to conduct."""
    head = plug_head(pose)
    i = min(range(N_SOCKETS), key=lambda k: abs(head[1] - SOCKET_Y[k]))
    s = socket_xyz(i)
    inside = abs(head[1] - s[1]) <= BORE_Y / 2 + IN_TOL and abs(head[2] - s[2]) <= BORE_Z / 2 + IN_TOL
    return i if inside and head[0] + HEAD_R - s[0] >= depth else None


def plug_yaw_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.atan2(r[1, 0], r[0, 0]))


def rocker_deg(pose) -> float:
    """The rocker's angle: +12 on (far end down), -12 off, 0 level."""
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return ROCKER_ON_DEG + math.degrees(math.atan2(r[0, 2], r[0, 0]))


def switch_closed(pose) -> bool:
    return bool(rocker_deg(pose) > ROCKER_CLOSED_DEG)


def plug_on_board(pose) -> bool:
    """The whole plug is over the board and not below it: its rear end and its tip."""
    p = np.asarray(pose, float)
    r = quat_matrix(p[3:7])
    for local in ((-BODY[0] / 2, 0.0, 0.0), (TIP_X, 0.0, PIN_DZ)):
        q = p[:3] + r @ np.array(local)
        if not (BOARD_X[0] <= q[0] <= BOARD_X[1] and BOARD_Y[0] <= q[1] <= BOARD_Y[1] and q[2] >= S - 0.003):
            return False
    return True


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


def hand_gap(arm, side, poses) -> float:
    """Smallest distance (m) from a gripper's outline points to any plug's centre or the rocker's pivot."""
    targets = [np.asarray(poses[n], float)[:3] for n in PLUG_NAMES] + [np.array(ROCKER_PIVOT)]
    return min(float(np.linalg.norm(p - t)) for p in hand_points(arm, side) for t in targets)


# -- the circuit: a disclosed rule worked out from which plugs are connected where and the switch ---------------
# terminals: each owns two sockets that are joined inside its block
TERMINALS = ("B-", "B+", "S1", "S2", "LA", "LB", "M-", "M+")
SOCKET_TERMINAL = ("B-", "B-", "B+", "B+", "S1", "S1", "S2", "S2", "LA", "LA", "LB", "LB", "M-", "M+")
SOCKET_LABEL = tuple(f"{t} {'ab'[k % 2]}" for k, t in enumerate(SOCKET_TERMINAL[:12])) + ("M-", "M+")
LEAD_NAMES = ("l1", "l2", "l3", "mp", "mn")
PLUG_NAMES = tuple(n + e for n in LEAD_NAMES for e in "ab")
EMF = 12.0                           # volts
R_BATTERY = 0.02                     # ohms: the battery's internal resistance
R_LAMP = 8.0                         # ohms: a 12 V 18 W lamp at working temperature
R_METER = 0.05                       # ohms: the ammeter between its terminals (its 5 A range has no fuse)
R_LEAD = 0.01                        # ohms: one lead
R_SWITCH = 0.01                      # ohms: the closed switch
SHORT_A = 20.0                       # amperes from the battery: at or above this it is short-circuited
LIT_A = 1.0                          # amperes through the lamp: at or above this it is lit
READ_TOL_A = 0.1
LAMP_LIGHT = 200000.0                # the drawn light inside the lit bulb
SMOKE_PUFFS = 3                      # grey puffs drawn over each lead that carries a short-circuit current
ROCKER_CLOSED_DEG = 0.0              # the switch is closed while its rocker is past level toward I


def connections(poses, depth=TOUCH):
    """{plug name: socket index or None} from measured plug poses: which socket's contact each plug's pin touches
    (TOUCH deep or more), which is what the circuit follows. Pass CONNECT for the plugs that are seated."""
    return {n: plug_socket(poses[n], depth) for n in PLUG_NAMES}


def half_connected(conn):
    """Leads with one plug in a socket and the other out (``conn`` from ``connections``): a loose pin on such a lead
    may be live."""
    return [lead for lead in LEAD_NAMES if (conn[lead + "a"] is None) != (conn[lead + "b"] is None)]


def switch_controls_lamp(conn) -> bool:
    """With the switch open no current flows through the lamp: nothing is wired round the switch."""
    return bool(solve(conn, False)["lamp_a"] < 0.05)


def partly_in(poses) -> bool:
    """Some plug is in a socket far enough to conduct but not past the catch."""
    return any(plug_socket(poses[n], TOUCH) is not None and plug_socket(poses[n]) is None for n in PLUG_NAMES)


def solve(conn, closed: bool):
    """Currents for a set of connections and a switch position, by nodal analysis. Returns a dict with the battery's
    current, the lamp's, the meter's (positive from its + terminal to its - terminal) and each lead's (absolute)."""
    idx = {t: k for k, t in enumerate(TERMINALS)}
    n = len(TERMINALS)
    g = np.zeros((n, n))
    rhs = np.zeros(n)

    def add(a, b, r):
        i, j = idx[a], idx[b]
        if i == j:
            return
        g[i, i] += 1 / r; g[j, j] += 1 / r; g[i, j] -= 1 / r; g[j, i] -= 1 / r

    add("B+", "B-", R_BATTERY)
    rhs[idx["B+"]] += EMF / R_BATTERY
    rhs[idx["B-"]] -= EMF / R_BATTERY
    add("LA", "LB", R_LAMP)
    add("M+", "M-", R_METER)
    if closed:
        add("S1", "S2", R_SWITCH)
    ends = {}
    for lead in LEAD_NAMES:
        a, b = conn.get(lead + "a"), conn.get(lead + "b")
        if a is not None and b is not None:
            ends[lead] = (SOCKET_TERMINAL[a], SOCKET_TERMINAL[b])
            add(*ends[lead], R_LEAD)
    g += np.eye(n) * 1e-9
    g[idx["B-"], :] = 0.0
    g[idx["B-"], idx["B-"]] = 1.0
    rhs[idx["B-"]] = 0.0
    v = np.linalg.solve(g, rhs)
    volt = {t: float(v[idx[t]]) for t in TERMINALS}
    out = {"battery_a": (EMF - (volt["B+"] - volt["B-"])) / R_BATTERY, "lamp_a": abs(volt["LA"] - volt["LB"]) / R_LAMP,
           "meter_a": (volt["M+"] - volt["M-"]) / R_METER}
    for lead in LEAD_NAMES:
        out[lead + "_a"] = abs(volt[ends[lead][0]] - volt[ends[lead][1]]) / R_LEAD if lead in ends and ends[lead][0] != ends[lead][1] else 0.0
    return out


def circuit(conn, closed: bool):
    """The circuit's state: currents, and whether the battery is short-circuited, the lamp is lit, and the meter
    reads the lamp's current (all of the lamp's current passes through it from + to -)."""
    c = solve(conn, closed)
    c["short"] = bool(c["battery_a"] >= SHORT_A)
    c["lamp_lit"] = bool(not c["short"] and c["lamp_a"] >= LIT_A)
    c["meter_reads_lamp"] = bool(c["lamp_lit"] and c["meter_a"] >= LIT_A and abs(c["meter_a"] - c["lamp_a"]) <= READ_TOL_A)
    c["meter_reversed"] = bool(c["meter_a"] <= -0.05)
    return c


class Rules:
    """The task's two disclosed rules. (1) The rocker's over-centre spring: once the rocker has been pushed past
    level, its drive's rest angle moves beyond the other stop, so it snaps over and stays. (2) The circuit: see
    ``circuit``; it is worked out anew every step from the measured plugs and the rocker's angle."""

    def __init__(self):
        self.on = True

    def update(self, step, poses):
        """Returns (mechanics, events); events: ('rocker', drive target in joint degrees)."""
        events = []
        deg = rocker_deg(poses["rocker"])
        if self.on and deg < -1.0:
            self.on = False
            events.append(("rocker", ROCKER_REST[1]))
        elif not self.on and deg > 1.0:
            self.on = True
            events.append(("rocker", ROCKER_REST[0]))
        conn = connections(poses)
        c = circuit(conn, switch_closed(poses["rocker"]))
        mech = {"rocker_deg": round(deg, 1), "switch_closed": bool(switch_closed(poses["rocker"])), "plug_partly_in": bool(partly_in(poses)),
                "battery_a": round(c["battery_a"], 2),
                "lamp_a": round(c["lamp_a"], 2), "meter_a": round(c["meter_a"], 2), "short": c["short"], "lamp_lit": c["lamp_lit"],
                "meter_reads_lamp": c["meter_reads_lamp"]}
        mech.update({f"{lead}_a": round(c[lead + "_a"], 1) for lead in LEAD_NAMES})
        return mech, events
