# scan-the-shopping-with-a-handheld-scanner

**Instruction:** "Scan the shopping and put it in the bagging area."

The US Bureau of Labor Statistics counts 3,106,300 cashier jobs (2025, Occupational Outlook Handbook) and lists 'Scan customers' purchases' and 'Bag or wrap customers' purchases' among what cashiers typically do: this is the core of the job. The skill is physical. The scanner is a tool held by its grip whose window has to be aimed at a small target at the right distance and angle, with nothing in between; a code that faces the wrong way has to be found and the item turned with the other hand; and each item has to be read exactly once, because an unread item in the bag is stock leaving unpaid and a second read charges the customer twice. Here three items stand on a checkout counter: a tin of beans, a carton of crackers and a juice carton. The crackers' barcode faces the robot, the juice's faces its right front, and the tin's faces away. A cordless handheld scanner stands in its cradle, a bagging tray is at one side and a customer display has one lamp per item.

## Why it matters

Scanning and bagging is everyday retail work, done millions of times a day, and it is a clean test of tool use with two hands: one hand holds a tool whose working end has to be aimed (not touched) at a target, the other hand presents the goods. Nothing in the instruction names the scanner, says which codes are visible, or says that the tin has to be turned; all of that is read from the scene. The two ways the job goes wrong in a real shop are both scored: an item bagged without a read, and an item read twice.

## Real parts

