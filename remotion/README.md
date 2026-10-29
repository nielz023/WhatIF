# Cut-out cartoon Shorts (Remotion)

Vertical 1080x1920 at 60 fps, delivered as 2160x3840. The first Short here is
`VacuumBalloon`: "Why fill a balloon with helium, when you could fill it with nothing?"

## Run it

```
cd remotion
npm install
npm run studio          # Remotion Studio: http://localhost:3000/VacuumBalloon
npm run render          # 4K: out/vacuum-4K.mp4 (gl 'angle' is set in remotion.config.ts)
```

`VacuumCutouts` is the check sheet with every cut-out on a coloured background.
For a quick preview without the depth-of-field blur: `--props='{"noBlur":true}'`.

## Where things are

| Path | What |
|---|---|
| `src/vacuum/Scene.tsx` | the Short: camera, pose timeline, physics, effects |
| `src/vacuum/timing.ts` | beat times from the voice (ElevenLabs Scribe word times + loudness pauses) |
| `src/vacuum/events.ts` | world layout and physics event times (shared with the sound) |
| `src/vacuum/poses.ts` | every pose of the character as its own drawing |
| `src/vacuum/draw/` | the cut-outs: character, balloon, pump, diamond, puffs, scenery, the 1670 scroll |
| `src/vacuum/cues.ts` | sound-effect cue list (time, level) |
| `public/vacuum/vo/take1.mp3` | voice: ElevenLabs, Tim Riley - Natural. Conversational, eleven_v4, one take |
| `public/vacuum/sfx/` | sound effects, made by `scripts/make_sfx.py` |
| `images/vacuum/` | word times, QA sheets (cut-outs, contact sheets, sound waveforms) |

## Scripts

- `python3 -I scripts/make_sfx.py`: rebuild the sound effects.
- `node scripts/stills.mjs <dir> <scale> <t1> <t2> ...` then `python3 -I scripts/sheet.py <dir> <out.png>`:
  contact sheet of stills at given times.
- `python3 -I scripts/popscan.py <video.mp4>`: flags frame-to-frame jumps; every flag should be an
  intended pose swap, impact or cut.

## The pictures

The cut-outs are vector drawings in code (`src/vacuum/draw/`) in the flat style: thick even black
outlines, flat colours, one soft shade. Higgsfield was not reachable from the cloud session that made
this Short, so no AI pictures were used. Each pose is a separate drawing; the scene swaps them inside
a squash, never with a cross-fade.
