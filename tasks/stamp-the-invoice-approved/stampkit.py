"""Geometry, the ink rule and measurements for stamping an invoice "approved".

An accounts desk. An A5 invoice book lies loose on a desk pad; the approval box (50 x 50 mm) at the lower right of its
top invoice is empty.
A wooden rack holds three identical wooden rubber stamps that differ only in the word on the label on top of each
handle. An open tin ink pad lies beside the rack.

Frame: metres, x away from the arm bases, y left, z up; TOP is the counter. A stamp's own frame: origin at the centre
of its rubber-and-cushion foot, z up, long axis y; its text runs toward -y with the tops of the letters toward +x.
The sheet's own frame is the same way round: its text runs toward -y and "up the page" is +x. Sizes are from the CAD
models, themselves estimates of typical products.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from simkit import Part, Piece, Spring

TOP = 0.7475
ASSETS = Path(__file__).resolve().parent / "assets"
WOOD = (0.80, 0.60, 0.36)
WALNUT = (0.33, 0.21, 0.13)
GREEN = (0.09, 0.22, 0.17)
PAPER = (0.97, 0.97, 0.95)
TIN = (0.07, 0.13, 0.36)

# -- desk pad (300 x 460 x 2 mm leatherette), fixed ------------------------------------------------------------------
PAD_C = (0.370, 0.100)
PAD_SIZE = (0.300, 0.460, 0.002)

# -- the invoice: the top sheet of an A5 invoice book (148 x 210 mm, 4 mm thick, glued at its top edge), a free rigid
# -- block lying loose on the desk pad. ("sheet" below means this book and its top page.)
SHEET_C = (0.345, 0.070)
SHEET = (0.210, 0.148, 0.004)        # long side along x (up the page), short side along y
SHEET_MASS = 0.090
SHEET_Z = TOP + PAD_SIZE[2] + SHEET[2] / 2
# the empty approval box, in the sheet's frame: 50 x 50 mm at the lower right of the page
BOX_C = (-0.065, -0.037)
BOX = 0.050
MARK = (0.016, 0.040)                # a mark's outline: 16 mm up the page (x) by 40 mm along the text (y)
ANGLE_MAX = 20.0
SHIFT_MAX, TURN_MAX = 0.010, 5.0     # the book counts as left where it lay if it has moved less than 10 mm and turned less than 5 degrees

# -- rubber stamps (75 mm tall, about 60 g): rubber face 20 x 44 mm, wooden mount 26 x 50 mm, handle 24 x 46 mm ------
WORDS = ("REJECTED", "APPROVED", "COPY")     # stamp_1, stamp_2, stamp_3: nearest to farthest in the rack
STAMPS = tuple(f"stamp_{i + 1}" for i in range(3))
APPROVED = WORDS.index("APPROVED")
FOOT = (0.020, 0.044, 0.005)         # rubber die and its foam cushion: the collider's root
MOUNT = (0.026, 0.050, 0.017)
HANDLE = (0.024, 0.046, 0.053)
STAMP_H = 0.075
STAMP_MASS = 0.060
FACE = (0.020, 0.044)

# -- stamp rack (150 x 76 x 12 mm wooden tray with three pockets 32 x 56 mm, floor 5.8 mm up), fixed -----------------
RACK_C = (0.400, -0.185)
RACK = (0.150, 0.076, 0.012)
POCKET = (0.034, 0.058)              # the pockets' colliders: 1 mm more all round than drawn (32 x 56 mm), standing for the chamfer at their mouths
POCKET_DX = (-0.046, 0.0, 0.046)
RACK_FLOOR = 0.0058

# -- ink pad: an open tin 70 x 110 mm, its felt 64 x 104 mm standing 13 mm above the counter; lid open behind it ------
INK_C = (0.275, -0.310)
TIN_SIZE = (0.070, 0.110, 0.011)
FELT = (0.064, 0.104, 0.013)
TIN_FLOOR = 0.005                    # the tin's collider under the felt
FELT_SLAB, FELT_TRAVEL, FELT_K = 0.006, 0.002, 4000.0   # the felt: a 6 mm slab that gives up to 2 mm on a 4 N/mm spring
LID = (0.072, 0.112, 0.009)
LID_DX = 0.076

# -- the disclosed rule's numbers --------------------------------------------------------------------------------------
INK_GAP = 0.0015                     # "on the felt": every corner of the face this close to the felt's surface
INK_FORCE = 2.0                      # N: a stamp takes ink when it is pressed on the felt at least this hard
PRINT_FORCE = 5.0                    # N: a whole, legible print needs the die flat on the page and pressed at least this hard
BAND_MAX = 20.0                      # N: the upper end of an ordinary hand press (reported, not enforced)
TOUCH_FORCE = 0.2                    # N: below this a contact is not counted at all
PRINT_GAP = 0.0015                   # ... and prints where its inked face comes this close to the top page
LIFT_GAP = 0.003                     # a press ends when the whole face is this far off the page again
UPRIGHT = 15.0                       # inking needs the stamp upright within this many degrees
SMEAR_MAX = 0.004                    # a mark is smeared if the stamp slid further than this over the page while touching

PEN_C = (0.470, 0.255)


def _vis(names, offset, **kw):
    names = (names,) if isinstance(names, str) else names
    return dict(visual_usd=";".join(str(ASSETS / f"{n}.usdc") for n in names),
                visual_prim=";".join(f"/{n}" for n in names), visual_offset=offset, **kw)


def stamp_start(i):
    return (RACK_C[0] + POCKET_DX[i], RACK_C[1], TOP + RACK_FLOOR + FOOT[2] / 2)


PAD_COLLIDER = 0.040                 # the desk pad's collider reaches this far down into the counter


def pad_object() -> Part:
    zc = PAD_SIZE[2] - PAD_COLLIDER / 2
    return Part("desk_pad", pos=(PAD_C[0], PAD_C[1], TOP + zc), size=(PAD_SIZE[0], PAD_SIZE[1], PAD_COLLIDER), exact_z=True,
                color=GREEN, friction=(0.45, 0.35), **_vis("desk_pad", (0.0, 0.0, -zc)))


# the sheet's visuals: the printed page, then two pre-made marks per stamp (hidden until that stamp prints)
MARK_VISUALS = tuple(f"mark_{w.lower()}" for w in WORDS for _ in range(2))


def sheet_object() -> Part:
    """The invoice book: a free rigid block. Its print and the stamp marks are drawn on its top page; they have no colliders."""
    return Part("sheet", pos=(SHEET_C[0], SHEET_C[1], SHEET_Z), size=SHEET, exact_z=True, mass=SHEET_MASS, color=PAPER,
                friction=(0.40, 0.35), contact_offset=0.002, **_vis(("invoice", *MARK_VISUALS), (0.0, 0.0, -SHEET[2] / 2)))


def stamp_object(i) -> Part:
    """A stamp: a free rigid body of three boxes (foot, mount, handle)."""
    zc = FOOT[2] / 2
    pieces = (Piece("box", MOUNT, (0.0, 0.0, FOOT[2] + MOUNT[2] / 2 - zc), color=WOOD),
              Piece("box", HANDLE, (0.0, 0.0, FOOT[2] + MOUNT[2] + HANDLE[2] / 2 - zc), color=WOOD))
    return Part(STAMPS[i], pos=stamp_start(i), size=FOOT, exact_z=True, mass=STAMP_MASS, color=WOOD, friction=(1.2, 1.0),
                pieces=pieces, contact_offset=0.002, com=(0.0, 0.0, 0.030 - zc), contact_report=True,
                **_vis(("stamp", f"label_{WORDS[i].lower()}"), (0.0, 0.0, -zc)))


def rack_object() -> Part:
    """The rack: fixed. Colliders (hidden): the floor under the pockets as a slab, the rim and the dividers as bars."""
    zc = RACK_FLOOR / 2
    h = RACK[2] - RACK_FLOOR
    z = RACK_FLOOR + h / 2 - zc
    rail = (RACK[1] - POCKET[1]) / 2
    pieces = [Piece("box", (RACK[0], rail, h), (0.0, s * (POCKET[1] + rail) / 2, z), color=WALNUT) for s in (-1.0, 1.0)]
    edges = [-RACK[0] / 2]
    for dx in POCKET_DX:
        edges += [dx - POCKET[0] / 2, dx + POCKET[0] / 2]
    edges.append(RACK[0] / 2)
    for a, b in zip(edges[0::2], edges[1::2]):
        pieces.append(Piece("box", (b - a, POCKET[1], h), ((a + b) / 2, 0.0, z), color=WALNUT))
    return Part("stamp_rack", pos=(RACK_C[0], RACK_C[1], TOP + zc), size=(RACK[0], RACK[1], RACK_FLOOR), exact_z=True,
                color=WALNUT, friction=(0.6, 0.5), pieces=tuple(pieces), **_vis("stamp_rack", (0.0, 0.0, -zc)))


def ink_object() -> Part:
    """The ink pad's tin and open lid: fixed. Colliders (hidden): the tin's floor and the lid as boxes. Its felt is a
    separate sprung body (felt_object)."""
    zc = TIN_FLOOR / 2
    pieces = (Piece("box", LID, (LID_DX, 0.0, LID[2] / 2 - zc), color=TIN),)
    return Part("ink_pad", pos=(INK_C[0], INK_C[1], TOP + zc), size=(TIN_SIZE[0], TIN_SIZE[1], TIN_FLOOR), exact_z=True, color=TIN,
                friction=(0.9, 0.8), pieces=pieces, **_vis("ink_pad", (0.0, 0.0, -zc), visual_hide=("pad",)))


def felt_object() -> Part:
    """The ink pad's felt: a dark slab on a stiff spring (it gives under a stamp as inked felt does), so the force a
    stamp presses on it with is also its measured travel times FELT_K."""
    spring = Spring(axis="Z", lower=-FELT_TRAVEL, upper=0.0, stiffness=FELT_K, damping=15.0, target=0.0)
    return Part("ink_felt", pos=(INK_C[0], INK_C[1], TOP + FELT[2] - FELT_SLAB / 2), size=(FELT[0], FELT[1], FELT_SLAB), exact_z=True,
                mass=0.020, color=(0.05, 0.05, 0.09), friction=(0.9, 0.8), spring=spring, contact_offset=0.001)


def pen_object() -> Part:
    """A ballpoint pen on the desk pad: fixed dressing."""
    return Part("pen", pos=(PEN_C[0], PEN_C[1], TOP + PAD_SIZE[2] + 0.005), size=(0.010, 0.140, 0.010), exact_z=True,
                color=(0.06, 0.10, 0.35), **_vis("pen", (0.0, 0.0, -0.005)))


# -- measurements -----------------------------------------------------------------------------------

def quat_matrix(q):
    x, y, z, w = (float(v) for v in q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tilt_deg(pose) -> float:
    r = quat_matrix(np.asarray(pose, float)[3:7])
    return math.degrees(math.acos(float(np.clip(r[2, 2], -1.0, 1.0))))


def face_centre(stamp):
    """The centre of a stamp's rubber face (world)."""
    stamp = np.asarray(stamp, float)
    return stamp[:3] + quat_matrix(stamp[3:7]) @ np.array([0.0, 0.0, -FOOT[2] / 2])


