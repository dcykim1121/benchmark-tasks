# stamp-the-invoice-approved

**Instruction:** "Approve the invoice."

The US Bureau of Labor Statistics counts 1,532,400 bookkeeping, accounting and auditing clerks (Occupational Outlook Handbook, 2025). Their listed duties include receiving and recording vouchers and checking documents for accuracy; on paper, a checked invoice is marked with a rubber stamp (approved, paid, received), as it also is in mail rooms, warehouses and clinics. The job has what a desk robot finds hard: the stamps look alike and differ only by a printed word, a stamp works only after a second step (the ink pad), the print must land flat, square and inside a 5 cm box, the loose invoice book slides unless the other hand holds it, and a wrong stamp on a document cannot be undone. Here an A5 invoice book lies loose on a desk pad, the approval box of its top invoice empty. A rack holds three wooden rubber stamps labelled REJECTED (red), APPROVED (green) and COPY (blue); an open ink pad lies beside it. The instruction names neither the stamp nor the box.

## Why it matters

Routine document handling is a large share of clerical work, and it is physical: a tool chosen by reading its label, a tool that must be prepared before it works, a placement that is judged afterwards with a ruler, and a second hand that steadies the work. Nothing in the instruction names the stamp, the ink pad or the box; all three are read off the scene. The wrong stamp is as easy to pick up as the right one, and its print on the invoice is final.

## Real parts

| object | real part | size / mass | pose (m) |
|---|---|---|---|
| desk pad | leatherette desk pad | 300 x 460 x 2 mm | centre (0.37, 0.10) |
| invoice book | A5 pad of printed invoices, glued at the top edge, loose | 148 x 210 x 4 mm, about 90 g | centre (0.345, 0.07); approval box 50 x 50 mm at (0.280, 0.033) |
| stamp rack | wooden tray with three felt-lined pockets | 150 x 76 x 12 mm | centre (0.40, -0.185) |
| stamps (3) | wooden block-handle rubber stamps, self-labelled REJECTED / APPROVED / COPY | 75 mm tall, face 20 x 44 mm, handle 24 x 46 mm, about 60 g | x = 0.354 / 0.400 / 0.446, y = -0.185 |
| ink pad | office stamp pad in a hinged tin, open | tin 70 x 110 mm, felt 64 x 104 mm, 13 mm high | felt centre (0.275, -0.310) |
| pen | ballpoint pen (dressing) | 140 mm | (0.47, 0.255) |

## Building the real parts

- **Stamps (3):** made-to-order wooden-mount rubber stamps from any stamp shop: rubber die 20 x 44 mm on 2.5 mm foam, the words APPROVED, REJECTED and COPY each inside a 16 x 40 mm frame. Mount and handle of planed beech: 50 x 26 mm foot, 24 x 46 mm handle, 75 mm tall overall, 60 g (+/- 10 g on a kitchen scale). A paper label 20 x 42 mm is glued on each handle top: white capitals 7.5 mm tall on green (APPROVED), red (REJECTED) and blue (COPY), reading the same way round as the die, so the judge can tell the stamps apart in the video. The labels face straight up and read from the robot's left to its right. They are legible in the overview picture and from a wrist camera within about 15 cm; in the 640-pixel top camera they are told apart by colour and position only.
- **Ink pad:** an ordinary felt office stamp pad in a hinged tin about 70 x 110 mm, black water-based ink, taped to the counter with its lid open. Keep the tin closed between sessions, at room temperature; do not leave it open for more than 2 hours. Before each session make one test print on scrap paper with a spare stamp pressed at about 10 N (kitchen scale under the pad): it must be fully legible, otherwise re-ink the felt. Re-ink after about 200 prints or one month.
- **Invoice book:** the invoice layout printed 25 times on 80 g A5 paper and glued along the top edge to a 0.6 mm greyboard back with padding glue: 148 x 210 x 4 mm, about 90 g. Lying on the desk pad it should start to slide at 0.3 to 0.5 N of sideways pull (spring scale). Replace it when it is under 3 mm thick.
- **Rack:** a 150 x 76 x 12 mm wooden block with three pockets 32 x 56 mm, 6 mm deep, routed or built up from strips, felt on the pocket floors; taped to the counter.
- **Desk pad and marks:** a 300 x 460 x 2 mm leatherette desk pad, its corners marked on the counter with 3 mm masking tape. Four L-shaped tape corners on the desk pad mark where the book lies; a second tick 10 mm outside each corner is the limit for "left where it lay".
- **Reset, every trial:** tear off the stamped invoice so the book shows a clean one; push the book into its tape corners; blot every stamp on scrap paper until it leaves no print (in the real trial a stamp is inked only by being pressed on the pad during the trial); stand the stamps in their pockets in the order REJECTED, APPROVED, COPY from the robot outward, labels reading toward the robot's right; open the ink pad.
- **Forces:** a legible print needs about 5 to 20 N on the stamp (check on a kitchen scale); the stamps lift out of their pockets under their own weight (no retention).
- **Reading the result:** the trial is filmed from the overview position; afterwards a photo is taken straight down on the book with a ruler lying beside the approval box (the printed box, 50 mm, is the scale). Position: all four corners of the print's frame inside the box lines. Whole and clean: the full frame and word are printed, with no ghost edge wider than 4 mm; any second print, however faint, is a second mark. In place: every corner of the book inside its 10 mm ticks, its edge within 5 degrees of the tape. Angle: the frame's long side against the box's lower line, with a protractor on the photo. Which stamp printed is read from the label colour in the video and from the printed word. The starting state (clean invoice, dry stamps) is not a zero condition; the zero is the moment a REJECTED or COPY print appears on the invoice.

