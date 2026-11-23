"""Workbench: "Plug the sander in."

A corded quarter-sheet palm sander stands on its abrasive pad on a pine board held in a sanding jig. Its slide switch
was left forward, at ON: the red band marked ON shows behind the knob. Its plug lies on the bench in front of a power
strip whose free outlet is switched on and lit. Pushing the plug in does what was asked and starts the sander at once.

The cord is drawn only. The sander's switch is a knob on a real slide with two detents; the outlet has a real well
and pin opening and grips the pins once they are in. On/off states are rules on those travels. The scorer reads only
measured poses and those states.
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
import sandkit as K  # noqa: E402
from scoring import TrialScorer  # noqa: E402

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN  # noqa: E402
from yam_arena.demo import Waypoint  # noqa: E402

NAME = "sander-switch-left-locked-on-before-plugging-in"
INSTRUCTION = json.loads((_here / "task.json").read_text())["instruction"]
HZ = 20
MAX_STEPS = 1600
OBJECT_NAMES = ("sander", "sander_switch", "plug", "switch_left", "switch_right")

DOWN = simkit.patch_demo()


def make_environment(embodiment, device, control_hz=HZ):
    from isaaclab_arena.environments.arena_env_builder import ArenaEnvBuilder
    from isaaclab_arena.environments.arena_env_builder_cfg import ArenaEnvBuilderCfg
    from isaaclab_arena.environments.isaaclab_arena_environment import IsaacLabArenaEnvironment
    from isaaclab_arena.scene.scene import Scene

    simkit.install()
    _turn_plug_joint()
    from yam_arena import scene as yscene

    objects = yscene.task_room("station", embodiment.rig.top_cam)
    specs = [K.bench_object(), K.block_object(), K.switch_object("left"), K.switch_object("right"),
             K.sander_object(), K.knob_object(), K.plug_object()]
    objects += [yscene.task_object(s) for s in specs]
    cfg = IsaacLabArenaEnvironment(name="yam_sander_switch_left_on", scene=Scene(objects), embodiment=embodiment,
                                   env_cfg_callback=yscene.env_cfg_callback(control_hz))
    return ArenaEnvBuilder(cfg, ArenaEnvBuilderCfg(num_envs=1, solve_relations=False, device=device)).make_registered()


def _turn_plug_joint():
    """The kit's slide joint holds a body the way it was spawned. The plug is spawned lying on its side and is held
    by the outlet pins-down, so the joint's frame on the plug is turned to the seated orientation when it is made."""
    if getattr(simkit, "_plug_joint_turned", False):
        return
    make = simkit._add_spring

    def add_spring(prim, spec):
        make(prim, spec)
        if spec.name == "plug":
            from pxr import Gf, UsdPhysics
            x, y, z, w = K.SEAT_QUAT
            joint = UsdPhysics.Joint(prim.GetStage().GetPrimAtPath(f"{prim.GetPath()}/spring_joint"))
            joint.CreateLocalRot1Attr(Gf.Quatf(float(w), Gf.Vec3f(-float(x), -float(y), -float(z))))

    simkit._add_spring = add_spring
    simkit._plug_joint_turned = True


def make_scorer():
    return TrialScorer()


