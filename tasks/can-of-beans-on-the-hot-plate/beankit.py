"""Geometry and measurements for heating a can of baked beans on a counter-top hot plate.

A kitchen counter. A single electric hot plate stands switched off, plugged into a power strip, its control console
facing the robot's right, a 16 cm steel saucepan standing empty on it. In front of it stands an unopened steel can of
baked beans with an easy-open lid, its ring-pull lifted. A bowl and a spoon lie at the back right. The beans are a
stand-in set of beads.

The can is a free body. Its lid is hinged on the can's rim at the side away from the ring-pull and held shut like a
spring until it has been torn open; see ``Stove``. The hot plate's switch is a sprung cap.

Frame: metres, x away from the arm bases, y left, z up; TOP is the counter. Sizes are from the CAD models, themselves
estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Hinge, Part, Piece, Spring

TOP = 0.7475
HZ = 20
ASSETS = Path(__file__).resolve().parent / "assets"
HOUSING = (0.34, 0.40, 0.50)
WHITE = (0.95, 0.95, 0.93)
STEEL = (0.78, 0.79, 0.80)
BEAN = (0.78, 0.34, 0.10)

HP_C = (0.400, 0.130)
PLATE_HALF = 0.090                   # the glass-ceramic top plate is 180 x 180 mm
PLATE_Z = 0.104                      # its top above the counter
PLATE_THICK = 0.009
HOUSING_HALF_X = 0.098               # housing: 196 mm wide (x)
HOUSING_Y = (-0.096, 0.098)          # the part of the housing under the plate, along y about HP_C
HOUSING_Z = 0.082
CONSOLE_Y = (-0.188, -0.096)         # the console: its face slopes from 36 mm at the front edge up to 82 mm
CONSOLE_Z = (0.036, 0.082)
SLOPE = math.atan2(CONSOLE_Z[1] - CONSOLE_Z[0], CONSOLE_Y[1] - CONSOLE_Y[0])
# the HEAT switch: a cap 24 x 16 mm on the console, 5 mm proud of it; pressed 2.5 mm straight down
SW_LOCAL = (-0.062, -0.1537, 0.0593)   # the centre of the cap's top, about HP_C and above the counter
SW_SIZE = (0.024, 0.016, 0.005)
SW_XY = (HP_C[0] + SW_LOCAL[0], HP_C[1] + SW_LOCAL[1])
SW_Z = SW_LOCAL[2] - SW_SIZE[2] / 2    # the cap's centre above the counter
SW_TRAVEL, SW_K, SW_ON = 0.0025, 600.0, 0.0015
LAMP_LOCAL = (-0.062, -0.1162, 0.0764)

# -- power strip (62 x 300 x 40 mm) the hot plate is plugged into, lying along y beyond the hot plate; fixed scenery -
STRIP_C = (0.600, 0.000)
STRIP = (0.062, 0.300, 0.040)

# -- saucepan, 16 cm: steel, 160 mm across, 75 mm tall, a 150 mm handle pointing left (+y). It stands on the plate ---
PAN_C = HP_C
PAN_R, PAN_H, PAN_FLOOR, PAN_WALL = 0.080, 0.075, 0.004, 0.003
PAN_R_IN = PAN_R - PAN_WALL
PAN_MASS = 0.50
HANDLE = (0.024, 0.150, 0.012)       # the handle's size; its middle is 175 mm from the pan's axis, 64 mm above its base
HANDLE_Y, HANDLE_Z = 0.175, 0.064

# -- the can: 73 mm across, 110 mm tall; lid 3.5 mm below the rim; ring-pull at the far side (+x), hinge at the near --
CAN_C = (0.250, -0.160)
CAN_R, CAN_H, CAN_FLOOR, CAN_WALL = 0.0365, 0.110, 0.004, 0.002
CAN_MASS = 0.25                      # the steel can and its sauce; with the lid and the 16 beads 0.29 kg (a real full can: about 0.45 kg)
LID_R, LID_T = 0.0340, 0.002
LID_Z = 0.1065                       # the lid's underside above the can's base
LID_MASS = 0.012
HINGE_X = -0.0345                    # the lid's hinge line in the can's frame: on the rim, at the side toward the arms
RING_X, RING_Z = 0.024, 0.0178       # the lifted ring-pull's middle: from the can's axis, and above the lid's underside
RING = (0.004, 0.022, 0.026)         # the lifted ring-pull as a collider: thin along x, 22 mm wide, 26 mm tall
SEAL_K = 0.015                       # N m per degree: the unbroken score line holds the lid shut like a spring ...
TEAR_DEG = 12.0                      # ... until the lid has been lifted this far (0.18 N m: about 3 N at the ring); then it is torn for good
HOLD_K = 0.004                       # N m per degree: the torn lid's bent metal holds it at the widest angle it has reached
LID_DAMP = 0.0005                    # N m s per degree
LID_MAX_DEG = 115.0
LID_OPEN_DEG = 70.0                  # the lid counts as open from here
N_BEADS = 16
BEAD_R = 0.006
BEAD_MASS = 0.002
ENOUGH = 13                          # 80 % of the beads, rounded up

# -- the rule's numbers ----------------------------------------------------------------------------------------------
ZONE_EDGE = 0.020                    # the heated zone reaches this far outside the plate's 180 x 180 mm outline ...
ZONE_UP = 0.150                      # ... and from the plate's top surface to this far above it
PAN_ON_Z = 0.010                     # the pan stands on the plate when its base is within this of the plate's top
UPRIGHT_DEG = 15.0
STAND_Z = 0.010                      # the can stands on the counter when its lowest point is within this of the counter
OFF_COUNTER = 0.05                   # a thing this far below the counter top has fallen off it
CLEAR = 0.030                        # grippers this far from the can, the pan and the switch

# -- fixed props at the back right: a white bowl and a spoon ---------------------------------------------------------
BOWL_C, BOWL_R, BOWL_H = (0.540, -0.280), 0.070, 0.060
SPOON_X, SPOON_Y, SPOON_H = (0.383, 0.560), (-0.389, -0.355), 0.006


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


def hot_plate_object() -> Part:
    """The hot plate: fixed. Colliders (hidden): the housing under the plate (the root), the riser and the top plate as
    boxes, the console as a low block with a sloping slab on it; under the HEAT switch the block is flat and lower, so
    the switch has room to travel. Drawn by the task, never touched by physics: its lamps and read-out lit or unlit and its
    round heating zone glowing or dark."""
    zc = HOUSING_Z / 2
    yc = (HOUSING_Y[0] + HOUSING_Y[1]) / 2
    cy = (CONSOLE_Y[0] + CONSOLE_Y[1]) / 2
    face = math.hypot(CONSOLE_Y[1] - CONSOLE_Y[0], CONSOLE_Z[1] - CONSOLE_Z[0])
    thick = 0.030
    n = (0.0, -math.sin(SLOPE), math.cos(SLOPE))
    mid_z = (CONSOLE_Z[0] + CONSOLE_Z[1]) / 2
    x0 = SW_LOCAL[0] + SW_SIZE[0] / 2 + 0.010          # the sloping slab starts this far along x, clear of the switch
    pieces = (
        Piece("box", (0.146, 0.146, PLATE_Z - PLATE_THICK - HOUSING_Z), (0.0, -yc, (HOUSING_Z + PLATE_Z - PLATE_THICK) / 2 - zc), color=HOUSING),
        Piece("box", (2 * PLATE_HALF, 2 * PLATE_HALF, PLATE_THICK), (0.0, -yc, PLATE_Z - PLATE_THICK / 2 - zc), color=WHITE),
        Piece("box", (2 * HOUSING_HALF_X, CONSOLE_Y[1] - CONSOLE_Y[0], CONSOLE_Z[0]), (0.0, cy - yc, CONSOLE_Z[0] / 2 - zc), color=HOUSING),
        Piece("box", (HOUSING_HALF_X - x0, face, thick),
              ((x0 + HOUSING_HALF_X) / 2, cy - yc - n[1] * thick / 2, mid_z - n[2] * thick / 2 - zc), rot=(SLOPE, 0.0, 0.0), color=HOUSING),
        Piece("box", (x0 + HOUSING_HALF_X, CONSOLE_Y[1] - CONSOLE_Y[0], 0.014), ((x0 - HOUSING_HALF_X) / 2, cy - yc, CONSOLE_Z[0] + 0.007 - zc), color=HOUSING),
    )
    kw = _vis(("hot_plate", "hot_plate_labels", "heat_lamp_on", "heat_lamp_off", "zone_on", "zone_off"), (0.0, -yc, -zc),
              visual_hide=("lamp", "switch_cap", "cord"))
    return Part("hot_plate", pos=(HP_C[0], HP_C[1] + yc, TOP + zc), size=(2 * HOUSING_HALF_X, HOUSING_Y[1] - HOUSING_Y[0], HOUSING_Z),
                exact_z=True, color=HOUSING, friction=(0.8, 0.7), pieces=pieces, **kw)


def switch_object() -> Part:
    """The HEAT switch: a sprung cap that is pushed straight down."""
    spring = Spring(axis="Z", lower=-SW_TRAVEL, upper=0.0, stiffness=SW_K, damping=6.0, target=0.0)
    return Part("heat_switch", pos=(SW_XY[0], SW_XY[1], TOP + SW_Z), size=SW_SIZE, exact_z=True, mass=0.003,
                color=(0.8, 0.1, 0.06), friction=(0.8, 0.7), spring=spring, contact_offset=0.001,
                **_vis(("heat_cap_on", "heat_cap_off"), (-SW_LOCAL[0], -SW_LOCAL[1], -SW_Z)))


def strip_object() -> Part:
    """The power strip with the hot plate's plug in it, the hot plate's mains lead, and two other things plugged in:
    fixed scenery. Colliders (hidden): the strip and the three plugs as boxes; the leads are drawn only. Its switches
    are drawn lit."""
    zc = STRIP[2] / 2
    dark = (0.06, 0.06, 0.06)
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, -0.015, zc + 0.013), color=dark),
              Piece("box", (0.046, 0.046, 0.028), (0.006, 0.045, zc + 0.014), color=WHITE),
              Piece("box", (0.034, 0.044, 0.036), (0.006, -0.075, zc + 0.018), color=dark))
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=WHITE,
                friction=(0.5, 0.4), pieces=pieces,
                **_vis(("power_set", "strip_lamps_on", "strip_main_on", "hp_lead", "strip_clutter"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main", "cooker_cord")))



def props_object() -> Part:
    """A white bowl and a spoon at the back right: fixed. Colliders (hidden): a cylinder and a box."""
    zc = BOWL_H / 2
    spoon = Piece("box", (SPOON_X[1] - SPOON_X[0], SPOON_Y[1] - SPOON_Y[0], SPOON_H),
                  ((SPOON_X[0] + SPOON_X[1]) / 2 - BOWL_C[0], (SPOON_Y[0] + SPOON_Y[1]) / 2 - BOWL_C[1], SPOON_H / 2 - zc), color=STEEL)
    return Part("counter_props", pos=(BOWL_C[0], BOWL_C[1], TOP + zc), size=(BOWL_R, BOWL_H, BOWL_R), shape="cylinder", exact_z=True,
                color=WHITE, friction=(0.6, 0.5), pieces=(spoon,), **_vis("counter_props", (-BOWL_C[0], -BOWL_C[1], -zc)))


def pan_pos():
    return (PAN_C[0], PAN_C[1], TOP + PLATE_Z + PAN_FLOOR / 2)


def pan_object() -> Part:
    """The saucepan: a free rigid body standing on the hot plate, hollow (a floor and a ring of twenty staves), with its
    handle as a box."""
    zc = PAN_FLOOR / 2
    pieces = _staves(PAN_R - PAN_WALL / 2, PAN_WALL, PAN_FLOOR, PAN_H, zc, 20, STEEL)
    pieces.append(Piece("box", HANDLE, (0.0, HANDLE_Y, HANDLE_Z - zc), color=(0.05, 0.05, 0.05)))
    return Part("saucepan", pos=pan_pos(), size=(PAN_R - 0.008, PAN_FLOOR, PAN_R - 0.008), shape="cylinder", exact_z=True,
                mass=PAN_MASS, color=STEEL, friction=(0.8, 0.7), pieces=tuple(pieces), contact_offset=0.002,
                com=(0.0, 0.0, 0.025 - zc), **_vis("saucepan", (0.0, 0.0, -zc)))


def can_pos():
    return (CAN_C[0], CAN_C[1], TOP + CAN_FLOOR / 2)


def lid_pos():
    return (CAN_C[0], CAN_C[1], TOP + LID_Z + LID_T / 2)


def can_object() -> Part:
    """The can: a free rigid body, hollow (a floor and a ring of sixteen staves), so the beads can be poured out."""
    zc = CAN_FLOOR / 2
    pieces = _staves(CAN_R - CAN_WALL / 2, CAN_WALL, CAN_FLOOR, CAN_H, zc, 16, STEEL, phase=math.pi / 16)
    return Part("bean_can", pos=can_pos(), size=(CAN_R - 0.003, CAN_FLOOR, CAN_R - 0.003), shape="cylinder", exact_z=True,
                mass=CAN_MASS, color=STEEL, friction=(1.2, 1.0), pieces=tuple(pieces), contact_offset=0.002,
                com=(0.0, 0.0, 0.050 - zc), **_vis("bean_can", (0.0, 0.0, -zc)))


def lid_object() -> Part:
    """The easy-open lid: a light body hinged on the can's rim at the side toward the arms (the pin along y), held shut
    like a spring until it has been torn; the task then makes it stay where it is left. Colliders (hidden): the disc as
    a cylinder and the lifted ring-pull as a thin box."""
    ring = Piece("box", RING, (RING_X, 0.0, RING_Z - LID_T / 2), color=STEEL)
    pivot = (CAN_C[0] + HINGE_X, CAN_C[1], TOP + LID_Z + LID_T)
    hinge = Hinge(pivot=pivot, axis="Y", damping=LID_DAMP, lower_deg=-LID_MAX_DEG, upper_deg=0.0, stiffness=SEAL_K,
                  target_deg=0.0, parent="bean_can", parent_pos=can_pos())
    return Part("can_lid", pos=lid_pos(), size=(LID_R, LID_T, LID_R), shape="cylinder", exact_z=True, mass=LID_MASS, color=STEEL,
                friction=(1.2, 1.0), pieces=(ring,), hinge=hinge, contact_offset=0.001, **_vis("can_lid", (0.0, 0.0, -LID_T / 2)))


def bead_positions():
    out = []
    for i in range(N_BEADS):
        layer, k = divmod(i, 7)
        if k == 0:
            dx = dy = 0.0
        else:
            a = math.pi / 3 * k + (math.pi / 6 if layer % 2 else 0.0)
            dx, dy = 0.020 * math.cos(a), 0.020 * math.sin(a)
        out.append((CAN_C[0] + dx, CAN_C[1] + dy, TOP + CAN_FLOOR + BEAD_R + 0.001 + 0.013 * layer))
    return out


def bead_objects() -> list[Part]:
    return [Part(f"bean{i + 1}", pos=p, size=(BEAD_R, BEAD_R, BEAD_R), shape="sphere", exact_z=True, mass=BEAD_MASS,
                 color=BEAN, friction=(0.05, 0.03), restitution=0.05, contact_offset=0.001, max_depenetration=0.5)
            for i, p in enumerate(bead_positions())]


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
    """Degrees between a thing's axis and straight up."""
    _, r = frame(pose)
    return math.degrees(math.acos(max(-1.0, min(1.0, float(r[2, 2])))))