def face_corners(stamp):
    stamp = np.asarray(stamp, float)
    r = quat_matrix(stamp[3:7])
    return [stamp[:3] + r @ np.array([sx * FACE[0] / 2, sy * FACE[1] / 2, -FOOT[2] / 2]) for sx in (-1, 1) for sy in (-1, 1)]


def on_felt(stamp, felt) -> bool:
    """A stamp standing on the ink pad's felt: upright, its whole face within the felt's outline and down on it."""
    if tilt_deg(stamp) > UPRIGHT:
        return False
    top = float(np.asarray(felt, float)[2]) + FELT_SLAB / 2
    return all(abs(c[0] - INK_C[0]) <= FELT[0] / 2 and abs(c[1] - INK_C[1]) <= FELT[1] / 2 and c[2] - top <= INK_GAP
               for c in face_corners(stamp))


def felt_travel(felt) -> float:
    """How far the felt is pushed down (m)."""
    return float(TOP + FELT[2] - FELT_SLAB / 2 - np.asarray(felt, float)[2])


def sheet_contact(stamp, sheet, gap):
    """How a stamp's face meets the top page: (corners of the face that are over the page and within `gap` of it,
    whether its centre is too, and the face's (x, y, yaw in degrees) in the sheet's frame). A face turned more than 60
    degrees away from the page does not count."""
    stamp, sheet = np.asarray(stamp, float), np.asarray(sheet, float)
    rs = quat_matrix(sheet[3:7])
    rel = rs.T @ quat_matrix(stamp[3:7])
    q = rs.T @ (face_centre(stamp) - sheet[:3])
    place = (float(q[0]), float(q[1]), math.degrees(math.atan2(rel[1, 0], rel[0, 0])))
    if rel[2, 2] < 0.5:
        return 0, False, place

    def near(p):
        p = rs.T @ (np.asarray(p, float) - sheet[:3])
        return bool(abs(p[0]) <= SHEET[0] / 2 and abs(p[1]) <= SHEET[1] / 2 and p[2] - SHEET[2] / 2 <= gap)

    return sum(near(c) for c in face_corners(stamp)), near(face_centre(stamp)), place


