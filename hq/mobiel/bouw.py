"""Bouwt dist/page.html: page.html + actuele status.json als startstand (de pagina leest daarna elke minuut live)."""
import json, pathlib, shutil, sys
here = pathlib.Path(__file__).parent
status = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/driftmark-hq/status.json")
seed = json.dumps(json.loads(status.read_text()), ensure_ascii=False).replace("</", "<\\/")
src = (here / "page.html").read_text()
out = src.replace("<script>\n(function", "<script>window.__DM_SEED__=" + seed + ";</script>\n<script>\n(function", 1)
d = here / "dist"; (d / "img").mkdir(parents=True, exist_ok=True)
(d / "page.html").write_text(out)
for f in (here / "assets").iterdir():
    if f.is_file() and f.suffix != ".js": shutil.copy(f, d / "img" / f.name)
shutil.rmtree(d / "kantoor", ignore_errors=True)
shutil.copytree(here / "assets" / "kantoor", d / "kantoor")
shutil.copy(here / "assets" / "kantoor-boot.js", d / "kantoor" / "kantoor-boot.js")
import re
for name in sorted(set(re.findall(r"\./img/([a-z0-9_]+\.jpg)", (here.parent / "src/components/office/DriftmarkDecor.tsx").read_text()))):
    shutil.copy(here.parent / "public/img" / name, d / "img" / name)
(d / "models").mkdir(exist_ok=True)
for m in (here.parent / "public/models").iterdir(): shutil.copy(m, d / "models" / m.name)
print("ok", len(out))
