"""Geometry, measurements and rules for taking a charged capacitor out of a charge and discharge rig.

A physics teaching-lab bench. A base board carries a DC supply box (rocker switch off, mains lead plugged into a lit
power strip), a single-pole double-throw knife switch standing open between its CHARGE and DISCHARGE jaws, a large can
capacitor lying in two clip posts, a discharge resistor, an earth terminal and a large voltmeter wired across the
capacitor, its needle at 300 V. A shorting link (an insulated bar with a fork contact at each end) stands parked on an
insulating rail on the board. A parts tray stands on the bench to the right of the board.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Every body spawns with identity orientation,
so a measured rotation is the body's rotation from rest. Sizes are from the CAD models, themselves estimates of typical
products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Anchor, Hinge, Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WOOD = (0.80, 0.68, 0.48)
WHITE = (0.94, 0.94, 0.92)
DARK = (0.10, 0.10, 0.11)
BLUE = (0.05, 0.13, 0.40)
RED = (0.82, 0.05, 0.05)
TRAYC = (0.12, 0.33, 0.62)

# -- base board (fixed), 420 mm (x) by 500 mm (y), 12 mm thick ------------------------------------------------------
BOARD_C = (0.400, 0.100)
BOARD = (0.420, 0.500, 0.012)
BT = BOARD[2]


def at(x_mm, y_mm, z_mm=0.0):
    """A point given in millimetres on the board's drawing, in the world."""
    return (BOARD_C[0] + x_mm / 1000.0, BOARD_C[1] + y_mm / 1000.0, TOP + z_mm / 1000.0)


# -- can capacitor: 50 mm across, 100 mm long, a stud 8 mm across and 24 mm long at each end; it lies along x with the
# outer 10 mm of each stud in the clip of a post; the far stud (+x) is its + terminal -----------------------------
CAP_R = 0.025
CAP_L = 0.100
STUD_R = 0.004
STUD_L = 0.024
CAP_MASS = 0.28
CAP0 = at(-100.0, -140.0, 55.0)      # its centre while it lies in the clips
CAP_SPAWN = (CAP0[0], CAP0[1], CAP0[2] + 0.0003)
POST_DX = 0.069
CLIP_FORCE = 4.5                     # newtons: the upward load (on top of the capacitor's weight) at which the clips let go
CLIP_K = 1500.0                      # N/m: the clips' leaves hold the studs down like a spring ...
CLIP_TRAVEL = CLIP_FORCE / CLIP_K    # ... and let go once the capacitor has been lifted this far (3 mm)
CLIP_DAMP = 10.0                     # N s/m
PRONG = (0.010, 0.0018, 0.013)       # a clip's leaf; two stand on each post, 0.4 mm clear of the stud on either side
PRONG_Y = 0.0053
MOVED = 0.002                        # either stud moved this far while charged (only a touch can do that): a shock
TOUCH = 0.005                        # a sampled gripper point this close to a live part counts as touching it: a shock

# -- knife switch: the lever turns about y at PIVOT; 0 degrees is straight up (open), -88 is down in the DISCHARGE jaw
# (toward the arms), +88 is down in the CHARGE jaw (away from them) ------------------------------------------------
PIVOT = at(-40.0, 40.0, 42.0)
HANDLE_R = 0.0975                    # the handle's centre from the pivot
HANDLE = (0.009, 0.055)              # its radius and length
BLADE = (0.014, 0.005, 0.066)
LEVER_MASS = 0.08
LEVER_STOP = 88.0
JAW_IN = 76.0                        # the blade meets the jaw's leaves here; from here on they push back
SEATED = 86.0                        # pushed this far it is seated; the jaw then holds it down on its stop
UNSEAT = 80.0                        # pulled back up past this it is out of the jaw again
JAW_K = 0.024                        # N m per degree: 0.24 N m at SEATED, about 2.5 N at the handle's centre
JAW_HOLD = 92.0                      # the drive's rest angle while seated: beyond the stop, so the blade is held on it
LEVER_DAMP = 0.0006                  # N m s per degree

# -- voltmeter: needle on a hinge about z; the scale runs from 0 V (45 degrees to the left of straight ahead) to 400 V
# (45 degrees to the right); the needle is spawned pointing at 300 V ----------------------------------------------
NEEDLE_PIVOT = at(42.0, -115.0, 55.0)
V0 = 300.0
V_FULL = 400.0
DEG_PER_VOLT = 90.0 / V_FULL
NEEDLE_K = 0.0002                    # N m per degree
NEEDLE_DAMP = 0.00002
NEEDLE_MASS = 0.02

# -- supply box with its rocker (hinge about y: 0 = off as it starts, 24 = on) ----------------------------------------
SUPPLY_C = at(100.0, 150.0)
SUPPLY = (0.100, 0.140, 0.070)
ROCKER_PIVOT = at(95.0, 110.0, 85.0)
ROCKER_ON = 12.0                     # past this the rocker snaps over and the supply is on
ROCKER_K = 0.0012                    # N m per degree
ROCKER_REST = (-4.0, 28.0)           # the drive's rest angle off and on (beyond the stops at -1 and 25)

# -- the circuit's rule ----------------------------------------------------------------------------------------
CAP_F = 470e-6                       # farads: the capacitor, an aluminium electrolytic rated 450 V
RES_OHM = 4700.0                     # ohms: the wirewound discharge resistor (and the supply's charging resistor)
TAU = RES_OHM * CAP_F                # 2.209 s: from 300 V it is below 50 V after 3.96 s (80 steps) and below 5 V after 9.04 s (181 steps)
LIVE = 50.0                          # volts: at or above this the capacitor is dangerous to touch
SAFE = 5.0                           # volts: below this it is discharged
SPARK_STEPS = 40

# -- parts tray (fixed), 190 mm (x) by 156 mm (y) outside, wall 30 mm, a ribbed rubber liner -----------------------
TRAY_C = (0.420, -0.245)
TRAY_HALF = (0.095, 0.078)
TRAY_WALL = 0.003
TRAY_H = 0.030
RIB_Y = (-0.045, -0.015, 0.015, 0.045)
RIB_TOP = 0.008
RIB_W = 0.006
CAP_REST_Z = TOP + RIB_TOP + math.sqrt(CAP_R ** 2 - 0.012 ** 2)      # its axis when it lies between two ribs
REST_Z_TOL = 0.006

