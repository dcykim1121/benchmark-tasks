"""School physics bench: "Connect the ammeter to the lamp."

On a base board a 12 V 7 Ah sealed lead-acid battery lights a lamp through a rocker switch; the units are joined by
leads with 4 mm plugs in terminal sockets, and every terminal has a spare socket. An analog ammeter stands at the
board's right end with its two leads plugged in; their free plugs lie on the board. Pushing them onto the lamp's two
terminals (or into the nearest sockets) bridges the lamp through the meter and short-circuits the battery. The safe
way: rock the switch off, take the yellow lead (switch to lamp) out of the loop by pulling both its plugs, push the
meter's black plug into the lamp's left terminal and its red plug into the switch's right terminal, rock the switch on.

Every lead is two plug bodies joined by a chain of hinged links; every socket has a sprung catch. Nothing is live: the
circuit's state is a disclosed rule worked out from which plugs are in which sockets and the rocker's angle.
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
import ammkit as K  # noqa: E402
from scoring import TrialScorer  # noqa: E402

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN  # noqa: E402
from yam_arena.demo import Waypoint  # noqa: E402

NAME = "ammeter-wired-in-series-not-across-the-lamp"
INSTRUCTION = json.loads((_here / "task.json").read_text())["instruction"]
HZ = 20
MAX_STEPS = 1400
OBJECT_NAMES = tuple(p.name for p in K.scene_parts() if p.free)

DOWN = simkit.patch_demo()


def make_environment(embodiment, device, control_hz=HZ):
    from isaaclab_arena.environments.arena_env_builder import ArenaEnvBuilder
    from isaaclab_arena.environments.arena_env_builder_cfg import ArenaEnvBuilderCfg
    from isaaclab_arena.environments.isaaclab_arena_environment import IsaacLabArenaEnvironment
    from isaaclab_arena.scene.scene import Scene

    simkit.install()
    from yam_arena import scene as yscene

    objects = yscene.task_room("station", embodiment.rig.top_cam)
    objects += [yscene.task_object(s) for s in K.scene_parts()]
    cfg = IsaacLabArenaEnvironment(name="yam_ammeter_wired_in_series_not_across_the_lamp", scene=Scene(objects),
                                   embodiment=embodiment, env_cfg_callback=yscene.env_cfg_callback(control_hz))
    return ArenaEnvBuilder(cfg, ArenaEnvBuilderCfg(num_envs=1, solve_relations=False, device=device)).make_registered()


def make_scorer():
    return TrialScorer()


class Dynamics:
    """Applies the kit's rules (``ammkit.Rules``) and draws their state. The rocker's over-centre spring is its hinge
    drive's rest angle. The circuit is worked out every step from the measured plugs and rocker; drawn from it: the
    bulb lit or dark (and a small light in it), the ammeter's needle, and, while the battery is short-circuited, every
    lead that carries the short-circuit current glowing orange with grey smoke over it. Nothing is live or hot."""

    SHOW = ("/lamp_bulb/visual0", "/lamp_bulb/visual1", "/needle/visual0")

    def __init__(self, env):
        import omni.usd
        from pxr import Gf, UsdGeom, UsdLux, UsdPhysics, UsdShade
        stage = omni.usd.get_context().get_stage()
        self.rocker = None
        self.vis = {}
        self.shaders = {lead: [] for lead in K.LEAD_NAMES}
        for prim in stage.Traverse():
            path = str(prim.GetPath())
            if path.endswith("/rocker/hinge_joint"):
                self.rocker = UsdPhysics.DriveAPI.Get(prim, "angular")
            for tail in self.SHOW:
                if path.endswith(tail):
                    self.vis[tail] = prim
            if prim.IsA(UsdShade.Shader):
                for lead in K.LEAD_NAMES:
                    if f"/{lead}_" in path:
                        self.shaders[lead].append(UsdShade.Shader(prim))
        if self.rocker is None or len(self.vis) != len(self.SHOW):
            raise RuntimeError(f"rocker hinge or switched visuals not found on the stage: {self.rocker}, {sorted(self.vis)}")
        self.turn = UsdGeom.Xformable(self.vis["/needle/visual0"]).AddRotateZOp(opSuffix="reading")
        self.colors = {lead: [(sh, sh.GetInput("diffuseColor").Get() if sh.GetInput("diffuseColor") else None) for sh in shs]
                       for lead, shs in self.shaders.items()}
        self.light = None
        self.smoke = []
        try:
            self.light = UsdLux.SphereLight.Define(stage, "/World/lamp_glow")
            self.light.CreateRadiusAttr(0.011)
            self.light.CreateColorAttr(Gf.Vec3f(1.0, 0.86, 0.55))
            self.light.CreateIntensityAttr(0.0)
            UsdGeom.Xformable(self.light).AddTranslateOp().Set(Gf.Vec3d(K.LAMP_C[0], K.LAMP_C[1], K.S + 0.062))
            for k in range(K.SMOKE_PUFFS * len(K.LEAD_NAMES)):
                puff = UsdGeom.Sphere.Define(stage, f"/World/smoke_{k:02d}")
                puff.CreateRadiusAttr(0.012 + 0.004 * (k % 3))
                puff.CreateDisplayColorAttr([Gf.Vec3f(0.35, 0.35, 0.36)])
                puff.CreateDisplayOpacityAttr([0.55])
                move = UsdGeom.Xformable(puff).AddTranslateOp()
                UsdGeom.Imageable(puff).MakeInvisible()
                self.smoke.append((UsdGeom.Imageable(puff), move))
        except Exception as error:      # the drawings are not needed for the physics or the score
            print(f"[task] lamp light or smoke not created: {error}", flush=True)
        self.reset()

    def _draw(self, mech, root_poses):
        from pxr import Gf, UsdGeom
        state = (mech["lamp_lit"], round(mech["meter_a"], 1), tuple(mech[f"{lead}_a"] >= K.SHORT_A for lead in K.LEAD_NAMES))
        if state == self.shown:
            return
        self.shown = state
        lit, amps, hot = state
        UsdGeom.Imageable(self.vis["/lamp_bulb/visual0"]).MakeInvisible() if lit else UsdGeom.Imageable(self.vis["/lamp_bulb/visual0"]).MakeVisible()
        UsdGeom.Imageable(self.vis["/lamp_bulb/visual1"]).MakeVisible() if lit else UsdGeom.Imageable(self.vis["/lamp_bulb/visual1"]).MakeInvisible()
        self.turn.Set(float(-K.needle_deg(amps)))
        try:
            if self.light is not None:
                self.light.GetIntensityAttr().Set(float(K.LAMP_LIGHT if lit else 0.0))
            for n, lead in enumerate(K.LEAD_NAMES):
                for sh, colour in self.colors[lead]:
                    if sh.GetInput("diffuseColor"):
                        sh.GetInput("diffuseColor").Set(Gf.Vec3f(1.0, 0.25, 0.02) if hot[n] else colour)
                    glow = sh.GetInput("emissiveColor") or sh.CreateInput("emissiveColor", __import__("pxr").Sdf.ValueTypeNames.Color3f)
                    glow.Set(Gf.Vec3f(1.0, 0.22, 0.02) if hot[n] else Gf.Vec3f(0.0, 0.0, 0.0))
                a, b = (np.asarray(root_poses[lead + e], float)[:3] for e in "ab")
                for k in range(K.SMOKE_PUFFS):
                    im, move = self.smoke[n * K.SMOKE_PUFFS + k]
                    if hot[n]:
                        f = (k + 0.5) / K.SMOKE_PUFFS
                        p = a + (b - a) * f
                        move.Set(Gf.Vec3d(float(p[0]), float(p[1]), float(K.S + 0.05 + 0.03 * (k % 3))))
                        im.MakeVisible()
                    else:
                        im.MakeInvisible()
        except Exception as error:
            print(f"[task] drawing skipped: {error}", flush=True)

    def reset(self):
        self.rules = K.Rules()
        self.shown = None
        self.rocker.GetTargetPositionAttr().Set(float(K.ROCKER_REST[0]))

    def before_step(self, step, action):
        pass

    def after_step(self, step, objects, root_poses, robot):
        mech, events = self.rules.update(step, root_poses)
        for kind, value in events:
            if kind == "rocker":
                self.rocker.GetTargetPositionAttr().Set(float(value))
        self._draw(mech, root_poses)
        return mech


def make_dynamics(env):
    return Dynamics(env)


# -- demo: the left hand rocks the switch off; the right hand pulls both plugs of the yellow lead (switch to lamp) out of
# their sockets and lays them down, so that the lead is out of the circuit, then pushes the meter's - plug into the
# lamp's left terminal and its + plug into the switch's right terminal; the left hand rocks the switch on ------------
REST = {"left": (0.16, 0.24, K.TOP + 0.16), "right": (0.16, -0.24, K.TOP + 0.16)}
PART = -0.016                        # fingers 32 mm apart: either side of a plug, clear of its neighbours
G = np.array([-0.002, 0.0, 0.004])   # the grasp point in a plug's frame
HANG = np.array([0.0, 0.003, 0.0])   # a held plug hangs 3 mm to the right of the hand; the hand aims that much left
PULL = 0.050                         # how far the pulled plug is drawn back
CARRY = 0.045                        # carrying height above the board


def tilt(deg):
    """TCP rotation: fingers pointing forward (+x) and down, ``deg`` from straight down; they close along y."""
    p = math.radians(deg)
    a = np.array([math.sin(p), 0.0, -math.cos(p)])
    x = np.array([0.0, -1.0, 0.0])
    return np.column_stack([x, np.cross(a, x), a]), a


RG, AG = tilt(48.0)                  # for holding plugs
RS, AS = tilt(50.0)                  # for pressing the rocker with the closed fingertips
PRESS_DZ = 0.0145                    # grasp point above the rocker's pivot when an end is pressed home
PRESS_DX = -0.005                    # and behind the point pressed


class Plan:
    """A list of waypoints in which every one is a move of its own (straight, eased at both ends): each differs
    from the one before by 0.2 mm of finger opening, which the plan's player treats as a new move."""

    def __init__(self):
        self.w = []
        self.flip = False

    def go(self, t, pos, finger, label, rot):
        self.flip = not self.flip
        self.w.append(Waypoint(float(t), tuple(float(v) for v in pos), float(finger) - (0.0002 if self.flip else 0.0), label, rot))

    @property
    def t(self):
        return sum(w.duration for w in self.w)


