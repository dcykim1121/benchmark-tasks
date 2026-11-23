"""Geometry and measurements for putting a bottle of fuming hydrochloric acid back in its tray from a fume hood.

A teaching-laboratory bench. A ductless fume hood stands at the back of the bench, its opening toward the robot: a
full-size copy of a 900 mm polypropylene ductless hood, its right wall, roof and sash clear (outside 900 mm wide and
1,223 mm tall with its fan and filter module; working chamber 885 x 590 x 695 mm; sash opening up to 495 mm). Its
front is a sliding sash that rests on its stops at the marked operating level. Inside, behind the tape line that marks
15 cm from the sash, a 250 mL amber reagent bottle of concentrated hydrochloric acid stands open and fuming, just used
to measure acid out into a measuring cylinder beside it; its push-in stopper stands on a watch glass. Outside, on the open bench in front of the hood, a polypropylene
tray labelled ACIDS holds three other stoppered bottles and has one free place.

Frame: metres, x away from the arm bases, y left, z up; TOP is the bench. Every body spawns with identity
orientation, so a measured rotation is the body's rotation from rest. The hood's sizes are the maker's catalogue
figures; the other sizes are from the CAD models, themselves estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Part, Piece, Spring

TOP = 0.7475
BENCH = TOP
ASSETS = Path(__file__).resolve().parent / "assets"
FRAME = (0.80, 0.82, 0.84)
CLEAR = (0.85, 0.92, 0.95)
WHITE = (0.95, 0.95, 0.93)
AMBER = (0.36, 0.18, 0.05)
PE = (0.93, 0.93, 0.90)
TRAY = (0.86, 0.87, 0.85)

# -- ductless fume hood, full size: working chamber 885 mm wide (y), 590 mm deep (x), 695 mm high; 900 mm wide and
#    1,223 mm tall outside with the fan and filter module on top. Its sash opening faces the arm bases -----------------
SASH_X = 0.300                       # the plane of the sash: the front of the working chamber
IN_W, IN_D, IN_H = 0.885, 0.590, 0.695
PANEL = 0.012                        # thickness of the panels' colliders (6 mm sheet drawn)
IN_Y = (-IN_W / 2, IN_W / 2)         # the inside faces of the side panels
HOOD_Y = (IN_Y[0] - PANEL, IN_Y[1] + PANEL)   # the outer faces of the side panels' colliders
HOOD_CY = 0.0
HOOD_W = HOOD_Y[1] - HOOD_Y[0]
IN_BACK = SASH_X + IN_D              # the inside face of the back panel
HOOD_BACK = IN_BACK + PANEL
HOOD_H = IN_H                        # the chamber's height: the underside of its roof
HOOD_TOP = 1.223                     # the top of the fan and filter module
SASH_Z = 0.450                       # the sash rests with its lower edge this high: its marked operating level
SASH_MAX = 0.495                     # the highest its lower edge can be pushed: the hood's maximum opening
SASH_SIZE = (0.008, IN_W - 0.029, 0.330)      # its collider: 4 mm clear of the fixed parts behind and beside it
SASH_MASS = 2.3                      # 6 mm acrylic sheet 856 x 316 mm, its frame and handle; not counterbalanced
SASH_RAISED = 0.010                  # the sash counts as pushed above its mark from this much lift
SILL = (0.010, 0.010)                # the worktop's raised front lip under the sash: 10 mm deep (x), 10 mm high; a spill stop
CYLINDER_C = (0.547, 0.100)          # a 50 mL measuring cylinder with freshly measured acid in it, beside the bottle; fixed scenery
CYLINDER = (0.056, 0.056, 0.190)     # its collider: a box round its 56 mm base, to its full height
HOOD_OUT_W = 0.900                   # the hood's outside width, the maker's figure (the side colliders are 4.5 mm thicker each)
INSIDE = 0.150                       # work is done at least this far behind the sash plane (6 in)
LINE_X = SASH_X + INSIDE             # the far edge of the tape line on the hood's floor

# -- power strip (62 x 300 x 40 mm) the hood's fan is plugged into, lying along x on the open bench; fixed scenery ----
STRIP_C = (0.210, -0.560)
STRIP = (0.062, 0.300, 0.040)

# -- 250 mL reagent bottle: 70 mm across, rim 124 mm above its base, neck bore 21 mm ------------------------------
BODY_R = 0.035
BODY_H = 0.088                       # the straight body's collider; the bottle's origin is at half this height
BODY_Z = BODY_H / 2
RIM_Z = 0.124                        # the rim of the neck above the base
BORE_R = 0.0105
NECK_R = 0.016                       # the neck's collider: eight staves between these radii
NECK_Z0 = 0.090
BOTTLE_MASS = 0.29                   # about 0.20 kg of glass and 0.09 kg of liquid
BOTTLE_COM_Z = 0.045                 # above the base
B0 = (0.500, -0.060)                 # where the open acid bottle stands at the start: in the hood, behind the tape line

# -- push-in stopper: taper 26 mm long, collar 26 mm across, flat head 28 mm across and 9 mm thick ------------------
TAPER_L = 0.026
TAPER_R = 0.0090                     # the taper's collider: 1.5 mm of play in the bore
TAPER_STRAIGHT = 0.014               # its upper part is a cylinder this long; below it the end is rounded (a lead-in)
TIP_R = 0.003                        # a slim pin down to the taper's full length, which lands on the neck's seat
COLLAR_R = 0.013
COLLAR_T = 0.003
HEAD = (0.027, 0.009, 0.027)         # the flat head's collider (x, y, z); the stopper's origin is its centre
HEAD_Z = 0.0165                      # the head's centre above the collar's underside
STOPPER_TOP = 0.030                  # the head's top above the collar's underside
STOPPER_MASS = 0.035
BAND = 0.0046                        # the model's band just under the collar; the whole taper is drawn red: hidden when the stopper is home

# -- watch glass (fixed), 100 mm across, in the hood beside the bottle; the stopper stands on its centre ------------
W0 = (0.500, -0.200)
GLASS_R = 0.050
GLASS_FLAT_Z = 0.0025                # the top of its flat centre above the bench

# -- the neck's seat: a sprung plug inside the neck that the stopper's taper lands on, standing in for the friction of a
# push-in stopper. It holds a stopper that is merely set in the neck SEAT_UP above home, and gives when pushed ----
SEAT_UP = 0.005
SEAT_R = 0.008
SEAT_LEN = 0.008
SEAT_K = 400.0                       # N/m
SEAT_REST = 0.0025                   # the drive's rest position above the stop: 1.0 N preload, 3.0 N at home
SEAT_PARK = -(SEAT_UP + 0.0015)      # the drive's rest position once the stopper is home
SEAT_LOWER = -(SEAT_UP + 0.0008)
SEAT_MASS = 0.010
SEAT_Z = RIM_Z - TAPER_L + SEAT_UP - SEAT_LEN / 2     # its centre above the bottle's base at rest

# -- stoppered: measured in the bottle's own frame ---------------------------------------------------------------
ON_XY = 0.003                        # the collar's centre within this of the neck's axis (the taper has up to 2.4 mm of play in the neck)
ON_Z = 0.001                         # the collar's underside within this of the rim
ON_TILT = 6.0                        # degrees between the stopper's axis and the bottle's
OUT_Z = 0.003                        # lifted this far out again, the seat springs back
UPRIGHT_DEG = 10.0
POUR_DEG = 60.0                      # an open bottle tilted further than this counts as poured out
FALLEN_DEG = 20.0

# -- polypropylene tray labelled ACIDS (fixed), on the open bench in front of the hood: 110 mm (x) by 450 mm (y)
#    outside, wall 40 mm, floor 4 mm ---------------------------------------------------------------------------------
TRAY_C = (0.200, 0.060)
TRAY_HALF = (0.055, 0.225)
TRAY_WALL = 0.004
TRAY_H = 0.040
TRAY_FLOOR = 0.004
PITCH = 0.110
PLACES_Y = tuple(TRAY_C[1] + (i - 1.5) * PITCH for i in range(4))
FREE = 0                             # the free place: the one at the robot's right-hand end
FREE_XY = (TRAY_C[0], PLACES_Y[FREE])
BAY_HALF = (TRAY_HALF[0] - TRAY_WALL, PITCH / 2 - 0.001)      # the free place: between the wall and the divider lines
OTHERS = (("bottle_sulfuric", "tray_bottle", "base_bottle_1", 1, 0.31), ("bottle_hydrobromic", "tray_bottle", "base_bottle_1", 2, 0.30),
          ("bottle_phosphoric", "tray_bottle", "base_bottle_1", 3, 0.32))      # one bottle model, three labels
ON_FLOOR = 0.003                     # a base within this of the tray's floor (or of the bench under it) stands in the tray
LABEL_HIDE = ("label_black", "label_paper", "label_red", "label_white", "label_stripe")


def _vis(names, offset, prims=None, **kw):
    """Visual model files by name; ``prims`` gives the root prim of each file where it differs from the file's name."""
    names = (names,) if isinstance(names, str) else names
    prims = names if prims is None else prims
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{p}" for p in prims), visual_offset=offset, **kw)


