"""Geometry and measurements for putting away a bottle of instant glue left beside an open first-aid box.

A home counter after a small repair. A bottle of instant glue, capped, stands on the counter. An open first-aid box holds a row of small dropper bottles: saline, eye drops that look almost the same as the
glue, and one empty well beside the eye drops. A tool caddy with an empty compartment stands on the other side.

Frame: metres, x away from the arm bases, y left, z up; TOP is the counter. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WHITE = (0.96, 0.96, 0.95)
RED = (0.74, 0.08, 0.06)
GREY = (0.82, 0.84, 0.85)
CREAM = (0.94, 0.92, 0.86)

# -- the small dropper bottle (the glue and the eye drops are the same bottle): 30 mm across, 54 mm to the flat
#    shoulder ring, nozzle tip at 80 mm, 86 mm tall with its cap on -------------------------------------------
B_R, B_H = 0.015, 0.054
NOZ_R, NOZ_H = 0.0025, 0.026           # the nozzle's collider: a cone standing on the shoulder, thinner than the nozzle and neck are drawn
B_MASS = 0.030                         # about 20 g of contents and a 10 g bottle
# -- its long pointed push-on cap: 19 mm across at the rim, 32 mm tall, hollow ---------------------------------
CAP_H = 0.032
CAP_RO, CAP_RI = 0.0095, 0.00625       # lower ring (the ribbed grip), rim to 14 mm
CAP_LOW = 0.014
CAP_MID_RO, CAP_MID_RI = 0.0070, 0.0052
CAP_MID_TOP, CAP_HIGH_RI = 0.020, 0.0042
CAP_PLUG_Z = (0.027, 0.032)            # the closed top
CAP_ROOT_Z = (CAP_PLUG_Z[0] + CAP_PLUG_Z[1]) / 2
CAP_MASS = 0.003
SEAT_XY = 0.0030                       # the cap is on when its axis is within this of the bottle's axis,
SEAT_Z = 0.003                         # its rim within this of the shoulder ring,
SEAT_TILT = 12.0                       # and it is in line with the bottle within this many degrees
SNAP_XY = SEAT_XY                      # the push fit catches there

GLUE_C = (0.255, -0.130)

# -- first-aid box: base tray 200 (x) x 130 (y) x 40 mm, deep lid 50 mm hinged along its +y rim -----------------
BOX_C = (0.400, -0.195)
BOX_HALF = (0.100, 0.065)
BOX_RIM = 0.040
BOX_WALL, BOX_FLOOR = 0.003, 0.003
RACK_Y = (0.024, 0.062)                # the bottle rack along the hinge wall, in the box's frame
RACK_TOP = 0.021
WELL = 0.033                           # the wells are drawn round; their colliders are square pockets this wide
WELLS_X = (-0.050, 0.0, 0.050)         # empty, eye drops, saline
WELL_Y = 0.043
EMPTY_WELL = (BOX_C[0] + WELLS_X[0], BOX_C[1] + WELL_Y)
EYE_C = (BOX_C[0] + WELLS_X[1], BOX_C[1] + WELL_Y)
SALINE_C = (BOX_C[0] + WELLS_X[2], BOX_C[1] + WELL_Y)
SALINE_H = 0.074
HINGE_Y = BOX_C[1] + BOX_HALF[1]
PIVOT = (BOX_C[0], HINGE_Y, TOP + BOX_RIM)
LID_LEN, LID_DEEP, LID_T = 0.130, 0.050, 0.003
LID_OPEN = 100.0                       # degrees: it starts swung right back, leaning 10 degrees past upright on its stop
LID_MASS = 0.10
LID_SHUT = 5.0                         # degrees from closed
KEEP_OFF = 0.050                       # the glue must end at least this far from the eye drops (gap between the two bottles)

# -- tool caddy: open tray 250 (x) x 170 (y) x 32 mm with an empty compartment at its near left corner ----------
CADDY_C = (0.425, 0.0565)
CADDY_HALF = (0.125, 0.085)
CADDY_H, CADDY_WALL, CADDY_FLOOR = 0.032, 0.003, 0.003
COMP_X = (-0.122, -0.050)              # the empty compartment, in the caddy's frame
COMP_Y = (0.005, 0.082)
COMP_C = (CADDY_C[0] + sum(COMP_X) / 2, CADDY_C[1] + sum(COMP_Y) / 2)
MUG_C = (0.470, 0.290)
MUG_IN_ASSET = (0.135, 0.290)
MUG_R, MUG_H = 0.041, 0.095


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    names = tuple(n for n in names if (ASSETS / f"{n}.usdc").exists())
    if not names:
        return {}
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _staves(r_in, r_out, z0, z1, zc, n, color):
    r, thick = (r_in + r_out) / 2, r_out - r_in
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(Piece("box", (thick, 2 * r * math.tan(math.pi / n) + 0.0006, z1 - z0),
                         (r * math.cos(a), r * math.sin(a), (z0 + z1) / 2 - zc), rot=(0.0, 0.0, a), color=color))
    return out


def _bottle(name, c, z, pieces, vis, mass=B_MASS):
    return Part(name, pos=(c[0], c[1], z + B_H / 2), size=(B_R, B_H, B_R), shape="cylinder", exact_z=True, mass=mass,
                color=WHITE, friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.001, **vis)


def glue_object() -> Part:
    """The glue bottle: a free rigid body. Colliders (hidden): the body as a cylinder, the nozzle as a cone."""
    nozzle = Piece("cone", (NOZ_R, NOZ_H, NOZ_R), (0.0, 0.0, B_H / 2 + NOZ_H / 2), color=WHITE)
    return _bottle("glue", GLUE_C, TOP, (nozzle,), _vis(("glue_bottle", "glue_label"), (0.0, 0.0, -B_H / 2)))


def cap_object() -> Part:
    """The glue's cap, pushed on the bottle: a separate rigid body, hollow (rings of staves and a closed top). Its
    push fit is a joint to the bottle, on from the start."""
    zc = CAP_ROOT_Z
    pieces = _staves(CAP_RI, CAP_RO, 0.0, CAP_LOW, zc, 8, WHITE) + _staves(CAP_MID_RI, CAP_MID_RO, CAP_LOW, CAP_MID_TOP + 0.004, zc, 8, WHITE)
    pos = (GLUE_C[0], GLUE_C[1], TOP + B_H + zc)        # it starts pushed on the bottle
    seat = (0.0, 0.0, B_H / 2 + zc)                      # the seated cap's origin in the bottle's frame
    fit = Spring(axis="Z", lower=-0.0004, upper=0.0004, stiffness=3000.0, damping=3.0, target=0.0, parent="glue",
                 parent_pos=tuple(p - s for p, s in zip(pos, seat)))
    return Part("glue_cap", pos=pos, size=(CAP_MID_RO, CAP_PLUG_Z[1] - CAP_PLUG_Z[0], CAP_MID_RO), shape="cylinder", exact_z=True,
                mass=CAP_MASS, color=WHITE, friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.001, spring=fit,
                com=(0.0, 0.0, 0.007 - zc), **_vis("glue_cap", (0.0, 0.0, -zc)))


def eye_object() -> Part:
    """The eye drops, cap on, standing in the middle well of the first-aid box: a free rigid body."""
    h = CAP_H - 0.003                                    # 3 mm short, so the lid's collider clears it when shut
    cap = Piece("cylinder", (CAP_MID_RO, h, CAP_MID_RO), (0.0, 0.0, B_H / 2 + h / 2), color=WHITE)
    return _bottle("eye_drops", EYE_C, TOP + BOX_FLOOR, (cap,), _vis(("eye_drops", "eye_label"), (0.0, 0.0, -B_H / 2)))


def box_object() -> Part:
    """The first-aid box's base with its rack, the saline bottle and the dressings: fixed. Colliders (hidden): floor,
    walls, the rack as blocks leaving three square pockets, the saline bottle and the dressings as simple solids."""
    zc = BOX_FLOOR / 2
    hx, hy, w = BOX_HALF[0], BOX_HALF[1], BOX_WALL
    wz = BOX_RIM / 2 - zc
    p = [Piece("box", (2 * hx, w, BOX_RIM), (0.0, s * (hy - w / 2), wz), color=WHITE) for s in (1, -1)]
    p += [Piece("box", (w, 2 * hy, BOX_RIM), (s * (hx - w / 2), 0.0, wz), color=WHITE) for s in (1, -1)]
    rz, rh = (BOX_FLOOR + RACK_TOP) / 2 - zc, RACK_TOP - BOX_FLOOR
    y0, y1 = WELL_Y - WELL / 2, WELL_Y + WELL / 2
    p.append(Piece("box", (0.150, y0 - RACK_Y[0], rh), (0.0, (RACK_Y[0] + y0) / 2, rz), color=GREY))
    p.append(Piece("box", (0.150, RACK_Y[1] - y1, rh), (0.0, (y1 + RACK_Y[1]) / 2, rz), color=GREY))
    edges = [-0.075] + [x + s * WELL / 2 for x in WELLS_X for s in (-1, 1)] + [0.075]
    for a, b in zip(edges[0::2], edges[1::2]):
        p.append(Piece("box", (b - a, WELL, rh), ((a + b) / 2, WELL_Y, rz), color=GREY))
    p.append(Piece("cylinder", (B_R, SALINE_H, B_R), (WELLS_X[2], WELL_Y, BOX_FLOOR + SALINE_H / 2 - zc), color=WHITE))
    p.append(Piece("box", (0.095, 0.062, 0.020), (0.042, -0.025, BOX_FLOOR + 0.010 - zc), color=CREAM))
    p.append(Piece("cylinder", (0.021, 0.050, 0.021), (-0.062, -0.025, BOX_FLOOR + 0.021 - zc), axis="Y", color=WHITE))
    return Part("first_aid_box", pos=(BOX_C[0], BOX_C[1], TOP + zc), size=(2 * hx, 2 * hy, BOX_FLOOR), exact_z=True, color=WHITE,
                friction=(0.5, 0.4), pieces=tuple(p), **_vis(("first_aid_box", "box_labels"), (0.0, 0.0, -zc)))


def _rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def lid_object() -> Part:
    """The first-aid box's lid: a free rigid body on a hinge along the box's +y rim, standing open on its stop. It is
    modelled closed and placed swung back by LID_OPEN. Colliders (hidden): top plate and four walls."""
    r = _rx(-LID_OPEN)
    half = BOX_HALF[0]
    closed = [((2 * half, LID_LEN, LID_T), (0.0, -LID_LEN / 2, LID_DEEP - LID_T / 2)),
              ((2 * half, LID_T, LID_DEEP - LID_T - 0.001), (0.0, -LID_LEN + LID_T / 2, (LID_DEEP - LID_T + 0.001) / 2)),
              ((2 * half, LID_T, LID_DEEP - LID_T - 0.001), (0.0, -LID_T / 2, (LID_DEEP - LID_T + 0.001) / 2)),
              ((LID_T, LID_LEN, LID_DEEP - LID_T - 0.001), (half - LID_T / 2, -LID_LEN / 2, (LID_DEEP - LID_T + 0.001) / 2)),
              ((LID_T, LID_LEN, LID_DEEP - LID_T - 0.001), (-half + LID_T / 2, -LID_LEN / 2, (LID_DEEP - LID_T + 0.001) / 2))]
    root = r @ np.array(closed[0][1])
    pos = tuple(float(v) for v in np.array(PIVOT) + root)
    roll = -math.radians(LID_OPEN)
    pieces = [Piece("box", size, tuple(float(v) for v in r @ np.array(c) - root), rot=(roll, 0.0, 0.0), color=WHITE) for size, c in closed]
    hinge = Hinge(pivot=PIVOT, axis="X", damping=0.02, lower_deg=0.0, upper_deg=LID_OPEN, friction=0.002)
    return Part("lid", pos=pos, size=(0.001, 0.001, 0.001), shape="sphere", exact_z=True, mass=LID_MASS, color=WHITE,
                friction=(0.6, 0.5), pieces=tuple(pieces), hinge=hinge, contact_offset=0.002,
                **_vis(("first_aid_lid", "lid_labels"), tuple(float(-v) for v in root), visual_rpy_deg=(-LID_OPEN, 0.0, 0.0)))


MUG_PARTS = ("mug_body", "mug_handle", "mug_crack", "mug_crack_low")
CADDY_PARTS = ("tray", "dividers", "tape_roll", "tape_core", "screwdriver_handle", "screwdriver_shaft", "knife_body", "knife_slider")


def caddy_object() -> Part:
    """The tool caddy with a tape roll, a screwdriver and a cutter in it: fixed. Colliders (hidden): floor, walls,
    dividers and the tools as simple solids."""
    zc = CADDY_FLOOR / 2
    hx, hy, w = CADDY_HALF[0], CADDY_HALF[1], CADDY_WALL
    wz = CADDY_H / 2 - zc
    p = [Piece("box", (2 * hx, w, CADDY_H), (0.0, s * (hy - w / 2), wz), color=RED) for s in (1, -1)]
    p += [Piece("box", (w, 2 * hy, CADDY_H), (s * (hx - w / 2), 0.0, wz), color=RED) for s in (1, -1)]
    dz, dh = (CADDY_FLOOR + 0.028) / 2 - zc, 0.028 - CADDY_FLOOR
    p.append(Piece("box", (2 * hx, 0.0025, dh), (0.0, 0.005, dz), color=RED))
    p.append(Piece("box", (0.0025, hy - 0.005, dh), (-0.050, (hy + 0.005) / 2, dz), color=RED))
    p.append(Piece("cylinder", (0.036, 0.048, 0.036), (0.045, 0.044, CADDY_FLOOR + 0.024 - zc), color=RED))
    p.append(Piece("box", (0.205, 0.028, 0.026), (-0.0075, -0.030, CADDY_FLOOR + 0.013 - zc), color=RED))
    p.append(Piece("box", (0.150, 0.020, 0.011), (-0.015, -0.062, CADDY_FLOOR + 0.0055 - zc), color=RED))
    return Part("tool_caddy", pos=(CADDY_C[0], CADDY_C[1], TOP + zc), size=(2 * hx, 2 * hy, CADDY_FLOOR), exact_z=True, color=RED,
                friction=(0.6, 0.5), pieces=tuple(p), **_vis("tool_caddy", (0.0, 0.0, -zc), visual_hide=MUG_PARTS))


def mug_object() -> Part:
    """The mended mug: fixed; a cylinder collider."""
    off = (-MUG_IN_ASSET[0], -MUG_IN_ASSET[1], -MUG_H / 2)
    return Part("mug", pos=(MUG_C[0], MUG_C[1], TOP + MUG_H / 2), size=(MUG_R, MUG_H, MUG_R), shape="cylinder", exact_z=True,
                color=CREAM, friction=(0.6, 0.5), **_vis("tool_caddy", off, visual_hide=CADDY_PARTS))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def bottle_points(pose):
    """Base centre, body centre and shoulder centre of a dropper bottle from its pose (its origin is the body centre)."""
    pose = np.asarray(pose, float)
    axis = quat_matrix(pose[3:7])[:, 2]
    return pose[:3] - axis * B_H / 2, pose[:3].copy(), pose[:3] + axis * B_H / 2


def bottle_outline(pose):
    """Points on a dropper bottle's whole outline: its axis and eight points round its wall at the base, the middle
    and the shoulder, and its nozzle tip."""
    pose = np.asarray(pose, float)
    r = quat_matrix(pose[3:7])
    pts = [pose[:3] + r[:, 2] * (0.080 - B_H / 2)]
    for h in (-B_H / 2, 0.0, B_H / 2):
        c = pose[:3] + r[:, 2] * h
        pts.append(c)
        for k in range(8):
            a = math.pi / 4 * k
            pts.append(c + B_R * (math.cos(a) * r[:, 0] + math.sin(a) * r[:, 1]))
    return pts


def cap_fit(glue, cap):
    """The cap relative to the glue bottle: (distance of the cap's rim centre from the bottle's axis, height of the
    rim above the shoulder ring, angle between the two axes in degrees)."""
    glue, cap = np.asarray(glue, float), np.asarray(cap, float)
    rg, rc = quat_matrix(glue[3:7]), quat_matrix(cap[3:7])
    rim = cap[:3] - rc[:, 2] * CAP_ROOT_Z
    q = rg.T @ (rim - glue[:3])
    ang = math.degrees(math.acos(float(np.clip(rg[:, 2] @ rc[:, 2], -1.0, 1.0))))
    return float(math.hypot(q[0], q[1])), float(q[2] - B_H / 2), ang


def cap_seated(glue, cap, xy=SEAT_XY) -> bool:
    off, up, ang = cap_fit(glue, cap)
    return bool(off <= xy and -0.002 <= up <= SEAT_Z and ang <= SEAT_TILT)


def _in_box_outline(p, grow=0.0) -> bool:
    return bool(abs(p[0] - BOX_C[0]) <= BOX_HALF[0] + grow and abs(p[1] - BOX_C[1]) <= BOX_HALF[1] + grow)


def in_first_aid_box(pose) -> bool:
    """A dropper bottle in the first-aid box: any point of its outline inside the box's outline and below its rim
    (in a well, on the rack or on the dressings, wholly or partly)."""
    return any(_in_box_outline(p) and p[2] < TOP + BOX_RIM for p in bottle_outline(pose))


def on_first_aid_box(pose) -> bool:
    """A dropper bottle on or against the first-aid box: any point of its outline over the box or within 5 mm of its
    walls, no higher than 2 cm above the shut lid (lying or standing on the lid or the rim, or leaning on the box)."""
    return any(_in_box_outline(p, 0.005) and p[2] < TOP + BOX_RIM + LID_DEEP + 0.020 for p in bottle_outline(pose))


def cap_in_first_aid_box(cap) -> bool:
    """The glue's cap in the first-aid box: within the box's outline and below the shut lid's top."""
    cap = np.asarray(cap, float)
    return bool(_in_box_outline(cap) and cap[2] < TOP + BOX_RIM + LID_DEEP)