# -- shorting link: an insulated bar 130 x 16 x 14 mm along x with a leg at each end; each leg ends in a fork contact
# whose two leaves straddle a stud 8 mm across. Its origin is the middle of the bar. It starts parked on an insulating
# rail (a rod 8 mm across on two stand-offs) between the capacitor and the knife switch -----------------------------
LINK_BAR = (0.130, 0.016, 0.014)
LINK_H = 0.044                       # the bar's middle above the stud axis when the link is seated
LINK_FORK_X = 0.058                  # the forks' centres from the link's middle (116 mm apart)
LINK_FORK_W = 0.007                  # a fork's width along the stud
LINK_TIP = 0.006                     # the leaves reach this far below the stud axis when seated
LINK_ROOT = 0.0045                   # the slot's root above the stud axis when seated (0.5 mm above the stud)
LINK_LEAF = (0.0044, 0.0062)         # a leaf's inner and outer face from the slot's middle
LINK_BARE = 0.013                    # the legs are bare metal from this far below the bar's middle down to the tips
LINK_MASS = 0.05
RAIL_C = at(-100.0, -58.0, 26.0)     # the middle of the parking rail's axis
RAIL = (0.004, 0.136)                # its radius and length (along x)
LINK0 = (RAIL_C[0], RAIL_C[1], RAIL_C[2] + LINK_H)   # the link's origin while it stands parked
PARK_FORCE = 3.0                     # newtons on top of its weight: the forks' grip on the rail
PARK_TORQUE = 0.5
# the forks' catch on the studs (rule 5), in terms of s, the height of the link above its seat
LINK_CAPTURE = 0.009                 # the leaves reach the studs: from here down they are guided ...
LINK_REST_IN = 0.008                 # ... and resisted, as by a spring that would rest here
LINK_K_IN = 500.0                    # N/m
LINK_LATCH = 0.002                   # pushed down to here the leaves close round the studs (3 N) ...
LINK_K_HOLD = 1000.0                 # N/m: ... and then pull the link home and hold it
LINK_UNLATCH = 0.0035                # pulled back up to here (3.5 N) they let go again
LINK_SEATED = 0.001                  # home: within this of its seat
LINK_FREE = 0.011                    # above this the leaves are clear of the studs
LINK_DAMP = 6.0                      # N s/m
INSERT_N = LINK_K_IN * (LINK_REST_IN - LINK_LATCH)      # 3.0 N
RETAIN_N = LINK_K_HOLD * LINK_UNLATCH                   # 3.5 N
CAPTURE_XY = 0.003                   # the forks are over the studs when the link is within this of its seat line, along and across
CAPTURE_DEG = 5.0                    # and its bar is in line with the capacitor's axis within this (the flared leaves and round studs centre it)
HELD_XY = 0.005                      # a link further than this from its seat line, or HELD_DEG out of line, is not on the studs
HELD_DEG = 8.0
LINK_TOUCH = 0.0015                  # a fork leaf this close to a conductor is in contact with it
LINK_ANY_WAY = True                  # the catch works with the link either way round and from any side of the capacitor
EARTH_POST = at(-166.0, 184.0)       # the earth terminal's post, 14 mm across, to 27 mm above the bench

# -- power strip (fixed scenery) -------------------------------------------------------------------------------
STRIP_C = (0.650, 0.410)
STRIP = (0.062, 0.300, 0.040)


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def _rel(p, z_mid):
    """Offset of a world point from the board's centre (the rig's root collider)."""
    return (p[0] - BOARD_C[0], p[1] - BOARD_C[1], p[2] - (TOP + BT / 2) + z_mid)


def rig_object() -> Part:
    """The base board and everything fixed on it. Colliders (hidden): the board, the supply box (10 mm lower than
    drawn, so that the rocker can tip), the meter's housing, the switch's base plate, the two clip posts with their
    clips' leaves, the resistor and the parking rail's base and stand-offs as boxes, the rail as a cylinder. The switch's
    jaws, the wires and the leads are drawn only. The lit lamp is a second drawing."""
    post_h = 0.055 - STUD_R - BT
    pieces = [
        Piece("box", (SUPPLY[0], SUPPLY[1], SUPPLY[2] - 0.010), _rel(SUPPLY_C, BT + (SUPPLY[2] - 0.010) / 2), color=DARK),
        Piece("box", (0.140, 0.180, 0.040), _rel(at(90.0, -115.0), BT + 0.020), color=DARK),
        Piece("box", (0.160, 0.040, 0.008), _rel(at(-40.0, 40.0), BT + 0.004), color=WHITE),
        Piece("box", (0.016, 0.070, 0.030), _rel(at(-150.0, 110.0), BT + 0.015), color=DARK),
        Piece("cylinder", (RAIL[0], RAIL[1], RAIL[0]), _rel((RAIL_C[0], RAIL_C[1], TOP), RAIL_C[2] - TOP), axis="X", color=WHITE, friction=(0.3, 0.25)),
        Piece("box", (0.088, 0.024, 0.003), _rel((RAIL_C[0], RAIL_C[1], TOP), BT + 0.0015), color=DARK),
    ]
    for s in (-1, 1):
        h = RAIL_C[2] - TOP - RAIL[0] - BT
        pieces.append(Piece("box", (0.010, 0.014, h), _rel((RAIL_C[0] + s * 0.030, RAIL_C[1], TOP), BT + h / 2), color=DARK))
    for s in (-1, 1):
        pieces.append(Piece("box", (0.012, 0.024, post_h), _rel((CAP0[0] + s * POST_DX, CAP0[1], TOP), BT + post_h / 2), color=DARK))
        for t in (-1, 1):
            pieces.append(Piece("box", PRONG, _rel((CAP0[0] + s * POST_DX, CAP0[1] + t * PRONG_Y, TOP), BT + post_h + PRONG[2] / 2),
                                color=DARK, friction=(0.3, 0.25)))
    return Part("rig_board", pos=(BOARD_C[0], BOARD_C[1], TOP + BT / 2), size=BOARD, exact_z=True, color=WOOD, friction=(0.6, 0.5),
                pieces=tuple(pieces), **_vis(("rig_board", "lamp_on"), (0.0, 0.0, -BT / 2)))


def capacitor_object() -> Part:
    """The capacitor: a free rigid body held where it lies by the clips' grip: a slide joint straight up from where it
    lies, with a stop below (the clips' seat takes any push downward) and a spring that holds it down (CLIP_K); the
    rule in the task switches the joint off for good once the capacitor has been lifted CLIP_TRAVEL, which takes
    CLIP_FORCE on top of its weight. Colliders (hidden): the can and its two studs as cylinders. The spark is a second
    drawing."""
    studs = tuple(Piece("cylinder", (STUD_R, STUD_L, STUD_R), (s * (CAP_L + STUD_L) / 2, 0.0, 0.0), axis="X", color=WHITE) for s in (-1, 1))
    clip = Spring(axis="Z", lower=0.0, upper=0.030, stiffness=CLIP_K, damping=CLIP_DAMP, target=0.0)
    return Part("capacitor", pos=CAP_SPAWN, size=(CAP_R, CAP_L, CAP_R), shape="cylinder", axis="X",
                exact_z=True, mass=CAP_MASS, color=BLUE, friction=(1.2, 1.0), pieces=studs, contact_offset=0.002,
                spring=clip, **_vis(("capacitor", "spark"), (0.0, 0.0, 0.0)))


