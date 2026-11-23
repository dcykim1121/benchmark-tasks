# stamp-the-invoice-approved

**Instruction:** "Approve the invoice."

Almost everyone has stamped paper or watched it done: a PAID or date stamp at a shop counter, a due date in a library book, a parcel at the post office, a passport, a child's ink-stamp set. People judge the result at a glance: the right stamp, a clean whole print, square, inside its box. Office and mail-room staff still do it daily. For a robot it is harder than it looks: the stamps look alike and differ only by a printed word; a stamp works only after a second step, a press on the ink pad; a legible print needs a real press of about 5 to 20 N with the die flat on the paper, square and inside a 5 cm box; the loose invoice book slides unless the other hand holds it; and a wrong stamp on a document cannot be undone. Here an A5 invoice book lies loose on a desk pad, the approval box of its top invoice empty. A rack holds three wooden rubber stamps labelled REJECTED (red), APPROVED (green) and COPY (blue); an open ink pad lies beside it. The instruction names neither the stamp nor the box.

## Why it matters

Stamping a document is something almost everyone has done or watched, and anyone can judge the result at a glance. It is also physical: a tool chosen by reading its label, a tool that must be prepared before it works, a placement that is judged afterwards with a ruler, and a second hand that steadies the work. Nothing in the instruction names the stamp, the ink pad or the box; all three are read off the scene. The wrong stamp is as easy to pick up as the right one, and its print on the invoice is final.

## Real parts

| object | real part | size / mass | pose (m) |
|---|---|---|---|
| desk pad | leatherette desk pad | 300 x 460 x 2 mm | centre (0.37, 0.10) |
| invoice book | A5 pad of printed invoices, glued at the top edge, loose | 148 x 210 x 4 mm, about 90 g | centre (0.345, 0.07); approval box 50 x 50 mm at (0.280, 0.033) |
| stamp rack | wooden tray with three felt-lined pockets | 150 x 76 x 12 mm | centre (0.40, -0.185) |
| stamps (3) | wooden block-handle rubber stamps, self-labelled REJECTED / APPROVED / COPY | 75 mm tall, face 20 x 44 mm, handle 24 x 46 mm, about 60 g | x = 0.354 / 0.400 / 0.446, y = -0.185 |
| ink pad | office stamp pad in a hinged tin, open | tin 70 x 110 mm, felt 64 x 104 mm, 13 mm high, gives up to 2 mm | felt centre (0.275, -0.310) |
| pen | ballpoint pen (dressing) | 140 mm | (0.47, 0.255) |

## Building the real parts

- **Stamps (3):** made-to-order wooden-mount rubber stamps from any stamp shop: rubber die 20 x 44 mm on 2.5 mm foam, the words APPROVED, REJECTED and COPY each inside a 16 x 40 mm frame. Mount and handle of planed beech: 50 x 26 mm foot, 24 x 46 mm handle, 75 mm tall overall, 60 g (+/- 10 g on a kitchen scale). A paper label 20 x 42 mm is glued on each handle top: white capitals 7.5 mm tall on green (APPROVED), red (REJECTED) and blue (COPY), reading the same way round as the die, so the judge can tell the stamps apart in the video. The labels face straight up and read from the robot's left to its right. They are legible in the overview picture and from a wrist camera within about 15 cm; in the 640-pixel top camera they are told apart by colour and position only.
- **Ink pad:** an ordinary felt office stamp pad in a hinged tin about 70 x 110 mm, black water-based ink, taped to the counter with its lid open. Keep the tin closed between sessions, at room temperature; do not leave it open for more than 2 hours. Before each session make one test print on scrap paper with a spare stamp pressed at about 10 N (kitchen scale under the pad): it must be fully legible, otherwise re-ink the felt. Re-ink after about 200 prints or one month.
- **Invoice book:** the invoice layout printed 25 times on 80 g A5 paper and glued along the top edge to a 0.6 mm greyboard back with padding glue: 148 x 210 x 4 mm, about 90 g. Lying on the desk pad it should start to slide at 0.3 to 0.5 N of sideways pull (spring scale). Replace it when it is under 3 mm thick.
- **Rack:** a 150 x 76 x 12 mm wooden block with three pockets 32 x 56 mm, 6 mm deep, routed or built up from strips, felt on the pocket floors; taped to the counter.
- **Desk pad and marks:** a 300 x 460 x 2 mm leatherette desk pad, its corners marked on the counter with 3 mm masking tape. Four L-shaped tape corners on the desk pad mark where the book lies; a second tick 10 mm outside each corner is the limit for "left where it lay".
- **Reset, every trial:** tear off the stamped invoice so the book shows a clean one; push the book into its tape corners; blot every stamp on scrap paper until it leaves no print (in the real trial a stamp is inked only by being pressed on the pad during the trial); stand the stamps in their pockets in the order REJECTED, APPROVED, COPY from the robot outward, labels reading toward the robot's right; open the ink pad.
- **Forces:** with this pad and paper each stamp must give a whole, legible print at 5 to 20 N and only a faint or partial one under its own weight. Check each stamp once per session on scrap paper lying on a kitchen scale: a reading of 0.5 to 2 kg while pressing gives the whole print. Inking should need about 0.2 kg or more on the pad. The stamps lift out of their pockets under their own weight (no retention). In the trial the ink on the paper is the evidence of the press: whole and legible means a real press, faint or partial means a touch.
- **Reading the result:** the trial is filmed from the overview position; afterwards a photo is taken straight down on the book with a ruler lying beside the approval box (the printed box, 50 mm, is the scale). Position: all four corners of the print's frame inside the box lines. Whole and clean: the full frame and word are printed, with no ghost edge wider than 4 mm; any second print, however faint, is a second mark. In place: every corner of the book inside its 10 mm ticks, its edge within 5 degrees of the tape. Angle: the frame's long side against the box's lower line, with a protractor on the photo. Which stamp printed is read from the label colour in the video and from the printed word. The starting state (clean invoice, dry stamps) is not a zero condition; the zero is the moment a REJECTED or COPY print appears on the invoice.

