"""Geometry and measurements for taking the head off a cream whipper that is still under gas pressure.

A kitchen counter. A 0.5 L stainless cream whipper stands upright: bottle, screw-on head with its dispensing lever,
decorator tip and a charger holder with a charger still screwed on. A mixing bowl stands under the tip, a dish drainer
at the left, a carton of cream chargers, a dessert plate and a whisk at the back.

The bottle is a free body. The head turns on the bottle's axis (a revolute joint between the two, with the thread's
drag) and the lever is hinged on the head and sprung outward. Gas pressure is a rule on the measured lever travel and
time; see ``Whipper``.

Frame: metres, x away from the arm bases, y left, z up; TOP is the counter. Sizes are estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece

TOP = 0.7475
HZ = 20
ASSETS = Path(__file__).resolve().parent / "assets"
STEEL = (0.78, 0.79, 0.80)
BLACK = (0.05, 0.05, 0.05)
WHITE = (0.93, 0.93, 0.91)

# -- the whipper (whipper frame: origin at the centre of the bottle's base; lever toward -x, decorator tip toward +x,
# -- charger holder toward -y) ---------------------------------------------------------------------------------------
W = (0.300, -0.030)                  # where it stands
BOTTLE_R, BOTTLE_H = 0.039, 0.156    # bottle body: 78 mm across, 156 mm to the shoulder
NECK_R, NECK_Z = 0.0285, (0.157, 0.178)   # threaded neck
BOTTLE_MASS = 0.45                   # steel bottle (about 0.40 kg) and the little cream left in it
COLLAR_R, COLLAR_IN, COLLAR_Z = 0.040, 0.0335, (0.157, 0.191)   # the head's ribbed grip ring: 80 mm across, 34 mm tall
BODY_R, BODY_Z = 0.033, (0.191, 0.249)                         # the head's valve body above the ring
HEAD_MASS = 0.30                     # head with decorator tip, charger holder and the spent charger in it
HEAD_ZC = (BODY_Z[0] + BODY_Z[1]) / 2
SEAT = (0.0, 0.0, HEAD_ZC - BOTTLE_H / 2)   # the head's origin in the bottle's frame while it is screwed on
NOZZLE_TIP = (0.077, 0.0, 0.214)     # the decorator tip's end
HOLDER_END = (0.0, -0.087, 0.254)    # the charger holder's end
LEVER_PIVOT = (-0.028, 0.0, 0.242)   # the lever's pin
LEVER_TIP = (-0.050, 0.0, 0.196)     # the lever's free end at rest
LEVER_L = math.hypot(LEVER_TIP[0] - LEVER_PIVOT[0], LEVER_TIP[2] - LEVER_PIVOT[2])   # 51 mm
LEVER_MASS = 0.03
LEVER_FULL_DEG = 11.0                # the lever's travel to its stop: about 10 mm at its end
LEVER_OPEN_DEG = 6.0                 # from here the valve is open: about 5 mm at its end
LEVER_K = 0.027                      # N m per degree
LEVER_PRELOAD_DEG = 6.0              # the spring is wound this far at rest: 3 N at the lever's end at rest, 6 N at the opening point, 9 N on the stop
LEVER_DAMP = 0.0004                  # N m s per degree
THREAD_DAMP = 0.021                  # N m s per degree: the thread's and gasket's drag (1.2 N m s per radian)
SEAL_K = 0.05                        # N m per degree: the tightened head's gasket holds it like a spring ...
SEAL_BREAK_DEG = 8.0                 # ... until it has been turned this far either way (0.4 N m); then it lets go for good

# -- the rule's numbers ----------------------------------------------------------------------------------------------
VENT_S = 6.0                         # seconds the valve must be open, in all, for the gas to be gone (assumed; see README)
UNSCREW_DEG = 540.0                  # the head comes free after one and a half turns anticlockwise seen from above (assumed)
LOOSE_DEG = 20.0                     # turned this far (net, anticlockwise) the head's gasket no longer seals (assumed)
TIPPED_DEG = 45.0                    # reported only: the charged whipper lying over further than this with no gripper on it
OFF_COUNTER = 0.05                   # a part this far below the counter top has fallen off it
HEAD_OFF = 0.030                     # the head is off when it is this far from where it sits on the bottle
CLEAR = 0.030                        # grippers this far from both parts
REST_Z = 0.015                       # a part rests in the drainer when its lowest point is within this of the drainer's floor

# -- fixed things ----------------------------------------------------------------------------------------------------
BOWL_C, BOWL_R, BOWL_H = (0.465, -0.030), 0.103, 0.092
RACK_X, RACK_Y, RACK_H = (0.170, 0.430), (0.130, 0.430), 0.024       # dish drainer, outside
RACK_WALL, RACK_FLOOR = 0.006, 0.006
TUMBLER = (0.385, 0.385, 0.036, 0.096)                                # x, y, radius, height
BOX_X, BOX_Y, BOX_H = (0.559, 0.611), (-0.306, -0.194), 0.074
PLATE_C, PLATE_R, PLATE_H = (0.585, 0.330), 0.075, 0.012
WHISK_X, WHISK_Y, WHISK_H = (0.574, 0.626), (0.094, 0.252), 0.052


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _box(x, y, z, origin, color):
    """A hidden box collider spanning x, y, z (each a (low, high) pair, z above the counter), relative to ``origin``."""
    return Piece("box", (x[1] - x[0], y[1] - y[0], z[1] - z[0]),
                 ((x[0] + x[1]) / 2 - origin[0], (y[0] + y[1]) / 2 - origin[1], (z[0] + z[1]) / 2 - origin[2]), color=color)


def _staves(r, thick, z0, z1, zc, n, color, phase=0.0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        out.append(Piece("box", (thick, 2 * math.pi * r / n + 0.003, z1 - z0),
                         (r * math.cos(a), r * math.sin(a), (z0 + z1) / 2 - zc), rot=(0.0, 0.0, a), color=color))
    return out


def counter_object() -> Part:
    """Everything fixed on the counter: mixing bowl, dish drainer with a tumbler in its far corner, carton of
    chargers, dessert plate, whisk. Colliders (hidden): the bowl as a ring of staves, the drainer as a floor and four rims, boxes."""
    deep = 0.040
    c = ((RACK_X[0] + RACK_X[1]) / 2, (RACK_Y[0] + RACK_Y[1]) / 2, (RACK_FLOOR - deep) / 2)
    w = RACK_WALL
    pieces = [
        _box((RACK_X[0], RACK_X[0] + w), RACK_Y, (0.0, RACK_H), c, WHITE),
        _box((RACK_X[1] - w, RACK_X[1]), RACK_Y, (0.0, RACK_H), c, WHITE),
        _box(RACK_X, (RACK_Y[0], RACK_Y[0] + w), (0.0, RACK_H), c, WHITE),
        _box(RACK_X, (RACK_Y[1] - w, RACK_Y[1]), (0.0, RACK_H), c, WHITE),
        Piece("cylinder", (TUMBLER[2], TUMBLER[3], TUMBLER[2]), (TUMBLER[0] - c[0], TUMBLER[1] - c[1], TUMBLER[3] / 2 - c[2]), color=WHITE),
        _box(BOX_X, BOX_Y, (0.0, BOX_H), c, WHITE),
        Piece("cylinder", (PLATE_R, PLATE_H, PLATE_R), (PLATE_C[0] - c[0], PLATE_C[1] - c[1], PLATE_H / 2 - c[2]), color=WHITE),
        _box(WHISK_X, WHISK_Y, (0.0, WHISK_H), c, WHITE),
        Piece("cylinder", (0.046, 0.004, 0.046), (BOWL_C[0] - c[0], BOWL_C[1] - c[1], 0.002 - c[2]), color=STEEL),
    ]
    for i in range(16):                                   # the bowl's wall, leaning outward
        a = 2 * math.pi * i / 16
        r = 0.075
        pieces.append(Piece("box", (0.004, 2 * math.pi * r / 16 + 0.012, 0.105),
                            (BOWL_C[0] + r * math.cos(a) - c[0], BOWL_C[1] + r * math.sin(a) - c[1], 0.046 - c[2]),
                            rot=(0.0, math.radians(32.0), a), color=STEEL))
    return Part("counter", pos=(c[0], c[1], TOP + c[2]), size=(RACK_X[1] - RACK_X[0], RACK_Y[1] - RACK_Y[0], RACK_FLOOR + deep), exact_z=True,
                color=WHITE, friction=(0.6, 0.5), pieces=tuple(pieces), **_vis("counter_set", (-c[0], -c[1], -c[2])))


def bottle_pos():
    return (W[0], W[1], TOP + BOTTLE_H / 2)


def head_pos():
    return (W[0], W[1], TOP + HEAD_ZC)


def bottle_object() -> Part:
    """The bottle: a free body standing on the counter. Colliders (hidden): body and neck as cylinders."""
    zc = BOTTLE_H / 2
    neck = Piece("cylinder", (NECK_R, NECK_Z[1] - NECK_Z[0], NECK_R), (0.0, 0.0, (NECK_Z[0] + NECK_Z[1]) / 2 - zc), color=STEEL)
    return Part("whipper_bottle", pos=bottle_pos(), size=(BOTTLE_R, BOTTLE_H, BOTTLE_R), shape="cylinder", exact_z=True, mass=BOTTLE_MASS,
                color=STEEL, friction=(1.2, 1.0), pieces=(neck,), contact_offset=0.002, **_vis(("whipper_bottle", "burst"), (0.0, 0.0, -zc)))


def head_object() -> Part:
    """The head: a free body screwed on the bottle: a revolute joint on the bottle's axis with the thread's drag, which
    the task switches off when the head has been turned free. Colliders (hidden): valve body as a cylinder, grip ring
    as a ring of staves round the neck, decorator tip and charger holder as cylinders."""
    zc = HEAD_ZC
    pieces = _staves((COLLAR_R + COLLAR_IN) / 2, COLLAR_R - COLLAR_IN, COLLAR_Z[0], COLLAR_Z[1], zc, 36, BLACK)
    pieces.append(Piece("cylinder", (0.009, 0.050, 0.009), (0.0525, 0.0, 0.2188 - zc), rot=(0.0, math.radians(102.0), 0.0), color=WHITE))
    pieces.append(Piece("cylinder", (0.0115, 0.074, 0.0115), (0.0, -0.0563, 0.2332 - zc), rot=(math.radians(55.0), 0.0, 0.0), color=STEEL))
    pivot = (W[0], W[1], TOP + COLLAR_Z[0])
    hinge = Hinge(pivot=pivot, axis="Z", damping=THREAD_DAMP, lower_deg=-1e6, upper_deg=1e6, stiffness=SEAL_K, target_deg=0.0, parent="whipper_bottle", parent_pos=bottle_pos())
    return Part("whipper_head", pos=head_pos(), size=(BODY_R, BODY_Z[1] - BODY_Z[0], BODY_R), shape="cylinder", exact_z=True, mass=HEAD_MASS,
                color=STEEL, friction=(1.2, 1.0), pieces=tuple(pieces), hinge=hinge, contact_offset=0.002,
                **_vis(("whipper_head", "jet", "lamp_on", "lamp_off"), (0.0, 0.0, -zc)))


def lever_object() -> Part:
    """The dispensing lever: a light body hinged on the head (pin along y), sprung outward against its rest stop.
    Colliders (hidden): the bar and its end pad as boxes."""
    d = np.array([LEVER_TIP[0] - LEVER_PIVOT[0], 0.0, LEVER_TIP[2] - LEVER_PIVOT[2]]) / LEVER_L
    beta = math.atan2(-d[2], d[0])
    bar = Piece("box", (LEVER_L, 0.015, 0.0045), tuple(float(v) for v in d * LEVER_L / 2), rot=(0.0, beta, 0.0), color=STEEL)
    pad = Piece("box", (0.020, 0.019, 0.0055), tuple(float(v) for v in d * (LEVER_L - 0.006)), rot=(0.0, beta, 0.0), color=STEEL)
    pos = (W[0] + LEVER_PIVOT[0], W[1], TOP + LEVER_PIVOT[2])
    hinge = Hinge(pivot=pos, axis="Y", damping=LEVER_DAMP, lower_deg=-LEVER_FULL_DEG, upper_deg=0.0, stiffness=LEVER_K,
                  target_deg=LEVER_PRELOAD_DEG, parent="whipper_head", parent_pos=head_pos())
    return Part("whipper_lever", pos=pos, size=(0.004, 0.004, 0.004), shape="sphere", exact_z=True, mass=LEVER_MASS, color=STEEL,
                friction=(1.0, 0.8), pieces=(bar, pad), hinge=hinge, contact_offset=0.001, **_vis("whipper_lever", (0.0, 0.0, 0.0)))


# -- measurements ----------------------------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def frame(pose):
    pose = np.asarray(pose, float)
    return pose[:3], quat_matrix(pose[3:7])


def tilt_deg(pose) -> float:
    """Degrees between a part's axis and straight up."""
    _, r = frame(pose)
    return math.degrees(math.acos(max(-1.0, min(1.0, float(r[2, 2])))))


