"""Stateful scorer for "Approve the invoice." From measured poses, the robot's measured grasp points and the marks
reported by the task's ink rule (a mark: stamp index, place and angle on the top page, whole or partial, smear).

Any REJECTED or COPY mark on the invoice, however slight, at any time, is a latched 0. 0.5: an APPROVED mark whose
centre is inside the approval box. 1.0: exactly one mark on the invoice, the APPROVED one, whole and not smeared, its
whole 40 x 16 mm outline inside the box and its text within 20 degrees of the page's text, the invoice book left where
it lay on the desk pad (moved less than 10 mm, turned less than 5 degrees), the other two stamps still standing in the
rack, and the APPROVED stamp put down (not dropped) off the book with both hands away from it, all held 1 s."""
from __future__ import annotations

import math

import numpy as np

import stampkit as K

HZ = 20
HOLD_S = 1.0
STILL = 0.005                        # m/s: a stamp slower than this is at rest
HAND_CLEAR = 0.070                   # m: both grasp points at least this far from the stamp's handle


class TrialScorer:
    def __init__(self):
        self.step = 0
        self.held = 0
        self.wrong = False
        self.dropped = False
        self.prev = None

    def update(self, step, objects, root_poses, robot, mechanics=None, **_):
        if step != self.step + 1:
            raise ValueError("scorer needs one update per control step")
        self.step = step
        mech = mechanics or {}
        marks = [list(m) for m in mech.get("marks", [])]
        inked = list(mech.get("inked", [False] * len(K.STAMPS)))
        sheet = np.asarray(root_poses["sheet"], float)
        stamp = np.asarray(root_poses[K.STAMPS[K.APPROVED]], float)
        approved = [m for m in marks if int(m[0]) == K.APPROVED]
        if len(approved) != len(marks):
            self.wrong = True
        centre = any(K.centre_in_box(m) for m in approved)
        last = approved[-1] if approved else None
        offset, angle = K.mark_offset(last) if last else (-1.0, 0.0)
        whole = bool(len(marks) == 1 and len(approved) == 1 and K.outline_in_box(last))
        clean = bool(last is not None and int(last[4]) == 1 and float(last[5]) <= 1000 * K.SMEAR_MAX)
        square = bool(last is not None and abs(angle) <= K.ANGLE_MAX)
        on_pad = K.sheet_on_pad(sheet)
        speed = 0.0 if self.prev is None else float(np.linalg.norm(stamp[:3] - self.prev)) * HZ
        self.prev = stamp[:3].copy()
        grip = K.handle_centre(stamp)
        clear = all(math.dist(np.asarray(robot[s]["tcp"], float)[:3], grip) > HAND_CLEAR for s in ("left", "right")) if robot else True
        racked = K.in_rack(stamp)
        if clear and stamp[2] > K.TOP + 0.050:
            self.dropped = True              # in the air with no hand at it
        down = bool(K.TOP <= stamp[2] <= K.TOP + 0.030 and speed < STILL and clear and not K.over_sheet(stamp, sheet) and not self.dropped)
        others = all(K.in_rack(root_poses[n]) for i, n in enumerate(K.STAMPS) if i != K.APPROVED)
        score = 0.5 if centre else 0.0
        in_place = K.sheet_in_place(sheet)
        done = whole and clean and square and in_place and down and others
        self.held = self.held + 1 if done else 0
        if done and self.held >= HOLD_S * HZ:
            score = 1.0
        if self.wrong:
            score = 0.0
        shift = K.sheet_shift(sheet)
        return {"score": float(score), "success": bool(score == 1.0), "marks": len(marks), "approved_marks": len(approved),
                "wrong_stamp_mark": bool(self.wrong), "inked": [bool(v) for v in inked],
                "mark_centre_in_box": bool(centre), "mark_outline_in_box": whole, "mark_square": square,
                "mark_whole": bool(last is not None and int(last[4]) == 1), "mark_smear_mm": round(float(last[5]), 1) if last else 0.0,
                "press_force_n": float(last[6]) if last else 0.0, "press_force_at_print_n": float(last[7]) if last else 0.0,
                "ink_force_n": float((mech.get("ink_force_n") or [0.0] * len(K.STAMPS))[K.APPROVED]),
                "prints_off_sheet": int(sum(mech.get("prints_off_sheet", []))), "other_stamps_in_rack": bool(others),
                "mark_offset_mm": round(float(offset), 1), "mark_angle_deg": round(float(angle), 1),
                "sheet_on_desk_pad": bool(on_pad), "sheet_in_place": bool(in_place), "sheet_shift_mm": round(shift[0], 1), "sheet_turn_deg": round(shift[1], 1),
                "stamp_put_down": down, "stamp_in_rack": bool(racked), "hands_clear": bool(clear),
                "held_frames": self.held, "dropped": bool(self.dropped), "clear": bool(clear)}