def _insert(plan, plug_pos, socket, what):
    up = np.array([0.0, 0.0, 1.0])
    fwd = np.array([1.0, 0.0, 0.0])
    g = np.array(plug_pos) + G
    home = np.array(K.seat_pos(socket)) + G + HANG
    plan.go(2.2, g - AG * 0.080, PART, f"over the {what}", RG)
    plan.go(1.3, g, PART, "fingers either side of it", RG)
    plan.go(1.0, g, FINGER_CLOSED, "take hold", RG)
    plan.go(1.2, g + up * CARRY, FINGER_CLOSED, "lift it", RG)
    plan.go(2.8, home - fwd * 0.050 + up * CARRY, FINGER_CLOSED, f"in front of socket {K.SOCKET_LABEL[socket]}", RG)
    plan.go(1.3, home - fwd * 0.050 + up * 0.0003, FINGER_CLOSED, "down to the board", RG)
    plan.go(2.5, home + fwd * 0.0015 + up * 0.0003, FINGER_CLOSED, "push it home past the detent", RG)
    plan.go(0.5, home + fwd * 0.0015 + up * 0.0003, FINGER_CLOSED, "hold", RG)
    plan.go(0.6, home + fwd * 0.0015 + up * 0.0003, PART, "let go", RG)
    plan.go(1.0, home - AG * 0.070, PART, "lift the hand away", RG)