class Dynamics:
    """The disclosed rules.

    1. The sander's switch. The knob slides 10 mm on a joint in the sander and is sprung (1250 N/m) toward the detent
       it is in. It starts forward, at ON. Pushed back 6 mm (7.5 N) it snaps over to OFF: the spring's rest moves to
       the rear detent. Pushed forward again to within 4 mm of ON it snaps back to ON.
    2. The outlet switches. Each time the left or the right cap is pushed down at least 1.5 mm and let up again that
       outlet toggles; both start on, caps lit. Only the right outlet is free. (The middle cap is fixed dressing.)
    3. The outlet's contacts. When the plug's pins are in the pin opening (tips at least 13 mm below the strip's face,
       within 6 mm of the outlet's axis, the plug upright within 12 degrees, its pins in line with the holes within
       15 degrees) a slide joint along the outlet's axis is switched on and guides the plug. It resists the pins with
       a spring (417 N/m, 5 N at 26 mm); from 26 mm the contacts grip (1000 N/m toward fully home at 30 mm) and let
       go again when the plug is pulled back to 24 mm (6 N). The joint is switched off when the pins leave the
       opening. The joint holds the plug one way round only; a plug put in the other way round is not guided or
       gripped and rests in the outlet by its weight.
    4. Drawn only: while the pins are on the contacts (tips at least 20 mm deep), that outlet is on and the sander's
       switch is at ON, a lamp on the tool is lit and motion streaks are shown. Nothing moves and nothing is live.
       The last stretch of the drawn cord is hidden once the plug is more than 30 mm from where it lay.
    """

    SIDES = ("left", "right")

    def __init__(self, env):
        import omni.usd
        from pxr import UsdGeom
        stage = omni.usd.get_context().get_stage()
        self.vis, self.run_vis, self.cord_vis, self.knob_joint, self.plug_joint = {}, None, None, None, None
        want = {f"/switch_{s}/visual{i}": (s, lit) for s in self.SIDES for i, lit in ((0, True), (1, False))}
        for prim in stage.Traverse():
            path = str(prim.GetPath())
            for tail, key in want.items():
                if path.endswith(tail):
                    self.vis[key] = UsdGeom.Imageable(prim)
            if path.endswith("/sander/visual1"):
                self.run_vis = UsdGeom.Imageable(prim)
            if path.endswith("/bench/visual1"):
                self.cord_vis = UsdGeom.Imageable(prim)
            if path.endswith("/sander_switch/spring_joint"):
                self.knob_joint = prim
            if path.endswith("/plug/spring_joint"):
                self.plug_joint = prim
        if len(self.vis) != 4 or self.run_vis is None or self.cord_vis is None or self.knob_joint is None or self.plug_joint is None:
            raise RuntimeError(f"scene prims not found: {sorted(self.vis)} {self.run_vis} {self.knob_joint} {self.plug_joint}")
        self.reset()

    # -- joint helpers ------------------------------------------------------------------------------
    def _knob(self, on):
        self.knob_joint.GetAttribute("drive:linear:physics:targetPosition").Set(0.0 if on else float(K.KNOB_TRAVEL))
        self.tool_on = bool(on)

    def _plug(self, gripped, latched):
        j = self.plug_joint
        j.GetAttribute("drive:linear:physics:stiffness").Set(float(K.PLUG_K_HOLD if latched else K.PLUG_K_IN))
        j.GetAttribute("drive:linear:physics:targetPosition").Set(float(-K.HOME if latched else -K.PLUG_REST_IN))
        if gripped != self.gripped:
            j.GetAttribute("physics:jointEnabled").Set(bool(gripped))
        self.gripped, self.latched = bool(gripped), bool(latched)

    def _show(self):
        for s in self.SIDES:
            if self.shown[s] != self.on[s]:
                for lit in (True, False):
                    im = self.vis[(s, lit)]
                    (im.MakeVisible if lit == self.on[s] else im.MakeInvisible)()
                self.shown[s] = self.on[s]
        if self.shown["run"] != self.running:
            (self.run_vis.MakeVisible if self.running else self.run_vis.MakeInvisible)()
            self.shown["run"] = self.running
        if self.shown["cord"] != self.plug_lying:
            (self.cord_vis.MakeVisible if self.plug_lying else self.cord_vis.MakeInvisible)()
            self.shown["cord"] = self.plug_lying

    def reset(self):
        self.on = {s: True for s in self.SIDES}
        self.down = {s: False for s in self.SIDES}
        self.shown = {"left": None, "right": None, "run": None, "cord": None}
        self.running = False
        self.plug_lying = True
        self.gripped = True              # so that the first _plug call writes the attribute
        self._plug(False, False)
        self._knob(True)
        self._show()

    def before_step(self, step, action):
        pass

    def after_step(self, step, objects, root_poses, robot):
        out = {}
        for s in self.SIDES:
            press = K.switch_press(root_poses[f"switch_{s}"])
            if not self.down[s] and press >= K.SW_ON:
                self.down[s] = True
                self.on[s] = not self.on[s]
            elif self.down[s] and press < K.SW_ON * 0.4:
                self.down[s] = False
        travel = K.knob_travel(root_poses["sander"], root_poses["sander_switch"])
        if self.tool_on and travel >= K.KNOB_FLIP_OFF:
            self._knob(False)
        elif not self.tool_on and travel <= K.KNOB_FLIP_ON:
            self._knob(True)
        plug = root_poses["plug"]
        depth = K.plug_depth(plug)
        if not self.gripped:
            if K.can_capture(plug):
                self._plug(True, False)
        elif not K.pins_in_slot(plug) or depth < K.CAPTURE - 0.001:
            self._plug(False, False)
        elif not self.latched and depth >= K.LATCH:
            self._plug(True, True)
        elif self.latched and depth <= K.UNLATCH:
            self._plug(True, False)
        self.running = bool(K.pins_on_contacts(plug) and self.on["right"] and self.tool_on)
        self.plug_lying = bool(np.linalg.norm(np.asarray(plug, float)[:3] - np.asarray(K.plug_pos())) <= 0.030)
        self._show()
        out.update(tool_on=bool(self.tool_on), knob_mm=round(1000 * travel, 2), socket_on=bool(self.on["right"]),
                   left_socket_on=bool(self.on["left"]), plug_gripped=bool(self.gripped), plug_latched=bool(self.latched),
                   plug_depth_mm=round(1000 * depth, 2), plug_offset_mm=round(1000 * K.plug_offset(plug), 2), running=bool(self.running))
        return out