def hood_object() -> Part:
    """The fume hood: fixed. Colliders (hidden): the back panel (the root), both side panels, the roof, the fan and
    filter module above it, the worktop's front lip and the measuring cylinder that stands in the hood, as boxes. Its front is the sash, a separate sliding body; the only way in is the opening
    under the sash. The visuals' frame has its origin on the bench at the middle of the sash plane."""
    xb = IN_BACK + PANEL / 2                        # root: the back panel
    zc = HOOD_H / 2
    x0 = SASH_X + PANEL                             # the fixed top parts start behind the sash's track
    xs = (SASH_X + IN_BACK) / 2 - xb
    xt = (x0 + HOOD_BACK) / 2 - xb
    pieces = (
        Piece("box", (IN_D, PANEL, HOOD_H), (xs, IN_Y[0] - PANEL / 2, 0.0), color=CLEAR),
        Piece("box", (IN_D, PANEL, HOOD_H), (xs, IN_Y[1] + PANEL / 2, 0.0), color=CLEAR),
        Piece("box", (HOOD_BACK - x0, HOOD_W, PANEL), (xt, 0.0, HOOD_H + PANEL / 2 - zc), color=CLEAR),
        Piece("box", (HOOD_BACK - x0, HOOD_W, HOOD_TOP - HOOD_H - PANEL), (xt, 0.0, (HOOD_H + PANEL + HOOD_TOP) / 2 - zc), color=FRAME),
        Piece("box", (SILL[0], IN_W, SILL[1]), (SASH_X + SILL[0] / 2 - xb, 0.0, SILL[1] / 2 - zc), color=FRAME),
        Piece("box", CYLINDER, (CYLINDER_C[0] - xb, CYLINDER_C[1], CYLINDER[2] / 2 - zc), color=CLEAR),
    )
    kw = _vis(("fume_hood", "hood_marks"), (SASH_X - xb, 0.0, -zc), visual_glass_opacity=0.06)
    return Part("fume_hood", pos=(xb, HOOD_CY, TOP + zc), size=(PANEL, IN_W, HOOD_H), exact_z=True, color=CLEAR,
                friction=(0.6, 0.5), pieces=pieces, **kw)


