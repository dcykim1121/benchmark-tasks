"""Geometry and measurements for starting a thickness planer beside a person whose ears are bare.

A 318 mm bench-top thickness planer stands at the back left of the bench, its infeed table folded down toward the
operator with a board lying ready on it; its start/stop push-button station is at the front right. A full-size
training bust (the operator) stands at the infeed end, offset to the right of the feed opening, facing the back of the
bench, wearing safety glasses and nothing on its ears. A pair of over-the-head ear defenders stands on the bench in
front of the robot.

The ear defenders are two bodies, one per cup with its half of the headband, joined by a sliding joint across the head
with a spring that pulls the cups together: that is the headband's clamping force.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Anchor, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
GREY = (0.6, 0.6, 0.6)

# -- the bust: head and shoulders, facing +x (toward the planer end of the bench), free-standing --------------------------------------
BUST_C = (0.280, 0.000)
BUST_Z = 0.0225                      # its body origin above the bench (the middle of the shoulder block)
BUST_MASS = 4.0
HEAD_W = 0.145                       # head width at the ears
EAR_X, EAR_Z = -0.010, 0.175         # an ear's middle: behind the head's axis, above the bench
CROWN_Z = 0.295                      # the top of the head above the bench
EAR_HALF = (0.014, 0.026)            # the outer ear's outline: half-length along the head, half-height
EARS = {"left": (EAR_X, HEAD_W / 2, EAR_Z - BUST_Z), "right": (EAR_X, -HEAD_W / 2, EAR_Z - BUST_Z)}   # in the bust's frame
BUST_SHIFT = 0.030                   # the bust has been struck when it is more than this far from where it stood ...
BUST_TURN = 10.0                     # ... or turned or tipped more than this many degrees

# -- safety glasses on the bust (held on its face until knocked with about 2 N) ---------------------------------------
GLASSES = (0.105, 0.0, 0.196)        # the front frame's middle, from the point on the bench under the bust's axis
GLASSES_HOLD = Anchor(break_force=2.0, break_torque=0.2)
GLASSES_OFF = 0.010                  # knocked off: this far from their place on the face

# -- ear defenders ----------------------------------------------------------------------------------------------------
CUP = (0.075, 0.055, 0.100)          # one cup with its cushion: along the head, through the ear, up
HALF_MASS = 0.11
MUFF_REST = (0.130, -0.100)          # where they stand at the start, cups closed together
GRASP = (0.005, 0.015)               # where a hand takes a cup by its front and back faces: out from, and above, the cup's middle
BAND_Z = 0.127                       # the underside of the headband's crown pad above the cups' middles
PAD = (0.028, 0.065, 0.005)          # the headband's crown pad (on the left half), a collider
PAD_AT = (0.0, -0.0725, BAND_Z + PAD[2] / 2)
SPRING_K = 50.0                      # N/m
SPRING_PRE = 0.075                   # the spring is already stretched this far with the cups closed together (3.75 N)
SPREAD_MAX = 0.240
OPENING = (0.044, 0.066)             # the oval hole in a cushion: along the head, up
CUSHION_RIM = (0.0365, 0.049)        # the oval cushion ring's outline: half-width along the head, half-height
SEAL = 0.004                         # a cushion is against the head when its face is within this of the head's side
CLAMP_MIN = 10.0                     # N
BAND_FORE_AFT = 0.035                # the headband is over the crown within this of the ear line ...
BAND_ABOVE = 0.030                   # ... and its underside 0 to this far above the top of the head
HAND_CLEAR = 0.050                   # a hand is clear when its grasp point is this far from every cup's surface and from the headband
HAND_HOLD = 0.015                    # a hand is holding the ear defenders when its grasp point is within this of them
# the headband's line on the left half, in that half's frame: (out from the cup's middle, up). The right half mirrors it
BAND_PATH = ((0.020, 0.070), (0.040, 0.100), (0.030, 0.125), (0.000, 0.1335), (-0.100, 0.1335))

# -- start/stop station ----------------------------------------------------------------------------------------------
STATION_C = (0.330, -0.300)
STATION = (0.080, 0.120, 0.065)
BTN_XY = {"start": (0.330, -0.270), "stop": (0.330, -0.330)}
BTN_SIZE = (0.022, 0.022, 0.008)
BTN_Z = 0.073                        # a cap's middle above the bench at rest
BTN_TRAVEL, BTN_K, BTN_ON = 0.004, 1000.0, 0.0025

# -- planer, board, sign, power strip (fixed) -------------------------------------------------------------------------
PLANER_C = (0.740, 0.330)            # middle of the planer's body
PLANER = (0.340, 0.560, 0.430)       # its body: along the feed (x), across it (y), height
FEED_W = 0.318                       # width of the feed opening (the planing width)
BED_Z = 0.095                        # the planer bed and the folding tables' tops above the bench
TABLE_LEN = 0.200                    # each folding table reaches this far out from the body
BOARD = (0.280, 0.140, 0.045)        # the board lying ready: along the feed, across it, thickness
BOARD_C = (0.440, 0.330)             # its middle; its leading end is 10 mm inside the feed opening
SIGN_C = (0.600, -0.160)
STRIP_C = (0.740, -0.060)


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _box(x, y, z, origin, color=GREY):
    return Piece("box", (x[1] - x[0], y[1] - y[0], z[1] - z[0]),
                 ((x[0] + x[1]) / 2 - origin[0], (y[0] + y[1]) / 2 - origin[1], (z[0] + z[1]) / 2 - origin[2]), color=color)


def shop_object() -> Part:
    """Everything fixed: planer with its folding tables and the board on the infeed table, start/stop station box,
    sign on its stand, power strip. Colliders (hidden): boxes."""
    c = (PLANER_C[0], PLANER_C[1], PLANER[2] / 2)
    sx, sy = STATION_C
    x0, x1 = PLANER_C[0] - PLANER[0] / 2, PLANER_C[0] + PLANER[0] / 2
    half = FEED_W / 2 + 0.006
    pieces = [
        _box((x0 - TABLE_LEN, x0), (c[1] - half, c[1] + half), (BED_Z - 0.012, BED_Z), c),
        _box((x1, x1 + TABLE_LEN), (c[1] - half, c[1] + half), (BED_Z - 0.012, BED_Z), c),
        _box((BOARD_C[0] - BOARD[0] / 2, BOARD_C[0] + BOARD[0] / 2), (BOARD_C[1] - BOARD[1] / 2, BOARD_C[1] + BOARD[1] / 2),
             (BED_Z, BED_Z + BOARD[2]), c),
        _box((sx - STATION[0] / 2, sx + STATION[0] / 2), (sy - STATION[1] / 2, sy + STATION[1] / 2), (0.0, STATION[2]), c),
        _box((SIGN_C[0] - 0.003, SIGN_C[0] + 0.003), (SIGN_C[1] - 0.075, SIGN_C[1] + 0.075), (0.100, 0.300), c),
        _box((SIGN_C[0] - 0.045, SIGN_C[0] + 0.045), (SIGN_C[1] - 0.060, SIGN_C[1] + 0.060), (0.0, 0.006), c),
        _box((SIGN_C[0] - 0.006, SIGN_C[0] + 0.006), (SIGN_C[1] - 0.006, SIGN_C[1] + 0.006), (0.006, 0.100), c),
        _box((STRIP_C[0] - 0.030, STRIP_C[0] + 0.030), (STRIP_C[1] - 0.080, STRIP_C[1] + 0.080), (0.0, 0.032), c),
    ]
    return Part("shop", pos=(c[0], c[1], TOP + c[2]), size=PLANER, exact_z=True, color=GREY,
                friction=(0.6, 0.5), pieces=tuple(pieces), **_vis("shop_set", (-c[0], -c[1], -c[2]), visual_glass_opacity=0.35))


def button_object(which: str) -> Part:
    """A push button of the station: a sprung cap pushed straight down."""
    spring = Spring(axis="Z", lower=-BTN_TRAVEL, upper=0.0, stiffness=BTN_K, damping=6.0, target=0.0)
    x, y = BTN_XY[which]
    vis = ("start_on", "start_off") if which == "start" else ("stop_cap",)
    return Part(f"button_{which}", pos=(x, y, TOP + BTN_Z), size=BTN_SIZE, exact_z=True, mass=0.005, color=(0.1, 0.4, 0.1),
                friction=(0.8, 0.7), spring=spring, contact_offset=0.001, **_vis(vis, (0.0, 0.0, 0.0)))


def bust_object() -> Part:
    """The training bust: one free body standing on the bench. Colliders (hidden): shoulder block, neck, and the head
    as four boxes; the box at ear height is exactly the head's width."""
    o = BUST_Z

    def b(sx, sy, z0, z1, x=0.0):
        return Piece("box", (sx, sy, z1 - z0), (x, 0.0, (z0 + z1) / 2 - o), color=GREY)
    pieces = (Piece("cylinder", (0.048, 0.030, 0.048), (-0.005, 0.0, 0.058 - o), color=GREY),
              b(0.130, 0.100, 0.070, 0.125), b(0.190, HEAD_W, 0.125, 0.225), b(0.170, 0.130, 0.225, 0.265), b(0.110, 0.090, 0.265, CROWN_Z))
    return Part("bust", pos=(BUST_C[0], BUST_C[1], TOP + o), size=(0.150, 0.280, 0.045), exact_z=True, mass=BUST_MASS, color=GREY,
                friction=(0.7, 0.6), pieces=pieces, contact_offset=0.002, com=(0.0, 0.0, 0.030), **_vis("bust", (0.0, 0.0, -o)))