def switch_press(sw) -> float:
    """How far the hot plate's switch is pushed down (m)."""
    return float(TOP + SW_Z - np.asarray(sw, float)[2])


def lid_deg(lid, can) -> float:
    """How far the lid is lifted from shut, in degrees about its hinge, measured against the can."""
    _, rc = frame(can)
    _, rl = frame(lid)
    rel = rc.T @ rl
    return max(0.0, -math.degrees(math.atan2(rel[0, 2], rel[2, 2])))


def can_points(can):
    """The can's outline: eight points round its base and eight round its rim."""
    p, r = frame(can)
    out = []
    for z in (-CAN_FLOOR / 2, CAN_H - CAN_FLOOR / 2):
        for i in range(8):
            a = math.pi * i / 4
            out.append(p + r @ np.array([CAN_R * math.cos(a), CAN_R * math.sin(a), z]))
    return out


def in_zone(q) -> bool:
    """A point in the heated zone: over the plate's outline grown by ZONE_EDGE, from 5 mm below the plate's top (a
    measuring tolerance) to ZONE_UP above it."""
    half = PLATE_HALF + ZONE_EDGE
    return bool(abs(q[0] - HP_C[0]) <= half and abs(q[1] - HP_C[1]) <= half and TOP + PLATE_Z - 0.005 <= q[2] <= TOP + PLATE_Z + ZONE_UP)


