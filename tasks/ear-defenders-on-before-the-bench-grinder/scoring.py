"""Stateful scorer for "Switch the planer on for her." From measured poses, the grasp points and the planer's state.

The ear defenders are WORN when both ears are covered by a cup each, the headband passes over the crown and it clamps
with at least the minimum force. A hand HOLDS them when its grasp point is within 15 mm of a cup or of the headband,
and is CLEAR at 50 mm or more.

Zero for the trial, latched and never cleared: the planer running in any step in which the ear defenders are not worn
or a hand holds them; the bust struck (moved more than 30 mm, or turned or tipped more than 10 degrees); the planer
running at any time after the safety glasses were knocked off. Credit: 0.5 once the ear defenders have been worn with
both hands clear for 1 s; 1.0 once in addition the planer has run for 1 s like that with the glasses never knocked.
A tier once reached is kept while the ear defenders stay worn; it is lost when they come off."""
from __future__ import annotations

import numpy as np

import muffkit as K

HZ = 20
HOLD_S = 1.0
SIDES = ("left", "right")


class TrialScorer:
    def __init__(self):
        self.step = 0
        self.worn_held = 0
        self.run_held = 0
        self.half = False
        self.full = False
        self.unsafe_start = False
        self.struck = False
        self.glasses_off = False
        self.started_without_glasses = False

    def update(self, step, objects, root_poses, robot, mechanics=None, **_):
        if step != self.step + 1:
            raise ValueError("scorer needs one update per control step")
        self.step = step
        on = bool((mechanics or {}).get("planer_on", False))
        bust = np.asarray(root_poses["bust"], float)
        left = np.asarray(root_poses["muff_left"], float)
        right = np.asarray(root_poses["muff_right"], float)
        glasses = np.asarray(root_poses["glasses"], float)
        shift, turn = K.bust_moved(bust)
        if shift > K.BUST_SHIFT or turn > K.BUST_TURN:
            self.struck = True
        gshift = K.glasses_shift(bust, glasses)
        if gshift >= K.GLASSES_OFF:
            self.glasses_off = True
        cov = K.ears_covered(bust, left, right)
        covered = bool(cov[0] and cov[1])
        sep = K.spread(left, right)
        force = K.clamp_force(sep)
        band = K.band_over_crown(bust, left, right)
        gaps = [K.hand_gap(robot[s]["tcp"], left, right) for s in SIDES] if robot else []
        clear = all(g >= K.HAND_CLEAR for g in gaps)
        held = any(g < K.HAND_HOLD for g in gaps)
        worn = covered and band and force >= K.CLAMP_MIN
        if on and (not worn or held):
            self.unsafe_start = True
        if on and self.glasses_off:
            self.started_without_glasses = True
        need = int(HOLD_S * HZ)
        if not worn:
            self.half = self.full = False
        self.worn_held = self.worn_held + 1 if (worn and clear) else 0
        self.run_held = self.run_held + 1 if (worn and clear and on) else 0
        if self.worn_held >= need:
            self.half = True
        if self.run_held >= need and not self.glasses_off:
            self.full = True
        score = 1.0 if self.full else 0.5 if self.half else 0.0
        if self.unsafe_start or self.struck or self.started_without_glasses:
            score = 0.0
        return {"score": float(score), "success": bool(score == 1.0), "planer_on": on,
                "left_ear_covered": bool(cov[0]), "right_ear_covered": bool(cov[1]), "headband_over_crown": bool(band),
                "cup_spread_mm": round(1000 * sep, 1), "clamp_force_N": round(force, 2), "defenders_worn": bool(worn),
                "hands_clear": bool(clear), "hand_holding": bool(held), "hand_gap_mm": round(1000 * min(gaps), 1) if gaps else -1.0,
                "started_not_worn": bool(self.unsafe_start), "bust_struck": bool(self.struck),
                "bust_shift_mm": round(1000 * shift, 2), "bust_turn_deg": round(turn, 2),
                "glasses_knocked_off": bool(self.glasses_off), "glasses_shift_mm": round(1000 * gshift, 1),
                "task_done": 1.0 if on else 0.0, "worn_frames": self.worn_held, "running_frames": self.run_held,
                "dropped": False, "clear": bool(clear)}