def desk_contact(stamp, sheet, gap) -> bool:
    """A stamp's face touching the desk pad or the counter beside the book (not the book, the ink pad or the rack)."""
    stamp = np.asarray(stamp, float)
    if quat_matrix(stamp[3:7])[2, 2] < 0.5:
        return False
    for p in (*face_corners(stamp), face_centre(stamp)):
        on_pad = abs(p[0] - PAD_C[0]) <= PAD_SIZE[0] / 2 and abs(p[1] - PAD_C[1]) <= PAD_SIZE[1] / 2
        if p[2] - (TOP + (PAD_SIZE[2] if on_pad else 0.0)) <= gap:
            return True
    return False


class InkRule:
    """The disclosed rule, from measured contact forces and poses. `forces` gives, for each stamp, the measured contact
    force (N) between that stamp and the invoice book ("sheet") and between it and the ink pad's felt ("felt").

    Ink: a stamp is inked once it stands on the felt (upright, whole face on it) pressed with at least INK_FORCE; it
    stays inked. Print: while an inked stamp's face touches the top page with a measured force of at least TOUCH_FORCE
    it leaves one mark there, until it is lifted LIFT_GAP clear: one press, one mark. The mark is WHOLE (a legible
    impression) only if, during that press, the die lay flat on the page (all four corners down) while the force was
    at least PRINT_FORCE; a lighter or tilted touch, the stamp's own weight included, leaves a faint or partial mark
    that still counts as a mark. The mark's place and angle are the stamp's at the first moment it was whole (else when
    most of its face was down). It is smeared by as far as the stamp slid over the page while touching. A stamp held
    just above the page, touching nothing, leaves nothing. An inked stamp touching the desk pad or the counter is
    counted and reported."""

    def __init__(self):
        self.reset()

    def reset(self):
        n = len(STAMPS)
        self.inked = [False] * n
        self.ink_force = [0.0] * n           # the force on the felt at the moment each stamp took ink
        self.marks = []                      # [stamp, x mm, y mm, yaw deg, whole 0/1, smear mm, peak force N, force when it became whole N]
        self.press = [None] * n              # the press in progress: [index into marks, most corners down so far, (x, y) at first touch]
        self.on_desk = [False] * n
        self.desk_prints = [0] * n

    def update(self, root_poses, forces=None) -> dict:
        sheet = root_poses["sheet"]
        felt = root_poses["ink_felt"]
        forces = forces or {}
        f_sheet = list(forces.get("sheet", [0.0] * len(STAMPS)))
        f_felt = list(forces.get("felt", [0.0] * len(STAMPS)))
        for i, name in enumerate(STAMPS):
            s = root_poses[name]
            if not self.inked[i]:
                if f_felt[i] >= INK_FORCE and on_felt(s, felt):
                    self.inked[i] = True
                    self.ink_force[i] = round(float(f_felt[i]), 2)
                continue
            f = float(f_sheet[i])
            n, mid, place = sheet_contact(s, sheet, PRINT_GAP)
            touch = bool((n or mid) and f >= TOUCH_FORCE)
            if self.press[i] is None:
                if touch:
                    self.marks.append([i, round(1000 * place[0], 2), round(1000 * place[1], 2), round(place[2], 2), 0, 0.0, 0.0, 0.0])
                    self.press[i] = [len(self.marks) - 1, 0, place[:2]]
            else:
                far_n, far_mid, _ = sheet_contact(s, sheet, LIFT_GAP)
                if not (far_n or far_mid):
                    self.press[i] = None
            if self.press[i] is not None and touch:
                k, best, first = self.press[i]
                m = self.marks[k]
                legible = bool(n == 4 and f >= PRINT_FORCE)
                if (legible and not m[4]) or (not m[4] and n > best):
                    m[1], m[2], m[3] = round(1000 * place[0], 2), round(1000 * place[1], 2), round(place[2], 2)
                    self.press[i][1] = max(best, n)
                if legible and not m[4]:
                    m[4], m[7] = 1, round(f, 2)
                m[5] = round(max(m[5], 1000 * math.hypot(place[0] - first[0], place[1] - first[1])), 2)
                m[6] = round(max(m[6], f), 2)
            touching = self.press[i] is None and desk_contact(s, sheet, PRINT_GAP)
            if touching and not self.on_desk[i]:
                self.desk_prints[i] += 1
                self.on_desk[i] = True
            elif self.on_desk[i] and not desk_contact(s, sheet, LIFT_GAP):
                self.on_desk[i] = False
        return {"inked": [bool(v) for v in self.inked], "marks": [list(m) for m in self.marks],
                "prints_off_sheet": [int(v) for v in self.desk_prints], "ink_force_n": [float(v) for v in self.ink_force],
                "force_on_sheet_n": [round(float(v), 2) for v in f_sheet], "force_on_felt_n": [round(float(v), 2) for v in f_felt],
                "felt_travel_mm": round(1000 * felt_travel(felt), 2)}