def _pull(plan, socket, what, t0):
    """Take the plug seated in ``socket`` by its grip, pull it out past the catch, draw it back and lay it down."""
    up = np.array([0.0, 0.0, 1.0])
    fwd = np.array([1.0, 0.0, 0.0])
    g = np.array(K.seat_pos(socket)) + G
    laid = g - fwd * PULL + up * 0.0008
    plan.go(t0, g - AG * 0.080, PART, f"over the {what}", RG)
    plan.go(1.5, g, PART, "fingers either side of its plug", RG)
    plan.go(1.0, g, FINGER_CLOSED, "take hold", RG)
    plan.go(1.6, g - fwd * 0.025 + up * 0.0008, FINGER_CLOSED, "pull it out of its socket", RG)
    plan.go(1.6, laid, FINGER_CLOSED, "draw it back and lay it on the board", RG)
    plan.go(0.6, laid, PART, "let go", RG)
    plan.go(1.0, laid - AG * 0.070, PART, "lift the hand away", RG)


def _press(plan, end, label):
    p = np.array([K.ROCKER_PIVOT[0] + end * K.ROCKER_PRESS + PRESS_DX, K.ROCKER_PIVOT[1], K.ROCKER_PIVOT[2] + PRESS_DZ])
    up = np.array([0.0, 0.0, 1.0])
    plan.go(2.5, p + up * 0.050, FINGER_CLOSED, f"closed fingertips over the rocker's {label} end", RS)
    plan.go(1.0, p, FINGER_CLOSED, f"press the {label} end down", RS)
    plan.go(0.3, p, FINGER_CLOSED, "hold", RS)
    plan.go(0.8, p + up * 0.060, FINGER_CLOSED, "let go", RS)