| object | real part | size / mass | pose (m) |
|---|---|---|---|
| handheld scanner | cordless pistol-grip barcode scanner (real trial: paired to a laptop that logs each read) | 100 x 64 x 160 mm, grip 34 x 30 mm, 180 g | standing in the cradle |
| cradle | the scanner's charging cradle | 96 x 86 x 30 mm, socket 42 x 38 x 18 mm | socket at (0.33, -0.36) |
| beans | tin of baked beans | 66 mm across, 110 mm tall, 300 g | (0.375, 0.13), barcode away from the robot |
| crackers | carton of crackers (real trial: empty carton ballasted to 200 g) | 110 x 55 x 170 mm, 200 g | (0.40, -0.01), barcode toward the robot |
| juice | gable-top juice carton (real trial: filled with water) | 60 x 60 x 140 mm, 250 g | (0.47, -0.11), turned 70 degrees, barcode toward the robot's right front |
| counter mat | rubber checkout mat | 220 x 380 x 2 mm | (0.435, 0.0) |
| bagging tray | shallow plastic tray | 240 x 220 mm, rim 22 mm | (0.36, 0.29) |
| customer display | pole display with three lamps (real trial: the laptop's screen) | 180 mm wide, 285 mm tall | (0.62, 0.12) |

## Building the real parts

Nothing here is special-made; every part is an ordinary shop item or a printed sticker.

- **Scanner and stand:** any cordless pistol-grip 1D/2D barcode scanner sold with a charging cradle or stand in which it stands upright by the foot of its grip (the common retail type). Limits for this station: grip 28 to 36 mm thick where it is held, mass 150 to 250 g with battery, overall height 150 to 180 mm, scan window at least 40 x 20 mm at the front of the head. Pair it to a laptop as a keyboard device with a text file open, suffix set to Enter, so that each read writes one line; add the time with any keystroke logger or film the laptop screen. In the scanner's settings set the same-code re-read delay to 0.5 s and the beeper on. Tape the cradle down on its outline with the scanner's window facing away from the robot.
- **Tin:** a full, sealed 400 to 420 g tin is heavier than the simulated 300 g; use a 300 g tin (66 mm x 110 mm class), or an empty tin of that size refilled with dry rice to 300 g and resealed with its lid taped. Paper label left on.
- **Crackers carton:** an empty cracker or cereal-bar carton cut down or chosen at about 110 x 55 x 170 mm, ballasted to 200 g with a bag of dry rice taped inside at the middle, flaps glued shut.
- **Juice carton:** an empty, rinsed gable-top carton about 60 x 60 x 140 mm (250 to 330 ml), refilled with 190 ml of water to make 250 g and recapped; or filled with dry rice to 250 g if liquids are not allowed at the station.
- **Barcodes:** three different EAN-13 codes printed black on white matt sticker paper at 45 x 30 mm (bars about 38 mm wide and 20 mm tall, digits under them), one per item, long side level: on the tin 85 mm up (centre) on one side; on the crackers carton 110 mm up on one narrow face; on the juice carton 90 mm up on one side face. Any other barcode already printed on a package is covered with plain tape, so that each item has exactly one readable code.
- **Tray:** any shallow plastic tray about 240 x 220 mm inside a 20 to 25 mm rim (a cafeteria or drawer tray), taped down.
- **Mat:** a 220 x 380 mm piece of 2 mm black rubber or neoprene sheet, taped down; tape outlines on it mark where each item stands and an arrow marks which way each barcode faces.
- **Display:** not needed for scoring: the scanner's beep and the laptop's log stand in for the lamps. If wanted, three green LEDs or stickers on a card behind the mat.
- **Start state:** tin with its barcode facing directly away from the robot; crackers carton with its barcode on the face toward the robot; juice carton turned 70 degrees anticlockwise (seen from above) from barcode-toward-robot, so that its barcode faces the robot's right front. Positions as in the table above, within 5 mm of the tape outlines.
- **Reset between trials:** put the three items back on their outlines and check the three facings against the arrows; stand the scanner in its cradle; clear the log file; make one test read of a spare code and delete that line.
- **Judging:** the log (one line per read: time, code), the trial video from the side and a top photo at the end; see Scoring.

## Scoring

Read from measured poses every step. A read of an item registers when the scanner's window is aimed at its barcode: barcode centre 5 to 20 cm from the window centre and within 3 cm of the window's axis line, axis within 30 degrees of the barcode's normal, a clear line of sight (window on the barcode's outward side; the straight line from window to barcode passes through no item's body, its own included), held 0.5 s. One code at a time: the one nearest the axis. A code is read again (a double charge) if the aim has left it for 0.5 s and then holds on it again. An item is in the tray when every corner of its bounding box (the whole item, not its centre) is inside the tray's outline and it is down on the tray's floor or on other goods in it, standing or lying; it is bagged once it is also let go (both grippers at least 3 cm from it). Each item earns 1/3 when it has been read exactly once and is bagged at the end. An item put in the tray unread (0.5 s on its floor, or let go on the goods in it) latches unscanned_in_bag: that item earns nothing and the trial is capped at 0.33, even if it is read afterwards. Every extra read takes 1/3 off (floor 0); the item read twice also earns nothing. An item that leaves the counter, or is dropped, thrown or knocked (it moves faster than 0.5 m/s with no gripper at it), earns nothing. With all three items earned the score is 0.9 until the scanner is put away for 1 s: both grippers at least 8 cm from its grip, and it stands in its cradle or lies on the counter, no part of it over the tray or within 2 cm of an item, never dropped; then 1.0. Taking an item out of the tray and putting it back changes nothing; a read item put back on the counter earns nothing. An item held up to the scanner in its cradle is read by the same rule. Doing nothing scores 0. Reported: reads per item, double reads, items bagged, items dropped, the flag, scanner put down. Real trial: the scanner's log has one line per read (time, code) with its same-code delay set to 0.5 s. Reads per item = lines with that item's code; exactly one line each is required; a second line is a double charge. A read through or from behind an item cannot happen. From the video: the time each item is first set down in the tray or on goods in it; if that is before its log line, the flag is set. An item that falls more than 2 cm out of the gripper or is knocked over earns nothing. From a top photo at the end: each item wholly inside the tray's rim, grippers clear; scanner in its stand or lying on the counter clear of tray and goods.

## Simulation notes

- **Reading a barcode:** a rule, not optics. Each step the window's centre and axis are taken from the scanner's measured pose and each barcode's centre and normal from its item's measured pose; distance, angle and aim are tested, then the line of sight: the window must be on the barcode's outward side and 49 points along the straight line from window to barcode must all lie outside every item's collider (drawn in 2 mm). A 0.5 s hold registers a read. Grippers, the tray and the cradle do not block the line. The scorer recomputes the reads from the trajectory with the same rule, so a run can be rescored.
- **Scanner:** a free body, 180 g, two box colliders (grip and head); its window is at (0.068, 0, 0.128) m in its own frame (origin under the grip's foot, grip along z) and looks along +x tipped 10 degrees down.
- **Cradle:** fixed; a socket of four blocks round a floor, 2 to 4 mm wider each side than drawn (it stands for the drawn socket's flared mouth). The scanner stands in it under its own weight.
- **Goods:** free rigid bodies with one primitive collider each (the juice carton has a second box for its gable), uniform contents.
- **Tray, mat, display:** fixed. The display's three lamps are drawn unlit or lit; the rule switches them.
- **Printed faces and barcodes:** thin coloured geometry, no textures; invented product names, no brands.

PhysX 240 Hz, rigid. The scanner reads nothing optically: a read is a rule on measured poses (distance, angle, aim, line of sight past the goods' colliders, 0.5 s hold). Grippers, tray and cradle do not block the line; glare, focus and bar orientation are not modelled. Lamps are switched by the rule. Colliders are primitives under CAD visuals: scanner two boxes, cradle a socket 2 to 4 mm wider than drawn, cartons boxes, tin a cylinder, tray a floor and four walls. Labels are thin geometry.

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
