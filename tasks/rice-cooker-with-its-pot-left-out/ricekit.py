"""Geometry and measurements for putting washed rice into a rice cooker whose inner pot was left out to dry.

A kitchen counter. A small electric rice cooker stands plugged in, its lid open and its cooking cavity empty: the
bare heating plate is in view. Its inner pot, washed, stands on a drying mat beside it. A measuring cup holds the
washed rice and its water. Rice and water are a stand-in set of beads.

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
WHITE = (0.95, 0.95, 0.93)
DARK = (0.16, 0.16, 0.17)
CLEAR = (0.85, 0.92, 0.95)
RICE = (0.96, 0.95, 0.90)
MAT = (0.55, 0.62, 0.68)

# -- rice cooker (250 x 220 x 165 mm body, lid open behind). Its cooking cavity is 150 mm across; COOK_C is its axis --
COOK_C = (0.450, 0.040)
CAV_R = 0.075
CAV_COLLIDER_R = 0.079             # the collider's bore: 4 mm more, so a pot let down slightly off-centre still goes in
MOUTH_CHAMFER = 0.014              # the collider's mouth has a 45-degree lead-in this wide: it stands for the 14 mm rounded corner of the real pot's base, which the pot's collider (a plain cylinder) lacks
DECK_Z = 0.165                       # the top of the body round the cavity mouth, above the counter
PLATE_Z = 0.085                      # where the inner pot's base rests (the heating plate and its sprung sensor)
BODY_X = (-0.105, 0.145)             # the body's footprint about the cavity axis, along x
BODY_HALF_Y = 0.110

# -- inner pot (144 mm across, 85 mm tall, 2 mm wall, about 180 g), washed, on a drying mat ----------------------
POT_R, POT_H, POT_FLOOR, POT_WALL = 0.072, 0.085, 0.004, 0.003
POT_MASS = 0.18
MAT_C = (0.245, -0.130)
MAT_SIZE = (0.200, 0.240, 0.007)
POT_C = (0.250, -0.120)
SEAT_XY = 0.008                      # the pot is seated when its axis is within this of the cavity's axis

# -- measuring cup with the washed rice and its water (87 mm tall, 60 to 80 mm across) ---------------------------
CUP_SCALE = 0.83
J_R, J_H, J_FLOOR, J_WALL = 0.0335, 0.087, 0.005, 0.003
J_MASS = 0.20
J_LEAN = math.radians(6.9)
JUG_C = (0.450, -0.250)
N_BEADS = 28
BEAD_R = 0.004
BEAD_MASS = 0.0005

# -- power strip (62 x 300 x 40 mm) the cooker is plugged into, lying along y behind the cup; fixed -------------
STRIP_C = (0.660, -0.160)
STRIP = (0.062, 0.300, 0.040)


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _staves(r, thick, z0, z1, zc, n, color, lean=0.0, phase=0.0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        out.append(Piece("box", (thick, 2 * math.pi * r / n + 0.004, z1 - z0),
                         (r * math.cos(a), r * math.sin(a), (z0 + z1) / 2 - zc), rot=(0.0, lean, a), color=color))
    return out


def cooker_object() -> Part:
    """The cooker: fixed. Colliders (hidden): the heating plate as a plug up to where the pot rests, the body round the
    cavity as a ring of blocks, the back of the body and the open lid as boxes."""
    zc = PLATE_Z / 2
    thick = 0.030
    c = MOUTH_CHAMFER
    pieces = _staves(CAV_COLLIDER_R + c / 2, c, PLATE_Z - 0.002, DECK_Z - c, zc, 16, WHITE)
    pieces += _staves(CAV_COLLIDER_R + c + (thick - c) / 2, thick - c, PLATE_Z - 0.002, DECK_Z, zc, 16, WHITE)
    face = 0.012                                          # the lead-in: a ring of sloping faces from the bore out to the deck
    r_face = CAV_COLLIDER_R + c / 2 + face / 2 * math.cos(math.pi / 4)
    z_face = DECK_Z - c / 2 - face / 2 * math.sin(math.pi / 4)
    half = c * math.sqrt(2.0) / 2
    pieces += _staves(r_face, face, z_face - half, z_face + half, zc, 16, WHITE, lean=math.pi / 4)
    back = BODY_X[1] - 0.095
    pieces.append(Piece("box", (back, 2 * BODY_HALF_Y, DECK_Z), (0.095 + back / 2, 0.0, DECK_Z / 2 - zc), color=WHITE))
    pieces.append(Piece("box", (0.045, 0.210, 0.210), (0.166, 0.0, DECK_Z + 0.103 - zc), rot=(0.0, math.radians(10.0), 0.0), color=WHITE))
    kw = _vis("rice_cooker", (0.0, 0.0, -zc), visual_hide=("cord",))
    return Part("rice_cooker", pos=(COOK_C[0], COOK_C[1], TOP + zc), size=(CAV_R - 0.001, PLATE_Z, CAV_R - 0.001), shape="cylinder",
                exact_z=True, color=WHITE, friction=(0.3, 0.25), pieces=tuple(pieces), **kw)


def mat_object() -> Part:
    kw = _vis("drying_mat", (0.0, 0.0, -MAT_SIZE[2] / 2), visual_rpy_deg=(0.0, 0.0, 90.0))
    return Part("drying_mat", pos=(MAT_C[0], MAT_C[1], TOP + MAT_SIZE[2] / 2), size=MAT_SIZE, exact_z=True, color=MAT,
                friction=(0.9, 0.8), **kw)


def strip_object() -> Part:
    """The power strip with the cooker's plug in it and the cooker's cord: fixed. Colliders (hidden): the strip and the
    plug as boxes; the cords are drawn only."""
    zc = STRIP[2] / 2
    pieces = (Piece("box", (0.038, 0.038, 0.022), (0.006, 0.015, zc + 0.011), color=WHITE),)
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=WHITE,
                friction=(0.5, 0.4), pieces=pieces, **_vis("power_set", (0.0, 0.0, -zc)))


def pot_object() -> Part:
    """The inner pot: a free rigid body, hollow (a floor and a ring of staves)."""
    zc = POT_FLOOR / 2
    r = POT_R - POT_WALL / 2
    pieces = _staves(r, POT_WALL, POT_FLOOR, POT_H, zc, 24, DARK)
    kw = _vis("inner_pot", (0.0, 0.0, -zc))
    return Part("inner_pot", pos=(POT_C[0], POT_C[1], TOP + MAT_SIZE[2] + zc), size=(POT_R - 0.002, POT_FLOOR, POT_R - 0.002),
                shape="cylinder", exact_z=True, mass=POT_MASS, color=DARK, friction=(1.2, 1.0), pieces=tuple(pieces),
                contact_offset=0.002, com=(0.0, 0.0, 0.030 - zc), **kw)


def jug_object() -> Part:
    """The measuring cup: a free rigid body, hollow (a ring of staves), so the beads can be poured out of it."""
    zc = J_FLOOR / 2
    pieces = _staves(J_R, J_WALL, J_FLOOR, J_H, zc, 12, CLEAR, lean=J_LEAN, phase=math.pi / 12)
    return Part("jug", pos=(JUG_C[0], JUG_C[1], TOP + zc), size=(J_R - 0.002, J_FLOOR, J_R - 0.002), shape="cylinder",
                exact_z=True, mass=J_MASS, color=CLEAR, friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.002,
                com=(0.0, 0.0, 0.045 - zc), yaw=math.pi,
                **_vis("measuring_cup", (0.0, 0.0, -zc), visual_hide=("vinegar",), visual_glass_opacity=0.25, visual_scale=CUP_SCALE))


def bead_positions():
    out = []
    for i in range(N_BEADS):
        layer, k = divmod(i, 7)
        if k == 0:
            dx = dy = 0.0
        else:
            a = math.pi / 3 * k + (math.pi / 6 if layer % 2 else 0.0)
            dx, dy = 0.0185 * math.cos(a), 0.0185 * math.sin(a)
        out.append((JUG_C[0] + dx, JUG_C[1] + dy, TOP + J_FLOOR + BEAD_R + 0.001 + 0.0085 * layer))
    return out


def bead_objects() -> list[Part]:
    return [Part(f"rice{i + 1}", pos=p, size=(BEAD_R, BEAD_R, BEAD_R), shape="sphere", exact_z=True, mass=BEAD_MASS,
                 color=RICE, friction=(0.05, 0.03), restitution=0.05, contact_offset=0.001, max_depenetration=0.5)
            for i, p in enumerate(bead_positions())]


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def in_jug(jug, p) -> bool:
    jug = np.asarray(jug, float)
    q = quat_matrix(jug[3:7]).T @ (np.asarray(p, float)[:3] - jug[:3])
    return bool(math.hypot(q[0], q[1]) <= J_R + 0.004 and -0.004 <= q[2] <= J_H)


def in_pot(pot, p) -> bool:
    """A bead in the inner pot: inside its wall, between its floor and 2 cm above its rim."""
    pot = np.asarray(pot, float)
    q = quat_matrix(pot[3:7]).T @ (np.asarray(p, float)[:3] - pot[:3])
    return bool(math.hypot(q[0], q[1]) <= POT_R and -0.004 <= q[2] <= POT_H + 0.020)


def pot_seated(pot) -> bool:
    """The inner pot is in the cooker: its axis on the cavity's axis, upright, its base down on the heating plate."""
    pot = np.asarray(pot, float)
    return bool(math.hypot(pot[0] - COOK_C[0], pot[1] - COOK_C[1]) <= SEAT_XY and tilt_deg(pot) < 5.0
                and pot[2] <= TOP + PLATE_Z + POT_FLOOR / 2 + 0.006)


def in_cooker_body(p) -> bool:
    """A point inside the cooker's body: within the cavity's outline and below its deck."""
    p = np.asarray(p, float)
    return bool(math.hypot(p[0] - COOK_C[0], p[1] - COOK_C[1]) <= CAV_R + 0.004 and p[2] < TOP + DECK_Z)


def strip_distance(p) -> float:
    """Horizontal distance from a point to the power strip's outline (m); 0 over the strip."""
    dx = max(abs(float(p[0]) - STRIP_C[0]) - STRIP[0] / 2, 0.0)
    dy = max(abs(float(p[1]) - STRIP_C[1]) - STRIP[1] / 2, 0.0)
    return math.hypot(dx, dy)


def on_cooker(p) -> bool:
    """A point resting on the cooker's top outside the cavity (its deck)."""
    p = np.asarray(p, float)
    return bool(BODY_X[0] <= p[0] - COOK_C[0] <= BODY_X[1] and abs(p[1] - COOK_C[1]) <= BODY_HALF_Y
                and TOP + DECK_Z - 0.002 <= p[2] <= TOP + DECK_Z + 0.03 and not in_cooker_body(p))