LINK_JOINT_ON_CAP = tuple(a - b for a, b in zip(LINK0, CAP_SPAWN))                      # the catch joint's frame on the capacitor
LINK_JOINT_ON_LINK = (LINK_JOINT_ON_CAP[0], LINK_JOINT_ON_CAP[1], LINK_JOINT_ON_CAP[2] - LINK_H)   # and on the link: they meet when it is seated


def link_object() -> Part:
    """The shorting link, standing parked with its forks on the rail: a free rigid body held there by the forks' grip
    (a fixed joint that lets go at PARK_FORCE). Colliders (hidden): the bar, the two legs and the four leaves as boxes;
    the leaves' colliders stand 2 mm clear of a stud on either side, the catch joint centres them. The slide joint to
    the capacitor (the forks' catch, rule 5) is defined switched off; the rule in the task switches it on while the
    forks are on the studs. A second drawing: its green lamp lit."""
    leg = LINK_H - LINK_ROOT - LINK_BAR[2] / 2
    pieces = []
    for s in (-1, 1):
        pieces.append(Piece("box", (LINK_FORK_W, LINK_BAR[1], leg), (s * LINK_FORK_X, 0.0, -LINK_BAR[2] / 2 - leg / 2), color=DARK, friction=(0.3, 0.25)))
        for t in (-1, 1):
            pieces.append(Piece("box", (LINK_FORK_W, 0.002, LINK_ROOT + LINK_TIP), (s * LINK_FORK_X, t * 0.007, -LINK_H + (LINK_ROOT - LINK_TIP) / 2),
                                color=DARK, friction=(0.3, 0.25)))
    catch = Spring(axis="Z", lower=-0.0005, upper=0.030, stiffness=LINK_K_IN, damping=LINK_DAMP, target=LINK_REST_IN,
                   parent="capacitor", parent_pos=CAP_SPAWN, local=LINK_JOINT_ON_LINK, enabled=False)
    return Part("shorting_link", pos=LINK0, size=LINK_BAR, exact_z=True, mass=LINK_MASS, color=(0.04, 0.42, 0.14), friction=(1.2, 1.0),
                pieces=tuple(pieces), contact_offset=0.002, spring=catch, anchor=Anchor(break_force=PARK_FORCE, break_torque=PARK_TORQUE),
                **_vis(("shorting_link", "link_green_on"), (0.0, 0.0, 0.0)))


def lever_object() -> Part:
    """The knife switch's lever: one rigid body on a hinge along y, standing straight up. Colliders (hidden): the blade
    as a box, the handle as a cylinder. It is balanced about its pivot, so it stays where it is left."""
    hinge = Hinge(pivot=PIVOT, axis="Y", damping=LEVER_DAMP, lower_deg=-LEVER_STOP, upper_deg=LEVER_STOP, stiffness=0.0, target_deg=0.0)
    pieces = (Piece("box", BLADE, (0.0, 0.0, 0.007 + BLADE[2] / 2), color=WHITE),
              Piece("cylinder", (HANDLE[0], HANDLE[1], HANDLE[0]), (0.0, 0.0, HANDLE_R), color=DARK, friction=(1.2, 1.0)))
    return Part("knife_lever", pos=PIVOT, size=(0.012, 0.014, 0.012), exact_z=True, mass=LEVER_MASS, color=DARK, friction=(0.8, 0.6),
                hinge=hinge, pieces=pieces, contact_offset=0.002, com=(0.0, 0.0, 0.0), **_vis("knife_lever", (0.0, 0.0, 0.0)))


def needle_object() -> Part:
    """The voltmeter's needle: a light body on a hinge about z whose drive follows the voltage."""
    f = math.radians(-45.0 + DEG_PER_VOLT * V0)
    c, s = math.cos(f), -math.sin(f)
    hinge = Hinge(pivot=NEEDLE_PIVOT, axis="Z", damping=NEEDLE_DAMP, lower_deg=-DEG_PER_VOLT * (V_FULL - V0) - 2.0,
                  upper_deg=DEG_PER_VOLT * V0 + 1.0, stiffness=NEEDLE_K, target_deg=0.0)
    arm = Piece("box", (0.090, 0.003, 0.001), (0.049 * c, 0.049 * s, 0.0), rot=(0.0, 0.0, math.atan2(s, c)), color=DARK)
    return Part("meter_needle", pos=NEEDLE_PIVOT, size=(0.008, 0.008, 0.002), exact_z=True, mass=NEEDLE_MASS, color=DARK,
                friction=(0.3, 0.25), hinge=hinge, pieces=(arm,), contact_offset=0.0005, **_vis("needle", (0.0, 0.0, -0.001)))


def rocker_object() -> Part:
    """The supply's rocker switch: a small body on a hinge along y, off (its near side, marked O, down) as it starts.
    Two drawings: dark while off, lit red while on."""
    hinge = Hinge(pivot=ROCKER_PIVOT, axis="Y", damping=0.00002, lower_deg=-1.0, upper_deg=25.0, stiffness=ROCKER_K, target_deg=ROCKER_REST[0])
    top = Piece("box", (0.034, 0.022, 0.004), (0.0, 0.0, -0.001), rot=(0.0, math.radians(-12.0), 0.0), color=DARK)
    return Part("supply_rocker", pos=ROCKER_PIVOT, size=(0.004, 0.020, 0.003), exact_z=True, mass=0.02, color=DARK, friction=(0.8, 0.6),
                hinge=hinge, pieces=(top,), contact_offset=0.001, **_vis(("rocker_off", "rocker_on"), (0.0, 0.0, 0.0), visual_rpy_deg=(0.0, -12.0, 0.0)))


def tray_object() -> Part:
    hx, hy, w, f = TRAY_HALF[0], TRAY_HALF[1], TRAY_WALL, 0.004
    zc = TRAY_H / 2
    pieces = [Piece("box", (w, 2 * hy, TRAY_H - f), (-hx + w / 2, 0.0, zc), color=TRAYC), Piece("box", (w, 2 * hy, TRAY_H - f), (hx - w / 2, 0.0, zc), color=TRAYC),
              Piece("box", (2 * hx, w, TRAY_H - f), (0.0, -hy + w / 2, zc), color=TRAYC), Piece("box", (2 * hx, w, TRAY_H - f), (0.0, hy - w / 2, zc), color=TRAYC)]
    pieces += [Piece("box", (2 * hx - 0.012, RIB_W, RIB_TOP - f), (0.0, y, (RIB_TOP + f) / 2 - f / 2), color=DARK, friction=(1.0, 0.8)) for y in RIB_Y]
    return Part("parts_tray", pos=(TRAY_C[0], TRAY_C[1], TOP + f / 2), size=(2 * hx, 2 * hy, f), exact_z=True, color=TRAYC,
                friction=(0.8, 0.6), pieces=tuple(pieces), **_vis("parts_tray", (0.0, 0.0, -f / 2)))