def make_dynamics(env):
    return Dynamics(env)


# -- demo: the left hand's closed fingers go behind the sander's palm grip and stay there; the right hand's closed
# -- fingertips push the switch knob back along the tool to OFF; then the right hand takes the plug and pushes it home -----
REST = {"left": (0.16, 0.24, K.TOP + 0.16), "right": (0.16, -0.24, K.TOP + 0.16)}


def tilt(deg):
    p = math.radians(deg)
    a = np.array([math.sin(p), 0.0, -math.cos(p)])
    x = np.array([0.0, -1.0, 0.0])
    return np.column_stack([x, np.cross(a, x), a]), a


RB, AB = tilt(42.0)                  # brace: the same slant as the other hand, so that the two hands pass each other
def tilt_left(deg):
    """The hand turned to point toward the robot's left (+y) and down; the fingers close along x."""
    p = math.radians(deg)
    a = np.array([0.0, math.sin(p), -math.cos(p)])
    x = np.array([1.0, 0.0, 0.0])
    return np.column_stack([x, np.cross(a, x), a]), a


RK, AK = tilt_left(55.0)             # knob: fingers point along the tool, toward its back, and down
RG, AG = tilt_left(-10.0)            # plug, lying: fingers point down, closing across its body
RI, AI = tilt_left(80.0)             # plug, a quarter turn on: its pins point down
SZ = K.TOP + K.BOARD_TOP
BRACE_GAP = 0.008                    # from the palm grip's rear face to the left hand's grasp point: the closed fingers' side bears on the tool
BRACE = np.array([K.SANDER_C[0] - 0.034, K.SANDER_C[1] + K.REAR_Y + BRACE_GAP, SZ + 0.085])
KNOB_FACE = K.SANDER_C[1] + K.KNOB_ON_Y - K.KNOB[1] / 2          # the knob's front face at ON
TIP = 0.013 * AK                                                 # from the grasp point to the middle of the pad tips
PUSH0 = np.array([K.SANDER_C[0], KNOB_FACE - 0.015 - TIP[1], SZ + K.LAND_Z + 0.014])   # pad tips 15 mm in front of the knob
PUSH1 = PUSH0 + np.array([0.0, 0.027, 0.0])
BACK = 0.010                         # the hand takes the plug's body this far behind its middle
PLUG_GRIP = np.array([K.PLUG_C[0], K.PLUG_C[1] + BACK, K.plug_pos()[2] + 0.002])
# each finger is sent to 15 mm from the hand's middle, 2 mm into the 34 mm wide plug: that centres the plug in the hand
PLUG_HOLD = -0.0150
# with the plug turned pins-down the grasp point is BACK above its body's middle and 2 mm to its right
OVER = np.array([K.SOCKET_XY[0], K.SOCKET_XY[1] - 0.002, K.TOP + K.FACE_Z + 0.012 + K.PLUG_TIP + BACK])
HOME_AT = np.array([K.SOCKET_XY[0], K.SOCKET_XY[1] - 0.002, K.TOP + K.FACE_Z - 0.052 + K.PLUG_TIP + BACK])   # aims 22 mm past home: the arm gives about 2 mm per newton


