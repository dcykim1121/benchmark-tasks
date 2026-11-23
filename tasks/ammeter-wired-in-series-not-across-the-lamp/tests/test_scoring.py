"""Scorer tests without the simulator: synthetic plug and rocker poses fed to the scorer step by step.
Run from the task folder:  python tests/test_scoring.py   (needs numpy; the scene kit's simulator imports are stubbed)."""
import math
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.modules.setdefault("simkit", MagicMock())
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import ammkit as K  # noqa: E402
import scoring as S  # noqa: E402

FAR = {"left": {"tcp": [0.16, 0.24, K.TOP + 0.16]}, "right": {"tcp": [0.16, -0.24, K.TOP + 0.16]}}
START = dict(K.START)


def pose(x, y, z):
    return [x, y, z, 0.0, 0.0, 0.0, 1.0]


def at(socket, depth=None):
    """A plug in a socket; ``depth`` (m) of its tip behind the mouth if not fully home."""
    x, y, z = K.seat_pos(socket)
    return pose(x if depth is None else K.XF + depth - K.TIP_X, y, z)


def rocker(deg):
    f = math.radians(deg - K.ROCKER_ON_DEG)
    return [*K.ROCKER_PIVOT, 0.0, math.sin(f / 2), 0.0, math.cos(f / 2)]


LAID = pose(K.SEAT_X - 0.050, K.SOCKET_Y[8], K.PLUG_Z)       # the yellow lead's lamp-end plug pulled out and laid on the board
LAID_A = pose(K.SEAT_X - 0.050, K.SOCKET_Y[7], K.PLUG_Z)     # its switch-end plug likewise
N = 10                                                       # steps in 0.5 s: a short this long is latched


def tilted(socket, deg, depth=0.0185):
    """A plug in a socket with its nose ``deg`` down, its pin's head 1.5 mm below the socket's axis."""
    th = math.radians(deg)
    q = [0.0, math.sin(th / 2), 0.0, math.cos(th / 2)]
    head = np.array([K.XF + depth - K.HEAD_R, K.SOCKET_Y[socket], K.S + K.AXIS_H - 0.0015])
    c = head - K.quat_matrix(q) @ np.array([K.HEAD_X, 0.0, K.PIN_DZ])
    return [*c, *q]


def frame(on=True, robot=FAR, **plugs):
    """Poses for a state: every plug where it starts unless given as name=socket index, name=pose, or name=None (free
    plug left lying)."""
    poses = {"rocker": rocker(12.0 if on else -12.0), "mpb": pose(*K.FREE_MP), "mnb": pose(*K.FREE_MN)}
    for name, socket in START.items():
        poses[name] = at(socket)
    for name, v in plugs.items():
        poses[name] = at(v) if isinstance(v, int) else v
    return {"poses": poses, "robot": robot}


def run(frames):
    sc = S.TrialScorer()
    r = None
    for i, f in enumerate(frames, 1):
        r = sc.update(i, None, f["poses"], f["robot"])
    return r


RESULTS = []


def show(name, r, want):
    ok = bool(want(r))
    RESULTS.append(ok)
    print(("OK  " if ok else "FAIL"), name, "| score", r["score"], "| shorted", r["battery_shorted"], "| battery", r["battery_a"], "A | lamp lit",
          r["lamp_lit"], "| meter", r["meter_a"], "A")


SERIES = dict(l2a=LAID_A, l2b=LAID, mnb=9, mpb=6)            # the meter in the yellow lead's place
HALF = dict(l2b=LAID, mnb=9, mpb=6)                          # the same, but the yellow lead still hangs from the switch's terminal
TRAP = dict(mpb=9, mnb=10)                                   # the meter on the lamp's two terminals
show("nothing done", run([frame()] * 60), lambda r: r["score"] == 0.0 and r["lamp_lit"] and not r["battery_shorted"])
show("done right: switch off, yellow lead out, meter in its place, switch on", run([frame(False)] * 5 + [frame(False, l2b=LAID)] * 5 + [frame(False, l2a=LAID_A, l2b=LAID)] * 5 + [frame(False, **SERIES)] * 5 + [frame(**SERIES)] * 40),
     lambda r: r["score"] == 1.0 and abs(r["meter_a"] - 1.48) < 0.02)
