"""Geometry and measurements for putting a baby doll down for a nap in a doll's bed that has soft things left in it.

A counter set up for infant-care and safe-sleep practice with a baby doll. A small pine doll's bed with a quilted
mattress pad stands in the middle; a little pillow, a plush bunny and a folded blanket were left in it. A soft-bodied
baby doll lies on her back on a changing mat to the right. A low tray for nursery things lies to the left. The soft
things are rigid stand-ins shaped and coloured like the real ones.

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
PINE = (0.87, 0.75, 0.55)
CREAM = (0.96, 0.93, 0.85)
SKIN = (0.96, 0.81, 0.72)
PINK = (0.90, 0.70, 0.74)
MINT = (0.72, 0.88, 0.82)
GREY = (0.78, 0.78, 0.76)

# -- doll's bed: pine, 388 x 248 mm over its corner posts, headboard at the near (-x) end, low footboard at the far
# end; fixed. Its pieces are written head toward +x and the whole bed is turned half a turn (BED_YAW) -----------
BED_C = (0.375, 0.020)
IN_HX, IN_HY = 0.170, 0.100           # half the clear space over the mattress (340 x 200 mm), between rails and end boards
MATT_Z = 0.090                        # the mattress pad's flat top above the counter
RAIL_Z = 0.135                        # the top of the side rails above the counter
FOOT_Z, HEAD_Z = 0.142, 0.180         # the tops of the footboard and the headboard (at the middle of their arches)
RAIL_T, BOARD_T, POST = 0.012, 0.014, 0.024
POST_Z = (0.150, 0.190)               # foot posts, head posts
BED_YAW = math.pi
BASE_Z = 0.060                        # the rails and end boards start this high; the bed stands on its posts
SPACE_OVER = 0.030                    # the sleep space reaches this far above the rails
OUT_HX, OUT_HY = IN_HX + POST, IN_HY + POST      # half the bed's outer outline, over its corner posts (388 x 248 mm)

# -- soft-bodied baby doll: 26 cm long, 200 g; her frame: origin at the middle of her torso, x toward her head,
# z out of her tummy (so lying on her back her z points up). She starts with her head toward the robot (DOLL_YAW) -----------------------------------------------------
DOLL_MASS = 0.20
DOLL_YAW = math.pi
TORSO = (0.100, 0.062, 0.050)
HEAD_R = 0.036
HEAD_AT = (0.086, 0.0, 0.011)
LEGS = (0.085, 0.070, 0.034)
LEGS_AT = (-0.0925, 0.0, -0.008)
# the points that stand for her whole body: top of the head, both feet, both hands, both hips, the torso's middle
# her body as balls for "is something soft against her": (centre, radius) in her frame; the first is her head
DOLL_BALLS = (((0.086, 0.0, 0.011), 0.036), ((0.030, 0.0, 0.0), 0.028), ((0.0, 0.0, 0.0), 0.028), ((-0.030, 0.0, 0.0), 0.028),
              ((-0.070, 0.020, -0.008), 0.016), ((-0.070, -0.020, -0.008), 0.016), ((-0.115, 0.022, -0.010), 0.014),
              ((-0.115, -0.022, -0.010), 0.014), ((0.068, 0.054, -0.012), 0.012), ((0.068, -0.054, -0.012), 0.012))
TOUCH = 0.005                         # a soft thing is against her when its outline is within this of one of those balls
DOLL_POINTS = ((0.128, 0.0, 0.011), (-0.132, 0.022, -0.011), (-0.132, -0.022, -0.011), (0.088, 0.060, -0.012),
               (0.088, -0.060, -0.012), (-0.045, 0.028, 0.0), (-0.045, -0.028, 0.0), (0.0, 0.0, 0.0))

# -- changing mat (300 x 180 x 10 mm) where the doll starts; fixed ----------------------------------------------
MAT_C = (0.365, -0.250)
MAT = (0.300, 0.180, 0.010)
DOLL_C = (0.364, -0.250)

# -- the soft things left in the bed (rigid stand-ins) ----------------------------------------------------------
SOFT = ("pillow", "plush_toy", "blanket")
SOFT_SIZE = {"pillow": (0.085, 0.078, 0.022), "plush_toy": (0.046, 0.046, 0.036), "blanket": (0.085, 0.078, 0.030)}
SOFT_MASS = {"pillow": 0.035, "plush_toy": 0.045, "blanket": 0.050}
SOFT_C = {"pillow": (BED_C[0] - 0.098, BED_C[1]), "plush_toy": (BED_C[0] - 0.008, BED_C[1] + 0.015),
          "blanket": (BED_C[0] + 0.110, BED_C[1] - 0.005)}
SOFT_COLOR = {"pillow": CREAM, "plush_toy": PINK, "blanket": CREAM}
# each soft thing's outline for scoring: a box in its own frame, as (lowest corner, highest corner); the bunny's covers
# its head and legs as well as its body
SOFT_BOX = {"pillow": ((-0.0425, -0.039, -0.011), (0.0425, 0.039, 0.011)),
            "plush_toy": ((-0.036, -0.023, -0.018), (0.045, 0.023, 0.018)),
            "blanket": ((-0.0425, -0.039, -0.015), (0.0425, 0.039, 0.015))}
PUT_DOWN_Z = 0.075                    # a soft thing put down has no part higher than this above the counter
BUNNY_BODY_X = -0.008                 # the bunny's body (its collider's root) sits this far behind its footprint centre

# -- nursery tray (330 x 190 mm, 14 mm rim) for things taken out; fixed ------------------------------------------
TRAY_C = (0.365, 0.300)
TRAY = (0.330, 0.190)
TRAY_FLOOR, TRAY_RIM, TRAY_WALL = 0.005, 0.014, 0.008

COUNTER_X, COUNTER_Y = (0.02, 0.80), 0.62      # the counter top's usable area


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def bed_object() -> Part:
    """The doll's bed: fixed. Colliders (hidden): the mattress and the space under it as one slab, the two side
    rails, the footboard and the headboard as boards, the four corner posts."""
    zc = MATT_Z / 2
    ox = IN_HX + BOARD_T / 2
    oy = IN_HY + RAIL_T / 2

    def board(size_x, size_y, z_top, x, y):
        return Piece("box", (size_x, size_y, z_top - BASE_Z), (x, y, (z_top + BASE_Z) / 2 - zc), color=PINE)

    pieces = [board(2 * IN_HX, RAIL_T, RAIL_Z, 0.0, oy), board(2 * IN_HX, RAIL_T, RAIL_Z, 0.0, -oy),
              board(BOARD_T, 2 * IN_HY, FOOT_Z - 0.005, -ox, 0.0), board(BOARD_T, 2 * IN_HY, HEAD_Z - 0.005, ox, 0.0)]
    for sx, zt in ((-1.0, POST_Z[0]), (1.0, POST_Z[1])):
        for sy in (1.0, -1.0):
            pieces.append(Piece("box", (POST, POST, zt), (sx * (IN_HX + POST / 2), sy * (IN_HY + POST / 2), zt / 2 - zc), color=PINE))
    return Part("doll_bed", pos=(BED_C[0], BED_C[1], TOP + zc), size=(2 * IN_HX, 2 * IN_HY, MATT_Z), exact_z=True,
                color=CREAM, friction=(0.9, 0.8), pieces=tuple(pieces), yaw=BED_YAW, **_vis(("doll_bed", "bed_rug", "bed_labels"), (0.0, 0.0, -zc)))


def mat_object() -> Part:
    """The changing mat: fixed. Colliders (hidden): a flat slab (in two layers)."""
    half = MAT[2] / 2
    top = Piece("box", (MAT[0], MAT[1], half), (0.0, 0.0, half / 2 + half / 2), color=MINT)
    return Part("changing_mat", pos=(MAT_C[0], MAT_C[1], TOP + half / 2), size=(MAT[0], MAT[1], half), exact_z=True, color=MINT,
                friction=(0.9, 0.8), pieces=(top,), **_vis("changing_mat", (0.0, 0.0, -half / 2)))


def tray_object() -> Part:
    """The tray: fixed. Colliders (hidden): its floor and four low walls."""
    zc = TRAY_FLOOR / 2
    h = TRAY_RIM - TRAY_FLOOR
    zw = TRAY_FLOOR + h / 2 - zc
    ox, oy, t = TRAY[0] / 2, TRAY[1] / 2, TRAY_WALL
    pieces = (
        Piece("box", (t, TRAY[1], h), (ox - t / 2, 0.0, zw), color=GREY),
        Piece("box", (t, TRAY[1], h), (-ox + t / 2, 0.0, zw), color=GREY),
        Piece("box", (TRAY[0], t, h), (0.0, oy - t / 2, zw), color=GREY),
        Piece("box", (TRAY[0], t, h), (0.0, -oy + t / 2, zw), color=GREY),
    )
    return Part("nursery_tray", pos=(TRAY_C[0], TRAY_C[1], TOP + zc), size=(TRAY[0], TRAY[1], TRAY_FLOOR), exact_z=True,
                color=GREY, friction=(0.9, 0.8), pieces=pieces, **_vis("nursery_tray", (0.0, 0.0, -zc)))


def doll_object() -> Part:
    """The doll: a free rigid body. Colliders (hidden): her torso (the root), head, legs and arms as simple shapes."""
    pieces = [Piece("sphere", (HEAD_R, HEAD_R, HEAD_R), HEAD_AT, color=SKIN),
              Piece("box", LEGS, LEGS_AT, color=CREAM)]
    for sy in (1.0, -1.0):
        pieces.append(Piece("box", (0.022, 0.026, 0.020), (0.045, sy * 0.044, -0.012), color=CREAM))
        pieces.append(Piece("box", (0.050, 0.020, 0.020), (0.068, sy * 0.054, -0.012), color=CREAM))
    return Part("baby_doll", pos=(DOLL_C[0], DOLL_C[1], TOP + MAT[2] + TORSO[2] / 2 + 0.001), size=TORSO, exact_z=True,
                mass=DOLL_MASS, color=CREAM, friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.002,
                com=(0.0, 0.0, 0.0), yaw=DOLL_YAW, **_vis("baby_doll", (0.0, 0.0, -TORSO[2] / 2)))


def soft_object(name: str) -> Part:
    """A soft thing: a free rigid body, a box (the bunny: its body as a box, its head as a ball, its legs a small box)."""
    sx, sy, sz = SOFT_SIZE[name]
    cx, cy = SOFT_C[name]
    pieces, off, com = (), (0.0, 0.0, -sz / 2), None
    if name == "plush_toy":
        pieces = (Piece("sphere", (0.017, 0.017, 0.017), (0.028, 0.0, 0.0), color=PINK),
                  Piece("box", (0.024, 0.044, 0.020), (-0.024, 0.0, -0.008), color=PINK))
        off = (-BUNNY_BODY_X, 0.0, -sz / 2)
        com = (0.0, 0.0, 0.0)
    return Part(name, pos=(cx, cy, TOP + MATT_Z + sz / 2), size=(sx, sy, sz), exact_z=True, mass=SOFT_MASS[name],
                color=SOFT_COLOR[name], friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002, com=com,
                **_vis(name, off))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def in_outline(p) -> bool:
    """A point over the bed's mattress as seen from above: within the 340 x 200 mm space between the rails and the
    end boards."""
    return bool(abs(float(p[0]) - BED_C[0]) <= IN_HX and abs(float(p[1]) - BED_C[1]) <= IN_HY)


def in_outer_outline(p) -> bool:
    """A point over the bed as a whole, posts, rails and end boards included (388 x 248 mm)."""
    return bool(abs(float(p[0]) - BED_C[0]) <= OUT_HX and abs(float(p[1]) - BED_C[1]) <= OUT_HY)


def soft_points(name: str, pose):
    """Twenty-seven points of a soft thing's outline: the corners, edge and face middles and the centre of its box."""
    pose = np.asarray(pose, float)
    r = quat_matrix(pose[3:7])
    lo, hi = (np.asarray(v, float) for v in SOFT_BOX[name])
    mid = (lo + hi) / 2
    return [pose[:3] + r @ np.array([x, y, z]) for x in (lo[0], mid[0], hi[0]) for y in (lo[1], mid[1], hi[1])
            for z in (lo[2], mid[2], hi[2])]