def lever_deg(lever, head) -> float:
    """How far the lever is pushed in from its rest stop, in degrees about its pin."""
    _, rh = frame(head)
    _, rl = frame(lever)
    rel = rh.T @ rl
    return max(0.0, -math.degrees(math.atan2(rel[0, 2], rel[2, 2])))


def head_yaw_deg(head, bottle) -> float:
    """The head's angle about the bottle's axis relative to the bottle, -180 to 180 (anticlockwise from above is positive)."""
    _, rh = frame(head)
    _, rb = frame(bottle)
    rel = rb.T @ rh
    return math.degrees(math.atan2(rel[1, 0], rel[0, 0]))


def head_gap(head, bottle) -> float:
    """How far the head is from where it sits when screwed on the bottle (m)."""
    ph, _ = frame(head)
    pb, rb = frame(bottle)
    return float(np.linalg.norm(ph - (pb + rb @ np.asarray(SEAT))))


def bottle_points(bottle):
    """The bottle's outline: eight points round its base and eight round its shoulder."""
    p, r = frame(bottle)
    out = []
    for z in (-BOTTLE_H / 2, BOTTLE_H / 2):
        for i in range(8):
            a = math.pi * i / 4
            out.append(p + r @ np.array([BOTTLE_R * math.cos(a), BOTTLE_R * math.sin(a), z]))
    return out