def strip_object() -> Part:
    """The power strip with the supply's plug in it: fixed scenery, drawn switched on. Colliders (hidden): the strip and
    the plug as boxes."""
    zc = STRIP[2] / 2
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, -0.015, zc + 0.013), color=DARK),)
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=WHITE, friction=(0.5, 0.4),
                pieces=pieces, yaw=math.pi,
                **_vis(("power_set", "strip_lamps_on", "strip_main_on"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main", "cooker_cord", "lead")))


# -- measurements -----------------------------------------------------------------------------------------------
def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def lever_deg(pose) -> float:
    """The knife switch's lever: 0 straight up, negative toward the arms (DISCHARGE), positive away (CHARGE)."""
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.atan2(r[0, 2], r[0, 0]))


def rocker_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.atan2(r[0, 2], r[0, 0]))


def needle_volts(pose) -> float:
    """What the needle points at, from its measured angle about z."""
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return V0 - math.degrees(math.atan2(r[1, 0], r[0, 0])) / DEG_PER_VOLT


def needle_target(volts) -> float:
    return DEG_PER_VOLT * (V0 - float(volts))


def handle_centre(deg):
    t = math.radians(deg)
    return np.array(PIVOT) + HANDLE_R * np.array([math.sin(t), 0.0, math.cos(t)])


def cap_axis(pose):
    p = np.asarray(pose, float)
    return p[:3], quat_matrix(p[3:7])[:, 0]


# -- the capacitor in its clips: judged by its two studs ----------------------------------------------------------
STUD_C = CAP_L / 2 + STUD_L / 2      # a stud's centre from the capacitor's centre, along its axis
CLIP_AXIAL = 0.004                   # a stud is in its clip within this along the line of the clips (x) ...
CLIP_SIDE = 0.0015                   # ... this sideways (y) ...
CLIP_UP = 0.006                      # ... and from CLIP_DOWN below to CLIP_UP above where it lay at the start
CLIP_DOWN = 0.0015


def stud_centres(pose):
    c, ax = cap_axis(pose)
    return [c - ax * STUD_C, c + ax * STUD_C]


def _stud_pairs(pose, rest):
    """The two studs' displacements from the two clips, for the pairing (either way round) that moves them least."""
    a, b = stud_centres(pose), stud_centres(rest)
    ways = ([a[0] - b[0], a[1] - b[1]], [a[0] - b[1], a[1] - b[0]])
    return min(ways, key=lambda w: max(float(np.linalg.norm(d)) for d in w))


def cap_moved(pose, rest) -> float:
    """How far the capacitor has moved from ``rest``, its pose in its clips at the start: the larger of its two studs'
    displacements (so a twist or one end lifted counts, not only its centre)."""
    return max(float(np.linalg.norm(d)) for d in _stud_pairs(pose, rest))


def in_clips(pose, rest) -> bool:
    """Both studs are inside their clips: each within CLIP_AXIAL along the clips' line, CLIP_SIDE sideways, and
    between CLIP_DOWN below and CLIP_UP above where it lay at the start."""
    return bool(all(abs(d[0]) <= CLIP_AXIAL and abs(d[1]) <= CLIP_SIDE and -CLIP_DOWN <= d[2] <= CLIP_UP for d in _stud_pairs(pose, rest)))


# -- distances from sampled gripper points to the live parts, all taken as flat-ended cylinders -----------------------
BLADE_BARE = 0.068                   # the blade is bare copper from the pivot to here, where the handle's guard collar begins
BLADE_R = 0.007


def _cyl_gaps(pts, a, b, r):
    """Distances from points (n x 3) to the flat-ended cylinder of radius r between a and b (0 inside it)."""
    pts = np.atleast_2d(np.asarray(pts, float))
    ab = np.asarray(b, float) - np.asarray(a, float)
    length = float(np.linalg.norm(ab))
    u = ab / length
    rel = pts - np.asarray(a, float)
    s = rel @ u
    rad = np.linalg.norm(rel - np.outer(s, u), axis=1)
    return np.hypot(np.maximum(np.maximum(-s, s - length), 0.0), np.maximum(rad - r, 0.0))


def cap_gaps(pose, pts):
    """Distances from points to the capacitor's outline: its can (50 mm across, 100 mm long) and its two stud terminals."""
    c, ax = cap_axis(pose)
    h, e = CAP_L / 2, CAP_L / 2 + STUD_L
    g = _cyl_gaps(pts, c - ax * h, c + ax * h, CAP_R)
    for s in (-1, 1):
        g = np.minimum(g, _cyl_gaps(pts, c + s * ax * h, c + s * ax * e, STUD_R))
    return g


def cap_gap(pose, point) -> float:
    return float(cap_gaps(pose, point).min())


def _rig_metal():
    """The rig's bare metal that is at the clip posts' voltage, as (end, end, radius) cylinders: the two clip posts with
    their clips, the knife switch's pivot and its two jaws, and the meter's two terminal screws. The blade is separate."""
    rods = []
    for s in (-1, 1):
        x = CAP0[0] + s * POST_DX
        rods.append((np.array([x, CAP0[1], TOP + BT]), np.array([x, CAP0[1], TOP + 0.064]), 0.012))
        rods.append((np.array([PIVOT[0] + s * 0.055, PIVOT[1], TOP + 0.020]), np.array([PIVOT[0] + s * 0.055, PIVOT[1], TOP + 0.048]), 0.007))
    rods.append((np.array([PIVOT[0], PIVOT[1], TOP + 0.020]), np.array(PIVOT) + np.array([0.0, 0.0, 0.008]), 0.008))
    for y in (-74.0, 74.0):
        rods.append((np.array(at(28.0, -115.0 + y, 52.0)), np.array(at(28.0, -115.0 + y, 61.0)), 0.0045))
    return rods


def blade_gaps(deg, pts):
    """Distances from points to the blade's bare copper, pivot to guard collar. A point level with the guard or the
    insulated handle (further than BLADE_BARE from the pivot along the lever) is never near the bare blade: the guard
    is in the way."""
    pts = np.atleast_2d(np.asarray(pts, float))
    t = math.radians(deg)
    d = np.array([math.sin(t), 0.0, math.cos(t)])
    piv = np.array(PIVOT)
    g = _cyl_gaps(pts, piv, piv + BLADE_BARE * d, BLADE_R)
    g[(pts - piv) @ d > BLADE_BARE] = 1.0
    return g


