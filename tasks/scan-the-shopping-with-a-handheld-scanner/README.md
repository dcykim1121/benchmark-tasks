# scan-the-shopping-with-a-handheld-scanner

**Instruction:** "Scan the shopping and put it in the bagging area."

Checkout work is one of the commonest jobs there is, and most of it is this: find the barcode on each item, point the scanner at it, hear it read once, and bag the item. The skill is physical. The scanner is a tool held by its grip whose window has to be aimed at a small target at the right distance and angle; a code that faces the wrong way has to be found and the item turned with the other hand; and each item has to be read exactly once, because an unread item in the bag is stock walking out unpaid and a second read charges the customer twice. Here three items stand on a checkout counter: a tin of beans, a carton of crackers and a juice carton. The crackers' barcode faces the robot, the juice's faces its right front, and the tin's faces away. A cordless handheld scanner stands in its cradle, a bagging tray is at one side and a customer display has one lamp per item.

## Why it matters

Scanning and bagging is everyday retail work, done millions of times a day, and it is a clean test of tool use with two hands: one hand holds a tool whose working end has to be aimed (not touched) at a target, the other hand presents the goods. Nothing in the instruction names the scanner, says which codes are visible, or says that the tin has to be turned; all of that is read from the scene. The two ways the job goes wrong in a real shop are both scored: an item bagged without a read, and an item read twice.

## Real parts