def over_zone(q) -> bool:
    """A point over the heated zone's outline seen from above, at any height."""
    half = PLATE_HALF + ZONE_EDGE
    return bool(abs(q[0] - HP_C[0]) <= half and abs(q[1] - HP_C[1]) <= half)


def can_in_zone(can) -> bool:
    """Any point of the can's outline in the heated zone (on the plate, in or on the pan, held low over it)."""
    return any(in_zone(q) for q in can_points(can))


def can_stands_off(can) -> bool:
    """The can stands upright on the counter with its whole outline outside the heated zone's outline seen from above."""
    pts = can_points(can)
    low = min(float(q[2]) for q in pts)
    return bool(tilt_deg(can) <= UPRIGHT_DEG and TOP - 0.005 <= low <= TOP + STAND_Z and not any(over_zone(q) for q in pts))


def pan_on_plate(pan) -> bool:
    """The pan stands upright on the plate: eight points round its base inside the plate's outline, the base down on it."""
    p, r = frame(pan)
    pts = [p + r @ np.array([0.072 * math.cos(math.pi * i / 4), 0.072 * math.sin(math.pi * i / 4), -PAN_FLOOR / 2]) for i in range(8)]
    inside = all(abs(q[0] - HP_C[0]) <= PLATE_HALF and abs(q[1] - HP_C[1]) <= PLATE_HALF for q in pts)
    low = min(float(q[2]) for q in pts)
    return bool(inside and tilt_deg(pan) <= UPRIGHT_DEG and abs(low - (TOP + PLATE_Z)) <= PAN_ON_Z)