def bottle_gap(a, b) -> float:
    """Gap between two dropper bottles (m): the least distance between their axes, base to nozzle tip, less one body
    width."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    best = 1e9
    ua, ub = quat_matrix(a[3:7])[:, 2], quat_matrix(b[3:7])[:, 2]
    hs = np.linspace(-B_H / 2, 0.080 - B_H / 2, 9)
    for h in hs:
        pa = a[:3] + ua * h
        for g in hs:
            best = min(best, float(np.linalg.norm(pa - (b[:3] + ub * g))))
    return best - 2 * B_R


def over_caddy(pose) -> bool:
    """A dropper bottle in or on the tool caddy in any attitude: any point of its outline within the tray's outline and
    less than 8 cm above the counter."""
    return any(abs(p[0] - CADDY_C[0]) <= CADDY_HALF[0] and abs(p[1] - CADDY_C[1]) <= CADDY_HALF[1] and p[2] < TOP + 0.080
               for p in bottle_outline(pose))


def in_caddy(pose) -> bool:
    """A dropper bottle standing in the tool caddy: upright within 12 degrees, the whole of its base inside the tray's
    walls and down on the tray's floor."""
    base = bottle_points(pose)[0]
    return bool(abs(base[0] - CADDY_C[0]) <= CADDY_HALF[0] - CADDY_WALL - B_R + 0.002
                and abs(base[1] - CADDY_C[1]) <= CADDY_HALF[1] - CADDY_WALL - B_R + 0.002
                and base[2] <= TOP + CADDY_FLOOR + 0.006 and tilt_deg(pose) <= 12.0)


def lid_open_deg(lid) -> float:
    """How far the first-aid box's lid stands open (0 = shut on the rim, LID_OPEN = swung right back)."""
    q = np.asarray(lid, float)[3:7]
    turned = math.degrees(2.0 * math.atan2(float(q[0]), float(q[3])))
    return float(LID_OPEN - turned)