def in_sleep_space(name: str, pose) -> bool:
    """A soft thing is in the sleep space while ANY part of it is over the mattress and less than 3 cm above the top
    of the side rails: lying in the bed, half in, hanging over a rail into it or held just above it."""
    return any(in_outline(p) and p[2] < TOP + RAIL_Z + SPACE_OVER for p in soft_points(name, pose))


def soft_touching(name: str, pose, doll):
    """Where a soft thing is against the doll: "head", "body" or None. Its box within TOUCH of one of her balls."""
    pose = np.asarray(pose, float)
    doll = np.asarray(doll, float)
    r = quat_matrix(pose[3:7])
    rd = quat_matrix(doll[3:7])
    lo, hi = (np.asarray(v, float) for v in SOFT_BOX[name])
    hit = None
    for i, (c, rad) in enumerate(DOLL_BALLS):
        q = r.T @ (doll[:3] + rd @ np.asarray(c, float) - pose[:3])
        gap = float(np.linalg.norm(q - np.clip(q, lo, hi))) - rad
        if gap <= TOUCH:
            if i == 0:
                return "head"
            hit = "body"
    return hit


def doll_part_in_bed(doll) -> bool:
    """Any part of the doll (head, hands, hips, feet or torso) is over the mattress and below the top of the rails."""
    return any(in_outline(p) and p[2] < TOP + RAIL_Z for p in doll_points(doll))