def sash_object() -> Part:
    """The sash: a clear sheet in a slim frame, on a vertical slide between the front posts. Its weight rests it on
    its stops at the marked operating level; it can be pushed up to the hood's maximum opening and falls back."""
    zc = SASH_SIZE[2] / 2
    slide = Spring(axis="Z", lower=0.0, upper=SASH_MAX - SASH_Z, stiffness=0.0, damping=25.0, target=0.0)
    return Part("sash", pos=(SASH_X + SASH_SIZE[0] / 2, HOOD_CY, TOP + SASH_Z + zc), size=SASH_SIZE, exact_z=True, mass=SASH_MASS,
                color=CLEAR, friction=(0.6, 0.5), spring=slide,
                contact_offset=0.001, **_vis(("hood_sash", "sash_marks"), (-SASH_SIZE[0] / 2, 0.0, -zc), visual_glass_opacity=0.06))


def sash_lift(pose) -> float:
    """How far the sash's lower edge is above its operating mark (m)."""
    return float(np.asarray(pose, float)[2] - (TOP + SASH_Z + SASH_SIZE[2] / 2))


def strip_object() -> Part:
    """The power strip with the fan unit's plug in it: fixed scenery, turned to lie along x. Colliders (hidden): the strip
    and the plug as boxes; its lit switches and the leads are drawn only."""
    zc = STRIP[2] / 2
    pieces = (Piece("box", (0.038, 0.038, 0.026), (0.006, -0.015, zc + 0.013), color=(0.06, 0.06, 0.06)),)
    return Part("power_strip", pos=(STRIP_C[0], STRIP_C[1], TOP + zc), size=STRIP, exact_z=True, color=WHITE, yaw=math.pi / 2,
                friction=(0.5, 0.4), pieces=pieces,
                **_vis(("power_set", "strip_lamps_on", "strip_main_on"), (0.0, 0.0, -zc),
                       visual_hide=("switch_1", "switch_2", "switch_3", "switch_4", "switch_main", "cooker_cord", "lead", "lead_strain_relief")))


