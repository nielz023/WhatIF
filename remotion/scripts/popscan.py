"""Pop scan: mean frame-to-frame difference of a blurred 270x480 copy; flags frames above
2.2x the local median. python3 -I scripts/popscan.py video.mp4 [fps]"""
import subprocess, sys
import numpy as np
src = sys.argv[1]
fps = float(sys.argv[2]) if len(sys.argv) > 2 else 60
w, h = 270, 480
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={w}:{h},gblur=sigma=1.5,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
flags = []
for i in range(len(d)):
    lo, hi = max(0, i - 15), min(len(d), i + 16)
    med = np.median(d[lo:hi])
    if d[i] > 2.2 * max(med, 0.15) and d[i] > 0.6:
        flags.append((i + 1, (i + 1) / fps, d[i], med))
print(f'{len(fr)} frames, mean diff {d.mean():.2f}, max {d.max():.2f} at frame {d.argmax() + 1}')
for f, t, v, m in flags:
    print(f'  frame {f:5d}  t={t:6.3f}s  diff {v:6.2f}  local median {m:5.2f}')
np.save('/tmp/claude-0/-home-user-WhatIF/4351d7bd-2018-5d5b-9a7a-044a585b96ad/scratchpad/diffs.npy', d)
