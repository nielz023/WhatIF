"""Bouwt dist/page.html: page.html + actuele status.json als startstand (de pagina leest daarna elke minuut live)."""
import json, pathlib, shutil, sys
here = pathlib.Path(__file__).parent
status = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/driftmark-hq/status.json")
seed = json.dumps(json.loads(status.read_text()), ensure_ascii=False).replace("</", "<\\/")
src = (here / "page.html").read_text()
out = src.replace("<script>\n(function", "<script>window.__DM_SEED__=" + seed + ";</script>\n<script>\n(function", 1)
d = here / "dist"; (d / "img").mkdir(parents=True, exist_ok=True)
(d / "page.html").write_text(out)
for f in (here / "assets").iterdir(): shutil.copy(f, d / "img" / f.name)
print("ok", len(out))