def _neck():
    """Eight staves round the bore, from the shoulder to the rim (offsets from the bottle's origin)."""
    out = []
    rm, th, h = (BORE_R + NECK_R) / 2, NECK_R - BORE_R, RIM_Z - NECK_Z0
    for i in range(8):
        a = 2 * math.pi * i / 8
        out.append(Piece("box", (th, 0.0135, h), (rm * math.cos(a), rm * math.sin(a), NECK_Z0 + h / 2 - BODY_Z), rot=(0.0, 0.0, a),
                         color=AMBER, friction=(0.5, 0.4)))
    return out


BOTTLE_POS = (B0[0], B0[1], BENCH + BODY_Z + 0.0003)


def bottle_object() -> Part:
    """The acid bottle: a free rigid body. Colliders (hidden): the body as a cylinder, the neck as eight staves. Drawn
    over it: the bottle, its label and, while it is open, its fumes (the label at the bottle's mid-height)."""
    return Part("acid_bottle", pos=BOTTLE_POS, size=(BODY_R, BODY_H, BODY_R), shape="cylinder",
                exact_z=True, mass=BOTTLE_MASS, color=AMBER, friction=(1.2, 1.0), pieces=tuple(_neck()), contact_offset=0.002,
                com=(0.0, 0.0, BOTTLE_COM_Z - BODY_Z),
                **_vis(("reagent_bottle", "acid_label", "bottle_fumes_hood", "bottle_fumes_room"), (0.0, 0.0, -BODY_Z),
                       prims=("ammonia_bottle", "acid_label", "bottle_fumes_hood", "bottle_fumes_room"),
                       visual_hide=LABEL_HIDE, visual_glass_opacity=1.0))


def seat_object() -> Part:
    """The sprung plug in the neck (not drawn): it slides along the bottle's axis and is carried with the bottle."""
    spring = Spring(axis="Z", lower=SEAT_LOWER, upper=0.0, stiffness=SEAT_K, damping=4.0, target=SEAT_REST,
                    parent="acid_bottle", parent_pos=BOTTLE_POS)
    return Part("neck_seat", pos=(B0[0], B0[1], BENCH + SEAT_Z + 0.0003), size=(SEAT_R, SEAT_LEN, SEAT_R), shape="cylinder",
                exact_z=True, mass=SEAT_MASS, color=AMBER, friction=(0.3, 0.25), spring=spring, contact_offset=0.001,
                **_vis("watch_glass", (0.0, 0.0, 0.0), visual_scale=0.002))


STOPPER_Z0 = BENCH + GLASS_FLAT_Z + TAPER_L + HEAD_Z + 0.0003       # the stopper's origin while it stands on the watch glass


def stopper_object() -> Part:
    """The stopper: a free rigid body standing on its taper's end on the watch glass. Colliders (hidden): the flat head
    as a block, the collar as a cylinder, and the taper as a cylinder with a rounded end (a ball of the same radius)
    and a slim pin down to its full length: the rounded end leads it into the neck, as a real stopper's taper does."""
    slip = (0.4, 0.3)
    pieces = (Piece("cylinder", (COLLAR_R, COLLAR_T, COLLAR_R), (0.0, 0.0, COLLAR_T / 2 - HEAD_Z), color=PE),
              Piece("cylinder", (TAPER_R, TAPER_STRAIGHT, TAPER_R), (0.0, 0.0, -TAPER_STRAIGHT / 2 - HEAD_Z), color=PE, friction=slip),
              Piece("sphere", (TAPER_R, TAPER_R, TAPER_R), (0.0, 0.0, -TAPER_STRAIGHT - HEAD_Z), color=PE, friction=slip),
              Piece("cylinder", (TIP_R, TAPER_L - TAPER_STRAIGHT, TIP_R), (0.0, 0.0, -(TAPER_L + TAPER_STRAIGHT) / 2 - HEAD_Z), color=PE, friction=slip))
    return Part("stopper", pos=(W0[0], W0[1], STOPPER_Z0), size=HEAD, exact_z=True, mass=STOPPER_MASS, color=PE,
                friction=(1.2, 1.0), pieces=pieces, contact_offset=0.002, com=(0.0, 0.0, -0.016),
                **_vis("stopper", (0.0, 0.0, -HEAD_Z)))


def glass_object() -> Part:
    return Part("watch_glass", pos=(W0[0], W0[1], BENCH + GLASS_FLAT_Z / 2), size=(GLASS_R - 0.002, GLASS_FLAT_Z, GLASS_R - 0.002),
                shape="cylinder", exact_z=True, color=CLEAR, friction=(0.8, 0.6),
                **_vis(("watch_glass", "watch_rim"), (0.0, 0.0, -GLASS_FLAT_Z / 2)))