show("same, held only 10 steps", run([frame(False, **SERIES)] * 5 + [frame(**SERIES)] * 10), lambda r: r["score"] == 0.5)
show("meter in series, switch still open", run([frame(False, **SERIES)] * 40), lambda r: r["score"] == 0.5 and not r["lamp_lit"])
show("LOOSE LIVE PIN: only one yellow plug pulled, meter in the gap, switched on", run([frame(**HALF)] * 40), lambda r: r["score"] == 0.5 and r["leads_hanging_from_one_plug"] == 1 and r["lamp_lit"])
show("... then the other yellow plug pulled too", run([frame(**HALF)] * 20 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0)
show("TRAP: meter on the lamp's two terminals, switch closed", run([frame(**TRAP)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("trap for 0.5 s, then corrected to the right wiring", run([frame(**TRAP)] * N + [frame(False, **SERIES)] * 5 + [frame(**SERIES)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("short for 9 steps (0.45 s), then pulled out again and done right: not latched", run([frame()] * 5 + [frame(**TRAP)] * (N - 1) + [frame()] * 5 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0 and not r["battery_shorted"])
show("short for 10 steps (0.5 s), then pulled out again: latched", run([frame()] * 5 + [frame(**TRAP)] * N + [frame()] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("two shorts of 6 steps with a break between: not latched", run([frame(**TRAP)] * 6 + [frame()] * 2 + [frame(**TRAP)] * 6 + [frame()] * 20), lambda r: not r["battery_shorted"])
show("on the lamp's terminals with the switch open (no current yet)", run([frame(False, **TRAP)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"])
show("... the zero falls 0.5 s after the switch is closed, not before", run([frame(False, **TRAP)] * 10 + [frame(**TRAP)] * (N - 1)), lambda r: not r["battery_shorted"])
show("... and then it has fallen", run([frame(False, **TRAP)] * 10 + [frame(**TRAP)] * N), lambda r: r["battery_shorted"] and r["score"] == 0.0)
show("on the lamp's terminals the other way round", run([frame(mpb=10, mnb=9)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("across the battery, switch open", run([frame(False, mpb=2, mnb=0)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("across the battery the other way round, switch closed", run([frame(mpb=0, mnb=2)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("nearest sockets: red into the switch's right terminal, black into the lamp's right terminal", run([frame(mpb=6, mnb=10)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("meter from the switch's left terminal to the lamp's right terminal", run([frame(mpb=5, mnb=10)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("meter from battery + to the lamp's right terminal, switch open", run([frame(False, mpb=2, mnb=10)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("meter from the lamp's left terminal to battery -", run([frame(mpb=9, mnb=0)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("no meter: yellow lead's plug moved to the lamp's right terminal", run([frame(l2b=10)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("no meter: red lead's plug moved from the switch to battery -, switch open", run([frame(False, l1b=0)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("no meter: blue lead's plug moved from the lamp's right to its left terminal", run([frame(l3a=9)] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("NOT A SHORT: yellow lead taken out first, then the meter on the lamp's two terminals", run([frame(l2a=LAID_A, l2b=LAID, **TRAP)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"])
show("... and from there on to the right wiring", run([frame(l2a=LAID_A, l2b=LAID, **TRAP)] * 20 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0)
show("ROUND THE SWITCH: meter from the switch's left terminal to the lamp, lamp lit and read", run([frame(l2a=LAID_A, l2b=LAID, mpb=5, mnb=9)] * 40),
     lambda r: r["score"] == 0.0 and r["lamp_lit"] and r["meter_reads_lamp"] and not r["switch_controls_lamp"])
show("ROUND THE SWITCH: the same with the rocker off (lamp still lit)", run([frame(False, l2a=LAID_A, l2b=LAID, mpb=5, mnb=9)] * 40), lambda r: r["score"] == 0.0 and r["lamp_lit"])
show("ROUND THE SWITCH: meter from battery + to the lamp, yellow lead out", run([frame(l2a=LAID_A, l2b=LAID, mpb=2, mnb=9)] * 40), lambda r: r["score"] == 0.0 and not r["switch_controls_lamp"])
show("meter bridging the open switch, yellow lead in", run([frame(False, mpb=5, mnb=6)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"] and r["lamp_lit"])
show("meter backwards in the gap (needle against its left stop)", run([frame(l2a=LAID_A, l2b=LAID, mnb=6, mpb=9)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"] and r["meter_reversed"])
show("backwards, then turned round: no latch", run([frame(False, l2a=LAID_A, l2b=LAID, mnb=6, mpb=9)] * 10 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0)
show("meter in parallel with the yellow lead", run([frame(mpb=6, mnb=9)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"])
show("meter put in beside the yellow lead, then that lead taken out", run([frame(mpb=6, mnb=9)] * 10 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0)
show("plugs changed with the switch closed throughout, never shorted", run([frame(l2b=LAID)] * 5 + [frame(l2a=LAID_A, l2b=LAID)] * 5 + [frame(l2a=LAID_A, l2b=LAID, mnb=9)] * 5 + [frame(**SERIES)] * 40), lambda r: r["score"] == 1.0)
show("meter's - plug in the socket the yellow plug came out of", run([frame(**dict(SERIES, mnb=8))] * 40), lambda r: r["score"] == 1.0)
show("one meter plug connected (lamp's left terminal), the other still lying on the board", run([frame(mnb=9)] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"] and r["lamp_lit"])
show("lamp circuit broken and left so", run([frame(False, l2b=LAID)] * 40), lambda r: r["score"] == 0.0)
show("yellow lead taken out and nothing else", run([frame(l2a=LAID_A, l2b=LAID)] * 40), lambda r: r["score"] == 0.0 and not r["lamp_lit"])
show("PARTLY IN: - plug only 12 mm in, not past the catch: it conducts, lamp lit: 0.5", run([frame(**dict(SERIES, mnb=at(9, 0.012)))] * 40),
     lambda r: r["score"] == 0.5 and r["lamp_lit"] and r["plug_partly_in"] and not r["battery_shorted"])
show("PARTLY IN: right wiring, then a plug dragged back to 14 mm", run([frame(**SERIES)] * 15 + [frame(**dict(SERIES, mpb=at(6, 0.014)))] * 40), lambda r: r["score"] == 0.5 and r["plug_partly_in"])
show("PARTLY IN: trap plugs only 12 mm in the lamp's sockets: they conduct, a short", run([frame(mpb=at(9, 0.012), mnb=at(10, 0.012))] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("PARTLY IN: trap plugs 8 mm in for 0.5 s, then pulled back out: still zero", run([frame(mpb=at(9, 0.0082), mnb=at(10, 0.0082))] * N + [frame()] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
show("NEARNESS: trap plugs 6 mm in the mouths, not yet in the bores: no contact", run([frame(mpb=at(9, 0.006), mnb=at(10, 0.006))] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"])
show("NEARNESS: trap plugs lying with their tips at the mouths: no contact", run([frame(mpb=at(9, 0.0), mnb=at(10, 0.0))] * 40), lambda r: r["score"] == 0.0 and not r["battery_shorted"])
show("NEARNESS: - plug held 3 mm in front of its socket", run([frame(**dict(SERIES, mnb=at(9, -0.003)))] * 40), lambda r: r["score"] == 0.0)
show("just past the catch (15 mm) counts as seated", run([frame(**dict(SERIES, mnb=at(9, 0.0152), mpb=at(6, 0.0152)))] * 40), lambda r: r["score"] == 1.0)
show("TILTED: plugs fully in but held 13 degrees nose-down count as seated", run([frame(**dict(SERIES, mnb=tilted(9, 13.0), mpb=tilted(6, 13.0)))] * 40), lambda r: r["score"] == 1.0)
show("TILTED: trap plugs fully in, 13 degrees nose-down: a short", run([frame(mpb=tilted(9, 13.0), mnb=tilted(10, 13.0))] * 40), lambda r: r["score"] == 0.0 and r["battery_shorted"])
near = {"left": FAR["left"], "right": {"tcp": [K.SEAT_X - 0.03, K.SOCKET_Y[9], K.PLUG_Z + 0.02]}}
show("right wiring but a gripper still at a plug", run([frame(robot=near, **SERIES)] * 40), lambda r: r["score"] == 0.5 and not r["grippers_clear"])
off = pose(K.BOARD_X[0] - 0.03, K.SOCKET_Y[8], K.TOP + 0.014)
show("right wiring but a pulled plug dragged off the board", run([frame(**dict(SERIES, l2b=off))] * 40), lambda r: r["score"] == 0.5 and not r["plugs_on_board"])
jit = [frame(**dict(SERIES, l2b=pose(K.SEAT_X - 0.050 + 0.001 * (i % 2), K.SOCKET_Y[8], K.PLUG_Z))) for i in range(40)]
show("right wiring but a plug still moving", run(jit), lambda r: r["score"] == 0.5 and not r["at_rest"])
show("right wiring, a pulled yellow plug pushed 12 mm into a spare battery + socket: 0.5", run([frame(**dict(SERIES, l2b=at(2, 0.012)))] * 40),
     lambda r: r["score"] == 0.5 and r["plug_partly_in"] and r["leads_hanging_from_one_plug"] == 1)
O1A, O1B = pose(K.SEAT_X - 0.050, K.SOCKET_Y[3], K.PLUG_Z), pose(K.SEAT_X - 0.050, K.SOCKET_Y[4], K.PLUG_Z)
show("(scorer's generality) meter in the red lead's place, + at battery +", run([frame(l1a=O1A, l1b=O1B, mpb=2, mnb=5)] * 40), lambda r: r["score"] == 1.0)
print(f"{sum(RESULTS)} of {len(RESULTS)} passed")
sys.exit(0 if all(RESULTS) else 1)