| object | real part | size / mass | pose (m) |
|---|---|---|---|
| handheld scanner | cordless pistol-grip barcode scanner (real trial: paired to a laptop that logs each read) | 100 x 64 x 160 mm, grip 34 x 30 mm, 180 g | standing in the cradle |
| cradle | the scanner's charging cradle | 96 x 86 x 30 mm, socket 42 x 38 x 18 mm | socket at (0.33, -0.36) |
| beans | tin of baked beans | 66 mm across, 110 mm tall, 300 g | (0.375, 0.13), barcode away from the robot |
| crackers | carton of crackers (real trial: empty carton with a weight) | 110 x 55 x 170 mm, 200 g | (0.40, -0.01), barcode toward the robot |
| juice | gable-top juice carton (real trial: filled with water) | 60 x 60 x 140 mm, 250 g | (0.47, -0.11), turned 70 degrees, barcode toward the robot's right front |
| counter mat | rubber checkout mat | 220 x 380 x 2 mm | (0.435, 0.0) |
| bagging tray | shallow plastic tray | 240 x 220 mm, rim 22 mm | (0.36, 0.29) |
| customer display | pole display with three lamps (real trial: the laptop's screen) | 180 mm wide, 285 mm tall | (0.62, 0.12) |

## Scoring

Read from measured poses every step. A read of an item registers when the scanner's window is aimed at its barcode: barcode centre 5 to 20 cm from the window centre and within 3 cm of the window's axis line, axis within 30 degrees of the barcode's normal, held 0.5 s. A code is read again (a double charge) if the aim has left it for 0.5 s and then holds on it again. An item is in the tray when its whole bounding box is inside the tray's outline and it rests on the tray's floor, standing or lying; it counts as bagged once it is also let go (both grippers at least 3 cm from it). Each item earns 1/3 when it has been read exactly once and is bagged at the end. An item that is in the tray for 0.5 s without having been read latches unscanned_in_bag: that item earns nothing and the trial is capped at 0.33, even if it is read afterwards. Every extra read takes 1/3 off (floor 0); the item read twice also earns nothing. An item that leaves the counter earns nothing. With all three items earned the score is 0.9 while the scanner is in a hand, and 1.0 once it is out of the hands (standing in its cradle or lying on the counter, both grippers at least 8 cm from its grip) for 1 s. How the scanner and the item are brought together is free: an item held up to the scanner in its cradle is read by the same rule. Doing nothing scores 0. Reported: reads per item, double reads, items bagged, the flag, scanner put down. Real trial: the scanner's own log gives the reads per item and their times (a code logged twice is a double charge); the video shows whether an item went into the tray before its read; at the end the judge checks that all three stand or lie wholly inside the tray and that the scanner is out of the grippers.

## Simulation notes

- **Reading a barcode:** a rule, not optics. Each step the window's centre and axis are taken from the scanner's measured pose and each barcode's centre and normal from its item's measured pose; distance, angle and aim are tested and a 0.5 s hold registers a read. Occlusion is ignored: a code can be read through a gripper or another item. The scorer recomputes the reads from the trajectory with the same rule, so a run can be rescored.
- **Scanner:** a free body, 180 g, two box colliders (grip and head); its window is at (0.068, 0, 0.128) m in its own frame (origin under the grip's foot, grip along z) and looks along +x tipped 10 degrees down.
- **Cradle:** fixed; a socket of four blocks round a floor, 2 to 4 mm wider each side than drawn (it stands for the drawn socket's flared mouth). The scanner stands in it under its own weight.
- **Goods:** free rigid bodies with one primitive collider each (the juice carton has a second box for its gable), uniform contents.
- **Tray, mat, display:** fixed. The display's three lamps are drawn unlit or lit; the rule switches them.
- **Printed faces and barcodes:** thin coloured geometry, no textures; invented product names, no brands.

PhysX 240 Hz, rigid bodies. The scanner reads nothing optically: a read is a rule on the measured poses of the scanner and the items (distance, angle, aim, 0.5 s hold); things in between are ignored, so a code can be read through a gripper or another item. Lamps are visuals switched by the rule. Colliders are primitives under CAD visuals: scanner two boxes, cradle a socket of blocks 2 to 4 mm wider than drawn, cartons boxes, tin a cylinder, tray a floor and four walls. Labels are thin geometry.

## Demo

`task.py` contains a scripted waypoint demo. The right hand takes the scanner by its grip out of the cradle. It comes round to the juice carton's barcode and holds the window 10 cm from it for 1.5 s, lifts the aim off, and does the same at the crackers' barcode. Meanwhile the left hand takes the tin by its top from above, lifts it, turns it half round about the vertical and sets it down with its barcode toward the robot. The right hand reads the tin, lifts the aim off and stands the scanner back in its socket. The left hand then carries the tin, the crackers and the juice into the tray one at a time, each held by its sides, and lets go. It reaches a score of 1 after 1,403 steps.

## Reproduction

`runtime/` holds the exported runtime. From this task directory, with the `yam-inspect-isaac:6.1.0` image
(or `python3 runtime/build_image.py --image yam-inspect-isaac:6.1.0`):

```bash
# outputs go OUTSIDE the task folder: the runner snapshots the task folder into each run
OUT="$(cd .. && pwd)/scan-the-shopping-with-a-handheld-scanner-outputs"
mkdir -p /tmp/rc-task-home/tmp "$OUT"
docker run --rm --gpus device=0 --network host --shm-size 8g \
  -v "$PWD":/task:ro -v "$OUT":/outputs:rw \
  -v /tmp/rc-task-home:/tmp/task-home:rw -e HOME=/tmp/task-home -e TMPDIR=/tmp/task-home/tmp \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e OMNI_KIT_ACCEPT_EULA=YES -e ACCEPT_EULA=Y \
  --workdir /outputs --entrypoint /isaac-sim/python.sh yam-inspect-isaac:6.1.0 \
  /task/run.py --policy scripted --episodes 1 --livestream 0 --viz none
python runtime/rescore.py --task task.py "$OUT"/scan-the-shopping-with-a-handheld-scanner/RUN/episode-01/trajectory.jsonl \
  --expect "$OUT"/scan-the-shopping-with-a-handheld-scanner/RUN/episode-01/result.json
```

Seed 0; fixed starting poses with no randomisation. Control is 20 Hz and physics 240 Hz; the run limit is
2,400 control steps (120 s). The scripted demo takes about 70 simulated seconds (a few minutes of wall time on one GPU).
Each episode writes four 20 fps camera videos (overview, top and both wrist cameras), setup/final PNGs, the
measured state trajectory (`trajectory.jsonl`) and `result.json`. The scorer reads only measured poses of the
task's objects and the robot's measured grasp points; `rescore.py` replays it over the trajectory.

## Files

`task.py` (scene, the disclosed scan rule, scripted demo), `scoring.py` (stateful scorer and the scan counter),
`scankit.py` (sizes, hidden colliders and measurements), `simkit.py` (compound rigid parts, joints and the waypoint
demo controller, adapted from the accepted task `zip-top-bag-seal`, with visual-mesh support added), `assets/`
(visual meshes). The meshes were modelled for this task with parametric CAD scripts (CadQuery) and exported to USD;
no third-party assets. No hardware validation has been performed.