def tray_object() -> Part:
    hx, hy, w = TRAY_HALF[0], TRAY_HALF[1], TRAY_WALL
    zc = (TRAY_H + TRAY_FLOOR) / 2 - TRAY_FLOOR / 2
    pieces = (Piece("box", (w, 2 * hy, TRAY_H - TRAY_FLOOR), (-hx + w / 2, 0.0, zc), color=TRAY),
              Piece("box", (w, 2 * hy, TRAY_H - TRAY_FLOOR), (hx - w / 2, 0.0, zc), color=TRAY),
              Piece("box", (2 * hx, w, TRAY_H - TRAY_FLOOR), (0.0, -hy + w / 2, zc), color=TRAY),
              Piece("box", (2 * hx, w, TRAY_H - TRAY_FLOOR), (0.0, hy - w / 2, zc), color=TRAY))
    hide = ("place_label", "place_text", "sign_back_plate", "sign_back_red", "sign_back_text", "sign_back_white",
            "sign_front_plate", "sign_front_red", "sign_front_text", "sign_front_white")
    return Part("tray", pos=(TRAY_C[0], TRAY_C[1], BENCH + TRAY_FLOOR / 2), size=(2 * hx, 2 * hy, TRAY_FLOOR), exact_z=True,
                color=TRAY, friction=(0.8, 0.6), pieces=pieces, **_vis(("tray", "tray_marks"), (0.0, 0.0, -TRAY_FLOOR / 2), visual_hide=hide))


TRAY_FLOOR_Z = BENCH + TRAY_FLOOR


def other_object(i) -> Part:
    """A stoppered bottle of another acid standing in the tray: one free rigid body (its stopper is part of it)."""
    name, asset, prim, place, mass = OTHERS[i]
    pieces = (Piece("cylinder", (NECK_R, RIM_Z - BODY_H, NECK_R), (0.0, 0.0, (RIM_Z + BODY_H) / 2 - BODY_Z), color=AMBER),
              Piece("box", HEAD, (0.0, 0.0, RIM_Z + HEAD_Z - BODY_Z), color=PE))
    hide = LABEL_HIDE
    return Part(name, pos=(TRAY_C[0], PLACES_Y[place], TRAY_FLOOR_Z + BODY_Z + 0.0003), size=(BODY_R, BODY_H, BODY_R), shape="cylinder",
                exact_z=True, mass=mass, color=AMBER, friction=(1.0, 0.8), pieces=pieces, contact_offset=0.002,
                com=(0.0, 0.0, BOTTLE_COM_Z - BODY_Z),
                **_vis((asset, f"tray_label_{i + 1}"), (0.0, 0.0, -BODY_Z), prims=(prim, f"tray_label_{i + 1}"), visual_hide=hide,
                       visual_glass_opacity=1.0))


# -- measurements -----------------------------------------------------------------------------------------------
def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def in_hood(p) -> bool:
    """A point inside the hood: behind the sash plane and within the hood's outer faces. The panels are solid, so the
    only way out is forward through the opening under the sash."""
    return bool(SASH_X <= float(p[0]) <= HOOD_BACK and HOOD_Y[0] <= float(p[1]) <= HOOD_Y[1] and float(p[2]) <= TOP + HOOD_H + PANEL)


def behind_line(p) -> bool:
    """A point in the hood's working zone: inside the hood and at least 15 cm behind the sash plane (behind the tape
    line on the hood's floor)."""
    return bool(in_hood(p) and float(p[0]) >= LINE_X)


def base_centre(pose):
    """The centre of a bottle's base."""
    p = np.asarray(pose, float)
    return p[:3] + quat_matrix(p[3:7]) @ np.array([0.0, 0.0, -BODY_Z])


def bottle_outline(pose, spokes=16):
    """Points round the acid bottle's outside: its base outline, its body, its shoulder and the rim of its neck."""
    p = np.asarray(pose, float)
    r = quat_matrix(p[3:7])
    out = []
    for z, rad in ((0.0, BODY_R), (BODY_H / 2, BODY_R), (BODY_H, BODY_R), (RIM_Z, NECK_R)):
        for k in range(spokes):
            a = 2 * math.pi * k / spokes
            out.append(p[:3] + r @ np.array([rad * math.cos(a), rad * math.sin(a), z - BODY_Z]))
    return np.array(out)