## Scoring

Read every step from measured contact forces, measured poses and the disclosed ink rule. The simulator's physics reports the contact force between each stamp and the invoice book and between each stamp and the ink pad's felt; nothing prints or inks by nearness alone. Ink: a stamp is inked once it stands on the felt (upright within 15 degrees, whole face on the felt) pressed with at least 2 N; resting there under its own weight (0.6 N) does not ink it; once inked it stays inked. Print: while an inked stamp's face touches the top invoice with a measured force of at least 0.2 N it leaves one mark, until it is lifted 3 mm clear: one press, one mark; a second press is a second mark. The mark is WHOLE, a legible impression, only if during that press the die lay flat on the page (all four corners of the face down) while the measured force was at least 5 N (an ordinary hand press is about 5 to 20 N; the peak is reported, nothing extra happens above 20 N). A lighter or tilted touch, including an inked stamp merely laid on the page under its own weight, leaves a faint or partial mark: it counts as a mark, as a freshly inked rubber really does leave one, but never as a whole one. A stamp held just above the page, or a dry stamp pressed however hard, leaves nothing. A mark's place and angle are the stamp's at the first moment the mark was whole; it is smeared if the stamp slid more than 4 mm over the page while touching. Marks are measured in the book's own frame, so they move with it. Any REJECTED or COPY mark on the invoice, whole or partial, at any time, scores 0 for the trial (latched); inking those stamps or printing them on the desk pad does not. Otherwise 0.5: an APPROVED mark whose centre is inside the approval box. 1.0: exactly one mark on the invoice, the APPROVED one, whole and not smeared, all four corners of its 40 x 16 mm outline inside the box, its text within 20 degrees of the page's text (not upside down), the invoice book left where it lay on the desk pad (all of it on the pad, moved less than 10 mm and turned less than 5 degrees), the other two stamps still standing in the rack, and the APPROVED stamp put down, not dropped, off the book (in the rack or on the desk, at rest, both grasp points at least 7 cm from its handle), all held 1 s. Two marks score at most 0.5. Doing nothing scores 0. Holding the book is not scored by itself: it is what keeps the box where the stamp is aimed and the book in its place when the stamp lands or lifts off askew. Reported: inked, ink_force_n (force on the felt when the stamp took ink), press_force_n (peak force of the press) and press_force_at_print_n (force at the moment the mark became whole), marks, mark_whole, mark_smear_mm, mark_offset_mm, mark_angle_deg, prints_off_sheet (inked stamps touched to the desk pad or counter), sheet_shift_mm, sheet_turn_deg, stamp_in_rack, dropped. Real trial: the same rule, read from the video and from a photo taken straight down on the book afterwards with a ruler lying beside the box (the printed box, 50 mm, is the scale). The ink on the paper is the evidence of a real press: a real stamp prints its whole frame and word legibly only when it has been inked on the pad and pressed flat with about 5 to 20 N (0.5 to 2 kg on a kitchen scale under the book; the judge checks the stamps this way before the session), so a whole, legible print is a whole mark and anything fainter or partial is a mark that is not whole. A mark is any visible ink print a stamp left on the top invoice, faint or partial included; which stamp made it is read from the video (label colour) and from the printed word. The zero is the moment a REJECTED or COPY print appears on the invoice; the starting state (clean invoice, dry stamps) is not a zero condition. 0.5: an APPROVED print whose frame centre is inside the box lines. 1.0: exactly one print on the invoice, the APPROVED one, its whole frame and every letter printed legibly (a real press, not a faint touch) and not dragged (no ghost edge wider than 4 mm), all four corners of its 40 x 16 mm frame inside the box lines, the frame's long side within 20 degrees of the box's lower line (protractor on the photo) and the word upright, every corner of the book still inside its 10 mm tick marks and its edge within 5 degrees of the tape, the other two stamps still standing in the rack, and the stamp put down by the hand (not dropped), standing or lying off the book with both grippers at least 7 cm from its handle for 1 s. A second visible print, however faint, is a second mark. A press with a dry stamp leaves nothing and costs nothing. Ink prints on the desk pad are noted, not scored.

