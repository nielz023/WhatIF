#!/bin/sh
# Maakt dist/page.html na `npm run build` (vite wist hem).
cd "$(dirname "$0")/.." || exit 1
JS=$(grep -o 'assets/index-[^"]*\.js' dist/index.html); CSS=$(grep -o 'assets/index-[^"]*\.css' dist/index.html)
cat > dist/page.html <<EOT
<title>Driftmark HQ</title>
<style>:root{color-scheme:dark}html,body{background:#070b1a}</style>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="./$CSS">
<div id="root"></div>
<script type="module" src="./$JS"></script>
EOT
echo "$JS $CSS"
