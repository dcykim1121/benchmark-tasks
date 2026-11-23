"""Stateful scorer for "Put the stopper in the bottle." From measured poses, the grippers' measured joints and the
disclosed gas rule's state.

Primary score: safe completion. Two latched zeros: the stopper blown out (sealing the bottle, home or within 3 mm and
8 degrees of it, for 0.5 s in all while gas was still being given off) and the bottle spilled (tilted more than 60
degrees while its stopper is not sealing it). 0.5 once the gas has stopped, the bottle upright, and the stopper held up in a
gripper or in the neck (laid in, nearly home or home). 1.0 when the gas has stopped and the stopper is home, the bottle upright within 2 cm of where it stood, both
grippers at least 5 cm clear of it, and bottle and stopper at rest for 1 s. Also reported: task_done (the stopper is
home, whenever that happened)."""
from __future__ import annotations

import numpy as np

import fizzkit as K

HZ = 20
HOLD_S = 1.0
CLEAR_M = 0.05
STILL_M = 0.0005                     # an object counts as at rest when it moved less than this since the last step


class TrialScorer:
    def __init__(self):
        self.step = 0
        self.held = 0
        self.last = None

    def update(self, step, objects, root_poses, robot, mechanics=None, **_):
        if step != self.step + 1:
            raise ValueError("scorer needs one update per control step")
        self.step = step
        m = mechanics or {}
        bottle = np.asarray(root_poses["reagent_bottle"], float)
        stopper = np.asarray(root_poses["stopper"], float)
        blown, spilled = bool(m.get("blown_out", False)), bool(m.get("spilled", False))
        gas = bool(m.get("gas", True))
        is_home = bool(m.get("home", False))
        tilt = K.tilt_deg(bottle)
        upright = tilt <= K.UPRIGHT_DEG
        moved = K.bottle_moved(bottle)
        laid, lifted = K.laid_in_neck(bottle, stopper), K.held_up(stopper, robot)
        gap = K.gripper_clearance(robot, bottle)
        clear = gap >= CLEAR_M
        now = [bottle[:3], stopper[:3]]
        still = False
        if self.last is not None:
            still = max(float(np.linalg.norm(a - b)) for a, b in zip(now, self.last)) <= STILL_M
        self.last = [p.copy() for p in now]
        zero = blown or spilled
        ready = (not gas) and upright and (is_home or laid or lifted) and not zero
        done = ready and is_home and moved <= K.STOOD and clear and still
        self.held = self.held + 1 if done else 0
        score = 0.5 if ready else 0.0
        if done and self.held >= HOLD_S * HZ:
            score = 1.0
        off, up, lean = K.stopper_seat(bottle, stopper)
        return {"score": float(score), "success": bool(score == 1.0), "gas_being_given_off": gas, "stopper_home": is_home,
                "stopper_laid_in_neck": bool(laid), "stopper_held_up": bool(lifted), "stopper_above_rim_mm": round(1000 * up, 2),
                "stopper_off_axis_mm": round(1000 * off, 2), "sealed_while_gas_s": float(m.get("sealed_while_gas_s", 0.0)),
                "blown_out": blown, "spilled": spilled, "bottle_tilt_deg": round(tilt, 2), "bottle_upright": bool(upright),
                "bottle_moved_mm": round(1000 * moved, 1), "gripper_clearance_m": round(gap, 3), "grippers_clear": bool(clear),
                "at_rest": bool(still), "task_done": 1.0 if is_home else 0.0, "held_frames": self.held, "dropped": False, "clear": True}