## Simulation notes

- **Invoice book:** one free rigid block, 4 mm thick, 90 g, friction 0.40; it slides and turns on the desk pad, but its pages cannot bend, lift or tear. The top invoice's print is thin coloured geometry, no textures.
- **Stamps:** free rigid bodies of three boxes each (rubber foot, mount, handle), 60 g, under one CAD visual; the labels are thin coloured geometry on the handle tops.
- **Ink and press force:** the physics reports the contact force between each stamp and the invoice book and between each stamp and the felt (PhysX rigid contact views on the three stamps); the ink rule reads those forces (see Scoring). Inking needs 2 N or more on the felt; a whole, legible mark needs the die flat on the page at 5 N or more; a lighter touch by an inked stamp, its own 0.6 N weight included, leaves a faint mark that counts as a mark but not as a whole one; a stamp held just above the page leaves nothing. No fluid: ink never runs out, never transfers from one object to another and does not blot under a heavy press. A mark is drawn on the page as that stamp's whole framed word, in the label's colour, and moves with the book; the first two marks of each stamp are drawn, all are counted.
- **Rack, ink pad, desk pad, pen:** fixed; the rack's pockets are real recesses (a floor slab with rim and divider bars, 1 mm wider all round than drawn, standing for the chamfer at their mouths). The ink pad's tin and lid are boxes; its felt is a separate slab on a 4 N/mm spring with 2 mm of travel, so it gives under a stamp as inked felt does.
- **Holding the book:** the book is free (90 g, friction 0.40 on the desk pad), so a stamp that lands, presses or lifts off sideways pushes it; the scorer requires it to end within 10 mm and 5 degrees of where it lay, and a stamp dragged over a held book smears the mark instead. Measured once: with the holding hand barely touching (under 1 N) a 4 N press moved the book 1.9 mm; with the hand leaning on it at about 3 N a 9.8 N press moved it 0.1 mm. A fully unheld book under a careless press has not been measured.

PhysX 240 Hz, rigid bodies. Press force is the contact force PhysX reports between a stamp and the book or the felt. Ink is a rule on that force and on poses, not a fluid: a whole mark at 5 N or more with the die flat, a faint one below; it never runs out, transfers or blots. A mark is drawn as the stamp's framed word in its label colour (a real pad gives one colour). The book is one rigid block (4 mm, 90 g); the felt is a slab on a 4 N/mm spring; other parts are boxes under CAD visuals.

## Demo

`task.py` contains a scripted waypoint demo. The left hand lays its closed fingertips on the invoice's left margin and leans on them (about 3 N). The right hand comes down over the APPROVED stamp (the middle one), closes on the two ends of its handle, lifts it out of the rack, presses it on the ink pad (3 N when it takes ink, 5.5 N at the end of the dab), carries it over the approval box, stops just above the paper, sets it down flat and leans on it, lifts straight off, and lowers it back into its pocket in three stages. The left hand then lets the book go. The arms are compliant (about 0.35 N per mm of commanded travel), so the hand is sent 20 mm past the page to press: the measured press force rises to 9.8 N, the mark becomes whole as it passes 5 N (5.6 N at that step), and the book moves 0.1 mm. It reaches a score of 1 after 734 steps: the mark lands 1.7 mm from the box's centre, 1.6 degrees off square.

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
1,600 control steps (80 s). The scripted demo takes about 37 simulated seconds (a few minutes of wall time on one GPU).
Each episode writes four 20 fps camera videos (overview, top and both wrist cameras), setup/final PNGs, the
measured state trajectory (`trajectory.jsonl`) and `result.json`. The scorer reads only measured poses of the
task's objects, the robot's measured grasp points and the marks and measured press forces reported by the ink rule; `rescore.py` replays it
over the trajectory.

## Files

`task.py` (scene, the disclosed ink rule's drawing, scripted demo), `scoring.py` (stateful scorer), `stampkit.py`
(sizes, hidden colliders, the ink rule and measurements), `simkit.py` (compound rigid parts, joints and the waypoint
demo controller, adapted from the accepted task `zip-top-bag-seal`, with visual-mesh support added), `assets/`
(visual meshes). The meshes were modelled for this task with parametric CAD scripts (CadQuery) and exported to USD;
the labels, the invoice's print and the marks are thin coloured geometry made with a Blender script; no third-party
assets. No hardware validation has been performed.
