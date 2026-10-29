"""Contact sheet: python3 -I scripts/sheet.py <dir with tNN.NN.png> <out.png> [cols]"""
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
files = sorted(glob.glob(os.path.join(src, 't*.png')))
ims = [Image.open(f).convert('RGB') for f in files]
w, h = ims[0].size
tw = 270; th = int(h * tw / w)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 26)), (30, 30, 30))
try:
    font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 20)
except Exception:
    font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(zip(files, ims)):
    x = (i % cols) * tw; y = (i // cols) * (th + 26)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 26))
    d.text((x + 6, y + 2), os.path.basename(f)[1:-4] + ' s', fill=(255, 255, 255), font=font)
sheet.save(out)
print(out, sheet.size)