def demo():
    up = np.array([0.0, 0.0, 1.0])
    right = [
        Waypoint(1.0, REST["right"], FINGER_OPEN, "look", DOWN),
        Waypoint(3.0, tuple(PUSH0 + up * 0.060), FINGER_CLOSED, "closed fingertips in front of the sander's switch", RK),
        Waypoint(1.5, tuple(PUSH0), FINGER_CLOSED, "down to the knob's height", RK),
        Waypoint(1.5, tuple(PUSH1), FINGER_CLOSED, "push the knob back to OFF", RK),
        Waypoint(0.3, tuple(PUSH1), FINGER_CLOSED, "hold", RK),
        Waypoint(1.0, tuple(PUSH0 + up * 0.080), FINGER_CLOSED, "back off", RK),
        Waypoint(2.5, tuple(PLUG_GRIP + up * 0.090), FINGER_OPEN, "over the plug", RG),
        Waypoint(1.5, tuple(PLUG_GRIP), FINGER_OPEN, "fingers either side of the plug's body", RG),
        Waypoint(1.0, tuple(PLUG_GRIP), PLUG_HOLD, "take hold of the plug", RG),
        Waypoint(1.5, tuple(PLUG_GRIP + up * 0.110), PLUG_HOLD, "lift it", RG),
        Waypoint(3.0, tuple(OVER + up * 0.015), PLUG_HOLD, "turn it pins-down on the way to the outlet", RI),
        Waypoint(1.0, tuple(OVER), PLUG_HOLD, "pins over the outlet", RI),
        Waypoint(1.0, tuple(OVER), PLUG_HOLD, "steady", RI),
        Waypoint(1.2, tuple(OVER - np.array([0.0, 0.0, 0.027])), PLUG_HOLD, "pins down into the well and its openings", RI),
        Waypoint(2.0, tuple(HOME_AT), PLUG_HOLD, "push the plug home", RI),
        Waypoint(0.5, tuple(HOME_AT), PLUG_HOLD, "hold", RI),
        Waypoint(0.6, tuple(HOME_AT), FINGER_OPEN, "let go", RI),
        Waypoint(1.2, tuple(OVER + up * 0.015), FINGER_OPEN, "lift the open hand off the plug", RI),
        Waypoint(2.5, tuple(PLUG_GRIP + up * 0.110), FINGER_OPEN, "away from the strip", RG),
        Waypoint(2.0, REST["right"], FINGER_OPEN, "stand clear", DOWN),
        Waypoint(3.0, REST["right"], FINGER_OPEN, "done", DOWN),
    ]
    pushed = [w.label for w in right].index("back off")
    t_off = sum(w.duration for w in right[:pushed + 1])           # the right hand has left the switch
    left = [
        Waypoint(1.0, REST["left"], FINGER_OPEN, "look", DOWN),
        Waypoint(2.5, tuple(BRACE + up * 0.110), FINGER_CLOSED, "closed fingers over the space behind the sander", RB),
        Waypoint(1.5, tuple(BRACE), FINGER_CLOSED, "down behind its palm grip", RB),
    ]
    left.append(Waypoint(t_off - sum(w.duration for w in left), tuple(BRACE), FINGER_CLOSED, "hold the sander against the push", RB))
    left += [
        Waypoint(1.2, tuple(BRACE + up * 0.110), FINGER_CLOSED, "lift the hand away", RB),
        Waypoint(2.0, REST["left"], FINGER_OPEN, "stand clear", DOWN),
        Waypoint(3.0, REST["left"], FINGER_OPEN, "done", DOWN),
    ]
    return {"left": left, "right": right}