def in_pan(pan, q) -> bool:
    """A bead in the pan: inside its wall, between its floor and its rim."""
    p, r = frame(pan)
    loc = r.T @ (np.asarray(q, float)[:3] - p)
    return bool(math.hypot(loc[0], loc[1]) <= PAN_R_IN and -PAN_FLOOR / 2 <= loc[2] <= PAN_H - PAN_FLOOR / 2)


def off_counter(pose) -> bool:
    return bool(float(np.asarray(pose, float)[2]) < TOP - OFF_COUNTER)


def _cyl_gap(point, pose, radius, z0, z1) -> float:
    p, r = frame(pose)
    loc = r.T @ (np.asarray(point, float)[:3] - p)
    dz = max(z0 - loc[2], loc[2] - z1, 0.0)
    dr = max(math.hypot(loc[0], loc[1]) - radius, 0.0)
    return math.hypot(dr, dz)


def gripper_gap(tcp, can, pan, sw) -> float:
    """Distance from a gripper's grasp point to the nearest of: the can (as a cylinder up to its rim), the pan (as a
    cylinder, and its handle's far end and middle), the switch cap's centre."""
    d = _cyl_gap(tcp, can, CAN_R, -CAN_FLOOR / 2, CAN_H - CAN_FLOOR / 2)
    d = min(d, _cyl_gap(tcp, pan, PAN_R, -PAN_FLOOR / 2, PAN_H - PAN_FLOOR / 2))
    p, r = frame(pan)
    t = np.asarray(tcp, float)[:3]
    for y in (HANDLE_Y, HANDLE_Y + HANDLE[1] / 2):
        d = min(d, float(np.linalg.norm(t - (p + r @ np.array([0.0, y, HANDLE_Z - PAN_FLOOR / 2])))))
    return min(d, float(np.linalg.norm(t - np.asarray(sw, float)[:3])))