def head_points(head):
    """The head's outline: eight points round the grip ring's lower edge, the top of the valve body, the decorator
    tip's end, the charger holder's end and the lever's end."""
    p, r = frame(head)
    out = [p + r @ np.array([COLLAR_R * math.cos(math.pi * i / 4), COLLAR_R * math.sin(math.pi * i / 4), COLLAR_Z[0] - HEAD_ZC]) for i in range(8)]
    for q in ((0.0, 0.0, BODY_Z[1]), NOZZLE_TIP, HOLDER_END, LEVER_TIP):
        out.append(p + r @ np.array([q[0], q[1], q[2] - HEAD_ZC]))
    return out


def in_rack(points) -> bool:
    """Every point is over the drainer's floor, inside its rims, and the lowest is down on the floor."""
    w = RACK_WALL
    over = all(RACK_X[0] + w <= q[0] <= RACK_X[1] - w and RACK_Y[0] + w <= q[1] <= RACK_Y[1] - w for q in points)
    low = min(float(q[2]) for q in points)
    return bool(over and TOP <= low <= TOP + RACK_FLOOR + REST_Z)


def off_counter(pose) -> bool:
    return bool(float(np.asarray(pose, float)[2]) < TOP - OFF_COUNTER)


def bottle_gap(point, bottle) -> float:
    """Distance from a point to the bottle's surface (body and neck as one cylinder)."""
    p, r = frame(bottle)
    loc = r.T @ (np.asarray(point, float)[:3] - p)
    top = NECK_Z[1] - BOTTLE_H / 2
    dz = max(-BOTTLE_H / 2 - loc[2], loc[2] - top, 0.0)
    dr = max(math.hypot(loc[0], loc[1]) - BOTTLE_R, 0.0)
    return math.hypot(dr, dz)