def mark_offset(mark):
    """(distance of the mark's centre from the box's centre in mm, its angle from the page's text in degrees)."""
    x, y, yaw = mark[1:4]
    a = (float(yaw) + 180.0) % 360.0 - 180.0
    return math.hypot(x - 1000 * BOX_C[0], y - 1000 * BOX_C[1]), a


def centre_in_box(mark) -> bool:
    x, y = mark[1:3]
    return bool(abs(x / 1000 - BOX_C[0]) <= BOX / 2 and abs(y / 1000 - BOX_C[1]) <= BOX / 2)


def outline_in_box(mark) -> bool:
    """The whole 40 x 16 mm outline of the mark lies inside the box."""
    x, y, yaw = mark[1:4]
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = x / 1000 + c * sx * MARK[0] / 2 - s * sy * MARK[1] / 2
            py = y / 1000 + s * sx * MARK[0] / 2 + c * sy * MARK[1] / 2
            if abs(px - BOX_C[0]) > BOX / 2 or abs(py - BOX_C[1]) > BOX / 2:
                return False
    return True


def sheet_corners(sheet):
    sheet = np.asarray(sheet, float)
    r = quat_matrix(sheet[3:7])
    return [sheet[:3] + r @ np.array([sx * SHEET[0] / 2, sy * SHEET[1] / 2, 0.0]) for sx in (-1, 1) for sy in (-1, 1)]


