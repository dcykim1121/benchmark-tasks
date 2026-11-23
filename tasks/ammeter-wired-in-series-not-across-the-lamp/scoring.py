"""Stateful scorer for "Connect the ammeter to the lamp." From measured poses only.

Which socket's contact each plug touches is measured from the plugs' poses: a pin conducts once its end is 8 mm or more
inside a socket's bore, and a plug is seated once its end is 15 mm or more inside, past the sprung catch. The switch is
read from the rocker's angle. The circuit's currents follow from the conducting plugs and the switch by the kit's
disclosed rule (``ammkit.circuit``).

Latched 0 for the rest of the trial: the battery short-circuited (battery current of 20 A or more, by whatever route)
for 0.5 s without a break. 1.0, held for 1 s: never so shorted; the switch closed; the lamp lit; all of the lamp's
current passing through the ammeter from its + to its - terminal; the switch still controlling the lamp (no current
through the lamp with the switch open); every plug that is in a socket seated; every lead with both plugs in sockets
or both out (no lead hanging from one plug); every plug on the board; both grippers 5 cm from every plug's centre and
from the rocker's pivot; everything at rest. 0.5: never so shorted, the ammeter in series (with the switch closed all
of the lamp's current passes through it from + to -) and the switch still controlling the lamp, but the rest of the
1.0 state not reached. Anything else 0."""
from __future__ import annotations

import numpy as np

import ammkit as K

HZ = 20
HOLD_S = 1.0
CLEAR_M = 0.05
STILL_M = 0.0005                     # a plug counts as at rest when it moved less than this since the last step
STILL_DEG = 0.3                      # and the rocker when it turned less than this
SHORT_S = 0.5                        # a short circuit lasting this long without a break is latched


class TrialScorer:
    def __init__(self):
        self.step = 0
        self.held = 0
        self.shorted = False
        self.short_run = 0
        self.last = None

    def update(self, step, objects, root_poses, robot, mechanics=None, **_):
        if step != self.step + 1:
            raise ValueError("scorer needs one update per control step")
        self.step = step
        conn = K.connections(root_poses)
        deg = K.rocker_deg(root_poses["rocker"])
        closed = K.switch_closed(root_poses["rocker"])
        now = K.circuit(conn, closed)
        self.short_run = self.short_run + 1 if now["short"] else 0
        if self.short_run >= SHORT_S * HZ:
            self.shorted = True
        if_closed = now if closed else K.circuit(conn, True)
        partly = K.partly_in(root_poses)
        controls = K.switch_controls_lamp(conn)
        half = K.half_connected(conn)
        in_series = bool(not if_closed["short"] and if_closed["meter_reads_lamp"] and controls)
        on_board = all(K.plug_on_board(root_poses[n]) for n in K.PLUG_NAMES)
        gaps = [K.hand_gap(robot[side], side, root_poses) for side in ("left", "right")] if robot else [0.0, 0.0]
        clear = min(gaps) >= CLEAR_M
        pts = [np.asarray(root_poses[n], float)[:3] for n in K.PLUG_NAMES]
        still = False
        if self.last is not None:
            moved = max(float(np.linalg.norm(a - b)) for a, b in zip(pts, self.last[0]))
            still = moved <= STILL_M and abs(deg - self.last[1]) <= STILL_DEG
        self.last = ([p.copy() for p in pts], deg)
        done = (closed and now["lamp_lit"] and now["meter_reads_lamp"] and controls and not partly and not half
                and on_board and clear and still)
        self.held = self.held + 1 if done else 0
        score = 0.5 if in_series else 0.0
        if done and self.held >= HOLD_S * HZ:
            score = 1.0
        if self.shorted:
            score = 0.0
        out = {"score": float(score), "success": bool(score == 1.0), "battery_shorted": bool(self.shorted),
               "switch_closed": bool(closed), "rocker_deg": round(deg, 1), "lamp_lit": bool(now["lamp_lit"]),
               "battery_a": round(now["battery_a"], 2), "lamp_a": round(now["lamp_a"], 2), "meter_a": round(now["meter_a"], 2),
               "meter_reads_lamp": bool(now["meter_reads_lamp"]), "meter_reversed": bool(now["meter_reversed"]),
               "ammeter_in_series": in_series, "short_now": bool(now["short"]), "switch_controls_lamp": bool(controls),
               "plug_partly_in": bool(partly), "leads_hanging_from_one_plug": len(half), "plugs_on_board": bool(on_board), "gripper_gap_m": round(min(gaps), 3),
               "grippers_clear": bool(clear), "at_rest": bool(still), "held_frames": self.held,
               "task_done": 1.0 if (conn["mpb"] is not None and conn["mnb"] is not None) else 0.0, "dropped": False, "clear": True}
        for n in K.PLUG_NAMES:
            out[f"{n}_socket"] = -1 if conn[n] is None else int(conn[n])
        for n in ("l2b", "mpb", "mnb", "l2a"):
            i, depth, side = K.plug_in(root_poses[n])
            out[f"{n}_depth_mm"] = round(1000 * depth, 1)
            out[f"{n}_side_mm"] = round(1000 * side, 1)
            out[f"{n}_yaw"] = round(K.plug_yaw_deg(root_poses[n]), 1)
        return out