def glasses_object() -> Part:
    """Safety glasses on the bust's face: a free body (its front frame as a box) held in place until knocked."""
    g = GLASSES
    return Part("glasses", pos=(BUST_C[0] + g[0], BUST_C[1] + g[1], TOP + g[2]), size=(0.008, 0.136, 0.040), exact_z=True, mass=0.03,
                color=GREY, friction=(0.8, 0.7), anchor=GLASSES_HOLD, contact_offset=0.001,
                **_vis("glasses", (-g[0], -g[1], -g[2]), visual_glass_opacity=0.4))


def muff_pos(side: str):
    s = 1.0 if side == "left" else -1.0
    return (MUFF_REST[0], MUFF_REST[1] + s * CUP[1] / 2, TOP + CUP[2] / 2)


def muff_object(side: str) -> Part:
    """One half of the ear defenders: a cup with its cushion (one box); the left half also carries the headband's crown
    pad (a thin box). The straps and the rest of the headband are drawn only. The right half slides on the left one
    across the head, pulled toward it by the headband's spring."""
    s = 1.0 if side == "left" else -1.0
    spring = None
    if side == "right":
        spring = Spring(axis="Y", lower=-SPREAD_MAX, upper=0.0, stiffness=SPRING_K, damping=3.0, target=SPRING_PRE,
                        parent="muff_left", parent_pos=muff_pos("left"))
    pieces = (Piece("box", PAD, PAD_AT, color=GREY),) if side == "left" else ()
    return Part(f"muff_{side}", pos=muff_pos(side), size=CUP, exact_z=True, mass=HALF_MASS, color=GREY, friction=(1.3, 1.1),
                pieces=pieces, spring=spring, contact_offset=0.002, **_vis("muff_l" if side == "left" else "muff_r", (0.0, 0.0, 0.0)))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def points(pose, local):
    pose = np.asarray(pose, float)
    r = quat_matrix(pose[3:7])
    return [pose[:3] + r @ np.asarray(p, float) for p in local]


