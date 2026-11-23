"""Shop checkout: "Scan the shopping and put it in the bagging area."

Three items of shopping stand on the checkout counter: a carton of crackers, a small juice carton and a tin of
beans. Each has one barcode on one face. Two of the barcodes face the robot; the tin's faces away, so it cannot be
read until the tin is turned. A cordless handheld scanner stands in its cradle, a bagging tray is at one side and a
customer display has one lamp per item. Each item has to be scanned once, and only once, and put in the tray.

The scanner does not read anything optically: a read is a disclosed rule on the measured poses of the scanner and
the items (see `Dynamics`).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_here = Path(__file__).resolve().parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

import simkit  # noqa: E402
import scankit as K  # noqa: E402
from scoring import ScanCounter, TrialScorer  # noqa: E402

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN  # noqa: E402
from yam_arena.demo import Waypoint  # noqa: E402
from yam_arena.urdf import axis_angle_matrix  # noqa: E402

NAME = "scan-the-shopping-with-a-handheld-scanner"
INSTRUCTION = json.loads((_here / "task.json").read_text())["instruction"]
HZ = 20
MAX_STEPS = 2400
OBJECT_NAMES = ("scanner", *K.ITEM_NAMES)

DOWN = simkit.patch_demo()


def make_environment(embodiment, device, control_hz=HZ):
    from isaaclab_arena.environments.arena_env_builder import ArenaEnvBuilder
    from isaaclab_arena.environments.arena_env_builder_cfg import ArenaEnvBuilderCfg
    from isaaclab_arena.environments.isaaclab_arena_environment import IsaacLabArenaEnvironment
    from isaaclab_arena.scene.scene import Scene

    simkit.install()
    from yam_arena import scene as yscene

    objects = yscene.task_room("station", embodiment.rig.top_cam)
    specs = [K.mat_object(), K.cradle_object(), K.scanner_object(), K.tray_object(), K.display_object(),
             *(K.item_object(n) for n in K.ITEM_NAMES)]
    objects += [yscene.task_object(s) for s in specs]
    cfg = IsaacLabArenaEnvironment(name="yam_scan_the_shopping_with_a_handheld_scanner", scene=Scene(objects), embodiment=embodiment,
                                   env_cfg_callback=yscene.env_cfg_callback(control_hz))
    return ArenaEnvBuilder(cfg, ArenaEnvBuilderCfg(num_envs=1, solve_relations=False, device=device)).make_registered()


def make_scorer():
    return TrialScorer()


class Dynamics:
    """One disclosed rule: reading a barcode. The scanner reads an item's barcode when its window is aimed at it: the
    barcode's centre 5 to 20 cm from the window's centre and within 3 cm of the window's axis line, and the axis
    within 30 degrees of the barcode's normal, held for 0.5 s (10 steps). Nothing optical is simulated and things in
    between are ignored. On a read the item's lamp on the customer display lights and its count goes up by one. The
    same barcode is read again (a double charge) if the aim leaves it for 0.5 s and then holds on it again."""

    def __init__(self, env):
        import omni.usd
        from pxr import UsdGeom
        self.counter = ScanCounter()
        self.shown = None
        stage = omni.usd.get_context().get_stage()
        self.vis = {}
        want = {f"/customer_display/visual{2 * i - 1 + k}": (i, k == 0) for i in (1, 2, 3) for k in (0, 1)}
        for prim in stage.Traverse():
            path = str(prim.GetPath())
            for tail, key in want.items():
                if path.endswith(tail):
                    self.vis[key] = UsdGeom.Imageable(prim)
        if len(self.vis) not in (0, 6):
            raise RuntimeError(f"display lamp visuals not found on the stage: {sorted(self.vis)}")

    def _show(self):
        state = tuple(self.counter.count[n] > 0 for n in K.ITEM_NAMES)
        if self.shown != state and self.vis:
            for n, lit in zip(K.ITEM_NAMES, state):
                i = K.LAMP_OF[n]
                (self.vis[(i, True)].MakeVisible if lit else self.vis[(i, True)].MakeInvisible)()
                (self.vis[(i, False)].MakeInvisible if lit else self.vis[(i, False)].MakeVisible)()
            self.shown = state

    def reset(self):
        self.counter = ScanCounter()
        self.shown = None
        self._show()

    def before_step(self, step, action):
        pass

    def after_step(self, step, objects, root_poses, robot):
        fresh = self.counter.update(root_poses)
        self._show()
        out = {"scans": {n: int(c) for n, c in self.counter.count.items()}, "read_now": fresh[0] if fresh else ""}
        best = min(K.ITEM_NAMES, key=lambda n: K.aim(root_poses["scanner"], n, root_poses[n])[2])
        d, ang, off = K.aim(root_poses["scanner"], best, root_poses[best])
        out.update(aimed_at=best, aim_distance_cm=round(100 * d, 1), aim_angle_deg=round(ang, 1), aim_off_axis_cm=round(100 * off, 1))
        return out


def make_dynamics(env):
    return Dynamics(env)


# -- demo: the right hand takes the scanner and reads the two codes that face it; the left hand turns the tin half
# round; the right hand reads the tin and stands the scanner back in its cradle; the left hand bags the three items ---
REST = {"left": (0.16, 0.24, K.TOP + 0.16), "right": (0.16, -0.24, K.TOP + 0.16)}


def tilt(deg):
    p = math.radians(deg)
    a = np.array([math.sin(p), 0.0, -math.cos(p)])
    x = np.array([0.0, -1.0, 0.0])
    return np.column_stack([x, np.cross(a, x), a]), a


G_TILT, S_TILT, L_TILT = 70.0, 60.0, 60.0
RG, AG = tilt(G_TILT)                # taking the scanner: fingers point forward, 20 degrees below level, closing on the grip's sides
RS, AS = tilt(S_TILT)                # scanning: the hand tipped 10 degrees further down, so the window looks 20 degrees below level
RL, AL = tilt(L_TILT)                # the left hand's grip on the goods
GRASP_S = np.array([0.004, 0.0, K.S_GRASP_Z])           # the grasp point in the scanner's frame
SCAN_D = 0.100                       # the window is held this far from each barcode
ITEM_GRIP = {"bean_tin": (0.000, 0.055), "juice_carton": (0.000, 0.060), "cracker_carton": (-0.035, 0.085)}   # grasp (x from centre, height)
SLOT = {"bean_tin": (0.430, 0.232), "juice_carton": (0.300, 0.290), "cracker_carton": (0.415, 0.345)}        # where each goes in the tray
TIN_SET = (0.007, 0.001)             # the turned tin comes to rest this far from where it stood
HAND_Y = -0.004                      # the right arm settles 4 mm to its left of where it is sent at the cradle; it is sent that much further
FOOT_Y = 0.0135                      # in the hand the scanner leans 4.6 degrees to the side: its foot hangs this far to the right of where it was taken
VIA_R = ((0.20, -0.22, K.TOP + 0.17, 25.0), (0.20, -0.30, K.TOP + 0.15, 50.0))
VIA_L = ((0.20, 0.20, K.TOP + 0.17, 25.0), (0.22, 0.16, K.TOP + 0.15, 45.0))


def rz(deg):
    return axis_angle_matrix(np.array([0.0, 0.0, 1.0]), math.radians(deg))


def scan_pose(name):
    """Where and how the right hand holds the scanner to read an item where it stands (the tin: once it has been
    turned half round): the hand's grasp point and its rotation. """
    it = K.ITEMS[name]
    h = it["size"][1] if it["shape"] == "cylinder" else it["size"][2]
    yaw = 0.0 if name == "bean_tin" else math.degrees(it["yaw"])
    aim = 60.0 if name == "juice_carton" else 0.0            # the hand comes round as far as it reaches well: 10 degrees short of square
    sx, sy = TIN_SET if name == "bean_tin" else (0.0, 0.0)
    c = rz(yaw) @ np.asarray(it["code"], float)
    code = np.array([it["xy"][0] + sx + c[0], it["xy"][1] + sy + c[1], K.TOP + K.ITEM_Z0 + h / 2 + c[2]])
    hand = rz(aim) @ RS
    turn = hand @ RG.T                                       # the scanner in the hand, turned from how it stood
    return code - SCAN_D * (turn @ K.WINDOW_AXIS) - turn @ (K.WINDOW - GRASP_S), hand