## Scoring

Read every step from measured poses and from the disclosed ink rule. Rule: a stamp is inked once its rubber face has been pressed on the ink pad (whole face inside the felt's outline and within 2 mm of it, stamp upright within 15 degrees), and it stays inked. Each time an inked stamp's face touches the top invoice (any corner or the centre of the face over the page and within 1.5 mm of it, at any tilt) it leaves one mark, until it is lifted 3 mm clear: one press, one mark, however long it is held; a second press is a second mark, re-inked or not. A mark's place and angle are the stamp's when most of its face was down; it is whole if all four corners of the face were down at once, and smeared if the stamp slid more than 4 mm over the page while touching. A dry stamp leaves nothing. Marks are measured in the book's own frame, so they move with it. Any REJECTED or COPY mark on the invoice, whole or partial, at any time, scores 0 for the trial (latched); inking those stamps or printing them on the desk pad does not. Otherwise 0.5: an APPROVED mark whose centre is inside the approval box. 1.0: exactly one mark on the invoice, the APPROVED one, whole and not smeared, all four corners of its 40 x 16 mm outline inside the box, its text within 20 degrees of the page's text (not upside down), the invoice book left where it lay on the desk pad (all of it on the pad, moved less than 10 mm and turned less than 5 degrees), the other two stamps still standing in the rack, and the APPROVED stamp put down, not dropped, off the book (in the rack or on the desk, at rest, both grasp points at least 7 cm from its handle), all held 1 s. Two marks score at most 0.5. Doing nothing scores 0. Holding the book is not scored by itself: it is what keeps the box where the stamp is aimed and the book in its place when the stamp lands or lifts off askew. Reported: inked, marks, mark_whole, mark_smear_mm, mark_offset_mm, mark_angle_deg, prints_off_sheet (inked stamps touched to the desk pad or counter), sheet_shift_mm, sheet_turn_deg, stamp_in_rack, dropped. Real trial: the same rule, read from the video and from a photo taken straight down on the book afterwards with a ruler lying beside the box (the printed box, 50 mm, is the scale). A mark is any visible ink print a stamp left on the top invoice, faint or partial included; which stamp made it is read from the video (label colour) and from the printed word. The zero is the moment a REJECTED or COPY print appears on the invoice; the starting state (clean invoice, dry stamps) is not a zero condition. 0.5: an APPROVED print whose frame centre is inside the box lines. 1.0: exactly one print on the invoice, the APPROVED one, its whole frame and word printed and not dragged (no ghost edge wider than 4 mm), all four corners of its 40 x 16 mm frame inside the box lines, the frame's long side within 20 degrees of the box's lower line (protractor on the photo) and the word upright, every corner of the book still inside its 10 mm tick marks and its edge within 5 degrees of the tape, the other two stamps still standing in the rack, and the stamp put down by the hand (not dropped), standing or lying off the book with both grippers at least 7 cm from its handle for 1 s. A second visible print, however faint, is a second mark. A press with a dry stamp leaves nothing and costs nothing. Ink prints on the desk pad are noted, not scored.

## Simulation notes

- **Invoice book:** one free rigid block, 4 mm thick, 90 g, friction 0.40; it slides and turns on the desk pad, but its pages cannot bend, lift or tear. The top invoice's print is thin coloured geometry, no textures.
- **Stamps:** free rigid bodies of three boxes each (rubber foot, mount, handle), 60 g, under one CAD visual; the labels are thin coloured geometry on the handle tops.
- **Ink:** a rule on measured poses (see Scoring). A stamp pressed on the felt is inked and stays inked; every separate touch of an inked face on the top invoice leaves one mark, whole or partial, smeared or not; touches on the desk pad or counter are counted and reported. No fluid: ink never runs out and never transfers from one object to another (an inked stamp does not ink a gripper or another stamp). A mark is drawn on the page as that stamp's whole framed word, in the label's colour, and moves with the book; the first two marks of each stamp are drawn, all are counted.
- **Rack, ink pad, desk pad, pen:** fixed; the rack's pockets are real recesses (a floor slab with rim and divider bars, 1 mm wider all round than drawn, standing for the chamfer at their mouths), the ink pad is its felt, tin and open lid as boxes.
- **Holding the book:** the book is free (90 g, friction 0.40 on the desk pad), so a stamp that lands or lifts off sideways pushes it; the scorer requires it to end within 10 mm and 5 degrees of where it lay, and a stamp dragged over a held book smears the mark instead. In the scripted demo the stamp comes straight down and the book does not move at all (0.0 mm), so the demo does not show how much the holding hand contributes; that has not been measured with a careless press.

PhysX 240 Hz, rigid bodies. The invoice book is one rigid block (4 mm, 90 g): it slides and turns; its pages cannot bend or lift. Ink is a rule on measured poses, not a fluid: it never runs out or transfers between objects; a mark is always drawn as the stamp's whole framed word in its label colour (a real pad gives one colour). Stamps, rack, ink pad and desk pad are boxes under the CAD visuals (rack pockets 1 mm wider all round than drawn). Labels and print are thin coloured geometry.

## Demo

`task.py` contains a scripted waypoint demo. The left hand lays its closed fingertips on the invoice's left margin and keeps them there. The right hand comes down over the APPROVED stamp (the middle one), closes on the two ends of its handle, lifts it out of the rack, presses it on the ink pad, carries it over the approval box, stops just above the paper, presses it straight down in the box, lifts straight off, and lowers it back into its pocket in three stages. The left hand then lets the book go. It reaches a score of 1 after 700 steps: the mark lands 0.1 mm from the box's centre, 1.6 degrees off square, and the book does not move.

## Reproduction

`runtime/` holds the exported runtime. From this task directory, with the `yam-inspect-isaac:6.1.0` image
(or `python3 runtime/build_image.py --image yam-inspect-isaac:6.1.0`):

```bash
# outputs go OUTSIDE the task folder: the runner snapshots the task folder into each run
OUT="$(cd .. && pwd)/stamp-the-invoice-approved-outputs"
mkdir -p /tmp/rc-task-home/tmp "$OUT"
docker run --rm --gpus device=0 --network host --shm-size 8g \
  -v "$PWD":/task:ro -v "$OUT":/outputs:rw \
  -v /tmp/rc-task-home:/tmp/task-home:rw -e HOME=/tmp/task-home -e TMPDIR=/tmp/task-home/tmp \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e OMNI_KIT_ACCEPT_EULA=YES -e ACCEPT_EULA=Y \
  --workdir /outputs --entrypoint /isaac-sim/python.sh yam-inspect-isaac:6.1.0 \
  /task/run.py --policy scripted --episodes 1 --livestream 0 --viz none
python runtime/rescore.py --task task.py "$OUT"/stamp-the-invoice-approved/RUN/episode-01/trajectory.jsonl \
  --expect "$OUT"/stamp-the-invoice-approved/RUN/episode-01/result.json
```

Seed 0; fixed starting poses with no randomisation. Control is 20 Hz and physics 240 Hz; the run limit is
1,600 control steps (80 s). The scripted demo takes about 35 simulated seconds (a few minutes of wall time on one GPU).
Each episode writes four 20 fps camera videos (overview, top and both wrist cameras), setup/final PNGs, the
measured state trajectory (`trajectory.jsonl`) and `result.json`. The scorer reads only measured poses of the
task's objects, the robot's measured grasp points and the marks reported by the ink rule; `rescore.py` replays it
over the trajectory.

## Files

`task.py` (scene, the disclosed ink rule's drawing, scripted demo), `scoring.py` (stateful scorer), `stampkit.py`
(sizes, hidden colliders, the ink rule and measurements), `simkit.py` (compound rigid parts, joints and the waypoint
demo controller, adapted from the accepted task `zip-top-bag-seal`, with visual-mesh support added), `assets/`
(visual meshes). The meshes were modelled for this task with parametric CAD scripts (CadQuery) and exported to USD;
the labels, the invoice's print and the marks are thin coloured geometry made with a Blender script; no third-party
assets. No hardware validation has been performed.