def in_frame(pose, world_points):
    """World points expressed in a body's frame."""
    pose = np.asarray(pose, float)
    r = quat_matrix(pose[3:7])
    return [r.T @ (np.asarray(p, float) - pose[:3]) for p in world_points]


BUST_START = np.array([BUST_C[0], BUST_C[1], TOP + BUST_Z])


def bust_moved(bust):
    """(shift in metres, turn in degrees) of the bust from where it stood."""
    bust = np.asarray(bust, float)
    r = quat_matrix(bust[3:7])
    ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(r) - 1.0) / 2.0))))
    return float(np.linalg.norm(bust[:3] - BUST_START)), float(ang)


def glasses_shift(bust, glasses) -> float:
    """How far the glasses are from their place on the bust's face (m)."""
    place = np.array([GLASSES[0], GLASSES[1], GLASSES[2] - BUST_Z])
    return float(np.linalg.norm(in_frame(bust, [np.asarray(glasses, float)[:3]])[0] - place))


def button_press(btn) -> float:
    return float(TOP + BTN_Z - np.asarray(btn, float)[2])


def spread(left, right) -> float:
    """How far apart the two cushion faces are (m): the travel of the headband's joint."""
    d = in_frame(left, [np.asarray(right, float)[:3]])[0]
    return float(-d[1] - CUP[1])