def demo():
    up = np.array([0.0, 0.0, 1.0])
    foot = np.array([K.CRADLE_C[0], K.CRADLE_C[1], K.TOP + K.SOCKET_Z])
    grasp = foot + GRASP_S + np.array([0.0, HAND_Y, 0.0])
    back = grasp + np.array([0.0, FOOT_Y, 0.0])
    stage = (0.26, -0.20, K.TOP + 0.19)
    right = [
        Waypoint(1.0, REST["right"], FINGER_OPEN, "look", DOWN),
        *(Waypoint(1.0, v[:3], FINGER_OPEN, "turn the hand to face forward", tilt(v[3])[0]) for v in VIA_R),
        Waypoint(2.0, tuple(grasp - AG * 0.070), FINGER_OPEN, "behind the scanner's grip", RG),
        Waypoint(1.5, tuple(grasp), FINGER_OPEN, "fingers either side of the grip", RG),
        Waypoint(1.0, tuple(grasp), FINGER_CLOSED, "take the grip", RG),
        Waypoint(1.5, tuple(grasp + up * 0.100), FINGER_CLOSED, "lift the scanner out of its cradle", RG),
        Waypoint(1.5, stage, FINGER_CLOSED, "bring it in front of the shopping", RS),
    ]
    for name, label in (("juice_carton", "juice carton's"), ("cracker_carton", "crackers'"), ("bean_tin", "tin's")):
        p, hand = scan_pose(name)
        right += [Waypoint(1.5, tuple(p + up * 0.080), FINGER_CLOSED, f"above the aim at the {label} barcode", hand),
                  Waypoint(1.0, tuple(p), FINGER_CLOSED, f"aim at the {label} barcode", hand),
                  Waypoint(1.5, tuple(p), FINGER_CLOSED, f"hold on the {label} barcode", hand),
                  Waypoint(0.8, tuple(p + up * 0.080), FINGER_CLOSED, "lift the aim off it", hand)]
    t_scanned = sum(w.duration for w in right)
    right += [
        Waypoint(1.5, stage, FINGER_CLOSED, "draw the scanner back", RS),
        Waypoint(2.0, tuple(back + up * 0.100), FINGER_CLOSED, "over the cradle", RG),
        Waypoint(1.0, tuple(back + up * 0.100), FINGER_CLOSED, "steady", RG),
        Waypoint(2.5, tuple(back + up * 0.003), FINGER_CLOSED, "stand the scanner in its socket", RG),
        Waypoint(0.8, tuple(back + up * 0.003), FINGER_OPEN, "let go", RG),
        Waypoint(1.5, tuple(back - AG * 0.070), FINGER_OPEN, "draw back", RG),
        *(Waypoint(1.0, v[:3], FINGER_OPEN, "turn the hand back down", tilt(v[3])[0]) for v in VIA_R[::-1]),
        Waypoint(1.5, REST["right"], FINGER_OPEN, "stand clear", DOWN),
    ]

    tin = K.ITEMS["bean_tin"]
    top = np.array([tin["xy"][0], tin["xy"][1], K.TOP + K.ITEM_Z0 + tin["size"][1] - 0.028])

    def yawed(deg):
        return rz(deg) @ DOWN

    left = [
        Waypoint(1.0, REST["left"], FINGER_OPEN, "look", DOWN),
        Waypoint(2.5, tuple(top + up * 0.045), FINGER_OPEN, "over the tin", yawed(-90.0)),
        Waypoint(1.5, tuple(top), FINGER_OPEN, "fingers round its top", yawed(-90.0)),
        Waypoint(1.0, tuple(top), FINGER_CLOSED, "take the tin", yawed(-90.0)),
        Waypoint(1.0, tuple(top + up * 0.030), FINGER_CLOSED, "lift it", yawed(-90.0)),
        *(Waypoint(1.0, tuple(top + up * 0.030), FINGER_CLOSED, "turn the tin half round", yawed(a)) for a in (-45.0, 0.0, 45.0, 90.0)),
        Waypoint(1.0, tuple(top + up * 0.003), FINGER_CLOSED, "set it down, barcode toward the scanner", yawed(90.0)),
        Waypoint(0.8, tuple(top + up * 0.003), FINGER_OPEN, "let go", yawed(90.0)),
        Waypoint(1.5, tuple(top + up * 0.045), FINGER_OPEN, "lift the hand away", yawed(90.0)),
        Waypoint(2.0, REST["left"], FINGER_OPEN, "wait while the scanner reads", DOWN),
    ]
    wait = t_scanned + 1.5 - sum(w.duration for w in left)
    left.append(Waypoint(max(wait, 0.5), REST["left"], FINGER_OPEN, "wait while the scanner reads", DOWN))
    left += [Waypoint(1.0, v[:3], FINGER_OPEN, "turn the hand to face forward", tilt(v[3])[0]) for v in VIA_L]
    for name, label in (("bean_tin", "tin"), ("cracker_carton", "crackers"), ("juice_carton", "juice")):
        it = K.ITEMS[name]
        dx, gz = ITEM_GRIP[name]
        sx, sy = TIN_SET if name == "bean_tin" else (0.0, 0.0)
        face = rz(-20.0) if name == "juice_carton" else np.eye(3)     # the juice carton stands turned: the hand comes square to its sides
        rot, a = face @ RL, face @ AL
        g0 = np.array([it["xy"][0] + sx + dx, it["xy"][1] + sy, K.TOP + K.ITEM_Z0 + gz])
        g1 = np.array([SLOT[name][0] + dx, SLOT[name][1], K.TOP + K.TRAY_FLOOR + gz + 0.004])
        lift = 0.070
        left += [
            Waypoint(2.0, tuple(g0 - a * 0.090), FINGER_OPEN, f"in front of the {label}", rot),
            Waypoint(1.2, tuple(g0), FINGER_OPEN, f"fingers either side of the {label}", rot),
            Waypoint(1.0, tuple(g0), FINGER_CLOSED, f"take the {label}", rot),
            Waypoint(1.2, tuple(g0 + up * lift), FINGER_CLOSED, "lift it", rot),
            Waypoint(1.5, (0.300 + dx, g0[1], g0[2] + lift), FINGER_CLOSED, "draw it back off the mat", RL),
            Waypoint(2.0, (0.290 + dx, g1[1], g0[2] + lift), FINGER_CLOSED, "across to the bagging tray", RL),
            Waypoint(1.2, tuple(g1 + up * lift), FINGER_CLOSED, "over its place in the tray", RL),
            Waypoint(1.5, tuple(g1), FINGER_CLOSED, "set it down in the tray", RL),
            Waypoint(0.8, tuple(g1), FINGER_OPEN, "let go", RL),
            Waypoint(1.2, tuple(g1 - AL * 0.090), FINGER_OPEN, "draw back", RL),
        ]
    left += [
        *(Waypoint(1.0, v[:3], FINGER_OPEN, "turn the hand back down", tilt(v[3])[0]) for v in VIA_L[::-1]),
        Waypoint(1.5, REST["left"], FINGER_OPEN, "stand clear", DOWN),
        Waypoint(2.0, REST["left"], FINGER_OPEN, "done", DOWN),
    ]
    right.append(Waypoint(max(sum(w.duration for w in left) - sum(w.duration for w in right), 0.5), REST["right"], FINGER_OPEN, "done", DOWN))
    return {"left": left, "right": right}