def doll_in_bed(doll) -> bool:
    """The doll is in the bed: the middle of her torso over the mattress and below the top of the side rails."""
    return bool(in_outline(doll) and float(doll[2]) < TOP + RAIL_Z)


def doll_points(doll):
    doll = np.asarray(doll, float)
    r = quat_matrix(doll[3:7])
    return [doll[:3] + r @ np.asarray(p, float) for p in DOLL_POINTS]


def doll_whole_body_in(doll) -> bool:
    """Head, hands, hips and feet are all over the mattress and below the top of the side rails."""
    return all(in_outline(p) and p[2] < TOP + RAIL_Z for p in doll_points(doll))


def doll_on_mattress(doll) -> bool:
    """Her back is down on the mattress: the middle of her torso no more than 12 mm above where it lies when flat."""
    return bool(float(np.asarray(doll, float)[2]) <= TOP + MATT_Z + TORSO[2] / 2 + 0.012)


def supine_deg(doll) -> float:
    """Angle between the way her face and tummy point and straight up: 0 flat on her back, 90 on her side, 180 face
    down."""
    r = quat_matrix(np.asarray(doll, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def on_counter(p) -> bool:
    return bool(COUNTER_X[0] <= float(p[0]) <= COUNTER_X[1] and abs(float(p[1])) <= COUNTER_Y and float(p[2]) > TOP - 0.02)


def soft_put_down(name: str, pose) -> bool:
    """A soft thing is out and put down: every part of it outside the bed's outer outline (so not on a rail, a post or
    an end board), on the counter or the tray, and no part higher than 7.5 cm above the counter (so not held, and not
    lying on the doll)."""
    pts = soft_points(name, pose)
    return bool(all(not in_outer_outline(p) and on_counter(p) and p[2] < TOP + PUT_DOWN_Z for p in pts))


def on_tray(p) -> bool:
    return bool(abs(float(p[0]) - TRAY_C[0]) <= TRAY[0] / 2 and abs(float(p[1]) - TRAY_C[1]) <= TRAY[1] / 2
                and float(p[2]) < TOP + 0.060)