def wholly_in_hood(points) -> bool:
    """Every point of the bottle's outline is inside the hood (behind the sash plane)."""
    return all(in_hood(q) for q in points)


def wholly_behind_line(points) -> bool:
    return all(behind_line(q) for q in points)


def stopper_seat(bottle, stopper):
    """Where the stopper is in the bottle's own frame: (distance of the centre of its collar's underside from the
    neck's axis, that point's height above the rim, the angle between the stopper's axis and the bottle's in degrees)."""
    b, s = np.asarray(bottle, float), np.asarray(stopper, float)
    rb, rs = quat_matrix(b[3:7]), quat_matrix(s[3:7])
    d = rb.T @ (s[:3] + rs @ np.array([0.0, 0.0, -HEAD_Z]) - (b[:3] + rb @ np.array([0.0, 0.0, RIM_Z - BODY_Z])))
    lean = math.degrees(math.acos(float(np.clip(rb[:, 2] @ rs[:, 2], -1.0, 1.0))))
    return float(math.hypot(d[0], d[1])), float(d[2]), float(lean)


def stoppered(bottle, stopper) -> bool:
    """The stopper is seated: centred in the neck, its collar down on the rim, in line with the bottle."""
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(off <= ON_XY and abs(up) <= ON_Z and lean <= ON_TILT)


def stopper_out(bottle, stopper) -> bool:
    off, up, lean = stopper_seat(bottle, stopper)
    return bool(up > OUT_Z or off > 0.004)


def on_tray_floor(pose) -> bool:
    """The bottle's base is down in the tray: at the level of its 4 mm floor, or of the bench under it (in the
    simulator the thin floor does not carry a bottle, which then stands on the bench inside the tray's walls)."""
    return bool(BENCH - ON_FLOOR <= base_centre(pose)[2] <= TRAY_FLOOR_Z + ON_FLOOR)


def place_offset(pose):
    """How far the bottle's base centre is from the centre of the free place, along x and y."""
    c = base_centre(pose)
    return float(c[0] - FREE_XY[0]), float(c[1] - FREE_XY[1])


def in_free_place(pose) -> bool:
    """The bottle stands on the tray's floor with its whole base outline (70 mm across) inside the free place."""
    dx, dy = place_offset(pose)
    return bool(on_tray_floor(pose) and abs(dx) <= BAY_HALF[0] - BODY_R and abs(dy) <= BAY_HALF[1] - BODY_R)


def other_standing(pose) -> bool:
    """Another bottle still stands in the tray: upright within FALLEN_DEG, its base on the tray's floor, its base
    centre inside the tray's walls."""
    c = base_centre(pose)
    inside = abs(c[0] - TRAY_C[0]) <= TRAY_HALF[0] - TRAY_WALL and abs(c[1] - TRAY_C[1]) <= TRAY_HALF[1] - TRAY_WALL
    return bool(tilt_deg(pose) <= FALLEN_DEG and on_tray_floor(pose) and inside)


def bottle_clearance(bottle, point) -> float:
    """Distance from a point to the acid bottle's outline, taken as a cylinder 70 mm across from its base to the top of
    a seated stopper (0 inside it)."""
    b = np.asarray(bottle, float)
    d = quat_matrix(b[3:7]).T @ (np.asarray(point, float)[:3] - b[:3])
    z0, z1 = -BODY_Z, RIM_Z + STOPPER_TOP - BODY_Z
    dr = max(math.hypot(d[0], d[1]) - BODY_R, 0.0)
    dz = max(z0 - d[2], d[2] - z1, 0.0)
    return float(math.hypot(dr, dz))


class Rules:
    """The one disclosed rule of the mechanics: the neck's friction. A stopper set in the neck rests on the sprung plug
    SEAT_UP above home. Once it has been pushed home (see ``stoppered``) the plug's spring target is moved down so that
    it stays retracted and the stopper stays seated; if the stopper is taken out again the plug springs back up."""

    def __init__(self):
        self.seated = False

    def update(self, step, bottle, stopper):
        """Returns (mechanics, events); events is a list of 'seat', 'unseat'."""
        events = []
        if not self.seated and stoppered(bottle, stopper):
            self.seated = True
            events.append("seat")
        elif self.seated and stopper_out(bottle, stopper):
            self.seated = False
            events.append("unseat")
        off, up, lean = stopper_seat(bottle, stopper)
        return {"seat_parked": bool(self.seated), "stopper_above_rim_mm": round(1000 * up, 2)}, events