def rig_gaps(deg, pts):
    """Distances from points to the nearest of the rig's bare live metal parts (see ``_rig_metal``) or the bare blade."""
    g = blade_gaps(deg, pts)
    for a, b, r in _rig_metal():
        g = np.minimum(g, _cyl_gaps(pts, a, b, r))
    return g


def rig_gap(deg, point) -> float:
    return float(rig_gaps(deg, point).min())


def charge_jaw_gaps(pts):
    """Distances from points to the CHARGE jaw, which is at the supply's voltage whenever the supply is on."""
    x = PIVOT[0] + 0.055
    return _cyl_gaps(pts, np.array([x, PIVOT[1], TOP + 0.020]), np.array([x, PIVOT[1], TOP + 0.048]), 0.007)


# -- the shorting link on the capacitor -----------------------------------------------------------------------------
def matrix_quat_wxyz(r):
    """Rotation matrix to a quaternion (w, x, y, z)."""
    t = float(r[0, 0] + r[1, 1] + r[2, 2])
    if t > 0.0:
        k = math.sqrt(t + 1.0) * 2.0
        q = (0.25 * k, (r[2, 1] - r[1, 2]) / k, (r[0, 2] - r[2, 0]) / k, (r[1, 0] - r[0, 1]) / k)
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        k = math.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2]) * 2.0
        q = ((r[2, 1] - r[1, 2]) / k, 0.25 * k, (r[0, 1] + r[1, 0]) / k, (r[0, 2] + r[2, 0]) / k)
    elif r[1, 1] > r[2, 2]:
        k = math.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2]) * 2.0
        q = ((r[0, 2] - r[2, 0]) / k, (r[0, 1] + r[1, 0]) / k, 0.25 * k, (r[1, 2] + r[2, 1]) / k)
    else:
        k = math.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1]) * 2.0
        q = ((r[1, 0] - r[0, 1]) / k, (r[0, 2] + r[2, 0]) / k, (r[1, 2] + r[2, 1]) / k, 0.25 * k)
    return tuple(float(v) for v in q)


def link_fit(link, cap) -> dict:
    """How the link sits relative to the capacitor, measured in the capacitor's own frame. The link may come on from
    any side of the capacitor (its studs are round) and either way round, so its seat is taken along ``u``, the
    direction in which the link's own top points away from the capacitor's axis.
    s: height of the bar's middle above its seat along u (0 = home); along, side: its offset from the seat line along
    the capacitor's axis and across it; skew_deg: angle between the bar and the capacitor's axis; way: +1 or -1, which
    way round; frame_pos, frame_rot: where the catch joint's frame on the capacitor has to be for this u and way."""
    pl, pc = np.asarray(link, float), np.asarray(cap, float)
    rc = quat_matrix(pc[3:7])
    d = rc.T @ (pl[:3] - pc[:3])
    r = rc.T @ quat_matrix(pl[3:7])
    ex = np.array([1.0, 0.0, 0.0])
    way = 1.0 if r[0, 0] >= 0.0 else -1.0
    u = r[:, 2] - r[0, 2] * ex
    n = float(np.linalg.norm(u))
    u = u / n if n > 1e-6 else np.array([0.0, 0.0, 1.0])
    rad = d - d[0] * ex
    r0 = np.column_stack([way * ex, np.cross(u, way * ex), u])
    return {"s": float(rad @ u) - LINK_H, "along": float(d[0]), "side": float(rad @ np.cross(ex, u)),
            "skew_deg": math.degrees(math.acos(float(np.clip(abs(r[0, 0]), 0.0, 1.0)))), "way": way,
            "default_way": bool(way > 0 and u[2] >= math.cos(math.radians(1.0))),
            "frame_pos": tuple(float(v) for v in LINK_H * u + r0 @ np.array(LINK_JOINT_ON_LINK)), "frame_rot": matrix_quat_wxyz(r0)}


def link_over_studs(fit, xy=CAPTURE_XY, deg=CAPTURE_DEG) -> bool:
    return bool(abs(fit["along"]) <= xy and abs(fit["side"]) <= xy and fit["skew_deg"] <= deg)


def can_capture(fit) -> bool:
    """The forks' leaves are over the studs and have reached them: the catch can take hold."""
    return bool(-0.001 <= fit["s"] <= LINK_CAPTURE and link_over_studs(fit) and (LINK_ANY_WAY or fit["default_way"]))


def _fork_local():
    """Sample points on the two forks' bare leaves (link frame): both faces of both leaves at three places along the
    stud and six from tip to root, and the slot's root."""
    out = []
    for s in (-1, 1):
        for dx in (-0.003, 0.0, 0.003):
            for y in (-LINK_LEAF[1], -LINK_LEAF[0], LINK_LEAF[0], LINK_LEAF[1]):
                out += [(s * LINK_FORK_X + dx, y, float(z)) for z in np.linspace(-(LINK_H + LINK_TIP), -(LINK_H - LINK_ROOT), 6)]
            out.append((s * LINK_FORK_X + dx, 0.0, -(LINK_H - LINK_ROOT)))
    return np.array(out)


FORK_LOCAL = _fork_local()


def link_points(link, local):
    p = np.asarray(link, float)
    return p[:3] + np.asarray(local, float) @ quat_matrix(p[3:7]).T


def fork_points(link):
    """The forks' sample points in the world."""
    return link_points(link, FORK_LOCAL)


def _box_gaps(pts, lo, hi):
    """Distances from points (n x 3) to the axis-aligned box between corners lo and hi (0 inside it)."""
    pts = np.atleast_2d(np.asarray(pts, float))
    return np.linalg.norm(np.maximum(np.maximum(np.asarray(lo, float) - pts, pts - np.asarray(hi, float)), 0.0), axis=1)


def _parts_gap(pts, parts) -> float:
    """Smallest distance from any of the points to any of the parts: cylinders (end, end, radius) or boxes (lo, hi)."""
    return min((float((_cyl_gaps(pts, *q) if len(q) == 3 else _box_gaps(pts, *q)).min()) for q in parts), default=1.0)


def _post_boxes(sign):
    """A clip post (12 x 24 mm, up to the stud's underside) and its clip's two leaves above it, as boxes."""
    x = CAP0[0] + sign * POST_DX
    return [(np.array([x - 0.006, CAP0[1] - 0.012, TOP + BT]), np.array([x + 0.006, CAP0[1] + 0.012, CAP0[2] - STUD_R])),
            (np.array([x - 0.005, CAP0[1] - 0.0062, CAP0[2] - STUD_R]), np.array([x + 0.005, CAP0[1] + 0.0062, CAP0[2] + 0.009]))]


