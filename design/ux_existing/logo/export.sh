#!/usr/bin/env bash
# Render all riffy PNG assets from the source SVGs in ./svg into ./png
# Usage: bash export.sh
set -euo pipefail
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SVG=svg
OUT=png
mkdir -p "$OUT"
WRAP="$(mktemp -d)/wrap.html"

render () {  # src  width  height  outfile
  local src="$1" w="$2" h="$3" out="$4"
  printf '<!doctype html><meta charset=utf-8><style>html,body{margin:0;padding:0;background:transparent}img{display:block;width:100vw;height:100vh}</style><img src="file://%s/%s/%s">' "$PWD" "$SVG" "$src" > "$WRAP"
  "$CHROME" --headless=new --force-device-scale-factor=1 --hide-scrollbars \
    --window-size="$w","$h" --default-background-color=00000000 \
    --virtual-time-budget=2500 --screenshot="$OUT/$out" "file://$WRAP" >/dev/null 2>&1
  echo "  $out  (${w}x${h})"
}

echo "App icon (full-bleed, opaque):"
for s in 1024 512 256 192 180 167 152 120; do render riffy-icon-fullbleed.svg $s $s icon-$s.png; done

echo "Rounded icon + favicons (transparent corners):"
render riffy-icon.svg 512 512 icon-rounded-512.png
render riffy-icon.svg 32  32  favicon-32.png
render riffy-icon.svg 16  16  favicon-16.png

echo "PWA maskable (safe-zone, full-bleed):"
render riffy-icon-fullbleed.svg 512 512 maskable-512.png

echo "Android adaptive layers:"
render riffy-adaptive-foreground.svg 432 432 adaptive-foreground-432.png
render riffy-adaptive-background.svg 432 432 adaptive-background-432.png

echo "Android notification (white silhouette):"
render riffy-notification.svg 96 96 notification-96.png

echo "Marks (transparent):"
render riffy-mark.svg        512 531 mark-512.png
render riffy-mark-white.svg  512 531 mark-white-512.png
render riffy-mark-black.svg  512 531 mark-black-512.png

echo "Wordmark (transparent):"
render riffy-wordmark.svg       1024 517 wordmark-1024.png
render riffy-wordmark-white.svg 1024 517 wordmark-white-1024.png

echo "Lockup (transparent):"
render riffy-lockup.svg       1200 407 lockup-1200.png
render riffy-lockup-white.svg 1200 407 lockup-white-1200.png

echo "Social / splash (opaque):"
render riffy-og.svg     1200 630  og-1200x630.png
render riffy-splash.svg 2732 2732 splash-2732.png

echo "Done."