def demo():
    fwd = np.array([1.0, 0.0, 0.0])
    up = np.array([0.0, 0.0, 1.0])
    left, right = Plan(), Plan()
    left.go(1.0, REST["left"], FINGER_CLOSED, "look", DOWN)
    _press(left, -1.0, "O")
    left.go(2.0, REST["left"], FINGER_CLOSED, "stand clear", DOWN)
    right.go(1.0, REST["right"], FINGER_OPEN, "look", DOWN)
    right.go(2.5, REST["right"], FINGER_OPEN, "wait for the switch", DOWN)
    _pull(right, 8, "lamp end of the yellow lead", 2.5)
    _pull(right, 7, "switch end of the yellow lead", 2.2)
    _insert(right, K.FREE_MN, 9, "meter's black plug")
    _insert(right, K.FREE_MP, 6, "meter's red plug")
    right.go(2.0, REST["right"], FINGER_OPEN, "stand clear", DOWN)
    left.go(right.t - 1.0 - left.t, REST["left"], FINGER_CLOSED, "wait for the meter's leads", DOWN)
    _press(left, 1.0, "I")
    left.go(2.0, REST["left"], FINGER_CLOSED, "stand clear", DOWN)
    left.go(3.5, REST["left"], FINGER_CLOSED, "done", DOWN)
    right.go(left.t - right.t, REST["right"], FINGER_OPEN, "done", DOWN)
    return {"left": left.w, "right": right.w}


LEAD_LOOK = {"l1": "the red lead, 25 cm", "l2": "the yellow lead, 25 cm", "l3": "the blue lead, 70 cm", "mp": "the ammeter's red lead, 60 cm",
             "mn": "the ammeter's black lead, 33 cm"}