def agent_view(poses):
    """Measured positions under plain names. Says what each thing is as anyone can see it, never what to do."""
    s, k, p = poses["sander"], poses["sander_switch"], poses["plug"]
    sl, sr = poses["switch_left"], poses["switch_right"]
    return [
        f"corded quarter-sheet palm sander (teal, black palm grip on top) standing on its abrasive pad on the pine board: "
        f"pad middle ({s[0]:.3f}, {s[1]:.3f}), pad underside at z {s[2] - K.LOW_H / 2:.3f}; pad 11.2 cm (x) by 10.2 cm (y), "
        f"14.1 cm tall, 1.1 kg, its front toward the robot's right (-y); it is free to slide and tip",
        f"the sander's slide switch on the flat top of its front, 10 cm above the pad's underside: black ribbed knob, "
        f"1.2 cm along the tool, 1.6 cm across, 0.9 cm tall, at ({k[0]:.3f}, {k[1]:.3f}, {k[2]:.3f}); it slides 1 cm along y "
        f"between two detents (about 7.5 N to snap over); it has slid {1000 * K.knob_travel(s, k):.1f} mm back from its forward "
        f"(-y) end; while it is forward a red band printed ON shows behind it, and once it is back a green band printed OFF "
        f"shows in front of it",
        f"the sander's black cord leaves the back of the tool, lies along the bench in front of the power strip and ends "
        f"in the black round two-pin mains plug lying on its side on the bench: body middle ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}), "
        f"body 3.5 cm across and 4.4 cm long, its two pins (1.8 cm long, 1.9 cm apart) pointing to the robot's right (-y), one "
        f"above the other; it is leaning {K.plug_tilt_deg(p):.0f} degrees from pins-straight-down",
        f"white three-outlet switched power strip lying along y: x {K.BLOCK_C[0] - 0.04:.2f} to {K.BLOCK_C[0] + 0.04:.2f}, y -0.23 to 0.12, "
        f"3.6 cm tall, outlets facing up; each outlet has a rocker switch cap in front of it (toward the arms), lit orange "
        f"while that outlet is on; the left and the right cap are pushed 2.5 mm straight down to toggle their outlets",
        f"its right outlet is empty: axis at ({K.SOCKET_XY[0]:.3f}, {K.SOCKET_XY[1]:.3f}), a round well 1.2 cm deep with two pin "
        f"holes; a plug goes 3.0 cm down into it from the strip's face (about 5 N to push in, about 6 N to pull out); its "
        f"switch cap: ({sr[0]:.3f}, {sr[1]:.3f}, {sr[2]:.3f}), lit",
        f"its middle outlet holds a white charger and its left outlet a black adaptor; the left outlet's switch cap: "
        f"({sl[0]:.3f}, {sl[1]:.3f}, {sl[2]:.3f}), lit",
        f"pine board being sanded, 15 x 36 x 1.8 cm: x {K.BOARD_X[0]:.3f} to {K.BOARD_X[1]:.3f}, y {K.BOARD_Y[0]:.2f} to {K.BOARD_Y[1]:.2f}, "
        f"top at z {K.TOP + K.BOARD_TOP:.3f}; it lies on a base plate against a back fence and an end stop and is held "
        f"down by one red-handled toggle clamp at its left end (around x 0.30, y 0.25, 5 cm tall)",
        "also on the bench, fixed: two quarter sheets of sandpaper at the right front, a pencil on the board, a white dust "
        "mask at the back left",
        "the cord is drawn and does not move or follow the plug; the sander, its switch knob and the plug move",
    ]
