"""Geometry, measurements and rules for stoppering a reagent bottle in which a neutralisation is still giving off gas.

A chemistry bench with a dark bench mat. A clear 250 ml glass reagent bottle of citric acid solution to which sodium
hydrogencarbonate has just been added stands on the mat, fizzing: carbon dioxide bubbles rise through the liquid and a
froth sits on top. Its push-in plastic stopper stands on a watch glass beside it. The jar of sodium hydrogencarbonate
and its spatula stand by.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench, BENCH the top of the mat. Every body spawns
with identity orientation, so a measured rotation is the body's rotation from rest. Sizes are from the CAD models,
themselves estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
MAT = (0.075, 0.08, 0.09)
GLASS = (0.82, 0.90, 0.93)
PE = (0.93, 0.93, 0.90)
WHITE = (0.96, 0.96, 0.94)

# -- bench mat (fixed) ----------------------------------------------------------------------------------------
MAT_T = 0.004
MAT_C = (0.380, 0.0)
MAT_SIZE = (0.520, 0.900)
BENCH = TOP + MAT_T

# -- 250 ml reagent bottle: 70 mm across, rim 124 mm above its base, neck bore 21 mm ------------------------------
BODY_R = 0.035
BODY_H = 0.088                       # the straight body's collider; the bottle's origin is at half this height
BODY_Z = BODY_H / 2
RIM_Z = 0.124                        # the rim of the neck above the base
BORE_R = 0.0105
NECK_R = 0.016                       # the neck's collider: eight staves between these radii
NECK_Z0 = 0.090
BOTTLE_MASS = 0.29                   # about 0.20 kg of glass and 0.09 kg of liquid
BOTTLE_COM_Z = 0.045                 # above the base
B0 = (0.280, 0.0)                    # where the bottle stands

# -- push-in stopper: taper 26 mm long, collar 26 mm across, flat head 28 mm across and 9 mm thick ------------------
TAPER_L = 0.026
TAPER_R = 0.0090                     # the taper's collider is a cylinder: 1.5 mm of play in the bore
COLLAR_R = 0.013
COLLAR_T = 0.003
HEAD = (0.027, 0.009, 0.027)         # the flat head's collider (x, y, z); the stopper's origin is its centre
HEAD_Z = 0.0165                      # the head's centre above the collar's underside
STOPPER_TOP = 0.030                  # the head's top above the collar's underside
STOPPER_MASS = 0.035

# -- watch glass (fixed), 100 mm across; the stopper stands on its centre -----------------------------------------
W0 = (0.260, 0.150)
GLASS_R = 0.050
GLASS_FLAT_Z = 0.0025                # the top of its flat centre above the mat

# -- jar of sodium hydrogencarbonate with its spatula (fixed scenery) ---------------------------------------------
JAR_C = (0.420, -0.150)
JAR_R, JAR_H = 0.0315, 0.083

# -- the neck's seat: a sprung plug inside the neck that the stopper's taper lands on, standing in for the friction of a
# push-in stopper. It holds a stopper that is merely laid in the neck SEAT_UP above home, and gives when pushed ----
SEAT_UP = 0.005
SEAT_R = 0.008
SEAT_LEN = 0.008
SEAT_K = 400.0                       # N/m
SEAT_REST = 0.0025                   # the drive's rest position above the stop: 1.0 N preload, 3.0 N at home
SEAT_PARK = -(SEAT_UP + 0.0015)      # the drive's rest position once the stopper is home
SEAT_LOWER = -(SEAT_UP + 0.0008)
SEAT_MASS = 0.010
SEAT_Z = RIM_Z - TAPER_L + SEAT_UP - SEAT_LEN / 2     # its centre above the bottle's base at rest

# -- thresholds ------------------------------------------------------------------------------------------------
ON_XY = 0.002                        # home: the collar's centre within this of the neck's axis ...
ON_Z = 0.001                         # ... the collar's underside within this of the rim ...
ON_TILT = 4.0                        # ... and the stopper's axis within this many degrees of the bottle's
SEAL_Z = 0.003                       # sealing (for the zero only): the collar within this of the rim ...
SEAL_TILT = 8.0                      # ... and the stopper within this many degrees of the bottle's axis
OUT_Z = 0.003                        # lifted this far out again, the seat springs back
LAID_XY = 0.004                      # in the neck: the collar's centre within this of the axis, no more than LAID_Z above the rim ...
LAID_Z = 0.012
LAID_TILT = 15.0                     # ... and the right way up within this many degrees
HELD_Z = 0.030                       # held: lifted this far above where it stood on the watch glass ...
HELD_NEAR = 0.035                    # ... with a gripper's grasp point within this of the stopper's centre
UPRIGHT_DEG = 10.0
POUR_DEG = 60.0                      # an open bottle tilted further than this has poured out
STOOD = 0.020                        # the bottle counts as where it stood within this

# -- the gas ---------------------------------------------------------------------------------------------------
GAS_S = 25.0                         # carbon dioxide is given off for this long from the start of the trial
SEAL_S = 0.5                         # sealed for this long in all while gas is given off: the stopper is blown out
FIZZ_EVERY = 3                       # the three fizz drawings are shown in turn, each for this many control steps


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def mat_object() -> Part:
    return Part("bench_mat", pos=(MAT_C[0], MAT_C[1], TOP + MAT_T / 2), size=(MAT_SIZE[0], MAT_SIZE[1], MAT_T), exact_z=True,
                color=MAT, friction=(1.0, 0.8))


def _neck():
    """Eight staves round the bore, from the shoulder to the rim (offsets from the bottle's origin)."""
    out = []
    rm, th, h = (BORE_R + NECK_R) / 2, NECK_R - BORE_R, RIM_Z - NECK_Z0
    for i in range(8):
        a = 2 * math.pi * i / 8
        out.append(Piece("box", (th, 0.0135, h), (rm * math.cos(a), rm * math.sin(a), NECK_Z0 + h / 2 - BODY_Z), rot=(0.0, 0.0, a),
                         color=GLASS, friction=(0.5, 0.4)))
    return out


BOTTLE_POS = (B0[0], B0[1], BENCH + BODY_Z + 0.0003)


def bottle_object() -> Part:
    """The reagent bottle: a free rigid body. Colliders (hidden): the body as a cylinder, the neck as eight staves.
    More drawings ride on it: three frames of bubbles, froth and popping droplets (shown in turn while gas is given
    off), and the burst with the stopper in the air (shown once the stopper has been blown out)."""
    return Part("reagent_bottle", pos=BOTTLE_POS, size=(BODY_R, BODY_H, BODY_R), shape="cylinder", exact_z=True, mass=BOTTLE_MASS,
                color=GLASS, friction=(1.2, 1.0), pieces=tuple(_neck()), contact_offset=0.002, com=(0.0, 0.0, BOTTLE_COM_Z - BODY_Z),
                **_vis(("reaction_bottle", "fizz_a", "fizz_b", "fizz_c", "burst", "burst_stopper"), (0.0, 0.0, -BODY_Z), visual_glass_opacity=0.22))


def seat_object() -> Part:
    """The sprung plug in the neck (not drawn): it slides along the bottle's axis and is carried with the bottle."""
    spring = Spring(axis="Z", lower=SEAT_LOWER, upper=0.0, stiffness=SEAT_K, damping=4.0, target=SEAT_REST,
                    parent="reagent_bottle", parent_pos=BOTTLE_POS)
    return Part("neck_seat", pos=(B0[0], B0[1], BENCH + SEAT_Z + 0.0003), size=(SEAT_R, SEAT_LEN, SEAT_R), shape="cylinder",
                exact_z=True, mass=SEAT_MASS, color=GLASS, friction=(0.3, 0.25), spring=spring, contact_offset=0.001,
                **_vis("watch_glass", (0.0, 0.0, 0.0), visual_scale=0.002))


STOPPER_Z0 = BENCH + GLASS_FLAT_Z + TAPER_L + HEAD_Z + 0.0003       # the stopper's origin while it stands on the watch glass


def stopper_object() -> Part:
    """The stopper: a free rigid body standing on its taper's end on the watch glass. Colliders (hidden): the flat head
    as a block, the collar and the taper as cylinders."""
    pieces = (Piece("cylinder", (COLLAR_R, COLLAR_T, COLLAR_R), (0.0, 0.0, COLLAR_T / 2 - HEAD_Z), color=PE),
              Piece("cylinder", (TAPER_R, TAPER_L, TAPER_R), (0.0, 0.0, -TAPER_L / 2 - HEAD_Z), color=PE, friction=(0.4, 0.3)))
    return Part("stopper", pos=(W0[0], W0[1], STOPPER_Z0), size=HEAD, exact_z=True, mass=STOPPER_MASS, color=PE,
                friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002, com=(0.0, 0.0, -0.016),
                **_vis("stopper", (0.0, 0.0, -HEAD_Z)))


def glass_object() -> Part:
    return Part("watch_glass", pos=(W0[0], W0[1], BENCH + GLASS_FLAT_Z / 2), size=(GLASS_R - 0.002, GLASS_FLAT_Z, GLASS_R - 0.002),
                shape="cylinder", exact_z=True, color=GLASS, friction=(0.8, 0.6), **_vis("watch_glass", (0.0, 0.0, -GLASS_FLAT_Z / 2)))


def jar_object() -> Part:
    """The jar of sodium hydrogencarbonate with its spatula lying beside it: fixed scenery. Collider (hidden): the jar."""
    return Part("soda_jar", pos=(JAR_C[0], JAR_C[1], BENCH + JAR_H / 2), size=(JAR_R, JAR_H, JAR_R), shape="cylinder", exact_z=True,
                color=WHITE, friction=(0.6, 0.5), **_vis("soda_jar", (0.0, 0.0, -JAR_H / 2)))


# -- measurements -----------------------------------------------------------------------------------------------
def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def base_centre(pose):
    """The centre of the bottle's base."""
    p = np.asarray(pose, float)
    return p[:3] + quat_matrix(p[3:7]) @ np.array([0.0, 0.0, -BODY_Z])


def bottle_moved(pose) -> float:
    """How far the bottle's base centre is from where it stood, seen from above."""
    c = base_centre(pose)
    return float(math.hypot(c[0] - B0[0], c[1] - B0[1]))


def stopper_seat(bottle, stopper):
    """Where the stopper is in the bottle's own frame: (distance of the centre of its collar's underside from the
    neck's axis, that point's height above the rim, the angle between the stopper's axis and the bottle's in degrees)."""
    b, s = np.asarray(bottle, float), np.asarray(stopper, float)
    rb, rs = quat_matrix(b[3:7]), quat_matrix(s[3:7])
    d = rb.T @ (s[:3] + rs @ np.array([0.0, 0.0, -HEAD_Z]) - (b[:3] + rb @ np.array([0.0, 0.0, RIM_Z - BODY_Z])))
    lean = math.degrees(math.acos(float(np.clip(rb[:, 2] @ rs[:, 2], -1.0, 1.0))))
    return float(math.hypot(d[0], d[1])), float(d[2]), float(lean)


def home(bottle, stopper) -> bool:
    """The stopper is home (the bottle sealed): centred in the neck, its collar down on the rim, in line with the bottle."""
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(off <= ON_XY and abs(up) <= ON_Z and lean <= ON_TILT)


def stopper_out(bottle, stopper) -> bool:
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(up > OUT_Z or off > 0.004)


def sealing(bottle, stopper) -> bool:
    """The stopper closes the bottle well enough to hold gas in, home or nearly: in the neck, its collar within SEAL_Z of
    the rim and its axis within SEAL_TILT of the bottle's. Used for the blown-out zero only; credit needs ``home``."""
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(off <= LAID_XY and up <= SEAL_Z and lean <= SEAL_TILT)


def laid_in_neck(bottle, stopper) -> bool:
    """The stopper's taper is in the neck the right way up: laid in loosely, nearly home or home."""
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(off <= LAID_XY and up <= LAID_Z and lean <= LAID_TILT)


def held_up(stopper, robot) -> bool:
    """The stopper is held up in a gripper: its centre HELD_Z or more above where it stood on the watch glass and a
    gripper's grasp point within HELD_NEAR of it. A stopper put down somewhere else is not held."""
    p = np.asarray(stopper, float)[:3]
    if not robot or float(p[2]) - STOPPER_Z0 < HELD_Z:
        return False
    return bool(min(float(np.linalg.norm(np.asarray(robot[side]["tcp"], float)[:3] - p)) for side in ("left", "right")) <= HELD_NEAR)


# -- the grippers' outlines, sampled from the arms' measured joints (a gripper's own frame: z along the fingers, x the
# closing direction; the grasp point is the origin) ----------------------------------------------------------------
PAD_TIP, FINGER_BACK, PAD_THICK, PAD_HALF_W = 0.013, 0.077, 0.010, 0.010
BODY_HALF, BODY_SPAN, SAMPLE = (0.050, 0.025), (-0.134, -0.065), 0.010


def gripper_local(half_open):
    pts = [(0.0, 0.0, 0.0)]
    for sx in (-1.0, 1.0):
        for x in (sx * half_open, sx * (half_open + PAD_THICK)):
            for y in (-PAD_HALF_W, 0.0, PAD_HALF_W):
                pts += [(x, y, float(z)) for z in np.arange(PAD_TIP, -FINGER_BACK - 1e-9, -SAMPLE)]
    for x in np.linspace(-BODY_HALF[0], BODY_HALF[0], 11):
        for y in np.linspace(-BODY_HALF[1], BODY_HALF[1], 6):
            pts += [(float(x), float(y), float(z)) for z in np.linspace(BODY_SPAN[0], BODY_SPAN[1], 8)]
    return np.array(pts)


def hand_points(arm, side):
    """Points over a whole gripper (n x 3), 10 mm apart, from its measured joints and finger opening. Without joints,
    the grasp point alone."""
    tcp = np.asarray(arm["tcp"], float)[:3]
    if "joints" not in arm:
        return tcp.reshape(1, 3)
    from yam_arena import ik, station
    pos, rot = ik.tcp_pose(np.asarray(arm["joints"], float), station.BASES[side])
    half = float(np.mean(np.abs(np.asarray(arm.get("fingers", (0.0, 0.0)), float))))
    return np.asarray(pos, float) + gripper_local(half) @ np.asarray(rot, float).T


def gripper_clearance(robot, bottle) -> float:
    """The nearest sampled gripper point to the bottle's outline, taken as a cylinder 70 mm across from its base to the
    top of a seated stopper."""
    if not robot:
        return 1.0
    pts = np.vstack([hand_points(robot[side], side) for side in ("left", "right")])
    b = np.asarray(bottle, float)
    d = (pts - b[:3]) @ quat_matrix(b[3:7])
    z0, z1 = -BODY_Z, RIM_Z + STOPPER_TOP - BODY_Z
    dr = np.maximum(np.hypot(d[:, 0], d[:, 1]) - BODY_R, 0.0)
    dz = np.maximum(np.maximum(z0 - d[:, 2], d[:, 2] - z1), 0.0)
    return float(np.hypot(dr, dz).min())


class Rules:
    """The disclosed rules.

    (1) The gas. Carbon dioxide is given off for the first GAS_S seconds of the trial, then it stops. Bubbles and froth
    are drawn only while it lasts.
    (2) The neck's friction. A stopper laid in the neck rests on the sprung plug SEAT_UP above home and vents. Once it
    has been pushed home (see ``home``) the plug's spring target is moved down so that it stays retracted and the
    stopper stays seated; taken out again, the plug springs back up.
    (3) Blown out. Every step with the stopper sealing the bottle (home or nearly: see ``sealing``) while gas is being
    given off is a sealed step. SEAL_S seconds of
    sealed steps in all (a total over the trial, never reset) and the stopper is blown out: latched; the plug is
    released, and the burst is drawn with the stopper in the air.
    (4) Spilled. The bottle tilted more than POUR_DEG while its stopper is not sealing it has poured out: latched."""

    def __init__(self, hz=20):
        self.gas_steps = int(round(GAS_S * hz))
        self.seal_steps = int(round(SEAL_S * hz))
        self.parked = False
        self.sealed = 0
        self.blown = False
        self.spilled = False
        self.fizz = None

    def update(self, step, bottle, stopper):
        """Returns (mechanics, events). Events: ('seat', bool), ('fizz', bool), ('burst', True)."""
        events = []
        fizzing = step <= self.gas_steps
        if fizzing != self.fizz:
            self.fizz = fizzing
            events.append(("fizz", fizzing))
        is_home = home(bottle, stopper)
        if not self.blown:
            if not self.parked and step > 20 and is_home:
                self.parked = True
                events.append(("seat", True))
            elif self.parked and stopper_out(bottle, stopper):
                self.parked = False
                events.append(("seat", False))
        if fizzing and sealing(bottle, stopper):
            self.sealed += 1
            if not self.blown and self.sealed >= self.seal_steps:
                self.blown = True
                self.parked = False
                events.append(("seat", False))
                events.append(("burst", True))
        if tilt_deg(bottle) > POUR_DEG and not sealing(bottle, stopper):
            self.spilled = True
        off, up, lean = stopper_seat(bottle, stopper)
        mech = {"gas": bool(fizzing), "home": bool(is_home), "sealed_while_gas_s": round(self.sealed / 20.0, 2),
                "blown_out": bool(self.blown), "spilled": bool(self.spilled), "stopper_above_rim_mm": round(1000 * up, 2)}
        return mech, events
