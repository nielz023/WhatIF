# Montage video 3: scènes zonder eigen render

Volgens het script hebben scène 0 (teaser) en scène 2 (flash-forwards) geen eigen 3D-render. Ze worden in de montage geknipt uit beelden van andere scènes.

| Script | Bron | Audio |
|---|---|---|
| 0a-0e teaser dag 4 | n10a_stroom (0a-0c), n10c_voordeur 10c3 (0d), zwart 1 s (0e). De UE-versie van N00 mag ook. | N00-01 |
| 2a supermarkt dag 1 | n07b_supermarkt (rennende karren) | N02-01 |
| 2b vriend achter het stuur | n08c_vriend_auto | - |
| 2c zebra op de snelweg | n12a_snelweg (UE of Blender) | - |
| 2d de brug | n13a_brug (UE of Blender) | N02-02 |
| 2e sneeuw en slagboom | n17a_winter / n15a_slagboom | - |
| 2f oudere jongen in rood licht | n21b_middernacht (close-up) | N02-03 |
| 2b-kaart "1 DAY EARLIER" | zwart met witte tekst, 1 s | klok-tik |

Elk flash-forward-shot duurt 1,5-2 s, met een witte flitsframe ertussen en de beat op elke cut. Daaronder staat geen HUD.

## Eindmontage draaien (op de pc)

```
blender -b -P anim/edit/assemble_v3.py -- --scenes "<WHAT IF>\video3\scenes" --json "<map met out\<code>\montage.json>" --out "<WHAT IF>\video3\WHAT_IF_NO_RULES.mp4"
```

- `--preview 0-45` maakt een proefstuk op halve resolutie, `--allow-missing` zet zwart op de plek van ontbrekende scènes.
- In `videos/no-rules/ue_overlays.json` staat per Unreal-clip de scène, de bestandsnaam en de starttijd binnen die scène (t0, in seconden). De clip ligt als beeld over de Blender-scène, zonder eigen geluid.
- De mix wordt gemeten en via een limiter op -1 dBFS naar -14 LUFS gezet. Daarna is `<uit>_mix_master.wav` het enige geluidsspoor.