def clamp_force(sep: float) -> float:
    """The headband's clamping force at that spread (N)."""
    return SPRING_K * (SPRING_PRE + max(0.0, sep))


def _cushion(side: str):
    """A half's cushion face in its own frame: middle, and the four ends of the oval ring's outline."""
    s = 1.0 if side == "left" else -1.0
    y = -s * CUP[1] / 2
    a, b = CUSHION_RIM
    return (0.0, y, 0.0), [(a, y, 0.0), (-a, y, 0.0), (0.0, y, b), (0.0, y, -b)]


def cup_on_ear(bust, half, side: str, ear: str) -> bool:
    """That half's cup covers that ear: the cushion's face (its middle and the four ends of its outline) is against
    that side of the head, and the whole outer ear (the four ends of its outline) lies inside the cushion's oval
    opening."""
    mid, rim = _cushion(side)
    world = points(half, [mid] + rim)
    pts = in_frame(bust, world)
    e = np.asarray(EARS[ear])
    if any(abs(p[1] - e[1]) > SEAL for p in pts):
        return False
    ex, ez = EAR_HALF
    outline = [e + np.array(d) for d in ((ex, 0.0, 0.0), (-ex, 0.0, 0.0), (0.0, 0.0, ez), (0.0, 0.0, -ez))]
    for p in in_frame(half, points(bust, outline)):
        d = p - np.asarray(mid)
        if (d[0] / (OPENING[0] / 2)) ** 2 + (d[2] / (OPENING[1] / 2)) ** 2 > 1.0:
            return False
    return True


def ears_covered(bust, left, right):
    """(left ear covered, right ear covered), by one cup each, whichever way round the defenders are."""
    a = (cup_on_ear(bust, left, "left", "left"), cup_on_ear(bust, right, "right", "right"))
    b = (cup_on_ear(bust, right, "right", "left"), cup_on_ear(bust, left, "left", "right"))
    return a if sum(a) >= sum(b) else b


def band_point(left, right):
    """The band's middle at its crown pad's underside (world): the point midway between the two cups' middles, BAND_Z
    above them."""
    l = points(left, [(0.0, 0.0, BAND_Z)])[0]
    r = points(right, [(0.0, 0.0, BAND_Z)])[0]
    return (l + r) / 2


def band_over_crown(bust, left, right) -> bool:
    """The headband passes over the top of the head: the band's middle at its crown pad's underside within 35 mm fore, aft and
    sideways of the point above the ear line, and 0 to 30 mm above the crown."""
    p = in_frame(bust, [band_point(left, right)])[0]
    z = p[2] + BUST_Z
    return bool(abs(p[0] - EAR_X) <= BAND_FORE_AFT and abs(p[1]) <= BAND_FORE_AFT and CROWN_Z <= z <= CROWN_Z + BAND_ABOVE)


def grasp_point(half, side: str):
    s = 1.0 if side == "left" else -1.0
    return points(half, [(0.0, s * GRASP[0], GRASP[1])])[0]


def _band_samples(side: str):
    """Points every 10 mm or less along that half's fork and headband, in its frame."""
    s = 1.0 if side == "left" else -1.0
    line = ((CUP[1] / 2, 0.0),) + BAND_PATH
    out = []
    for (y0, z0), (y1, z1) in zip(line[:-1], line[1:]):
        n = max(1, int(math.ceil(math.hypot(y1 - y0, z1 - z0) / 0.010)))
        out += [(0.0, s * (y0 + (y1 - y0) * i / n), z0 + (z1 - z0) * i / n) for i in range(n + 1)]
    return out


def hand_gap(tcp, left, right) -> float:
    """Distance from a hand's grasp point to the ear defenders (m): to the nearest cup's surface (0 inside a cup) or
    the nearest point of the forks and the headband, crown span included."""
    t = np.asarray(tcp, float)[:3]
    best = 1e9
    for half, side in ((left, "left"), (right, "right")):
        p = in_frame(half, [t])[0]
        out = np.maximum(np.abs(p) - np.asarray(CUP) / 2, 0.0)
        best = min(best, float(np.linalg.norm(out)))
        for q in _band_samples(side):
            best = min(best, float(np.linalg.norm(p - np.asarray(q))))
    return best