def rig_nodes(deg, blade):
    """The rig's bare metal wired to each clip post, as two lists of cylinders (end, end, radius) and boxes (corner,
    corner). To the far post (the capacitor's +): the post and its clip, the knife switch's bare blade and pivot, the
    jaw the blade is seated in and the meter's + screw. To the near post (its -, bonded to earth): the post and its
    clip, the earth terminal's post and the meter's - screw."""
    t = math.radians(deg)
    piv = np.array(PIVOT)
    far = _post_boxes(1) + [
        (piv, piv + BLADE_BARE * np.array([math.sin(t), 0.0, math.cos(t)]), BLADE_R),
        (np.array([PIVOT[0], PIVOT[1], TOP + 0.020]), piv + np.array([0.0, 0.0, 0.008]), 0.008),
        (np.array(at(28.0, -115.0 - 74.0, 52.0)), np.array(at(28.0, -115.0 - 74.0, 61.0)), 0.0045)]
    if blade in ("discharge", "charge"):
        x = PIVOT[0] + (-0.055 if blade == "discharge" else 0.055)
        far.append((np.array([x, PIVOT[1], TOP + 0.020]), np.array([x, PIVOT[1], TOP + 0.048]), 0.007))
    near = _post_boxes(-1) + [
        (np.array([EARTH_POST[0], EARTH_POST[1], TOP + BT]), np.array([EARTH_POST[0], EARTH_POST[1], TOP + 0.027]), 0.007),
        (np.array(at(28.0, -115.0 + 74.0, 52.0)), np.array(at(28.0, -115.0 + 74.0, 61.0)), 0.0045)]
    return far, near


def circuit_nodes(cap, connected, deg, blade):
    """The conductors joined to the capacitor's + terminal and to its - terminal, as two lists. Always: its own two
    studs. While its studs are in the clips, also the rig's metal wired to the clip post each stud sits in (see
    ``rig_nodes``)."""
    c, ax = cap_axis(cap)
    h, e = CAP_L / 2, CAP_L / 2 + STUD_L
    plus, minus = [(c + ax * h, c + ax * e, STUD_R)], [(c - ax * h, c - ax * e, STUD_R)]
    if connected:
        far, near = rig_nodes(deg, blade)
        if ax[0] >= 0.0:
            plus, minus = plus + far, minus + near
        else:                                    # the capacitor was put back the other way round
            plus, minus = plus + near, minus + far
    return plus, minus


def link_contacts(link, cap, connected, deg, blade):
    """(gap from the link's fork leaves to the conductors joined to the capacitor's + terminal, gap to those joined to
    its - terminal)."""
    pts = fork_points(link)
    plus, minus = circuit_nodes(cap, connected, deg, blade)
    return _parts_gap(pts, plus), _parts_gap(pts, minus)


def _link_rods(link, bare_only):
    """The link as cylinders: its two legs' bare metal; and, unless bare_only, its legs up to the bar and the bar."""
    top = -LINK_BARE if bare_only else 0.0
    ends = link_points(link, [(s * LINK_FORK_X, 0.0, z) for s in (-1, 1) for z in (top, -(LINK_H + LINK_TIP))])
    rods = [(ends[0], ends[1], 0.008), (ends[2], ends[3], 0.008)]
    if not bare_only:
        bar = link_points(link, [(-LINK_BAR[0] / 2, 0.0, 0.0), (LINK_BAR[0] / 2, 0.0, 0.0)])
        rods.append((bar[0], bar[1], 0.011))
    return rods


def link_gaps(link, pts):
    """Distances from points to the link's outline (its bar and both legs)."""
    return np.min([_cyl_gaps(pts, a, b, r) for a, b, r in _link_rods(link, False)], axis=0)


def link_bare_gaps(link, pts):
    """Distances from points to the link's bare metal (both legs below the bar's collars)."""
    return np.min([_cyl_gaps(pts, a, b, r) for a, b, r in _link_rods(link, True)], axis=0)


def link_in_tray(link) -> bool:
    """Every corner of the link's outline seen from above (the bar's four corners and the four leaf tips) is inside
    the tray's walls."""
    hx, hy = LINK_BAR[0] / 2, LINK_BAR[1] / 2
    local = [(sx * hx, sy * hy, 0.0) for sx in (-1, 1) for sy in (-1, 1)]
    local += [(sx * LINK_FORK_X, sy * hy, -(LINK_H + LINK_TIP)) for sx in (-1, 1) for sy in (-1, 1)]
    return bool(all(abs(q[0] - TRAY_C[0]) <= TRAY_HALF[0] - TRAY_WALL and abs(q[1] - TRAY_C[1]) <= TRAY_HALF[1] - TRAY_WALL
                    for q in link_points(link, local)))


def cap_level_deg(pose) -> float:
    _, ax = cap_axis(pose)
    return math.degrees(math.asin(float(np.clip(abs(ax[2]), 0.0, 1.0))))


def in_tray(pose) -> bool:
    """The capacitor lies in the parts tray, turned any way round: every corner of its outline seen from above (the
    can's four corners and its two studs' ends) inside the tray's walls, lying level on the liner (in a valley between
    two ribs or across the ribs)."""
    c, ax = cap_axis(pose)
    flat = np.array([ax[0], ax[1], 0.0])
    n = float(np.linalg.norm(flat))
    if n < 1e-6:
        return False
    side = np.array([-ax[1], ax[0], 0.0]) / n
    pts = [c + s * ax * CAP_L / 2 + t * side * CAP_R for s in (-1, 1) for t in (-1, 1)]
    pts += [c + s * ax * (CAP_L / 2 + STUD_L) + t * side * STUD_R for s in (-1, 1) for t in (-1, 1)]
    inside = all(abs(p[0] - TRAY_C[0]) <= TRAY_HALF[0] - TRAY_WALL and abs(p[1] - TRAY_C[1]) <= TRAY_HALF[1] - TRAY_WALL for p in pts)
    lying = CAP_REST_Z - REST_Z_TOL <= c[2] <= TOP + RIB_TOP + CAP_R + REST_Z_TOL
    return bool(inside and lying and cap_level_deg(pose) <= 10.0)


# -- the gripper's outline, sampled from the arm's measured joints (its own frame: z along the fingers, x the closing
# direction; the grasp point is the origin) ------------------------------------------------------------------------
PAD_TIP = 0.013                      # the fingers reach this far beyond the grasp point ...
FINGER_BACK = 0.077                  # ... and this far behind it (90 mm in all)
PAD_THICK = 0.010
PAD_HALF_W = 0.010
BODY_HALF = (0.050, 0.025)           # the gripper's body behind the fingers
BODY_Z = (-0.134, -0.065)
SAMPLE = 0.010                       # spacing of the sampled points