class Stove:
    """The scene's state, from measured poses only. One instance per reader (the scene's rule and the scorer each keep
    their own), stepped once per control step.

    Heat: the hot plate starts switched off and cold. Each time its switch is pushed down at least SW_ON and let up
    again to less than 0.4 of that, the heat toggles; it counts as switched from the moment it is pushed down.
    Torn (latched): the lid has been lifted TEAR_DEG or more from shut; the can is no longer sealed.
    Widest: the widest angle the lid has reached; once torn it stays there.
    Burst (latched): the heat is on while the can is still sealed (not torn) and any point of its outline is in the
    heated zone.
    Fell (latched): the can or the pan fell off the counter.
    """

    def __init__(self):
        self.on = False
        self.down = False
        self.presses = 0
        self.torn = False
        self.widest = 0.0
        self.burst = False
        self.fell = False

    def step(self, can, lid, pan, sw):
        press = switch_press(sw)
        if not self.down and press >= SW_ON:
            self.down = True
            self.on = not self.on
            self.presses += 1
        elif self.down and press < SW_ON * 0.4:
            self.down = False
        open_deg = lid_deg(lid, can)
        self.widest = max(self.widest, open_deg)
        if open_deg >= TEAR_DEG:
            self.torn = True
        if self.on and not self.torn and can_in_zone(can):
            self.burst = True
        if off_counter(can) or off_counter(pan):
            self.fell = True
        return press, open_deg