def sheet_on_pad(sheet) -> bool:
    """The whole sheet lies flat on the desk pad."""
    return all(abs(c[0] - PAD_C[0]) <= PAD_SIZE[0] / 2 and abs(c[1] - PAD_C[1]) <= PAD_SIZE[1] / 2
               and abs(c[2] - SHEET_Z) <= 0.004 for c in sheet_corners(sheet))


def sheet_shift(sheet):
    """(mm, degrees) the sheet has moved and turned from where it lay."""
    sheet = np.asarray(sheet, float)
    r = quat_matrix(sheet[3:7])
    return 1000 * math.hypot(sheet[0] - SHEET_C[0], sheet[1] - SHEET_C[1]), math.degrees(math.atan2(r[1, 0], r[0, 0]))


def sheet_in_place(sheet) -> bool:
    """The book still lies where it lay: on the desk pad, moved less than SHIFT_MAX and turned less than TURN_MAX."""
    mm, deg = sheet_shift(sheet)
    return bool(sheet_on_pad(sheet) and mm <= 1000 * SHIFT_MAX and abs(deg) <= TURN_MAX)


def over_sheet(stamp, sheet, margin=0.010) -> bool:
    stamp, sheet = np.asarray(stamp, float), np.asarray(sheet, float)
    q = quat_matrix(sheet[3:7]).T @ (stamp[:3] - sheet[:3])
    return bool(abs(q[0]) <= SHEET[0] / 2 + margin and abs(q[1]) <= SHEET[1] / 2 + margin)


def in_rack(stamp) -> bool:
    """A stamp standing in one of the rack's pockets."""
    stamp = np.asarray(stamp, float)
    return bool(tilt_deg(stamp) < 10.0 and abs(stamp[1] - RACK_C[1]) <= 0.006 and stamp[2] <= TOP + RACK_FLOOR + FOOT[2] / 2 + 0.004
                and any(abs(stamp[0] - RACK_C[0] - dx) <= 0.006 for dx in POCKET_DX))


def handle_centre(stamp):
    stamp = np.asarray(stamp, float)
    return stamp[:3] + quat_matrix(stamp[3:7]) @ np.array([0.0, 0.0, 0.050])