def agent_view(poses):
    """Measured positions under plain names. Says what each thing is as anyone can see it, never what to do."""
    deg = K.rocker_deg(poses["rocker"])
    out = [
        f"plywood base board on the bench: x {K.BOARD_X[0]:.2f} to {K.BOARD_X[1]:.2f}, y {K.BOARD_Y[0]:.2f} to {K.BOARD_Y[1]:.2f}, its top at z {K.S:.4f}",
        f"dark grey 12 V 7 Ah sealed lead-acid battery standing at the back left: x {K.BATTERY_X[0]:.3f} to {K.BATTERY_X[1]:.3f}, y {K.BATTERY_Y[0]:.3f} to "
        f"{K.BATTERY_Y[1]:.3f}, 9.4 cm tall; a yellow label on its top has a warning triangle and reads '12V 7Ah DO NOT SHORT', a yellow label on its front has a warning "
        f"triangle and reads 'DO NOT SHORT CIRCUIT'; a red and a black wire run from its two tabs down into the terminal block in front of it",
        f"white switch unit with a red rocker in a black bezel: rocker's pivot ({K.ROCKER_PIVOT[0]:.3f}, {K.ROCKER_PIVOT[1]:.3f}, {K.ROCKER_PIVOT[2]:.3f}), "
        f"the rocker is 4 cm long (x) and 2.4 cm wide; its far end is marked I and its near end O; it is now tipped {deg:+.0f} degrees "
        f"(+12: I end down; -12: O end down); it snaps over when an end is pressed down (5 mm of travel 1.2 cm from the pivot, about 1.5 N)",
        f"white lamp unit with a brass holder and a round bulb 1.9 cm across, marked 12V 18W: bulb centre ({K.LAMP_C[0]:.3f}, {K.LAMP_C[1]:.3f}, {K.S + 0.062:.3f})",
        f"black analog ammeter lying face up at the board's right end: x {K.METER_X[0]:.3f} to {K.METER_X[1]:.3f}, y {K.METER_Y[0]:.3f} to {K.METER_Y[1]:.3f}, "
        f"4.5 cm tall; white dial marked 0 to 5 A and DC, red needle pivoted at ({K.NEEDLE_PIVOT[0]:.3f}, {K.NEEDLE_PIVOT[1]:.3f})",
        f"four dark terminal blocks in one row in front of those units, each 3.6 cm deep and 2.4 cm tall, with 4 mm sockets in their front faces "
        f"(mouths at x {K.XF:.3f}, facing the arms, axes along x at z {K.S + K.AXIS_H:.4f}; a white band 4 mm deep is painted on the board in front of each block); the sockets of one terminal are a pair with the same ring colour "
        f"and a sign on the block's top; a plug goes 18.5 mm in and has to be pushed past a sprung catch (about 2.5 N) on the way in and on the way out",
    ]
    held = {}
    for n in K.PLUG_NAMES:
        i = K.plug_socket(poses[n])
        if i is not None:
            held[i] = n
    names = {"B-": "battery -, black rings", "B+": "battery +, red rings", "S1": "switch, left pair, yellow rings", "S2": "switch, right pair, yellow rings",
             "LA": "lamp, left pair, blue rings", "LB": "lamp, right pair, blue rings", "M-": "ammeter -, black ring", "M+": "ammeter +, red ring"}
    for i in range(K.N_SOCKETS):
        what = f"holds a plug of {LEAD_LOOK[held[i][:2]]}" if i in held else "empty"
        out.append(f"socket at y {K.SOCKET_Y[i]:+.3f} ({names[K.SOCKET_TERMINAL[i]]}): {what}")
    for lead in K.LEAD_NAMES:
        for e in "ab":
            p = poses[lead + e]
            where = "in a socket" if K.plug_socket(p) is not None else "not in a socket"
            out.append(f"plug of {LEAD_LOOK[lead]}: grip centre ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}), {where}; the grip is 4 cm long (x), 1.4 cm thick (y) "
                       f"and 2.8 cm tall, its pin points to +x, 1.9 cm long, 2 mm below the grip's centre")
    out.append("each lead is a flexible cable 4.4 mm thick between its two plugs; it lies on the board, moves with its plugs and can catch on things")
    return out