def gripper_local(half_open):
    """Sample points over the whole gripper: on both fingers' inner and outer faces every SAMPLE along their length
    at three places across their width, and through the gripper's body on a grid no coarser than SAMPLE."""
    pts = [(0.0, 0.0, 0.0)]
    for sx in (-1.0, 1.0):
        for x in (sx * half_open, sx * (half_open + PAD_THICK)):
            for y in (-PAD_HALF_W, 0.0, PAD_HALF_W):
                pts += [(x, y, float(z)) for z in np.arange(PAD_TIP, -FINGER_BACK - 1e-9, -SAMPLE)]
    for x in np.linspace(-BODY_HALF[0], BODY_HALF[0], 11):
        for y in np.linspace(-BODY_HALF[1], BODY_HALF[1], 6):
            pts += [(float(x), float(y), float(z)) for z in np.linspace(BODY_Z[0], BODY_Z[1], 8)]
    return np.array(pts)


def hand_points(arm, side):
    """Points over a whole gripper (n x 3) from its measured joints and finger opening. Without joints, the grasp
    point alone."""
    tcp = np.asarray(arm["tcp"], float)[:3]
    if "joints" not in arm:
        return tcp.reshape(1, 3)
    from yam_arena import ik, station
    pos, rot = ik.tcp_pose(np.asarray(arm["joints"], float), station.BASES[side])
    half = float(np.mean(np.abs(np.asarray(arm.get("fingers", (0.0, 0.0)), float))))
    return np.asarray(pos, float) + gripper_local(half) @ np.asarray(rot, float).T


def gripper_gaps(pose, deg, robot, link=None):
    """(nearest sampled gripper point to the capacitor's outline, nearest to the rig's bare metal at the clip posts'
    voltage, nearest to the CHARGE jaw, nearest to the link's bare metal, nearest to the link's whole outline), over
    both grippers. Without a link pose the last two are 1."""
    if not robot:
        return 1.0, 1.0, 1.0, 1.0, 1.0
    pts = np.vstack([hand_points(robot[side], side) for side in ("left", "right")])
    lb, lw = (float(link_bare_gaps(link, pts).min()), float(link_gaps(link, pts).min())) if link is not None else (1.0, 1.0)
    return float(cap_gaps(pose, pts).min()), float(rig_gaps(deg, pts).min()), float(charge_jaw_gaps(pts).min()), lb, lw


