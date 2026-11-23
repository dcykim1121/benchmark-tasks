"""Stateful scorer for "Scan the shopping and put it in the bagging area." From measured poses and the scan rule.

Each of the three items earns 1/3 when it has been scanned exactly once and is in the bagging tray, let go. An item in the
tray that was never scanned earns nothing and latches `unscanned_in_bag`, which caps the trial at 0.33. Every extra
scan of an item (a double charge) takes 1/3 off. Full credit also needs the scanner out of the hands (in its cradle
or lying on the counter). Scans are counted here from the measured poses with the same disclosed rule the scene's
lamps use, so the score can be replayed from a trajectory."""
from __future__ import annotations

import numpy as np

import scankit as K

HZ = 20
HOLD_S = 1.0
BAG_HOLD = 10                        # steps an unscanned item must be in the tray before the flag latches
THIRD = 1.0 / 3.0


class ScanCounter:
    """The scan rule. A read of an item registers when the window has been aimed at its barcode for SCAN_HOLD steps
    in a row. The same code can be read again only after the aim has been off it for SCAN_REARM steps in a row."""

    def __init__(self):
        self.count = {n: 0 for n in K.ITEM_NAMES}
        self.held = {n: 0 for n in K.ITEM_NAMES}
        self.away = {n: K.SCAN_REARM for n in K.ITEM_NAMES}
        self.armed = {n: True for n in K.ITEM_NAMES}

    def update(self, root_poses):
        scanner = root_poses["scanner"]
        zone = {n: K.in_read_zone(scanner, n, root_poses[n]) for n in K.ITEM_NAMES}
        if sum(zone.values()) > 1:         # one code at a time: the nearest to the window's axis
            best = min((n for n in K.ITEM_NAMES if zone[n]), key=lambda n: K.aim(scanner, n, root_poses[n])[2])
            zone = {n: n == best for n in K.ITEM_NAMES}
        fresh = []
        for n in K.ITEM_NAMES:
            if zone[n]:
                self.away[n] = 0
                self.held[n] += 1
                if self.armed[n] and self.held[n] >= K.SCAN_HOLD:
                    self.count[n] += 1
                    self.armed[n] = False
                    fresh.append(n)
            else:
                self.held[n] = 0
                self.away[n] += 1
                if self.away[n] >= K.SCAN_REARM:
                    self.armed[n] = True
        return fresh


class TrialScorer:
    def __init__(self):
        self.step = 0
        self.held = 0
        self.scans = ScanCounter()
        self.bag_frames = {n: 0 for n in K.ITEM_NAMES}
        self.unscanned_in_bag = False
        self.lost = {n: False for n in K.ITEM_NAMES}

    def update(self, step, objects, root_poses, robot, mechanics=None, **_):
        if step != self.step + 1:
            raise ValueError("scorer needs one update per control step")
        self.step = step
        self.scans.update(root_poses)
        count = self.scans.count
        tcps = [robot[s]["tcp"] for s in ("left", "right")] if robot else []
        total = 0.0
        bagged = {}
        for n in K.ITEM_NAMES:
            pose = np.asarray(root_poses[n], float)
            if K.off_counter(pose):
                self.lost[n] = True
            inside = K.in_tray(n, pose) and not self.lost[n]
            bagged[n] = inside and K.let_go(n, pose, tcps)
            self.bag_frames[n] = self.bag_frames[n] + 1 if (inside and count[n] == 0) else 0
            if self.bag_frames[n] >= BAG_HOLD:
                self.unscanned_in_bag = True
            if bagged[n] and count[n] == 1:
                total += THIRD
        doubles = sum(max(c - 1, 0) for c in count.values())
        total = max(total - THIRD * doubles, 0.0)
        if self.unscanned_in_bag:
            total = min(total, 0.33)
        put_down = K.scanner_put_down(root_poses["scanner"], tcps) if tcps else False
        full = total > 0.999 and put_down
        self.held = self.held + 1 if full else 0
        if total > 0.999:
            score = 1.0 if self.held >= HOLD_S * HZ else 0.9
        else:
            score = round(total, 3)
        return {"score": float(score), "success": bool(score == 1.0),
                "scans_crackers": int(count["cracker_carton"]), "scans_juice": int(count["juice_carton"]),
                "scans_beans": int(count["bean_tin"]), "double_scans": int(doubles),
                "bagged_crackers": bool(bagged["cracker_carton"]), "bagged_juice": bool(bagged["juice_carton"]),
                "bagged_beans": bool(bagged["bean_tin"]), "items_bagged": int(sum(bagged.values())),
                "unscanned_in_bag": bool(self.unscanned_in_bag), "items_off_counter": int(sum(self.lost.values())),
                "scanner_put_down": bool(put_down), "scanner_in_cradle": bool(K.scanner_in_cradle(root_poses["scanner"])),
                "held_frames": self.held, "dropped": False, "clear": True}