def head_gap_point(point, head) -> float:
    """Distance from a point to the head's surface (grip ring and valve body as one 80 mm cylinder; the tip, holder
    and lever as their end points)."""
    p, r = frame(head)
    loc = r.T @ (np.asarray(point, float)[:3] - p)
    dz = max(COLLAR_Z[0] - HEAD_ZC - loc[2], loc[2] - (BODY_Z[1] - HEAD_ZC), 0.0)
    dr = max(math.hypot(loc[0], loc[1]) - COLLAR_R, 0.0)
    d = math.hypot(dr, dz)
    for q in (NOZZLE_TIP, HOLDER_END, LEVER_TIP):
        d = min(d, float(np.linalg.norm(loc - np.array([q[0], q[1], q[2] - HEAD_ZC]))))
    return d


class Whipper:
    """The whipper's state, from measured poses only. One instance per reader (the scene's rule and the scorer each
    keep their own), stepped once per control step.

    Pressure: starts at 1 (charged). While the lever is pushed in at least LEVER_OPEN_DEG with the head still on, it
    falls at 1 / VENT_S per second; at 0 the gas is gone.
    Turn: the head's net anticlockwise turn on the bottle, in degrees (turning back is subtracted), while the head is
    on. Up to SEAL_BREAK_DEG the gasket holds it back like a spring (SEAL_K); turned that far it lets go for good. At
    UNSCREW_DEG the thread lets go (``free``) and the head lifts off.
    Sprayed (latched): the head turned LOOSE_DEG or more while pressure remained: gas and cream spray past the gasket.
    Thrown (latched): the head came free of its thread while pressure remained.
    Fell (latched): the bottle or the head fell off the counter.
    """

    def __init__(self):
        self.pressure = 1.0
        self.turn = 0.0
        self.last_yaw = None
        self.free = False
        self.seal_broken = False
        self.sprayed = False
        self.thrown = False
        self.fell = False
        self.venting = False
        self.open_s = 0.0

    def step(self, bottle, head, lever, dt=1.0 / HZ):
        on = not self.free
        travel = lever_deg(lever, head)
        if on:
            yaw = head_yaw_deg(head, bottle)
            if self.last_yaw is not None:
                d = (yaw - self.last_yaw + 180.0) % 360.0 - 180.0
                self.turn += d
            self.last_yaw = yaw
        self.venting = bool(on and self.pressure > 0.0 and travel >= LEVER_OPEN_DEG)
        if self.venting:
            self.open_s += dt
            self.pressure = max(0.0, 1.0 - self.open_s / VENT_S)
            if self.pressure <= 1e-9:
                self.pressure = 0.0
        if on and abs(self.turn) >= SEAL_BREAK_DEG:
            self.seal_broken = True
        if on and self.turn >= LOOSE_DEG and self.pressure > 0.0:
            self.sprayed = True
        if on and self.turn >= UNSCREW_DEG:
            self.free = True
            if self.pressure > 0.0:
                self.thrown = True
        if off_counter(bottle) or off_counter(head):
            self.fell = True
        return travel
