#!/bin/sh
# Maakt dist/page.html na `npm run build` (vite wist hem).
cd "$(dirname "$0")/.." || exit 1
JS=$(grep -o 'assets/index-[^"]*\.js' dist/index.html); CSS=$(grep -o 'assets/index-[^"]*\.css' dist/index.html)
# de basisbibliotheken (react, iconen, beweging) tegelijk met de hoofdcode ophalen (verbeterlijst punt 68)
PRE=$(grep -o 'rel="modulepreload"[^>]*href="[^"]*"' dist/index.html | grep -o 'assets/[^"]*\.js' | sed 's#.*#<link rel="modulepreload" href="./&">#')
cat > dist/page.html <<EOT
<title>Driftmark HQ</title>
<style>:root{color-scheme:dark}html,body{background:#060a1c}</style>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="./$CSS">
$PRE
<div id="root"></div>
<script type="module" src="./$JS"></script>
EOT
echo "$JS $CSS"
