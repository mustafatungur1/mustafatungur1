"""Hazırlanmış gri portreden animasyonlu ASCII SVG üretir.

Her satır soldan sağa açılan bir maskeyle, yukarıdan aşağıya sırayla yazılır; sonra durur.
Kullanım: python scripts/make_ascii_svg.py assets/portrait_prepped.png ascii-portrait.svg
"""
import sys
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

COLS = 84
CHAR_W = 5.0          # px, font-size * 0.6 (monospace)
FONT = CHAR_W / 0.6
LINE_H = FONT * 1.0
PAD = 14
WIDTH = 440
MIN_H = 410            # yanındaki bilgi kartıyla aynı yükseklik
BORDER = "#d0d7de"
COLOR = "#1f2328"
BG = "#ffffff"
# Açık zemin: koyu pikseller yoğun karakter; maskelenen arka plan boşluk
RAMP = "@%#*+=-:."
NBSP = "\u00a0"         # tarayıcılar SVG'de baştaki normal boşlukları yutuyor
LINE_DUR = 0.35       # bir satırın yazılma süresi (sn)
LINE_GAP = 0.06       # satırlar arası gecikme (sn)


def to_ascii(path: str, cols: int = COLS, char_w: float = CHAR_W, line_h: float = LINE_H, ramp: str = RAMP) -> list[str]:
    img = Image.open(path).convert("LA")
    w, h = img.size
    # Karakterler kare değil: yüksekliği 0.6/1.0 oranında sıkıştır
    rows = int(h / w * cols * (char_w / line_h))
    arr = np.asarray(img.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    lum, alpha = arr[..., 0], arr[..., 1]
    lum = (lum - lum[alpha > 0.5].min()) / max(np.ptp(lum[alpha > 0.5]), 1e-6)  # kontrastı kişiye yay
    idx = (lum.clip(0, 1) * (len(ramp) - 1)).round().astype(int)
    lines = ["".join(ramp[i] if a > 0.5 else " " for i, a in zip(r, ar)).rstrip()
             for r, ar in zip(idx, alpha)]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def render(lines: list[str]) -> str:
    x0 = (WIDTH - COLS * CHAR_W) / 2
    content_h = PAD * 2 + len(lines) * LINE_H
    height = int(max(content_h, MIN_H))
    top = PAD + (height - content_h) / 2
    defs, texts = [], []
    for i, line in enumerate(lines):
        y = top + i * LINE_H
        begin = 0.3 + i * LINE_GAP
        defs.append(
            f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="{y:.1f}" width="0" height="{LINE_H + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{COLS * CHAR_W:.0f}" '
            f'begin="{begin:.2f}s" dur="{LINE_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        texts.append(
            f'<text x="{x0:.1f}" y="{y + LINE_H * 0.8:.1f}" clip-path="url(#c{i})">{escape(line).replace(' ', NBSP)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}">\n'
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>\n'
        f'<defs>{"".join(defs)}</defs>\n'
        f'<g fill="{COLOR}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{FONT:.2f}" xml:space="preserve" style="white-space:pre">\n' + "\n".join(texts) + "\n</g>\n</svg>\n"
    )


def main(src: str, dst: str) -> None:
    lines = to_ascii(src)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(render(lines))
    print(f"yazıldı: {dst} ({len(lines)} satır)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