class Rules:
    """The disclosed rules.

    (1) The knife switch's jaws. From JAW_IN degrees the jaw's leaves push the blade back (JAW_K per degree). Pushed to
    SEATED it is seated: the drive then holds it down on its stop at LEVER_STOP. Pulled back up past UNSEAT it is out.
    (2) The supply's rocker snaps over at ROCKER_ON degrees; past that the supply is on.
    (3) The circuit. The capacitor starts at V0 volts. While its studs are in the clips (see ``in_clips``) and the
    blade is seated in the DISCHARGE jaw, its voltage falls exponentially with time constant TAU; while the blade is
    seated in the CHARGE jaw and the supply is on, it rises toward V0 with the same time constant; otherwise it stays.
    While the shorting link's fork leaves are in contact (within LINK_TOUCH) with conductors joined to both of the
    capacitor's terminals (see ``circuit_nodes``) the capacitor is short-circuited: its voltage is zero.
    The meter shows the voltage across the clip posts: the capacitor's while its studs are in the clips, otherwise the
    supply's if that is connected (zero while the link joins the two posts' metal), otherwise zero.
    (4) Shock. A sampled point of a gripper within TOUCH of a live part at LIVE volts or more: the capacitor (its can
    and its two terminals) while it holds that voltage; the rig's bare metal (clip posts, meter terminals, the
    switch's bare blade, pivot and jaws) while the clip posts are at that voltage; the CHARGE jaw while the supply is
    on; the link's bare legs while a fork is in contact with any of these. Or the capacitor moved MOVED or more
    (either stud) from where it lay at the start while it holds that voltage. The switch's guard collar and insulated
    handle and the link's insulated bar are not live parts. Latched; a spark is drawn for SPARK_STEPS steps.
    (5) The link's forks. When the forks are over the studs (see ``can_capture``) and their leaves have reached them
    (LINK_CAPTURE above the seat) a slide joint between link and capacitor is switched on: it guides the link and
    resists it like a spring resting at LINK_REST_IN (LINK_K_IN); the catch always begins like this, however low the
    link is found, so the leaves have to be pushed over the studs. Pushed down to LINK_LATCH (INSERT_N) the leaves
    close round the studs: the spring then pulls the link home (LINK_K_HOLD) and holds it until it is pulled back up
    to LINK_UNLATCH (RETAIN_N). Above LINK_FREE the joint is switched off. The link is seated from the moment it is
    latched and within LINK_SEATED of home until it unlatches.
    (6) Early short. The link begins to short-circuit the capacitor (rule 3) while it holds SAFE volts or more: the
    shorting link put on before the capacitor was discharged. Latched. If it holds LIVE volts or more at that moment
    this is also reported as an arc and the spark is drawn for SPARK_STEPS steps.
    (7) The clips. The capacitor's slide joint (its clips) is switched off for good once it has been lifted
    CLIP_TRAVEL from where it lay."""

    def __init__(self, hz=20):
        self.dt = 1.0 / hz
        self.volts = V0
        self.blade = "open"
        self.zone = "free"
        self.on = False
        self.shock = ""
        self.early = ""                  # the link short-circuited the capacitor at SAFE volts or more (latched)
        self.arc = ""                    # ... at LIVE volts or more (reported)
        self.spark = 0
        self.left_clips = ""             # the blade's state when the capacitor last left its clips ("" while it is in them)
        self.connected = True
        self.rest = None                 # the capacitor's measured pose in its clips at the first step
        self.clip_holds = True
        self.catch = "off"               # the link's catch: "off", "in" (guided and resisted), "held" (latched)
        self.link_on = False             # the link is seated across both terminals
        self.link_proper = False         # ... and was put on in the rig, blade in DISCHARGE, capacitor below SAFE volts
        self.shorted = False
        self.bridge_ok = False           # the conditions when the present short began

    def _link(self, fit, events):
        """Rule 5: the catch's state from the link's measured fit; emits ('link', on, stiffness, target, frame_pos, frame_rot)."""
        was = self.catch
        if self.catch == "off":
            if can_capture(fit):
                self.catch = "in"            # always guided first: the leaves have to be pushed over the studs to latch
        elif fit["s"] > LINK_FREE or not link_over_studs(fit, HELD_XY, HELD_DEG):
            self.catch = "off"
        elif self.catch == "in" and fit["s"] <= LINK_LATCH:
            self.catch = "held"
        elif self.catch == "held" and fit["s"] >= LINK_UNLATCH:
            self.catch = "in"
        if self.catch != was:
            k, target = (LINK_K_HOLD, 0.0) if self.catch == "held" else (LINK_K_IN, LINK_REST_IN)
            events.append(("link", self.catch != "off", k, target, fit["frame_pos"], fit["frame_rot"], was == "off"))
        if self.catch != "held":
            self.link_on = False
        elif fit["s"] <= LINK_SEATED:
            self.link_on = True

    def update(self, step, lever, rocker, cap, robot, link=None):
        """Returns (mechanics, events). Events: ('lever', stiffness, target), ('rocker', target), ('spark', bool),
        ('needle', target), ('clip', bool), ('link', on, stiffness, target, frame_pos, frame_rot, newly_on),
        ('link_lamp', bool)."""
        events = []
        deg = lever_deg(lever)
        if self.blade == "open":
            if deg <= -SEATED:
                self.blade = "discharge"
            elif deg >= SEATED:
                self.blade = "charge"
        elif (self.blade == "discharge" and deg > -UNSEAT) or (self.blade == "charge" and deg < UNSEAT):
            self.blade = "open"
        if self.blade == "discharge":
            zone, drive = "hold-", (JAW_K, -JAW_HOLD)
        elif self.blade == "charge":
            zone, drive = "hold+", (JAW_K, JAW_HOLD)
        elif deg < -JAW_IN:
            zone, drive = "jaw-", (JAW_K, -JAW_IN)
        elif deg > JAW_IN:
            zone, drive = "jaw+", (JAW_K, JAW_IN)
        else:
            zone, drive = "free", (0.0, 0.0)
        if zone != self.zone:
            self.zone = zone
            events.append(("lever", drive[0], drive[1]))
        on = rocker_deg(rocker) > ROCKER_ON
        if on != self.on:
            self.on = on
            events.append(("rocker", ROCKER_REST[1] if on else ROCKER_REST[0]))
        if self.rest is None:
            self.rest = np.asarray(cap, float).copy()
        moved = cap_moved(cap, self.rest)
        connected = in_clips(cap, self.rest)
        if connected:
            self.left_clips = ""
        elif self.connected:
            self.left_clips = self.blade
        self.connected = connected
        if self.clip_holds and float(np.asarray(cap, float)[2] - self.rest[2]) >= CLIP_TRAVEL:
            self.clip_holds = False
            events.append(("clip", False))
        k = math.exp(-self.dt / TAU)
        if connected and self.blade == "discharge":
            self.volts *= k
        elif connected and self.blade == "charge" and self.on:
            self.volts = V0 - (V0 - self.volts) * k
        # -- the shorting link: its catch, and whether its forks join the capacitor's two terminals
        was_on = self.link_on
        fit, plus_gap, minus_gap = None, 1.0, 1.0
        if link is not None:
            fit = link_fit(link, cap)
            self._link(fit, events)
            plus_gap, minus_gap = link_contacts(link, cap, connected, deg, self.blade)
        short = plus_gap <= LINK_TOUCH and minus_gap <= LINK_TOUCH
        spark_now = False
        live_before = self.volts >= LIVE
        if short:
            if not self.shorted:
                self.bridge_ok = bool(connected and self.blade == "discharge" and self.volts < SAFE)
                if self.volts >= SAFE and not self.early:
                    self.early = "capacitor_shorted_before_it_was_discharged"
            if live_before and not self.arc:
                self.arc = "capacitor_shorted_at_50_volts_or_more"
                spark_now = True
            self.volts = 0.0
        else:
            self.bridge_ok = False
        self.shorted = short
        if self.link_on and not was_on:
            self.link_proper = bool(short and self.bridge_ok and connected and self.blade == "discharge")
        elif not self.link_on:
            self.link_proper = False
        if self.link_on != was_on:
            events.append(("link_lamp", self.link_on))
        supply_at_posts = self.on and self.blade == "charge"
        posts_joined = False                     # the link laid across the empty clip posts' metal
        if link is not None and not connected:
            far, near = rig_nodes(deg, self.blade)
            pts = fork_points(link)
            posts_joined = _parts_gap(pts, far) <= LINK_TOUCH and _parts_gap(pts, near) <= LINK_TOUCH
        meter = self.volts if connected else (V0 if (supply_at_posts and not posts_joined) else 0.0)
        cgap, rgap, jgap, lgap, lwhole = gripper_gaps(cap, deg, robot, link)
        link_live = False
        if link is not None and not short:
            touching_cap = min(plus_gap, minus_gap) <= LINK_TOUCH
            pts = fork_points(link)
            link_live = bool((live_before and touching_cap) or (meter >= LIVE and float(rig_gaps(deg, pts).min()) <= LINK_TOUCH)
                             or (self.on and float(charge_jaw_gaps(pts).min()) <= LINK_TOUCH))
        if not self.shock:
            if self.volts >= LIVE and moved >= MOVED:
                self.shock = "capacitor_moved_while_charged"
            elif self.volts >= LIVE and cgap <= TOUCH:
                self.shock = "capacitor_touched_while_charged"
            elif (meter >= LIVE and rgap <= TOUCH) or (self.on and jgap <= TOUCH) or (link_live and lgap <= TOUCH):
                self.shock = "live_metal_touched"
            if self.shock:
                spark_now = True
        if spark_now:
            self.spark = SPARK_STEPS
            events.append(("spark", True))
        elif self.spark > 0:
            self.spark -= 1
            if self.spark == 0:
                events.append(("spark", False))
        events.append(("needle", needle_target(meter)))
        mech = {"volts": round(self.volts, 3), "meter_volts": round(meter, 3), "blade": self.blade, "lever_deg": round(deg, 2),
                "supply_on": bool(self.on), "in_clips": bool(connected), "left_clips_with_blade": self.left_clips,
                "shock": self.shock, "early_short": self.early, "arc": self.arc, "moved_mm": round(1000 * moved, 2), "capacitor_gap_mm": round(1000 * cgap, 1),
                "live_metal_gap_mm": round(1000 * rgap, 1), "clips_hold": bool(self.clip_holds), "link_catch": self.catch,
                "link_on": bool(self.link_on), "link_proper": bool(self.link_proper), "link_shorts": bool(short),
                "link_s_mm": round(1000 * fit["s"], 2) if fit else 0.0, "link_gap_mm": round(1000 * lwhole, 1)}
        return mech, events
