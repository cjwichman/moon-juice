# Moon Juice — design and progress notes

Happy Glass–style puzzle in the retro-space suite (Hexoplanet, Comet Blast, Wormhole).
Draw one line. The line drops under gravity and grips whatever it lands on. Juice pours from a
saucer nozzle. The level clears when the cup holds juice above the dashed line for 0.9 s.

## Files

- `index.html` — the deployable single file. Built from `src/game.html` with matter.js inlined. Do not edit directly.
- `src/game.html` — game source. Contains a `/*__MATTER__*/` placeholder.
- `src/build.py` — inlines `vendor/matter.min.js` and writes `index.html`. Run after any edit to `src/game.html`.
- `vendor/matter.min.js` — matter-js 0.19.0 (MIT).
- `favicon.svg`, `favicon.ico`, `icon-32.png`, `icon-192.png`, `apple-touch-icon.png` — icon set. PNGs and ICO were rendered from the SVG.
- `tools/check.py` — headless level checks (Playwright + Chromium). `tools/solutions.json` holds one reference stroke per hand-built level.
- `NOTES.md` — this file.

## Build and check

    python3 src/build.py            # rebuild index.html
    python3 tools/check.py all      # every hand-built level: no-stroke run loses, reference stroke wins on 3 seeds
    python3 tools/check.py gen 16 215   # same checks for generated levels
    python3 tools/check.py play 9 '[[55,338],[305,535]]' 2500 out.png   # run a stroke and screenshot it

Requires Python 3 with `playwright` (Chromium installed) and Pillow. Deploy by copying `index.html` and the icon files.

## Level data

Levels live in `HAND` in `src/game.html`, in a 400 × 700 world. Fields: `noz` (dispensers), `plats` (static slabs, `k: 'rock' | 'ice'`), `pegs` (fixed pins), `cup` (`p` = slab index, `x`, optional `slide: true`), `ink`, `drops`, `fill`, `tip`. Levels past 15 come from `genLevel`, which jitters four verified patterns (`peg`, `ice`, `ledge`, `twin`) from a seed. `GEN_SKIP` lists seeds whose layout failed the automated check. Level n uses the n-th seed not in that set, so adding a seed never changes earlier levels.

## Physics decisions

- The cup is a fixed body unless the level sets `cup.slide` (ice levels). A free cup turned every ramp into a cup-shoving problem and was the main reason the first build could not get past level 4.
- A drawn line grips rock, ice, pins, and a fixed cup. Matter's kinetic friction impulse is a constant per step rather than a share of the load, so a resting line crept down its supports once juice piled on it. The pair override sets friction to `GRIP = 8`, which Matter clamps to the sliding speed, so lines stop sliding without gaining energy.
- Once a line has been still for 0.2 s it is made static (`settleStroke`). Levels are then deterministic across seeds.
- Juice is 110 circle bodies (radius 5) with air friction 0.02. The earlier 0.01 let a pile spilling off a ledge jet sideways far enough to reach cups two hundred units away.
- Circle piles in Matter have an angle of repose of about 20°, so juice behaves like coarse sand on anything flatter. Ledges that must drain are sloped 6–8°, the ice chute in level 10 is 22°, and lines that carry juice should drop at least 15°.
- Fill target = interior area to the fill line × 0.85 hexagonal packing ÷ particle area. A full cup holds about 40 drops.
- A stroke may not start within 8 units of a body and may not pass within 7 units of one (`clearStart`, `blocked`). A line committed while overlapping a body is kicked away violently.
- Physics substep is 1000/120 ms. Raising it to 1000/60 made friction worse in the first build.

## Level design rules

- A line needs two supports (pin, slab corner, cup rim). A line that pivots on one pin tips.
- The reference stroke is drawn above its supports by `12 + 14 × |slope|` units so it clears a 27-wide pin at any angle, then falls onto them.
- The end over the cup should overhang the rim corner by 10–20 units. Longer overhangs put the line inside the cup, where it displaces juice. Shorter ones slip off.
- The start should overhang its pin by 40 units or more.
- Juice leaving a steep line overshoots. Lines that end high above the cup should be shallow (level 13 is 27° and ends 50 units above the rim).
- Ice levels: the cup slides until it meets a stroke. With the stroke frozen in place the cup rests about 40 units uphill of it, so the nozzle sits over that spot. Reference strokes are small closed triangles about 30 × 24.

## Status

All 15 hand-built levels pass `check.py all`. Generated seeds 16–219 pass `check.py gen` with four seeds skipped. Seeds beyond that are unverified. The test hooks on `window.MJ` are left in the shipped file; they are inert during play.

## Progress log

- 2026-10-03 (earlier) — First build in chat: full UI, rendering, audio, free cup. Levels 3 and 5–14 failed verification. Chat stalled repeatedly on regenerating the file.
- 2026-10-03 — Rebuilt from the earlier source on disk. Fixed cup, grip override, stroke freezing, air friction 0.02. Redesigned levels 3, 5–10, 12–14 and retuned the ice levels. Added `genSolution` so generated levels are checked automatically. Icon set rendered. Clean repo layout.