def agent_view(poses):
    """Measured positions under plain names. Says what each thing is as anyone can see it, never what to do."""
    s = np.asarray(poses["scanner"], float)
    w, a = K.window(s)
    g = K.grip_centre(s)
    out = [
        f"cordless handheld barcode scanner (pistol grip, 100 x 64 x 160 mm, 180 g): the middle of its grip is at "
        f"({g[0]:.3f}, {g[1]:.3f}, {g[2]:.3f}); the grip is a bar 30 mm thick (its flat sides) and 34 mm deep; its scan window's centre "
        f"is at ({w[0]:.3f}, {w[1]:.3f}, {w[2]:.3f}) and looks along ({a[0]:.2f}, {a[1]:.2f}, {a[2]:.2f}); in the scanner's own frame "
        f"(origin under the grip's foot, grip along z) the window is at (0.068, 0, 0.128) m and looks along +x tipped 10 degrees toward -z",
        f"scanner cradle: its socket (42 x 38 mm, 18 mm deep) is at ({K.CRADLE_C[0]:.3f}, {K.CRADLE_C[1]:.3f}), floor at z {K.TOP + K.SOCKET_Z:.3f}; "
        f"the scanner stands in it on the foot of its grip",
    ]
    what = {"cracker_carton": "carton of crackers, 110 x 55 x 170 mm, 200 g", "juice_carton": "juice carton, 60 x 60 x 140 mm, 250 g",
            "bean_tin": "tin of beans, 66 mm across, 110 mm tall, 300 g"}
    for n in K.ITEM_NAMES:
        p = np.asarray(poses[n], float)
        c, nn = K.barcode(n, p)
        out.append(f"{what[n]}: centre ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}); its one barcode (45 x 30 mm) is centred at "
                   f"({c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f}) and faces ({nn[0]:.2f}, {nn[1]:.2f}, {nn[2]:.2f}); "
                   f"lamp {K.LAMP_OF[n]} on the customer display is its lamp")
    out += [
        f"bagging tray: centre ({K.TRAY_C[0]:.3f}, {K.TRAY_C[1]:.3f}), 24 cm (x) by 22 cm (y) outside, rim 22 mm high, floor at z {K.TOP + K.TRAY_FLOOR:.3f}",
        f"customer display on a pole at ({K.DISPLAY_C[0]:.3f}, {K.DISPLAY_C[1]:.3f}): three lamps, numbered 1 to 3 from its left end as the robot sees it; a lamp lights when its item has been read",
        "a barcode is read when the scanner's window is aimed at it for half a second: 5 to 20 cm away, the window's axis within 30 "
        "degrees of the barcode's normal and passing within 3 cm of its centre. Reading the same barcode again counts again",
    ]
    return out
