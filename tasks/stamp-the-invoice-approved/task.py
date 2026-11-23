"""Accounts desk: "Approve the invoice."

An A5 invoice book lies loose on a desk pad; the approval box at the lower right of its top invoice is empty. A wooden rack holds three
wooden rubber stamps that look the same except for the word on top of each handle: REJECTED, APPROVED, COPY. An open
ink pad lies beside the rack. The job is to take the APPROVED stamp, press it on the ink pad, hold the loose book
with the other hand, press the stamp squarely inside the box, and put the stamp back.

Ink is a disclosed rule on measured poses (see Dynamics); the marks it leaves are drawn on the sheet.
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
import stampkit as K  # noqa: E402
from scoring import TrialScorer  # noqa: E402

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN  # noqa: E402
from yam_arena.demo import Waypoint  # noqa: E402

NAME = "stamp-the-invoice-approved"
INSTRUCTION = json.loads((_here / "task.json").read_text())["instruction"]
HZ = 20
MAX_STEPS = 1600
OBJECT_NAMES = ("sheet", *K.STAMPS)

DOWN = simkit.patch_demo()


def make_environment(embodiment, device, control_hz=HZ):
    from isaaclab_arena.environments.arena_env_builder import ArenaEnvBuilder
    from isaaclab_arena.environments.arena_env_builder_cfg import ArenaEnvBuilderCfg
    from isaaclab_arena.environments.isaaclab_arena_environment import IsaacLabArenaEnvironment
    from isaaclab_arena.scene.scene import Scene

    simkit.install()
    from yam_arena import scene as yscene

    objects = yscene.task_room("station", embodiment.rig.top_cam)
    specs = [K.pad_object(), K.rack_object(), K.ink_object(), K.pen_object(), K.sheet_object(),
             *(K.stamp_object(i) for i in range(len(K.STAMPS)))]
    objects += [yscene.task_object(s) for s in specs]
    cfg = IsaacLabArenaEnvironment(name="yam_stamp_the_invoice_approved", scene=Scene(objects), embodiment=embodiment,
                                   env_cfg_callback=yscene.env_cfg_callback(control_hz))
    return ArenaEnvBuilder(cfg, ArenaEnvBuilderCfg(num_envs=1, solve_relations=False, device=device)).make_registered()


def make_scorer():
    return TrialScorer()


class Dynamics:
    """One disclosed rule: ink. A stamp is inked once its rubber face has been pressed on the ink pad (the whole face
    inside the felt's outline and within 2 mm of it, the stamp upright within 15 degrees), and it stays inked. Each
    time an inked stamp's face touches the top page (any corner or the centre of the face over the page and within
    1.5 mm of it) it leaves one mark there, until it is lifted 3 mm clear: one press, one mark. The mark's place and
    angle are the stamp's when most of its face was down; it is whole if all four corners were down at once, and
    smeared by as far as the stamp slid over the page while touching. A mark is drawn on the page as that stamp's
    framed word and moves with the book (the first two marks of each stamp are drawn; all count). An inked stamp
    touching the desk pad or the counter is counted and reported, not drawn."""

    def __init__(self, env):
        import omni.usd
        from pxr import UsdGeom
        self.rule = K.InkRule()
        stage = omni.usd.get_context().get_stage()
        found = {}
        for prim in stage.Traverse():
            path = str(prim.GetPath())
            for k in range(len(K.MARK_VISUALS)):
                if path.endswith(f"/sheet/visual{k + 1}"):
                    found[k] = prim
        if len(found) != len(K.MARK_VISUALS):
            raise RuntimeError(f"mark visuals not found on the stage: {sorted(found)}")
        self.slots = {}
        for k, prim in found.items():
            xf = UsdGeom.Xformable(prim)
            move = xf.GetOrderedXformOps()[0]
            turn = xf.AddRotateZOp()
            self.slots[k] = (UsdGeom.Imageable(prim), move, turn)
        self.drawn = {}

    def _draw(self):
        from pxr import Gf
        seen = [0] * len(K.STAMPS)
        for j, m in enumerate(self.rule.marks):
            i = int(m[0])
            nth, seen[i] = seen[i], seen[i] + 1
            if nth >= 2 or self.drawn.get(j) == m[1:4]:
                continue
            im, move, turn = self.slots[2 * i + nth]
            move.Set(Gf.Vec3d(m[1] / 1000.0, m[2] / 1000.0, K.SHEET[2] / 2 + 0.00035 + 0.00005 * j))
            turn.Set(float(m[3]))
            im.MakeVisible()
            self.drawn[j] = m[1:4]

    def reset(self):
        self.rule.reset()
        self.drawn = {}
        for im, _, _ in self.slots.values():
            im.MakeInvisible()

    def before_step(self, step, action):
        pass

    def after_step(self, step, objects, root_poses, robot):
        out = self.rule.update(root_poses)
        self._draw()
        return out


def make_dynamics(env):
    return Dynamics(env)


# -- demo: the left hand holds the invoice book down; the right hand takes the APPROVED stamp, inks it, stamps the box and
# -- puts the stamp back in the rack ---------------------------------------------------------------------------------
REST = {"left": (0.16, 0.24, K.TOP + 0.16), "right": (0.16, -0.24, K.TOP + 0.16)}


def tilt(deg):
    p = math.radians(deg)
    a = np.array([math.sin(p), 0.0, -math.cos(p)])
    x = np.array([0.0, -1.0, 0.0])
    return np.column_stack([x, np.cross(a, x), a]), a


RG, AG = tilt(25.0)                  # the stamp hand: 25 degrees from straight down; its fingers close along y on the handle's two ends
RH, AH = tilt(0.0)                   # the holding hand: straight down
GRIP_Z = 0.058                       # the hand holds the handle this far above the stamp's rubber face
TIP = 0.013                          # the fingertips reach this far past the grasp point
HOLD_XY = (0.370, 0.125)             # where the holding hand's closed fingertips rest: the invoice's left margin
AIM = (0.003, 0.002)                 # the held stamp settles this far short of where the hand is sent; the hand aims that much further
RACK_AIM = (0.002, 0.0005)           # likewise over the rack
LIFT = 0.115                         # the stamp is carried to and from its pocket this high, clear of its neighbours' tops
SHEET_TOP = K.TOP + K.PAD_SIZE[2] + K.SHEET[2]
BOX_XY = (K.SHEET_C[0] + K.BOX_C[0], K.SHEET_C[1] + K.BOX_C[1])
SQUEEZE = (-0.019, -0.0185)          # finger targets 4 mm inside the handle's ends, so the grip stays centred; alternating the two makes each move a straight, eased line


def demo():
    up = np.array([0.0, 0.0, 1.0])
    home = np.array(K.stamp_start(K.APPROVED)) + up * (GRIP_Z - K.FOOT[2] / 2)
    ink = np.array([K.INK_C[0], K.INK_C[1], K.TOP + K.FELT[2] - 0.001 + GRIP_Z])
    box = np.array([BOX_XY[0] + AIM[0], BOX_XY[1] + AIM[1], SHEET_TOP - 0.0007 + GRIP_Z])
    back = home + np.array([RACK_AIM[0], RACK_AIM[1], 0.0])
    held = [
        (1.5, home + up * LIFT, "lift it out of the rack"),
        (2.5, ink + up * 0.070, "over the ink pad"),
        (1.5, ink, "press it on the pad"),
        (0.6, ink, "dab"),
        (1.2, ink + up * 0.070, "lift"),
        (2.5, box + up * 0.060, "over the approval box"),
        (0.6, box + up * 0.060, "steady, square to the page"),
        (1.5, box + up * 0.008, "down to just above the paper"),
        (0.7, box + up * 0.008, "steady"),
        (1.0, box, "press it in the box"),
        (0.8, box, "press"),
        (1.5, box + up * 0.060, "lift straight off"),
        (3.0, back + up * LIFT, "back over its pocket"),
        (0.6, back + up * LIFT, "steady over the pocket"),
        (1.8, back + up * 0.030, "lower it toward the pocket"),
        (0.8, back + up * 0.030, "steady"),
        (1.0, back + up * 0.013, "down to the pocket's mouth"),
        (0.8, back + up * 0.013, "steady"),
        (1.5, back + up * 0.003, "slowly into the pocket"),
    ]
    n_off = [label for _, _, label in held].index("lift straight off") + 1
    right = [
        Waypoint(1.0, REST["right"], FINGER_OPEN, "look", DOWN),
        Waypoint(1.5, (0.25, -0.24, K.TOP + 0.20), FINGER_OPEN, "turn the hand", RG),
        Waypoint(2.0, tuple(home + up * LIFT), FINGER_OPEN, "over the APPROVED stamp", RG),
        Waypoint(1.5, tuple(home), FINGER_OPEN, "fingers past the two ends of its handle", RG),
        Waypoint(1.0, tuple(home), SQUEEZE[0], "take hold", RG),
    ]
    right += [Waypoint(d, tuple(p), SQUEEZE[(k + 1) % 2], label, RG) for k, (d, p, label) in enumerate(held)]
    t_grasp = sum(w.duration for w in right[:5])
    t_off = t_grasp + sum(d for d, _, _ in held[:n_off])
    right += [
        Waypoint(0.8, tuple(back + up * 0.003), FINGER_OPEN, "let go", RG),
        Waypoint(1.2, tuple(back + up * LIFT), FINGER_OPEN, "lift the hand away", RG),
        Waypoint(2.0, REST["right"], FINGER_OPEN, "stand clear", DOWN),
        Waypoint(3.0, REST["right"], FINGER_OPEN, "done", DOWN),
    ]
    tip = np.array([HOLD_XY[0], HOLD_XY[1], SHEET_TOP - 0.001])
    hold = tip - AH * TIP
    left = [
        Waypoint(1.0, REST["left"], FINGER_CLOSED, "look", DOWN),
        Waypoint(2.5, tuple(hold + up * 0.060), FINGER_CLOSED, "over the invoice's left margin", RH),
        Waypoint(1.5, tuple(hold), -0.001, "fingertips down on the invoice", RH),
        Waypoint(t_off - 5.0, tuple(hold), FINGER_CLOSED, "hold the book still", RH),
        Waypoint(1.5, tuple(hold + up * 0.060), -0.001, "let the book go", RH),
        Waypoint(2.0, REST["left"], FINGER_OPEN, "stand clear", DOWN),
        Waypoint(3.0, REST["left"], FINGER_OPEN, "done", DOWN),
    ]
    return {"left": left, "right": right}


def agent_view(poses):
    """Measured positions under plain names. Says what each thing is as anyone can see it, never what to do."""
    s = poses["sheet"]
    out = [
        f"dark green desk pad: centre ({K.PAD_C[0]:.3f}, {K.PAD_C[1]:.3f}), 30 cm (x) by 46 cm (y), 2 mm thick",
        f"invoice book (an A5 pad of printed invoices, 4 mm thick, about 90 g) lying loose on the desk pad: centre ({s[0]:.3f}, {s[1]:.3f}, {s[2]:.3f}), 21 cm (x) by "
        f"14.8 cm (y); the text of its top invoice reads from the robot's left to its right (toward -y), the top of the page is the far edge; an "
        f"empty printed box 5 cm square, headed APPROVAL, is at its near right corner, centre "
        f"({s[0] + K.BOX_C[0]:.3f}, {s[1] + K.BOX_C[1]:.3f}) as the book lies now",
        f"wooden stamp rack: centre ({K.RACK_C[0]:.3f}, {K.RACK_C[1]:.3f}), 15 cm (x) by 7.6 cm (y), 1.2 cm tall, three "
        f"pockets 3.2 cm (x) by 5.6 cm (y) in a row along x",
    ]
    for name in K.STAMPS:
        p = poses[name]
        out.append(f"wooden rubber stamp {name}: foot centre ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}), 7.5 cm tall, handle 2.4 cm (x) "
                   f"by 4.6 cm (y), rubber face 2 cm (x) by 4.4 cm (y), about 60 g; a label on top of its handle carries a printed word")
    out += [
        f"open ink pad in a blue tin: felt centre ({K.INK_C[0]:.3f}, {K.INK_C[1]:.3f}, {K.TOP + K.FELT[2]:.3f}), felt 6.4 cm (x) "
        f"by 10.4 cm (y); its lid lies open behind it",
        "a stamp takes ink when its rubber face is pressed flat on the felt and stays inked; wherever an inked face touches "
        "the invoice it leaves a mark of its word, one for each press",
        f"ballpoint pen on the desk pad at ({K.PEN_C[0]:.3f}, {K.PEN_C[1]:.3f})",
    ]
    return out
